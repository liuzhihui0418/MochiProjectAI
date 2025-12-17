# 文件名: videos.py
import json
import os
import threading
import time
import base64
import uuid
import logging
import subprocess  # 用于调用命令行
import requests
from fastapi import APIRouter
from pydantic import BaseModel

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 创建路由器
router = APIRouter()

# 视频存储路径 (请确保此路径存在)
VIDEO_ROOT_DIR = r"D:\yunManGongFangAI\Videos"
if not os.path.exists(VIDEO_ROOT_DIR):
    os.makedirs(VIDEO_ROOT_DIR, exist_ok=True)


# ================= 视频生成类 =================
class YunWuVideoGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://yunbaoymgf.chat"
        self.api_submit_path = "/v1/video/create"
        self.api_query_path = "/v1/video/query"
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504],
                        allowed_methods=["POST", "GET"])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Python/YunWuClient-FastAPI'
        }

    def _image_to_base64(self, image_path):
        if not os.path.exists(image_path): return None
        try:
            with open(image_path, "rb") as f:
                return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode('utf-8')}"
        except Exception as e:
            logging.error(f"图片转Base64失败: {e}")
            return None

    def make_http_request(self, method, path, payload=None):
        url = f"{self.base_url}{path}"
        try:
            if method == "POST":
                response = self.session.post(url, data=payload, headers=self.headers, timeout=60)
            else:
                response = self.session.get(url, headers=self.headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"请求异常: {e}")
            raise e

    def submit_video_task(self, prompt, image_path=None, duration=15, orientation="portrait"):
        payload = {
            "model": "sora-2", "orientation": orientation, "prompt": prompt,
            "size": "large", "duration": duration, "watermark": False, "images": []
        }
        if image_path:
            b64 = self._image_to_base64(image_path)
            if b64: payload["images"].append(b64)
        try:
            json_payload = json.dumps(payload)
            resp = self.make_http_request("POST", self.api_submit_path, json_payload)
            if not resp: return None
            if 'id' in resp: return resp['id']
            if 'task_id' in resp: return resp['task_id']
            if 'data' in resp and isinstance(resp['data'], dict):
                return resp['data'].get('id') or resp['data'].get('task_id')
            return None
        except Exception as e:
            logging.error(f"提交任务失败: {e}")
            return None

    def query_task_status(self, task_id):
        try:
            return self.make_http_request("GET", f"{self.api_query_path}?id={task_id}")
        except Exception as e:
            logging.warning(f"查询状态失败: {e}")
            return None

    def download_video(self, url, save_path):
        try:
            with self.session.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return save_path
        except Exception as e:
            logging.error(f"下载视频失败: {e}")
            return None


# ================= 任务状态管理 =================
video_tasks_store = {}


def generate_thumbnail_ffmpeg(video_path):
    """
    使用 FFmpeg 生成视频封面图，防崩溃版
    """
    try:
        if not os.path.exists(video_path):
            logging.error(f"视频文件不存在，无法生成封面: {video_path}")
            return None

        # 构造封面图路径 (.jpg)
        thumbnail_path = os.path.splitext(video_path)[0] + ".jpg"

        # 绝对路径处理，防止路径中有特殊字符导致问题
        video_path = os.path.abspath(video_path)
        thumbnail_path = os.path.abspath(thumbnail_path)

        # 构造命令
        cmd = [
            'ffmpeg', '-y',  # 覆盖输出
            '-i', video_path,  # 输入文件
            '-ss', '0.1',  # 时间点
            '-vframes', '1',  # 只截取1帧
            '-q:v', '2',  # 图片质量
            thumbnail_path  # 输出文件
        ]

        logging.info(f"正在生成封面: {' '.join(cmd)}")

        # 执行命令 (Windows 下 shell=True 有助于找到 ffmpeg，但要注意路径转义)
        # capture_output=True 可以防止控制台弹出黑框
        result = subprocess.run(
            cmd,
            shell=True if os.name == 'nt' else False,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            logging.error(f"FFmpeg执行失败: {result.stderr}")
            return None

        if os.path.exists(thumbnail_path):
            logging.info(f"封面生成成功: {thumbnail_path}")
            return thumbnail_path

        return None

    except FileNotFoundError:
        logging.error("未找到 FFmpeg，请先安装 FFmpeg 并添加到系统环境变量！")
        return None
    except Exception as e:
        logging.error(f"生成封面时发生未知错误: {str(e)}")
        return None


def background_video_worker(job_id, api_key, prompt, output_path, duration=15):
    """
    后台生成线程，修复取消后仍在跑的问题
    """
    generator = YunWuVideoGenerator(api_key)
    store = video_tasks_store[job_id]

    try:
        # 1. 启动前检查
        if store.get('status') == 'cancelled':
            logging.info(f"Job {job_id} 在启动前被取消")
            return

        store['status'] = 'submitting'
        store['msg'] = '正在提交任务...'

        task_id = generator.submit_video_task(prompt, duration=duration)
        if not task_id:
            raise Exception("提交失败：服务器未返回 Task ID")

        store['status'] = 'processing'
        store['msg'] = f'排队中 (ID: {task_id[:8]})'
        store['external_task_id'] = task_id

        start_time = time.time()
        timeout = 1800
        estimated_duration = 150

        while (time.time() - start_time) < timeout:
            # 2. 循环中检查取消
            if store.get('status') == 'cancelled':
                logging.info(f"Job {job_id} 循环中被取消")
                return

            # 进度模拟
            elapsed = time.time() - start_time
            fake_progress = int((elapsed / estimated_duration) * 95)
            if fake_progress > 95: fake_progress = 95

            # 查询状态
            status_res = generator.query_task_status(task_id)
            if not status_res:
                time.sleep(3)
                continue

            raw_status = "unknown"
            video_url = None

            if "status" in status_res: raw_status = status_res["status"]
            if "video_url" in status_res: video_url = status_res["video_url"]
            if "data" in status_res and isinstance(status_res["data"], dict):
                data = status_res["data"]
                if "status" in data: raw_status = data["status"]
                if "video_url" in data: video_url = data["video_url"]

            store['progress'] = fake_progress
            store['msg'] = f"AI生成中... {fake_progress}%"

            # === 成功处理逻辑 (重点修改区域) ===
            if raw_status in ["success", "completed", "finished"]:
                if video_url:
                    store['msg'] = "正在下载视频 (98%)..."
                    store['progress'] = 98

                    # 🔥🔥🔥 重点 1：下载前再次检查取消
                    if store.get('status') == 'cancelled':
                        logging.info(f"Job {job_id} 在下载前被取消，停止操作")
                        return

                    if generator.download_video(video_url, output_path):

                        # 🔥🔥🔥 重点 2：下载后、生成封面前，再次检查取消！
                        # (防止下载耗时期间用户点了取消，导致FFmpeg继续执行)
                        if store.get('status') == 'cancelled':
                            logging.info(f"Job {job_id} 在生成封面前被取消，停止操作")
                            return

                        store['msg'] = "正在生成预览图..."
                        thumb_path = generate_thumbnail_ffmpeg(output_path)

                        if thumb_path:
                            store['thumb_filename'] = os.path.basename(thumb_path)

                        store['progress'] = 100
                        store['status'] = 'success'
                        store['msg'] = '生成完成'
                        store['result'] = output_path
                        return
                raise Exception("生成成功但未返回下载地址")

            elif raw_status in ["failed", "error"]:
                err_msg = status_res.get("error", "未知错误")
                raise Exception(f"任务失败: {err_msg}")

            time.sleep(3)

        raise Exception("任务执行超时")

    except Exception as e:
        if store.get('status') == 'cancelled':
            return
        store['status'] = 'failed'
        store['msg'] = str(e)
        logging.error(f"Job {job_id} Error: {e}")


# ================= API 路由 =================
class GenerateVideoReq(BaseModel):
    prompt: str
    project_id: str = "default"
    clip_index: int = 0
    api_key: str = "your_key_here"


@router.post("/api/generate_video")
def api_generate_video_task(req: GenerateVideoReq):
    if not req.prompt: return {"status": "error", "msg": "提示词不能为空"}

    # ⚠️ 请确保 Key 正确
    real_key = "sk-VGte3SS7TDxOba718ET7sIOHCZTYowrawdlD2id4QCi2Bnx7"

    job_id = str(uuid.uuid4())
    project_dir = os.path.join(VIDEO_ROOT_DIR, req.project_id)
    os.makedirs(project_dir, exist_ok=True)
    filename = f"generated_{req.clip_index}_{int(time.time())}.mp4"
    output_path = os.path.join(project_dir, filename)

    video_tasks_store[job_id] = {
        "status": "pending", "progress": 0, "msg": "准备中",
        "result": None, "filename": filename, "project_id": req.project_id
    }

    t = threading.Thread(target=background_video_worker, args=(job_id, real_key, req.prompt, output_path))
    t.daemon = True
    t.start()
    return {"status": "success", "job_id": job_id, "msg": "任务已提交"}

# 🔥【关键点4】新增取消接口
@router.post("/api/cancel_task/{job_id}")
def api_cancel_task(job_id: str):
    if job_id in video_tasks_store:
        video_tasks_store[job_id]['status'] = 'cancelled'
        video_tasks_store[job_id]['msg'] = '正在取消...'
        logging.info(f"收到取消请求: {job_id}")
        return {"status": "success", "msg": "任务已标记取消"}
    return {"status": "error", "msg": "任务ID不存在"}


@router.get("/api/task_status/{job_id}")
def api_check_task_status(job_id: str):
    if job_id not in video_tasks_store: return {"status": "error", "msg": "任务不存在"}
    task = video_tasks_store[job_id]

    response = {
        "status": task['status'],
        "progress": task.get('progress', 0),
        "msg": task.get('msg', '')
    }

    if task['status'] == 'success':
        # 视频 URL
        relative_path = f"/{task['project_id']}/{task['filename']}"
        response["video_url"] = f"http://127.0.0.1:8000/video_storage{relative_path}"

        # ✅ 返回封面 URL
        if 'thumb_filename' in task:
            thumb_relative = f"/{task['project_id']}/{task['thumb_filename']}"
            response["cover_url"] = f"http://127.0.0.1:8000/video_storage{thumb_relative}"

    return response