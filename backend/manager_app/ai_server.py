import os
import sys
import time
import os
import sys
import time
import shutil
import tempfile
import http.client
import json
from fastapi import APIRouter
from pydantic import BaseModel

# 🔥 移除 Google SDK，引入阿里云 SDK
import dashscope
from dashscope import MultiModalConversation

# 🔥🔥 修复 Windows 下 print 中文报错的核心代码 🔥🔥
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

router = APIRouter()

# 🔥🔥🔥 配置你的 API Key 🔥🔥🔥
# 这里填入你的阿里云 DashScope API Key (sk-开头)
DASHSCOPE_API_KEY = "sk-b6731664f50f40df85f03997962cf1f2"
dashscope.api_key = DASHSCOPE_API_KEY

# 🔥 修正模型名称：阿里云最强视觉模型
MODEL_NAME = "qwen-vl-max"


# ================= 数据模型 (保持不变) =================
class AnalyzeRequest(BaseModel):
    video_path: str
    subtitle_text: str


class RewriteRequest(BaseModel):
    text: str

# ================= 常量定义 (保持不变) =================
DEFAULT_ROLE_PROMPT = """将文案改为剧本格式（需要注意，该文案仅为片段）。
根据剧情输出3-5个剧本镜头，输出内容包含：时间（总长度不超过13秒）、文案内容（解说词）、画面描述、运镜方式、声音设计。
输出结果不要解释、说明、思考过程，仅输出结论。
输出示例：

00:00-00:03	孩子也是早出晚归的小战士！	特写/中景： 一个小小的背影（可能是小学生或初中生）站在明亮的晨光中，背着一个看起来有点沉的蓝色/深色书包，侧脸坚毅但略带疲惫。	慢速推近（Slow Push-in），聚焦书包和孩子的侧脸。	BGM引入： 轻柔、带点史诗感（但不沉重）的钢琴或弦乐旋律。加入清脆的鸟鸣声和清晨微风声。
00:03-00:06	晨光中出门，夜色里归家，	场景切换： 画面一分为二或快速剪辑：<br>1. 左/上（晨光）： 孩子身影被初升的太阳拉长。<br>2. 右/下（夜色）： 孩子在略显昏暗的街道灯光下，步伐略显沉重地走着，背景有微弱的城市灯光。	快速交替的分割画面，或用一个快速的横向移动镜头（Panning）表现一整天的时光流逝。	BGM节奏略微加快，加入轻微的环境噪音（如远处车流声）。
00:06-00:09	他用小小的身躯扛起了名为成长的行囊，	特写/慢动作： 聚焦于孩子的肩膀和书包的肩带。书包上可以有轻微的光晕/颗粒感（象征“成长”的重量与潜力）。孩子的双手可能握紧了书包带。	极慢速推近到肩膀，或从下往上仰拍肩膀。	BGM音量微弱上升，加入轻微的“沙沙”声或金属的摩擦声，强调行囊的重量感。
00:09-00:13	我们的情绪是他回家的风霜还是暖灯，	对比场景：<br>1. 风霜（冷色）： 孩子站在门外，门缝透出冷白色/蓝色的光，孩子在门外略微停顿。<br>2. 暖灯（暖色）： 随后，门被打开，温暖的橘黄色灯光瞬间充盈画面，父母（只露背影或侧影）站在门口。	场景1使用固定镜头，场景2使用快速开门（拉远），光线对比强烈。	BGM转为更柔和的旋律。场景1加入轻微的冷风声。场景2加入温暖的“开关门”声和温馨的“嗡鸣”环境音。

接下来是正式的文案：
{{content}}
"""


# ================= 业务逻辑：AI 推理提示词 (已替换为 Qwen-VL-Max) =================
# ================= 业务逻辑：AI 推理提示词 (优化版) =================
def analyze_video_logic(video_path: str, subtitle_text: str):
    """
    核心视频分析逻辑 - 使用 阿里云 Qwen-VL-Max
    """
    # 1. 基础校验
    if not video_path:
        raise Exception("视频路径为空")

    if not os.path.exists(video_path):
        # 尝试修复路径斜杠问题
        video_path = video_path.replace("\\", "/")
        if not os.path.exists(video_path):
            raise Exception(f"本地视频文件不存在: {video_path}")

    # 打印日志方便调试
    try:
        file_size_bytes = os.path.getsize(video_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        print(f"🎬 正在分析视频: {os.path.basename(video_path)} ({file_size_mb:.2f} MB)")
    except Exception:
        pass

    try:
        # 2. 构造文件 URI
        # Qwen-VL Python SDK 支持 "file://绝对路径"
        abs_path = os.path.abspath(video_path)
        file_uri = f"file://{abs_path}"

        # 3. 构造 Prompt
        full_prompt = (
            f"请分析这个视频片段，结合字幕生成分镜。\n"
            f"字幕文本：{subtitle_text}\n"
            f"{DEFAULT_ROLE_PROMPT}"
        )

        # 4. 构造消息体
        messages = [
            {
                "role": "user",
                "content": [
                    {"video": file_uri},  # 传入视频
                    {"text": full_prompt}  # 传入文本指令
                ]
            }
        ]

        # 5. 发起调用 (注意：DashScope SDK 目前是阻塞调用的)
        # 前端 abort 后，这里的代码依然会运行直到结束，但前端不会等待结果
        response = MultiModalConversation.call(
            model=MODEL_NAME,  # 确保 MODEL_NAME = "qwen-vl-max" 已定义
            messages=messages,
            stream=False
        )

        # 6. 处理结果
        if response.status_code == 200:
            # 提取文本内容
            content_list = response.output.choices[0].message.content
            final_text = ""
            # 阿里云有时候返回的是列表，有时候直接是文本，做个兼容遍历
            for item in content_list:
                if "text" in item:
                    final_text += item["text"]

            print(f"✅ 分析成功: {os.path.basename(video_path)}")
            return final_text
        else:
            # 抛出具体的 API 错误码
            error_msg = f"Qwen API Error: code={response.code}, message={response.message}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)

    except Exception as e:
        print(f"❌ 分析过程出错: {str(e)}")
        # 打印详细堆栈，方便排查是 SDK 问题还是网络问题
        import traceback
        traceback.print_exc()
        raise e


# ================= 业务逻辑：AI 改写文案 (优化版) =================
def rewrite_text_logic(user_content):
    # 🔥 优化：增加 timeout=60 秒，防止请求卡死
    conn = http.client.HTTPSConnection("yunbaoymgf.chat", timeout=60)

    payload = json.dumps({
        "model": "deepseek-v3-250324",
        "max_tokens": 1000,
        "messages": [
            {
                "role": "system",
                "content": "你是一名专业的文本编辑，请严格按照以下要求对提供的文案进行改写。"
            },
            {
                "role": "user",
                "content": f"""你是一名专业的文本编辑，请严格按照以下要求对提供的文案进行改写。
***【核心任务】**
对文案进行逐句改写，确保：
1. **句式转换**：将句子中的被动语态（如“被...”）转换为“把”字句。
2. **文本润色**：用更流畅、自然的中文进行轻微润色，避免改变原意。
3. **语句衔接**：在保持每句独立性的前提下，使用恰当的关联词（如：接着、突然、结果、原来）增强句子间的逻辑连贯性。

**【严格约束】**
- **保持结构**：改写后必须与原文行数、句数完全一致。
- **格式统一**：输出时，每行内的多个句子**只用逗号“，”分隔**，不使用其他标点。
- **忠于原意**：不添加额外情节、对话或夸张表达。

**【输出格式】**
仅输出改写后的文案内容，不要包含"原文："或"改写："的前缀。

**【输入文案】**
{user_content}
"""
            }
        ],
        "temperature": 0.7,
        "stream": False
    })

    headers = {
        'Accept': 'application/json',
        'Authorization': 'sk-ecGw6OQNT0j6yiWEUy4G7HBObNxrcIaMkZfa8zJJJ1gpSmUl',
        'Content-Type': 'application/json'
    }

    try:
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # 🔥 优化：检查 HTTP 状态码
        if res.status != 200:
            error_msg = f"API Error {res.status}: {res.reason}"
            print(error_msg)
            raise Exception(error_msg)

        response_json = json.loads(data.decode("utf-8"))

        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API返回格式异常: {response_json}")

    except Exception as e:
        print(f"Rewrite Logic Error: {str(e)}")
        raise e
    finally:
        conn.close()


# ================= 注册路由 (保持不变) =================

@router.post("/rewrite")
def rewrite_endpoint(request: RewriteRequest):
    try:
        # 调用逻辑函数
        result = rewrite_text_logic(request.text)
        return {"success": True, "data": result}
    except Exception as e:
        # 返回错误信息
        return {"success": False, "msg": str(e)}


@router.post("/analyze_prompt")
def analyze_prompt_endpoint(request: AnalyzeRequest):
    try:
        # 传递视频路径和字幕 (注意：需要确保 analyze_video_logic 函数在其他地方已定义)
        # 如果 analyze_video_logic 在同一个文件中定义，直接调用即可
        # 如果是引用的，请确保已 import analyze_video_logic
        result = analyze_video_logic(request.video_path, request.subtitle_text)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "msg": str(e)}