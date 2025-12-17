# 文件位置: backend/manager_app/video_service.py

import os
import re
import glob
import subprocess
import shutil
import time
import requests
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from DrissionPage._configs.chromium_options import ChromiumOptions
from DrissionPage._pages.chromium_page import ChromiumPage

try:
    from backend.manager_app.config import SystemManager
except ImportError:
    from config import SystemManager


# ================= 0. 全局配置与单例管理 (增强版) =================

class BrowserManager:
    """
    🔥 浏览器单例管理器 (防断连版)
    """
    _page = None

    @classmethod
    def get_page(cls):
        # 1. 如果从未初始化，则初始化
        if cls._page is None:
            return cls._init_browser()

        # 2. 如果已存在，检查连接是否正常
        try:
            # 尝试发送一个轻量级指令测试连接
            # 如果浏览器已关闭或断连，这里会抛出异常
            if not cls._page.rect:
                raise Exception("窗口句柄丢失")
            cls._page.run_cdp('Browser.getVersion')  # 测试 CDP 连接
        except Exception as e:
            print(f"⚠️ 检测到浏览器连接断开 ({e})，正在自动重启...")
            cls.close()  # 确保清理旧进程
            return cls._init_browser()  # 重新启动

        return cls._page

    @classmethod
    def _init_browser(cls):
        print("🚀 [系统] 正在初始化后台浏览器实例...")
        try:
            co = ChromiumOptions()
            co.auto_port()  # 自动寻找可用端口
            co.headless(True)  # 无头模式
            co.mute(True)  # 静音

            # 关键配置：增加稳定性
            co.set_argument('--no-sandbox')
            co.set_argument('--disable-gpu')
            co.set_argument('--disable-dev-shm-usage')  # 防止内存溢出崩溃
            co.set_argument('--blink-settings=imagesEnabled=false')  # 不加载图片

            # 设置超时时间
            co.set_timeouts(base=15)

            cls._page = ChromiumPage(co)
            return cls._page
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            return None

    @classmethod
    def close(cls):
        try:
            if cls._page:
                cls._page.quit()
        except:
            pass
        finally:
            cls._page = None


# 建立全局 Session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})


# ================= 1. 视频处理核心类 =================
class VideoProcessor:
    @staticmethod
    def get_assets_dir(root_workspace, project_id):
        path = os.path.join(root_workspace, "temp_assets", str(project_id))
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def srt_time_to_seconds(time_str):
        time_str = time_str.replace(',', '.')
        try:
            h, m, s = time_str.split(':')
            return int(h) * 3600 + int(m) * 60 + float(s)
        except:
            return 0.0

    @staticmethod
    def parse_srt(srt_path):
        subtitles = []
        if not os.path.exists(srt_path): return subtitles
        try:
            with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            pattern = re.compile(
                r'(\d+)\s*\n(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*\n([\s\S]+?)(?=\n\n|\Z)',
                re.MULTILINE)
            matches = pattern.findall(content)
            for m in matches:
                subtitles.append({
                    "start": VideoProcessor.srt_time_to_seconds(m[1]),
                    "end": VideoProcessor.srt_time_to_seconds(m[2]),
                    "text": m[3].strip().replace('\n', ' ')
                })
        except Exception as e:
            print(f"SRT解析失败: {e}")
        return subtitles

    @staticmethod
    def split_video_by_segment_muxer(video_path, output_dir, interval=15):
        """
        🔥 [终极精准版] 强制关键帧 + 关闭场景检测
        """
        output_pattern = os.path.join(output_dir, "segment_%03d.mp4")

        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-map', '0',

            # --- 视频编码设置 ---
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',

            # 🔥 核心修复 1: 强制每隔 interval 秒插入一个关键帧
            # 这样切片器走到 15秒 时，正好踩在关键帧上，必定会切
            '-force_key_frames', f'expr:gte(t,n_forced*{interval})',

            # 🔥 核心修复 2: 关闭场景切换检测 (防止它在 14.9秒 自动插帧导致切片错位)
            '-sc_threshold', '0',

            # --- 音频编码设置 ---
            '-c:a', 'aac',
            '-b:a', '192k',

            # --- 切片设置 ---
            '-f', 'segment',
            '-segment_time', str(interval),
            '-reset_timestamps', '1',
            output_pattern
        ]

        print(f"✂️ [FFmpeg终极切片] 执行: {' '.join(cmd)}")

        use_shell = True if os.name == 'nt' else False

        try:
            subprocess.run(cmd, shell=use_shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"❌ 切片失败: {e}")
            return []

        files = sorted(glob.glob(os.path.join(output_dir, "segment_*.mp4")))

        clips_info = []
        for idx, file_path in enumerate(files):
            filename = os.path.basename(file_path)
            # 计算理论时间，防止界面显示误差
            start_time = idx * interval
            end_time = (idx + 1) * interval

            clips_info.append({
                "index": idx,
                "path": file_path,
                "url": filename,
                "start": start_time,
                "end": end_time
            })

        return clips_info

    @staticmethod
    def _split_video_reencode(video_path, output_dir, interval=15):
        """备用：重编码模式"""
        output_pattern = os.path.join(output_dir, "segment_%03d.mp4")
        cmd = [
            'ffmpeg', '-y', '-threads', '0',
            '-i', video_path, '-map', '0',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '25',
            '-c:a', 'aac', '-b:a', '128k',
            '-f', 'segment', '-segment_time', str(interval),
            '-reset_timestamps', '1',
            output_pattern
        ]
        use_shell = True if os.name == 'nt' else False
        subprocess.run(cmd, shell=use_shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# ================= 2. 视频下载逻辑 =================
def download_file_locally_logic(url, desc):
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title=f"请选择保存位置 - {desc[:10]}...")
        root.destroy()

        if not folder_path:
            return False, "用户取消了选择"

        safe_name = "".join([c for c in desc if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not safe_name: safe_name = f"video_{int(time.time())}"
        safe_name = safe_name[:50]

        file_path = os.path.join(folder_path, f"{safe_name}.mp4")

        with session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)

        return True, f"下载成功！保存至: {file_path}"

    except Exception as e:
        return False, str(e)


# ================= 3. 抖音解析逻辑 (强化版) =================
def parse_douyin_video_logic(raw_url):
    page = None
    tab = None
    try:
        # 1. 正则提取 URL
        url_pattern = re.compile(r'(https?://[a-zA-Z0-9\./\-_]+)')
        match = url_pattern.search(raw_url)

        if not match:
            return False, "未在文本中检测到有效的链接", None, None

        target_url = match.group(0)

        # 2. 解析短链 -> 长链
        if "v.douyin.com" in target_url:
            try:
                resp = session.get(target_url, allow_redirects=True, timeout=10)
                target_url = resp.url
            except:
                pass

        # 3. DrissionPage 解析
        page = BrowserManager.get_page()
        if not page:
            return False, "浏览器初始化失败", None, None

        # 打开新标签页
        tab = page.new_tab()

        # 核心：先开始监听，再访问
        tab.listen.start('aweme/v1/web/aweme/detail/')
        tab.get(target_url)

        # 等待数据包
        res = tab.listen.wait(timeout=15)

        if res:
            data = res.response.body
            video_info = data.get('aweme_detail', {})
            desc = video_info.get('desc', '未命名视频')
            url_list = video_info.get('video', {}).get('play_addr', {}).get('url_list', [])

            if url_list:
                # 成功后关闭标签页
                try:
                    tab.close()
                except:
                    pass
                return True, "解析成功", desc, url_list[-1]
            else:
                try:
                    tab.close()
                except:
                    pass
                return False, "未找到视频地址", None, None
        else:
            # 超时
            try:
                tab.close()
            except:
                pass
            return False, "解析超时", None, None

    except Exception as e:
        # 发生严重错误时，关闭标签页，并在 BrowserManager 标记异常
        print(f"❌ 解析逻辑异常: {e}")
        try:
            if tab: tab.close()
        except:
            # 如果 tab 关闭失败，说明浏览器可能崩了，重置单例
            BrowserManager.close()

        return False, f"解析出错: {str(e)}", None, None