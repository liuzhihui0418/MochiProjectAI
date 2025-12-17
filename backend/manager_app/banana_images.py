import os
import shutil
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gradio_client import Client
from PIL import Image  # 🔥 引入图片处理库

# 创建路由
router = APIRouter()

# 定义图片保存路径 (D盘)
BANANA_OUTPUT_DIR = r"D:\yunManGongFangAI\BananaOutput"

# 确保目录存在
if not os.path.exists(BANANA_OUTPUT_DIR):
    try:
        os.makedirs(BANANA_OUTPUT_DIR)
    except Exception as e:
        print(f"❌ 创建目录失败: {e}")


class BananaGenReq(BaseModel):
    server_url: str
    prompt: str
    steps: int = 6
    seed: int = -1
    width: int = 1024
    height: int = 768
    use_enhancer: bool = True


@router.post("/api/banana/generate")
async def generate_banana_image(req: BananaGenReq):
    """
    调用远程 Gradio 接口生成图片，并保存为 PNG
    """
    print(f"🍌 收到生图请求: URL={req.server_url} | Prompt={req.prompt[:20]}...")

    if not req.server_url.startswith("http"):
        return {"status": "error", "msg": "服务器链接无效"}

    try:
        clean_url = req.server_url.rstrip("/")
        client = Client(clean_url)

        print("🎨 正在发送指令给云端显卡...")
        result = client.predict(
            prompt=req.prompt,
            steps=req.steps,
            seed=req.seed,
            width=req.width,
            height=req.height,
            use_enhancer=req.use_enhancer,
            api_name="/run_inference"
        )

        temp_image_path = result[0]
        log_msg = result[1]

        # === 🔥 修改核心：转换为 PNG 格式 ===
        timestamp = int(time.time() * 1000)
        filename = f"banana_{timestamp}.png"  # 1. 后缀改为 png
        save_path = os.path.join(BANANA_OUTPUT_DIR, filename)

        # 2. 使用 PIL 打开并保存为 PNG (确保是真 PNG，不是假改名)
        img = Image.open(temp_image_path)
        img.save(save_path, format="PNG", quality=100)  # 质量拉满

        print(f"✅ PNG原图已保存: {save_path}")

        return {
            "status": "success",
            "image_url": f"/banana_storage/{filename}",
            "local_path": save_path,
            "server_log": log_msg
        }

    except Exception as e:
        print(f"❌ 生图失败: {e}")
        return {"status": "error", "msg": str(e)}