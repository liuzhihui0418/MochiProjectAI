import sys
import os

# =================================================================
# 🔥🔥🔥 强制禁用系统代理 (修复别人电脑连不上网/报错500的问题) 🔥🔥🔥
# =================================================================
# 很多用户的电脑开了 VPN 或残留了代理设置，会导致 Python requests 崩溃
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("all_proxy", None)
os.environ.pop("ALL_PROXY", None)
# =================================================================

import urllib3
import warnings
# 禁用不安全的 HTTPS 请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# 同时禁用相关的 SSL 警告
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
# ==========================================
# 🔥🔥🔥 核心修复补丁 (必须放在最前面) 🔥🔥🔥
# ==========================================
# 获取当前运行的临时目录 (PyInstaller 解压后的路径)
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# 强行把这个路径加入 Python 搜索路径
# 这样 Python 才能找到同目录下的 ai_server.py
sys.path.insert(0, base_path)
# ==========================================

# ==========================================
# 🔥 修复 0: 防止无控制台模式下的 print 崩溃
# ==========================================
class NullWriter:
    def write(self, text): pass

    def flush(self): pass

    def isatty(self): return False


if sys.stdout is None or sys.stderr is None:
    sys.stdout = NullWriter()
    sys.stderr = NullWriter()

import asyncio
import logging
import signal
import psutil


# ==========================================
# 🔥 修复 1: 屏蔽 Windows 10054 刷屏报错
# ==========================================
class SuppressWinError10054(logging.Filter):
    def filter(self, record):
        message = str(record.msg)
        # 屏蔽连接重置错误
        if 'WinError 10054' in message or 'ConnectionResetError' in message:
            return False
        # 屏蔽 proactor 相关的连接丢失回调错误
        if 'Exception in callback _ProactorBasePipeTransport._call_connection_lost' in message:
            return False

        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            if isinstance(exc_value, ConnectionResetError):
                return False
        return True


# 将过滤器应用到 asyncio 的 logger
logging.getLogger('asyncio').addFilter(SuppressWinError10054())

# 依然保留这个策略设置，作为双重保险
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import io
import multiprocessing
import json
import shutil
import random
import glob
import threading
import time
import webbrowser
import uvicorn
from typing import Optional
from datetime import datetime

# 第三方库
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import webview

# ==========================================
# 修复 2: 动态路径修复
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 🔥 1. 导入 ai_server 模块
# 确保 ai_server.py 和 main.py 在同一个目录下
import ai_server
import videos
import character_service  # <--- 🔥 新增：导入新建的模块
import character_video_service  # <--- 🔥 导入新文件
import banana_images  # <--- 🔥 新增这一行
# ==========================================
# 👇👇👇 替换 main.py 里的 video_service 导入部分 👇👇👇
# ==========================================

try:
    # 尝试路径 1: 完整路径
    from backend.manager_app.video_service import VideoProcessor, download_file_locally_logic, parse_douyin_video_logic
except ImportError as e1:
    try:
        # 尝试路径 2: 相对路径
        from video_service import VideoProcessor, download_file_locally_logic, parse_douyin_video_logic
    except ImportError as e2:
        print("❌ [严重] 视频服务模块导入失败！")
        print(f"详情 1: {e1}")
        print(f"详情 2: {e2}")
        print("💡 请检查是否安装了 DrissionPage: pip install DrissionPage")


        # 定义占位函数，防止 NameError 崩溃
        def parse_douyin_video_logic(*args, **kwargs):
            return False, "模块加载失败", None, None


        def download_file_locally_logic(*args, **kwargs):
            return False, "模块加载失败"


        class VideoProcessor:
            @staticmethod
            def parse_srt(*args): return []

            @staticmethod
            def split_video_by_segment_muxer(*args, **kwargs): return []
# 引入自定义模块
# ==========================================

# ==========================================
# 👇👇👇 必须全量替换 main.py 里的这块导入代码 👇👇👇
# ==========================================

# 引入自定义模块
try:
    # 路径尝试 1: 完整路径
    from backend.manager_app.config import (
        SystemManager,
        dynamicSpaces,
        CryptoUtils,
        videosSecondSpaces,
        VideosCharacter,
        CharacterLibraryStorage  # <--- 🔥 必须加上这一个！
    )
except ImportError:
    try:
        # 路径尝试 2: 相对路径 (Fallback)
        from config import (
            SystemManager,
            dynamicSpaces,
            CryptoUtils,
            videosSecondSpaces,
            VideosCharacter,
            CharacterLibraryStorage  # <--- 🔥 这里也必须加上！千万不能漏！
        )
    except ImportError:
        print("❌ 严重错误: 无法导入 config 模块，请检查文件路径")
        pass

# ================= 配置 =================
PORT = 8000

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 2. 将 ai_server 的路由挂载到主应用上
# 这样，访问 http://127.0.0.1:8000/rewrite 就会由 ai_server.py 处理
app.include_router(ai_server.router)
app.include_router(videos.router)  # <--- 必须加上这一行！
app.include_router(character_service.router) # <--- 🔥 新增：注册提取角色的路由
# 🔥 注册路由
app.include_router(character_video_service.router)
# 🔥🔥🔥 新增：注册 Banana 生图路由 🔥🔥🔥
app.include_router(banana_images.router)


# 视频目录
VIDEO_ROOT_DIR = r"D:\yunManGongFangAI\Videos"
if not os.path.exists(VIDEO_ROOT_DIR):
    try:
        os.makedirs(VIDEO_ROOT_DIR)
    except:
        pass

app.mount("/video_storage", StaticFiles(directory=VIDEO_ROOT_DIR), name="video_storage")

# 🔥🔥🔥 新增：挂载 Banana 图片目录 🔥🔥🔥
# 必须和 banana_images.py 里的 BANANA_OUTPUT_DIR 保持一致
BANANA_DIR = r"D:\yunManGongFangAI\BananaOutput"
if not os.path.exists(BANANA_DIR):
    try:
        os.makedirs(BANANA_DIR)
    except:
        pass
# 这样前端访问 /banana_storage/xxx.webp 就能看到图了
app.mount("/banana_storage", StaticFiles(directory=BANANA_DIR), name="banana_storage")

# ================= 模型定义 =================
class ActivateReq(BaseModel):
    key: str


class DownloadReq(BaseModel):
    video_url: str
    desc: str


class ProjectReq(BaseModel):
    name: str
    type: str
    ratio: str


class ParseReq(BaseModel):
    url: str


# ================= 接口实现 =================

@app.post("/api/analyze_video")
async def api_analyze_video(
        video_file: UploadFile = File(...),
        srt_file: UploadFile = File(None),
        project_id: str = Form(...),
        project_name: str = Form(...)
):
    try:
        if not os.path.exists("D:/"):
            return {"status": "error", "msg": "❌ 未检测到 D 盘！本软件强制要求 D 盘用于存储视频素材。"}

        project_video_dir = os.path.join(VIDEO_ROOT_DIR, str(project_id))
        os.makedirs(project_video_dir, exist_ok=True)

        video_path = os.path.join(project_video_dir, "source.mp4")
        with open(video_path, "wb") as f:
            shutil.copyfileobj(video_file.file, f)

        subtitles = []
        if srt_file:
            srt_path = os.path.join(project_video_dir, "source.srt")
            with open(srt_path, "wb") as f: shutil.copyfileobj(srt_file.file, f)
            subtitles = VideoProcessor.parse_srt(srt_path)

        clips = VideoProcessor.split_video_by_segment_muxer(video_path, project_video_dir, interval=15)

        for clip in clips:
            clip_start, clip_end = clip['start'], clip['end']
            matched_subs = [s['text'] for s in subtitles if clip_start <= (s['start'] + s['end']) / 2 < clip_end]
            clip['subtitle_text'] = " ".join(matched_subs)

        analysis_data = {
            "project_id": project_id,
            "project_name": project_name,
            "video_source_path": video_path,
            "video_dir": project_video_dir,
            "total_clips": len(clips),
            "clips": clips,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        ok, save_path = dynamicSpaces.save_analysis_result(project_name, analysis_data)
        return {"status": "success", "msg": "处理完成", "data": analysis_data}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.get("/api/project_data/{project_name}")
def api_get_project_data(project_name: str):
    try:
        root = SystemManager.get_root_workspace()
        safe_name = dynamicSpaces._make_safe_name(project_name)
        target_folders = ["SpaceDongSecondTaiMan", "SpaceDongYuanChuangTaiMan"]
        found_file = None
        for folder in target_folders:
            check_dir = os.path.join(root, folder, safe_name, "frameExtractions")
            if os.path.exists(check_dir):
                files = glob.glob(os.path.join(check_dir, "*.dat"))
                if files:
                    files.sort(key=os.path.getmtime, reverse=True)
                    found_file = files[0]
                    break
        if found_file:
            with open(found_file, 'r', encoding='utf-8') as f:
                encrypted = f.read().strip()
                json_str = CryptoUtils.decrypt_aes(encrypted, SystemManager.get_storage_key())
                if json_str:
                    return {"status": "success", "data": json.loads(json_str)}
        return {"status": "empty", "msg": "无历史数据"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


@app.post("/api/download_video_local")
def api_download_video_local(req: DownloadReq):
    success, msg = download_file_locally_logic(req.video_url, req.desc)
    if not success:
        return {"status": "warning", "msg": msg} if "取消" in msg else {"status": "error", "msg": msg}
    return {"status": "success", "msg": msg}


@app.post("/api/parse_video")
def api_parse_video(req: ParseReq):
    success, msg, desc, url = parse_douyin_video_logic(req.url)
    if success:
        return {"status": "success", "desc": desc, "video_url": url}
    else:
        return {"status": "error", "msg": msg}


@app.get("/api/machine_id")
def api_machine_id(): return {"machine_id": CryptoUtils.get_machine_id()}


@app.post("/api/activate")
def api_activate(req: ActivateReq):
    ok, msg = SystemManager.activate_license(req.key)
    return {"success": ok, "message": msg}


@app.get("/api/status")
def api_status():
    ok, info = SystemManager.verify_license()
    return {"activated": ok, "info": info}


@app.get("/api/projects")
def api_get_projects(): return dynamicSpaces.get_all()


@app.post("/api/create_project")
def api_create(req: ProjectReq):
    data = req.dict()
    data['id'] = random.randint(100000, 999999)
    ok, msg = dynamicSpaces.create_space(req.name, data)
    return {"status": "success" if ok else "error", "data": data, "detail": msg}


@app.delete("/api/delete_project/{name}")
def api_delete(name: str):
    ok, msg = dynamicSpaces.delete_space(name)
    return {"status": "success" if ok else "error"}


@app.get("/api/video_stream")
async def api_video_stream(path: str):
    if not os.path.exists(path):
        return {"status": "error", "msg": "文件不存在"}
    return FileResponse(path, media_type="video/mp4")



# 1. 保存接口
@app.post("/api/project/save")
async def save_project_state(data: dict = Body(...)):
    project_name = data.get("project_name")
    clips = data.get("clips")
    # 调用你写的保存类
    success, msg = videosSecondSpaces.save_project_data(project_name, clips)
    return {"status": "success" if success else "error", "msg": msg}

# 2. 加载接口
@app.get("/api/project/load")
async def load_project_state(project_name: str):
    # 调用你写的加载类
    success, data = videosSecondSpaces.load_project_data(project_name)
    if success:
        return {"status": "success", "data": data}
    else:
        return {"status": "empty", "msg": "No saved data found"}

# 3. 角色库保存接口
@app.post("/api/character/save")
async def save_character_library(data: dict = Body(...)):
    project_name = data.get("project_name")
    characters = data.get("characters")
    # 调用保存
    success, msg = VideosCharacter.save_characters(project_name, characters)
    return {"status": "success" if success else "error", "msg": msg}

# 4. 角色库加载接口
@app.get("/api/character/load")
async def load_character_library(project_name: str):
    success, data = VideosCharacter.load_characters(project_name)
    if success:
        return {"status": "success", "data": data}
    else:
        return {"status": "error", "msg": "Load failed"}


# ================= 风格角色档案库接口 (项目级) =================

@app.get("/api/style_library/load")
async def load_style_library(project_name: str):
    """
    加载指定项目的风格档案库
    需要参数: ?project_name=xxx
    """
    # 调用刚才写的类，传入 project_name
    success, data = CharacterLibraryStorage.load_library(project_name)
    if success:
        return {"status": "success", "data": data}
    else:
        return {"status": "error", "msg": str(data)}


@app.post("/api/style_library/save")
async def save_style_library(data: dict = Body(...)):
    """
    保存指定项目的风格档案库
    """
    project_name = data.get("project_name")
    characters = data.get("characters", [])

    if not project_name:
        return {"status": "error", "msg": "Missing project_name"}

    success, msg = CharacterLibraryStorage.save_library(project_name, characters)
    return {"status": "success" if success else "error", "msg": msg}

# ================= 静态文件 =================
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_path()
DIST_DIR = os.path.join(BASE_DIR, "dist")

if os.path.exists(DIST_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")


    @app.get("/{full_path:path}")
    async def serve_vue_app(full_path: str):
        # 🔥 修改这里：添加 analyze_prompt 到排除列表
        # 凡是 API 相关的请求，都让它穿透过去，不要返回 index.html
        if (full_path.startswith("api") or
                full_path.startswith("video_storage") or
                full_path.startswith("rewrite") or
                full_path.startswith("analyze_prompt")):
            raise HTTPException(status_code=404, detail="Not Found")

        index_path = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "UI files not found"}

# ================= 🚀 启动逻辑 =================

MODE = "GUI"  # "GUI" 或 "WEB"
server_instance = None

# 辅助函数：杀掉占用端口的进程
def release_port(port):
    """查找并终止占用指定端口的进程"""
    try:
        # print(f"🔍 检查端口 {port} 是否被占用...")
        # 注释掉 print 防止无控制台模式下极小概率的 I/O 错误
        found = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        # print(f"⚠️ 发现进程 {proc.info['name']} (PID: {proc.info['pid']}) 正在使用端口 {port}")
                        proc.terminate()
                        proc.wait(timeout=3)
                        # print(f"✅ 已终止 PID {proc.info['pid']}")
                        found = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            except Exception:
                pass
        if not found:
            pass  # print("✅ 端口空闲")
        time.sleep(1)
    except Exception:
        pass


def start_server():
    global server_instance
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="warning",  # 降低日志级别
        loop="asyncio"
    )
    server_instance = uvicorn.Server(config)
    server_instance.run()


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # 1. 启动前清理端口
    try:
        release_port(PORT)
    except:
        pass

    # 2. 启动后端线程
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    # 3. 根据模式执行
    if MODE == "GUI":
        time.sleep(1)
        try:
            webview.create_window(
                title="YunManGongFangAI",
                url=f"http://127.0.0.1:{PORT}",
                width=1440,
                height=900,
                resizable=True,
                confirm_close=True
            )
            webview.start()
        except Exception as e:
            pass

        if server_instance:
            server_instance.should_exit = True

    elif MODE == "WEB":
        print("=" * 50)
        print(f"🚀 服务已启动！请在浏览器访问：http://127.0.0.1:{PORT}")
        print("=" * 50)
        time.sleep(2)
        webbrowser.open(f"http://127.0.0.1:{PORT}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            if server_instance:
                server_instance.should_exit = True
            sys.exit(0)