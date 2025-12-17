import os
import shutil
import uuid
import cv2
import requests
import torch
import numpy as np
from tqdm import tqdm
from fastapi import APIRouter, UploadFile, File, Form
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

# 创建路由
router = APIRouter()

# ================= 配置路径 =================
BASE_DIR = r"D:\yunManGongFangAI"
UPSCALE_DIR = os.path.join(BASE_DIR, "UpscaleOutput")
MODEL_DIR = os.path.join(BASE_DIR, "models")

for d in [UPSCALE_DIR, MODEL_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

# ================= 模型自动下载逻辑 =================
MODELS = {
    "realesrgan-x4plus": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
    "realesrgan-x4plus-anime": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
}


def check_and_download_model(model_name):
    """如果模型不存在，自动下载"""
    model_path = os.path.join(MODEL_DIR, f"{model_name}.pth")
    if not os.path.exists(model_path):
        url = MODELS.get(model_name)
        if not url:
            raise Exception(f"未知的模型: {model_name}")

        print(f"⬇️ 正在自动下载模型: {model_name} ...")
        # 使用流式下载
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(model_path, 'wb') as f, tqdm(
                desc=model_name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                bar.update(size)
        print("✅ 模型下载完成！")
    return model_path


# ================= 核心推理类 =================
class UpscalerEngine:
    def __init__(self, model_name="realesrgan-x4plus-anime", device="cuda"):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        self.model_path = check_and_download_model(model_name)

        # 初始化模型架构
        if model_name == 'realesrgan-x4plus':  # 真实照片模型
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        elif model_name == 'realesrgan-x4plus-anime':  # 动漫模型
            model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
        else:
            raise Exception("暂不支持该模型")

        # 加载 RealESRGANer
        self.upscaler = RealESRGANer(
            scale=4,
            model_path=self.model_path,
            model=model,
            tile=400,  # 切块大小，防止爆显存
            tile_pad=10,
            pre_pad=0,
            half=True,  # 开启半精度加速
            device=self.device,
        )

    def process_image(self, img_path, out_path, out_scale=4):
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if len(img.shape) == 3 and img.shape[2] == 4:
            # 处理透明通道
            img_mode = 'RGBA'
        else:
            img_mode = None

        try:
            output, _ = self.upscaler.enhance(img, outscale=out_scale)
            cv2.imwrite(out_path, output)
            return True
        except Exception as e:
            print(f"推理出错: {e}")
            return False


# ================= API 接口 =================

@router.post("/api/upscale/image")
async def upscale_image(
        file: UploadFile = File(...),
        scale: int = Form(2),
        model: str = Form("realesrgan-x4plus-anime")
):
    try:
        # 1. 准备文件
        file_ext = file.filename.split(".")[-1]
        task_id = str(uuid.uuid4())
        input_filename = f"{task_id}_input.{file_ext}"
        output_filename = f"{task_id}_output.png"  # 输出统一为 png

        input_path = os.path.join(UPSCALE_DIR, input_filename)
        output_path = os.path.join(UPSCALE_DIR, output_filename)

        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 2. 调用引擎
        engine = UpscalerEngine(model_name=model)
        engine.process_image(input_path, output_path, out_scale=scale)

        return {
            "status": "success",
            "msg": "图片超分完成",
            "url": f"/upscale_storage/{output_filename}"
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"status": "error", "msg": str(e)}


@router.post("/api/upscale/video")
async def upscale_video(
        file: UploadFile = File(...),
        scale: int = Form(2),
        model: str = Form("realesrgan-x4plus-anime")
):
    try:
        # 1. 准备文件
        file_ext = file.filename.split(".")[-1]
        task_id = str(uuid.uuid4())
        input_filename = f"{task_id}_vid_in.{file_ext}"
        output_filename = f"{task_id}_vid_out.mp4"

        input_path = os.path.join(UPSCALE_DIR, input_filename)
        output_path = os.path.join(UPSCALE_DIR, output_filename)

        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        print(f"🎬 开始处理视频: {input_path}")

        # 2. 初始化引擎
        engine = UpscalerEngine(model_name=model)

        # 3. 使用 OpenCV 逐帧处理 (最稳妥的方式，不需要ffmpeg环境)
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 计算新分辨率
        new_w, new_h = int(width * scale), int(height * scale)

        # 视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (new_w, new_h))

        print(f"视频信息: {width}x{height} -> {new_w}x{new_h}, 总帧数: {total_frames}")

        pbar = tqdm(total=total_frames, desc="视频超分中")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            try:
                # 核心超分逻辑
                output, _ = engine.upscaler.enhance(frame, outscale=scale)
                writer.write(output)
                pbar.update(1)
            except Exception as e:
                print(f"帧处理失败: {e}")

        cap.release()
        writer.release()
        pbar.close()

        print("🎉 视频处理完成")

        return {
            "status": "success",
            "msg": "视频超分完成 (注意：OpenCV处理模式暂无音频)",
            "url": f"/upscale_storage/{output_filename}"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "msg": str(e)}