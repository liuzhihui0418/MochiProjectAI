# character_video_service.py
import os
import time
import json
import base64
import threading
import uuid
import requests
import logging
from fastapi import APIRouter
from pydantic import BaseModel
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter()

# ================= 配置区域 =================
# 视频保存根目录 (请确保路径正确)
VIDEO_SAVE_DIR = r"D:\yunManGongFangAI\Videos\Characters"
if not os.path.exists(VIDEO_SAVE_DIR):
    os.makedirs(VIDEO_SAVE_DIR, exist_ok=True)

# API KEY
API_KEY = "sk-VGte3SS7TDxOba718ET7sIOHCZTYowrawdlD2id4QCi2Bnx7"

# 任务存储 (内存中)
character_tasks_store = {}

# ================= 提示词模板 =================
PROMPT_TEMPLATE = """核心指令： 创建一个10秒无缝循环视频，并贴合作品形象创建角色声音，以较快的语速、清晰的口型重复一句对白，确保视听高度同步。

1. 场景与镜头：
背景： 纯白色背景（RGB 255,255,255），无阴影、纹理、渐变或杂物。
镜头： 固定全身镜头。人物从头到脚完整居中，镜头绝对静止。

2. 人物描述：
身份/外观： {description}

3.姿态： 自然站立。为配合快语速，手部可伴有简短、干脆的辅助手势（如说话时轻微摊手）。
表情与视线： 面带热情、感激的微笑。保持眼神交流。

4. 对白与音频（逻辑重构区）：
文本内容： “我是作品中的{label}，欢迎您使用我的角色。”

播报方式（全新逻辑）：
循环逻辑： 这句话的正常语速时长假设为T秒。在10秒内，将这段加速后的音频无缝循环播放，确保循环次数为整数次。
核心同步： 人物口型、加速的音频波形，两者必须在整个10秒内保持严格的帧级同步。

5. 技术规格与风格：
时长： 精确10秒。
景别： 固定全身镜头。
循环性： 第10秒末与第0秒初的状态（口型相位、音频相位）必须严丝合缝地衔接。
风格： 高质量3D渲染，灯光均匀无影，重点优化面部和嘴部动画的精度与清晰度。
"""

# 定义前端请求的参数结构
class MatchReq(BaseModel):
    task_id: str  # 对应 API 里的 from_task

# ================= API 工具类 =================
# ================= API 工具类 (修复版) =================
class YunWuClient:
    def __init__(self, api_key):
        self.base_url = "https://yunbaoymgf.chat"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Python/YunWuClient-v2'  # 伪装UA
        }
        self.session = requests.Session()

        # 🔥 增强重试机制 (针对 Cloudflare 和网络波动)
        retries = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504, 520, 522],
            allowed_methods=["POST", "GET"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def image_to_base64(self, path_or_data):
        """
        万能图片转Base64 (增强版)
        """
        if not path_or_data:
            return None

        # [情况1] 已经是 Base64
        if path_or_data.startswith("data:image"):
            return path_or_data

        # [情况2] 网络图片 URL (增加重试与超时)
        if path_or_data.startswith("http://") or path_or_data.startswith("https://"):
            try:
                logging.info(f"正在下载网络图片: {path_or_data}")
                # verify=False 忽略证书错误，timeout=60 避免卡死
                resp = requests.get(
                    path_or_data,
                    timeout=60,
                    verify=False,
                    proxies={"http": None, "https": None}
                )
                if resp.status_code == 200:
                    encoded = base64.b64encode(resp.content).decode('utf-8')
                    return f"data:image/jpeg;base64,{encoded}"
                else:
                    logging.error(f"网络图片下载失败 Code: {resp.status_code}")
                    return None
            except Exception as e:
                logging.error(f"网络图片下载异常: {e}")
                return None

        # [情况3] 本地文件路径
        if os.path.exists(path_or_data):
            try:
                with open(path_or_data, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode('utf-8')
                    return f"data:image/jpeg;base64,{encoded}"
            except Exception as e:
                logging.error(f"读取本地图片失败: {e}")
                return None

        return None

    def submit_task(self, prompt, image_path):
        url = f"{self.base_url}/v1/video/create"
        payload = {
            "model": "sora-2",
            "prompt": prompt,
            "size": "1080x1920",
            "duration": 10,
            "images": []
        }

        if image_path:
            b64 = self.image_to_base64(image_path)
            if b64:
                payload["images"].append(b64)
            else:
                logging.warning("图片转换失败，将仅使用纯文本生成")

        try:
            # 🔥 核心修复：Timeout=300, verify=False
            resp = self.session.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=300,  # 5分钟超时
                verify=False,  # 忽略SSL错误
                proxies={"http": None, "https": None}
            )

            resp.raise_for_status()
            data = resp.json()
            if 'id' in data: return data['id']
            if 'data' in data and 'id' in data['data']: return data['data']['id']

            logging.error(f"提交响应格式异常: {data}")
            return None

        except requests.exceptions.SSLError:
            logging.error("SSL 握手失败，请检查网络环境")
            raise
        except requests.exceptions.ConnectionError:
            logging.error("连接被断开 (RemoteDisconnected)，可能文件过大或网络波动")
            raise
        except Exception as e:
            logging.error(f"提交失败: {e}")
            raise e

    def query_status(self, task_id):
        url = f"{self.base_url}/v1/video/query?id={task_id}"
        try:
            # 🔥 核心修复：Timeout=300, verify=False
            resp = self.session.get(
                url,
                headers=self.headers,
                timeout=300,
                verify=False,
                proxies={"http": None, "https": None}
            )
            return resp.json()
        except Exception as e:
            logging.warning(f"查询状态失败(可忽略): {e}")
            return None

    def download(self, url, save_path):
        try:
            # 🔥 核心修复：Timeout=300, verify=False
            with self.session.get(
                    url,
                    stream=True,
                    timeout=300,
                    verify=False,
                    proxies={"http": None, "https": None}
            ) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return True
        except Exception as e:
            logging.error(f"下载失败: {e}")
            return False


def resolve_local_path(url_or_path: str):
    """将 http://localhost.../video_storage/... 转为本地 D 盘路径"""
    if "video_storage" in url_or_path:
        try:
            rel_path = url_or_path.split("video_storage/")[-1]
            full_path = os.path.join(r"D:\yunManGongFangAI\Videos", rel_path.replace("/", os.sep))
            # 解码 URL 中的中文字符
            import urllib.parse
            full_path = urllib.parse.unquote(full_path)
            return full_path
        except:
            pass
    return url_or_path


def background_worker(job_id, label, description, image_url):
    task = character_tasks_store[job_id]
    client = YunWuClient(API_KEY)

    try:
        prompt = PROMPT_TEMPLATE.format(label=label, description=description)
        local_img_path = resolve_local_path(image_url)

        task['msg'] = "正在提交到云端..."
        external_id = client.submit_task(prompt, local_img_path)

        if not external_id:
            raise Exception("API 未返回任务 ID")

        task['external_id'] = external_id
        task['status'] = "processing"

        start_time = time.time()
        while time.time() - start_time < 900:  # 等待 15 分钟
            status_data = client.query_status(external_id)

            remote_status = "unknown"
            video_url = None

            if status_data:
                if "status" in status_data:
                    remote_status = status_data["status"]
                elif "data" in status_data:
                    remote_status = status_data["data"].get("status")

                if "video_url" in status_data:
                    video_url = status_data["video_url"]
                elif "data" in status_data:
                    video_url = status_data["data"].get("video_url")

            elapsed = time.time() - start_time
            # 伪进度条逻辑优化
            if remote_status == "queued":
                task['msg'] = "云端排队中..."
                task['progress'] = 10
            elif remote_status == "processing":
                fake_progress = 10 + int((elapsed / 300) * 80)
                if fake_progress > 90: fake_progress = 90
                task['progress'] = fake_progress
                task['msg'] = f"云端渲染中... {fake_progress}%"

            if remote_status in ["success", "completed"]:
                if video_url:
                    task['msg'] = "下载视频中..."
                    filename = f"{label}_{uuid.uuid4().hex[:6]}.mp4"
                    save_path = os.path.join(VIDEO_SAVE_DIR, filename)

                    if client.download(video_url, save_path):
                        task['status'] = "success"
                        task['progress'] = 100
                        task['msg'] = "生成完成"
                        # 生成 Web 访问链接 (注意要进行 URL 编码以支持中文文件名)
                        import urllib.parse
                        encoded_filename = urllib.parse.quote(filename)
                        task['result_url'] = f"http://127.0.0.1:8000/video_storage/Characters/{encoded_filename}"
                        return
                else:
                    raise Exception("任务成功但无视频地址")

            elif remote_status in ["failed", "error"]:
                err = status_data.get("error") or status_data.get("data", {}).get("error") or "未知错误"
                raise Exception(f"云端生成失败: {err}")

            time.sleep(5)

        raise Exception("任务超时 (15分钟)")

    except Exception as e:
        logging.error(f"任务异常: {e}")
        task['status'] = "failed"
        task['msg'] = str(e)


# ================= 接口定义 =================
class CharVideoRequest(BaseModel):
    character_id: str | int
    label: str
    description: str
    image_url: str


@router.post("/generate_character_video")
def submit_character_video(req: CharVideoRequest):
    job_id = str(uuid.uuid4())
    character_tasks_store[job_id] = {
        "status": "pending",
        "progress": 0,
        "msg": "准备中...",
        "character_id": req.character_id
    }
    t = threading.Thread(
        target=background_worker,
        args=(job_id, req.label, req.description, req.image_url)
    )
    t.daemon = True
    t.start()
    return {"status": "success", "job_id": job_id, "msg": "任务已提交后台"}


@router.get("/api/character_task_status/{job_id}")
def get_character_task_status(job_id: str):
    if job_id not in character_tasks_store:
        return {"status": "error", "msg": "任务不存在"}

    task = character_tasks_store[job_id]
    return {
        "status": task['status'],
        "progress": task['progress'],
        "msg": task['msg'],
        "video_url": task.get('result_url'),
        # 🔥 新增：返回外部任务ID给前端，用于后续匹配ID
        "external_id": task.get('external_id')
    }


# ================= 匹配角色ID 接口 (修复版) =================
@router.post("/match_character_id")
def match_character_id_api(req: MatchReq):
    import http.client
    import json
    import ssl

    if not req.task_id:
        return {"status": "error", "msg": "缺少任务ID (from_task)"}

    # 🔥 修改点1：使用和你生成视频一样的域名 (中转商域名)
    host = "yunbaoymgf.chat"

    # 🔥 修改点2：忽略 SSL 证书验证，防止报错
    context = ssl._create_unverified_context()

    # 🔥 修改点3：设置超时时间 1200秒，防止一直卡住
    conn = http.client.HTTPSConnection(host, context=context, timeout=1200)

    # 构建 Payload
    payload = json.dumps({
        "timestamps": "1,3",
        "from_task": req.task_id
    })

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        logging.info(f"正在匹配角色ID... Task: {req.task_id}, Host: {host}")

        # 发送请求
        # 注意：如果中转商的路径不同，可能需要改为 /v1/sora/characters
        # 但通常保持原样即可，先试 /sora/v1/characters
        conn.request("POST", "/sora/v1/characters", payload, headers)

        res = conn.getresponse()
        data = res.read()
        response_str = data.decode("utf-8")

        logging.info(f"API 原始响应: {response_str}")  # 🔥 看控制台这里输出了什么

        if res.status != 200:
            return {"status": "error", "msg": f"API请求失败 [{res.status}]: {response_str}"}

        result = json.loads(response_str)

        # 解析 username 和 permalink (兼容多种返回格式)
        username = ""
        permalink = ""

        # 情况A: 直接在根目录
        if isinstance(result, dict) and "username" in result:
            username = result["username"]
            permalink = result.get("permalink", "")
        # 情况B: 在 data 对象里
        elif isinstance(result, dict) and "data" in result:
            if isinstance(result["data"], dict):
                username = result["data"].get("username")
                permalink = result["data"].get("permalink", "")
            elif isinstance(result["data"], list) and len(result["data"]) > 0:
                username = result["data"][0].get("username")
                permalink = result["data"][0].get("permalink", "")

        if username:
            # 🔥 核心修改：同时返回 permalink
            return {
                "status": "success",
                "username": username,
                "permalink": permalink
            }
        else:
            return {"status": "error", "msg": "响应中未找到username", "raw": result}

    except Exception as e:
        logging.error(f"匹配接口异常: {str(e)}")
        return {"status": "error", "msg": str(e)}
    finally:
        conn.close()