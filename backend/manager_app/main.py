# 文件位置: backend/manager_app/main.py

import os
import json
import hashlib
import base64
import shutil
import random
import uuid
import platform
import requests  # 必须安装: pip install requests
from datetime import datetime, timedelta
from typing import Optional

# 第三方库
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ================= 配置 =================
STORAGE_SALT = "yunmangongfang_storage_v1_salt"
CARD_SEED = "yunmangongfang_2024_secret"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= 1. 核心加密工具 =================
class CryptoUtils:
    @staticmethod
    def get_machine_id():
        try:
            node = uuid.getnode()
            system_info = f"{platform.node()}-{platform.system()}-{node}"
            machine_id = hashlib.md5(system_info.encode()).hexdigest().upper()
            return f"{machine_id[:4]}-{machine_id[4:8]}-{machine_id[8:12]}-{machine_id[12:16]}"
        except:
            return "UNKNOWN-DEVICE"

    @staticmethod
    def encrypt_aes(data_str: str, key: bytes) -> str:
        try:
            iv = os.urandom(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            encrypted_bytes = cipher.encrypt(pad(data_str.encode('utf-8'), AES.block_size))
            return base64.urlsafe_b64encode(iv + encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"加密失败: {e}")
            return None

    @staticmethod
    def decrypt_aes(encrypted_str: str, key: bytes) -> str:
        try:
            combined = base64.urlsafe_b64decode(encrypted_str)
            iv = combined[:16]
            ciphertext = combined[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            return None


# ================= 2. 卡密解密器 =================
class CardKeyEncryption:
    def __init__(self):
        self.secret_key = hashlib.sha256(CARD_SEED.encode()).digest()

    def decrypt_card_key(self, user_card_key):
        if not user_card_key or not user_card_key.startswith("ymgfjc-") or len(user_card_key) < 20:
            return None
        try:
            encrypted_b64 = user_card_key[7:]
            return CryptoUtils.decrypt_aes(encrypted_b64, self.secret_key)
        except:
            return None


# ================= 3. 系统管理 (SystemManager) =================
class SystemManager:
    @staticmethod
    def get_roaming_root():
        roaming_path = os.getenv('APPDATA')
        if not roaming_path:
            roaming_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return roaming_path

    @staticmethod
    def get_root_workspace():
        return os.path.join(SystemManager.get_roaming_root(), "instpopup_workspaces_man_creator")

    @staticmethod
    def get_license_path():
        return os.path.join(SystemManager.get_root_workspace(), "activation", "activation.dat")

    @staticmethod
    def get_storage_key():
        mid = CryptoUtils.get_machine_id()
        source = f"{mid}_{STORAGE_SALT}"
        return hashlib.sha256(source.encode()).digest()

    @staticmethod
    def verify_remote_api(real_api_key):
        """
        👉 核心闭环逻辑：
        1. 检查 Usage，必须为 0 (新卡)。
        2. 发送 Chat 请求验证并消耗 (锁卡)。
        """
        print(f"📡 开始云端闭环验证 API Key: {real_api_key[:8]}******")

        headers = {
            'Authorization': f'Bearer {real_api_key}',
            'Content-Type': 'application/json'
        }

        try:
            # === 第一步：查重 (Check Usage) ===
            # 查询该卡密是否已经被使用过
            # start_date 和 end_date 设置范围大一点以覆盖所有记录
            usage_url = "https://yunwu.ai/v1/dashboard/billing/usage?start_date=2020-01-01&end_date=2099-12-31"

            resp_usage = requests.get(usage_url, headers=headers, timeout=10)

            if resp_usage.status_code == 401:
                return False, "❌ 激活失败：卡密无效，请检查输入"

            if resp_usage.status_code != 200:
                print(f"❌ 查询 Usage 失败: {resp_usage.text}")
                return False, f"❌ 云端连接异常 (Code: {resp_usage.status_code})"

            usage_info = resp_usage.json()
            total_usage = float(usage_info.get('total_usage', 0))

            print(f"💰 卡密当前已用金额: {total_usage}")

            # [闭环关键]：如果已用金额不为 0，说明已经在别的机器激活过，或者跑过数据
            if total_usage > 0:
                return False, "❌ 该卡密已在其他设备激活 (已使用)，请购买新卡密！"

            print("✅ 检测为新卡 (Usage=0)，正在进行激活验证...")

            # === 第二步：激活/锁卡 (Chat Completions) ===
            # 发送一条请求，验证 Key 确实可用，并且产生微量消耗，导致下次 total_usage > 0
            chat_url = "https://yunwu.ai/v1/chat/completions"
            payload = {
                "model": "gpt-5",
                "messages": [{"role": "user", "content": "verify"}],
                "max_completion_tokens": 5,  # 消耗极少，只为锁卡
                "temperature": 1,
                "stream": False
            }

            resp_chat = requests.post(chat_url, json=payload, headers=headers, timeout=15)

            if resp_chat.status_code == 200:
                return True, "✅ 验证成功，卡密已激活并绑定本机"
            elif resp_chat.status_code == 401:
                return False, "❌ 激活失败：卡密权限不足或被封禁"
            else:
                return False, f"❌ 激活请求失败 (Code: {resp_chat.status_code})"

        except requests.exceptions.Timeout:
            return False, "❌ 网络连接超时，请检查网络"
        except Exception as e:
            print(f"验证异常: {e}")
            return False, "❌ 验证过程发生未知错误"

    @staticmethod
    def activate_license(card_key: str):
        card_key = card_key.strip()

        # 1. 解密卡密
        decryptor = CardKeyEncryption()
        real_api_key = decryptor.decrypt_card_key(card_key)

        if not real_api_key:
            return False, "❌ 卡密格式错误 (请使用 ymgfjc- 开头的卡密)"

        # 2. 云端闭环验证
        is_valid, msg = SystemManager.verify_remote_api(real_api_key)

        if not is_valid:
            return False, msg

        # 3. 验证通过，写入本地
        # 既然是新卡激活成功，给予有效期
        data = {
            "activated": True,
            "card_key": card_key,
            "real_api_key": real_api_key,
            "machine_id": CryptoUtils.get_machine_id(),
            "activation_date": datetime.now().strftime("%Y-%m-%d"),
            "expiry_date": (datetime.now() + timedelta(days=3650)).strftime("%Y-%m-%d")  # 10年
        }

        # 4. 加密存储
        json_str = json.dumps(data, ensure_ascii=False)
        storage_key = SystemManager.get_storage_key()
        encrypted_content = CryptoUtils.encrypt_aes(json_str, storage_key)

        try:
            license_path = SystemManager.get_license_path()
            os.makedirs(os.path.dirname(license_path), exist_ok=True)
            with open(license_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)
            print(f"✅ 激活文件写入成功: {license_path}")
            return True, "✅ 激活成功！"
        except Exception as e:
            return False, f"❌ 写入文件失败: {str(e)}"

    @staticmethod
    def verify_license():
        path = SystemManager.get_license_path()
        if not os.path.exists(path): return False, {}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                encrypted_content = f.read().strip()

            storage_key = SystemManager.get_storage_key()
            json_str = CryptoUtils.decrypt_aes(encrypted_content, storage_key)

            if json_str:
                data = json.loads(json_str)
                if data.get('activated'):
                    return True, data
        except Exception:
            pass
        return False, {}


# ================= 4. 空间管理 (dynamicSpaces) =================
class dynamicSpaces:
    @staticmethod
    def _make_safe_name(name):
        return "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name]).strip()

    @classmethod
    def _get_type_dir(cls, project_type: str):
        root = SystemManager.get_root_workspace()
        if project_type == "二创动态漫" or project_type == "secondary":
            folder_name = "SpaceDongSecondTaiMan"
        else:
            folder_name = "SpaceDongYuanChuangTaiMan"
        path = os.path.join(root, folder_name)
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def create_space(cls, name, data):
        safe_name = cls._make_safe_name(name)
        project_type = data.get("type", "原创动态漫")
        base_dir = cls._get_type_dir(project_type)

        space_dir = os.path.join(base_dir, safe_name, "creatSpace")
        os.makedirs(space_dir, exist_ok=True)
        config_path = os.path.join(space_dir, f"{safe_name}.dat")

        if os.path.exists(config_path):
            return False, "该项目名称已存在"

        data.update({
            "space_name": name,
            "safe_name": safe_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "id": data.get("id") or random.randint(1000, 9999)
        })

        json_str = json.dumps(data, ensure_ascii=False)
        storage_key = SystemManager.get_storage_key()
        encrypted = CryptoUtils.encrypt_aes(json_str, storage_key)

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(encrypted)
            return True, "创建成功"
        except Exception as e:
            return False, str(e)

    @classmethod
    def get_all(cls):
        root = SystemManager.get_root_workspace()
        target_folders = ["SpaceDongYuanChuangTaiMan", "SpaceDongSecondTaiMan"]
        storage_key = SystemManager.get_storage_key()
        projects = []

        for folder_name in target_folders:
            base_dir = os.path.join(root, folder_name)
            if not os.path.exists(base_dir): continue
            for item in os.listdir(base_dir):
                path = os.path.join(base_dir, item)
                if os.path.isdir(path):
                    sub_dir = os.path.join(path, "creatSpace")
                    if os.path.exists(sub_dir):
                        files = [f for f in os.listdir(sub_dir) if f.endswith('.dat')]
                        if files:
                            try:
                                with open(os.path.join(sub_dir, files[0]), 'r', encoding='utf-8') as f:
                                    enc = f.read().strip()
                                    json_str = CryptoUtils.decrypt_aes(enc, storage_key)
                                    if json_str: projects.append(json.loads(json_str))
                            except:
                                pass
        return sorted(projects, key=lambda x: x.get('created_at', ''), reverse=True)

    @classmethod
    def delete_space(cls, name):
        safe_name = cls._make_safe_name(name)
        root = SystemManager.get_root_workspace()
        target_folders = ["SpaceDongYuanChuangTaiMan", "SpaceDongSecondTaiMan"]
        deleted = False
        for folder_name in target_folders:
            path = os.path.join(root, folder_name, safe_name)
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    deleted = True
                except:
                    pass
        return (True, "删除成功") if deleted else (False, "项目不存在")


# ================= 5. API 路由 =================
class ActivateReq(BaseModel):
    key: str


class ProjectReq(BaseModel):
    name: str
    type: str
    ratio: str


@app.get("/api/machine_id")
def api_machine_id():
    return {"machine_id": CryptoUtils.get_machine_id()}


@app.post("/api/activate")
def api_activate(req: ActivateReq):
    print(f"📡 [API] 请求激活: {req.key}")
    ok, msg = SystemManager.activate_license(req.key)
    return {"success": ok, "message": msg}


@app.get("/api/status")
def api_status():
    ok, info = SystemManager.verify_license()
    if ok and "expiry_date" in info:
        info["expiry_date"] = info["expiry_date"]
    return {"activated": ok, "info": info}


@app.get("/api/projects")
def api_get_projects():
    return dynamicSpaces.get_all()


@app.post("/api/create_project")
def api_create(req: ProjectReq):
    data = req.dict()
    data['id'] = random.randint(100000, 999999)
    ok, msg = dynamicSpaces.create_space(req.name, data)
    if not ok: raise HTTPException(status_code=500, detail=msg)
    return {"status": "success", "data": data}


@app.delete("/api/delete_project/{name}")
def api_delete(name: str):
    ok, msg = dynamicSpaces.delete_space(name)
    if not ok: raise HTTPException(status_code=500, detail=msg)
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print(f"✅ 后端启动成功 (云端闭环验证版)")
    print(f"📂 根目录: {SystemManager.get_root_workspace()}")
    print("=" * 50)
    uvicorn.run(app, host="127.0.0.1", port=8000)