# character_service.py
import json
import http.client
import re
import requests
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ================= 配置区域 =================
# 请在此处填入你的 Yunwu/Gemini API Key
GEMINI_API_KEY = "sk-OMJNU2vqQUgFq3keMxS95M6XWz6E44jbQDDC1T1B1VutemSz"

# 🔥 定义核心后缀（这里是你要在生成时强制加上，但在前端隐藏的内容）
FIXED_SUFFIX = ",笔直的站立着，双手自然下垂，开心的表情,白色背景呈现, 角色设定图, 包含全身正面全身照,帅气的五官， 画布的中央, --ar 9:16 --niji 6,无任何字幕,只有图片,禁止出现任何字幕,全身像，只保留主体人物，其他的什么都不要啊，只要人物"


# ===========================================

class ExtractReq(BaseModel):
    text: str


class GenerateImageReq(BaseModel):
    prompt: str
    ratio: str = "1:1"


# ================= 1. 角色提取逻辑 (已修改 Prompt) =================

def call_llm_for_characters(user_content):
    conn = http.client.HTTPSConnection("yunbaoymgf.chat")

    system_prompt = "你是云漫工坊-MJ描述词生成专家。你的任务：从用户提供的完整故事/小说段落中，提取所有角色，并为每个角色生成独立、完整的Midjourney描述词。"

    # 🔥 修改点：Prompt 中去掉了强制后缀的要求，只要求生成外貌描述
    full_user_content = f"""
## 核心指令

### 1. 角色提取与标识
扫描全文，提取所有角色，并为每个角色创建**标准标识**：
- 格式：`一名[X]岁的[男人/女人/老人/少年/女孩]` + [可选特征]
- 示例：`一名30岁的年轻女人`、`一名66岁的老人`、`一名20岁的男人`、`一名20岁的古风帅哥`

**提取范围：**
- 明确姓名（王明、小红）
- 职位头衔（李老师、张经理）
- 关系称谓（母亲、好友）
- 特征代称（红裙女孩、白发老者）
- 明确指代的他/她

### 2. 生成描述词格式
每个描述词严格遵循以下结构：
[标准标识]：[年龄]的[男人/女人]，[颜色]的毛发，[毛发特征]，[眼睛颜色]的眼睛，[服装描述]，[服装带鞋子] ,[表情] ,[风格]
### 3. 年龄性别推断规则
- **年龄推断**：
  - 学生/少年/少女→15-22岁
  - 年轻人/青年→20-35岁
  - 老师/经理/职业人士→25-45岁
  - 中年→40-60岁
  - 老人/爷爷/奶奶→60岁以上
- **性别推断**：
  - 先生/男士/哥哥/爸爸→男人
  - 女士/小姐/姐姐/妈妈→女人
  - 中性姓名→根据上下文判断
- **特征补充**：
  - 古风/武侠角色→添加“古风”
  - 职业特征→添加“穿白大褂的医生”等

## 强制要求
0.**生成的图片一定给我禁止出现任何字幕，只要图片，这是硬性规定**
1. **标识必须明确**：每个描述词以“一名[X]岁的[性别][特征]”开头
2. **只输出图片**：不要出现任何带有任何分析、列表、解释的字幕
3. **每个角色独立一行**：行间用空行分隔
4. **固定部分不变**：最后的背景、构图、表情、参数一字不改

## 示例

**用户输入：**
“公司经理张伟今年35岁，他的助理小芳25岁。拜访客户时遇到一位60多岁的陈老先生。”

**正确输出：**
一名35岁的男人（公司经理张伟）：身高约178厘米, 黑色短发, 深棕色的眼睛,穿着深灰色西装套装配浅蓝色衬衫和深红色领带, 白色运动鞋,开心的表情, 动漫风格

一名25岁的年轻女人（助理小芳）：身高约165厘米,红色长发, 蓝色的眼睛, 穿着浅灰色职业套裙配白色衬衫,开心的表情,表情温柔微笑，红色高跟鞋,动漫风格

一名66岁的老人（陈老先生）：身高约172厘米, 银白色短发, 长脸有皱纹, 眉毛花白稀疏, 黑色的眼睛, 穿着深蓝色中山装，黑色的皮鞋, 开心的表情, 动漫风格

**用户输入：**
“武侠世界中，剑客凌云二十出头，一袭白衣。”

**正确输出：**
一名22岁的古风帅哥（剑客凌云）：身高约188厘米, 瓜子脸, 眉毛浓黑整齐, 红色的眼睛,, 黑色长发, 手里拿着一个红色耀眼的宝剑，宝剑出鞘的动作，穿着古代武侠的服装，配黑色长靴, 严肃的表情, 古风动漫风格

**待处理文案：**
{user_content}
"""

    payload = json.dumps({
        "model": "deepseek-v3-250324",
        "max_tokens": 2000,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_content}
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
        response_json = json.loads(data.decode("utf-8"))


        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0]["message"]["content"]
        else:
            print("API Error Response:", response_json)
            raise Exception("API返回格式异常或内容为空")

    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        raise e
    finally:
        conn.close()


def parse_character_output(llm_text):
    characters = []
    lines = [line.strip() for line in llm_text.split('\n') if line.strip()]
    pattern = re.compile(r"(.*?)[\(\uff08](.*?)[\)\uff09][:：]?(.*)")

    for i, line in enumerate(lines):
        match = pattern.match(line)
        if match:
            prefix = match.group(1).strip()
            label_name = match.group(2).strip()
            suffix = match.group(3).strip()

            clean_suffix = suffix
            if clean_suffix.startswith(",") or clean_suffix.startswith("，"):
                clean_suffix = clean_suffix[1:].strip()

            full_description = f"{prefix}, {clean_suffix}"

            characters.append({
                "id": i + 1000,
                "label": label_name,
                "description": full_description,  # 这里现在是干净的文本，没有后缀
                "checked": True,
                "image": None,
                "video": None,
                "type": "AI提取"
            })
        else:
            if len(line) > 10:
                characters.append({
                    "id": i + 1000,
                    "label": "未知角色",
                    "description": line,
                    "checked": True,
                    "image": None,
                    "video": None,
                    "type": "AI提取"
                })

    return characters


@router.post("/extract_characters")
async def extract_characters_api(req: ExtractReq):
    try:
        if not req.text.strip():
            return {"status": "error", "msg": "文案内容为空"}
        raw_text = call_llm_for_characters(req.text)
        parsed_data = parse_character_output(raw_text)
        return {"status": "success", "data": parsed_data}
    except Exception as e:
        return {"status": "error", "msg": str(e)}


# ================= 2. 角色图片生成逻辑 (已修改拼接逻辑 & 强制直连) =================

def call_gemini_for_image(prompt, ratio="9:16"):
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        raise Exception("请在后端 character_service.py 中配置 GEMINI_API_KEY")

    model = "gemini-2.5-flash-image"
    api_url = f"https://yunbaoymgf.chat/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # 构建 Payload
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": ratio,
                "imageSize": "1K"
            }
        }
    }

    print(f"Executing Gemini Image Gen with Prompt: {prompt[:50]}... (Suffix Hidden)")

    try:
        # 🔥🔥🔥 核心修改：强制禁用代理 🔥🔥🔥
        # proxies={"http": None, "https": None} 会强制 requests 忽略系统代理设置
        # 从而实现直连中转商 API，即使电脑开了全局梯子也能正常访问
        response = requests.post(
            api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=120,
            proxies={"http": None, "https": None}
        )

        if response.status_code != 200:
            raise Exception(f"API 请求失败 [{response.status_code}]: {response.text}")

        result = response.json()
        candidates = result.get('candidates', [])

        if not candidates:
            raise Exception("API 返回内容为空 (No candidates)")

        content_parts = candidates[0].get('content', {}).get('parts', [])

        for part in content_parts:
            if 'inlineData' in part or 'inline_data' in part:
                img_obj = part.get('inlineData') or part.get('inline_data')
                base64_data = img_obj.get('data')
                mime_type = img_obj.get('mimeType', 'image/jpeg')

                if base64_data:
                    return f"data:{mime_type};base64,{base64_data}"

        print("Full Response:", json.dumps(result, indent=2))
        raise Exception("未在响应中找到图片数据，可能是模型拒绝生成。")

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        raise e


@router.post("/generate_character_image")
async def generate_character_image_api(req: GenerateImageReq):
    try:
        if not req.prompt.strip():
            return {"status": "error", "msg": "描述词为空"}

        # 🔥 关键逻辑：在这里拼接后缀
        # 前端传来的 req.prompt 是干净的描述（例如：一名35岁的男人...动漫风格）
        # 我们在这里加上 FIXED_SUFFIX（...白色背景呈现, 角色设定图...）
        final_prompt = f"Anime style character design, best quality, detailed: {req.prompt}{FIXED_SUFFIX}"

        # 调用生成
        image_data_uri = call_gemini_for_image(final_prompt, req.ratio)

        return {"status": "success", "image_url": image_data_uri}

    except Exception as e:
        return {"status": "error", "msg": str(e)}