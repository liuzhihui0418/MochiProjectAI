# 文件位置: backend/manager_app/config.py

import os
import json
import hashlib
import shutil
import random
import uuid
import platform
import base64
import requests
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ================= 全局配置常量 =================
STORAGE_SALT = "yunmangongfang_storage_v1_salt"
CARD_SEED = "yunmangongfang_2024_secret"

# 你的 Nginx 接口地址
LICENSE_API_URL = "https://ai.yunmanybcz.chat/api/license/verify"


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
        """工作区根目录"""
        return os.path.join(SystemManager.get_roaming_root(), "instpopup_workspaces_man_creator")

    @staticmethod
    def get_license_path():
        """激活文件路径"""
        return os.path.join(SystemManager.get_root_workspace(), "activation", "activation.dat")

    @staticmethod
    def get_storage_key():
        """生成本地存储密钥"""
        mid = CryptoUtils.get_machine_id()
        source = f"{mid}_{STORAGE_SALT}"
        return hashlib.sha256(source.encode()).digest()

    @staticmethod
    def save_license_file(data):
        """统一的保存文件方法，方便调试"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            storage_key = SystemManager.get_storage_key()
            encrypted_content = CryptoUtils.encrypt_aes(json_str, storage_key)

            license_path = SystemManager.get_license_path()
            os.makedirs(os.path.dirname(license_path), exist_ok=True)

            with open(license_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)

            print(f"✅ [Config] 授权文件已成功写入: {license_path}")
            print(f"📝 [Config] 写入内容预览: ID={data.get('machine_id')}, Date={data.get('expiry_date')}")
            return True
        except Exception as e:
            print(f"❌ [Config] 写入文件失败: {e}")
            return False

    @staticmethod
    def activate_license(card_key: str):
        card_key = card_key.strip()
        decryptor = CardKeyEncryption()
        real_api_key = decryptor.decrypt_card_key(card_key)

        if not real_api_key: return False, "无效的卡密格式"
        if real_api_key == "TEST-API-KEY-BYPASS": return True, "测试模式"

        try:
            machine_id = CryptoUtils.get_machine_id()
            # 🔥 强制转为字符串并去除空白，防止特殊字符导致服务器崩溃
            machine_id = str(machine_id).strip()
        except Exception as e:
            machine_id = "UNKNOWN-DEVICE"

        msg = "验证中..."

        try:
            payload = {
                "card_key": real_api_key,
                "machine_id": machine_id,
                "raw_key": card_key
            }

            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(max_retries=2)
            session.mount('https://', adapter)
            session.mount('http://', adapter)

            # 🔥 打印调试信息（让用户截图黑色控制台给你看）
            print("-" * 30)
            print(f"🚀 发送 Payload: {payload}")
            print(f"🌐 目标 URL: {LICENSE_API_URL}")

            # 发送请求
            resp = session.post(LICENSE_API_URL, json=payload, timeout=15, verify=False)

            # 🔥 打印服务器返回的真实内容
            print(f"🔙 服务器状态码: {resp.status_code}")
            print(f"🔙 服务器返回内容: {resp.text}")
            print("-" * 30)

            # 如果服务器报错 (500/502/404)，把网页内容的前50个字返回给前端，方便排查
            if resp.status_code != 200:
                error_detail = resp.text[:100] if resp.text else "无返回内容"
                return False, f"服务器内部错误({resp.status_code}): {error_detail}"

            res_json = resp.json()

            if res_json.get("code") == 200:
                msg = res_json.get("msg", "激活成功")
                expiry_date = res_json.get("expiry_date")

                if not expiry_date:
                    expiry_date = (datetime.now() + timedelta(days=3650)).strftime("%Y-%m-%d %H:%M:%S")

                data = {
                    "activated": True,
                    "card_key": card_key,
                    "real_api_key": real_api_key,
                    "machine_id": machine_id,
                    "activation_date": datetime.now().strftime("%Y-%m-%d"),
                    "expiry_date": expiry_date,
                    "info": msg
                }

                save_ok = SystemManager.save_license_file(data)
                if not save_ok:
                    return False, "激活成功但本地写入失败"

                return True, msg
            else:
                return False, res_json.get("msg", "激活被拒绝")

        except requests.exceptions.ConnectionError:
            return False, "网络不通，请检查是否开启了VPN/代理"
        except requests.exceptions.SSLError:
            return False, "SSL握手失败，网络环境异常"
        except Exception as e:
            import traceback
            traceback.print_exc()  # 打印堆栈
            return False, f"客户端未知错误: {str(e)}"

    @staticmethod
    def get_network_time():
        try:
            res = requests.head("http://www.baidu.com", timeout=3)
            date_str = res.headers.get('Date')
            if date_str:
                return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT') + timedelta(hours=8)
        except:
            return None
        return None

    @staticmethod
    def verify_license():
        path = SystemManager.get_license_path()
        if not os.path.exists(path): return False, {}

        try:
            # 1. 读取本地文件
            with open(path, 'r', encoding='utf-8') as f:
                encrypted_content = f.read().strip()

            storage_key = SystemManager.get_storage_key()
            json_str = CryptoUtils.decrypt_aes(encrypted_content, storage_key)

            if not json_str: return False, {"msg": "授权文件损坏"}
            local_data = json.loads(json_str)

            # --- 数据自愈（防止字段缺失） ---
            data_changed = False
            if not local_data.get('machine_id'):
                local_data['machine_id'] = CryptoUtils.get_machine_id()
                data_changed = True
            if not local_data.get('expiry_date'):
                local_data['expiry_date'] = (datetime.now() + timedelta(days=3650)).strftime("%Y-%m-%d %H:%M:%S")
                data_changed = True

            if data_changed:
                SystemManager.save_license_file(local_data)

            # 获取参数
            raw_card_key = local_data.get('card_key')
            machine_id = CryptoUtils.get_machine_id()
            real_api_key = local_data.get('real_api_key')

            # 测试码特权
            if real_api_key == "TEST-API-KEY-BYPASS":
                return True, local_data

            # ==========================================================
            # 2. 🔥 联网严查 (这里是核心修改)
            # ==========================================================
            try:
                # 构造请求
                payload = {
                    "card_key": raw_card_key,  # 原始卡密
                    "machine_id": machine_id,
                    "raw_key": raw_card_key
                }
                resp = requests.post(LICENSE_API_URL, json=payload, timeout=5, verify=False)

                if resp.status_code == 200:
                    res_json = resp.json()

                    # 同步服务器的最新时间 (无论是过期还是续费，都同步)
                    server_expiry = res_json.get("expiry_date")
                    if server_expiry and local_data.get('expiry_date') != server_expiry:
                        print(f"🔄 [Verify] 同步服务器时间: {server_expiry}")
                        local_data['expiry_date'] = server_expiry
                        SystemManager.save_license_file(local_data)  # 写死到硬盘

                    # 🔥🔥🔥 执法时刻：如果服务器说不行，那就直接拒绝 🔥🔥🔥
                    if res_json.get("code") != 200:
                        err_msg = res_json.get('msg', '未知错误')
                        print(f"🚫 [Verify] 服务器拒绝: {err_msg}")

                        # 这里返回 False，前端就会收到 valid: false，从而跳回登录页或报错
                        return False, {"msg": f"授权失效: {err_msg}"}

                    # 如果服务器通过
                    return True, local_data

            except Exception as e:
                # 联网失败时不报错，继续走下面的本地校验
                pass

            # ==========================================================
            # 3. 本地/网络时间兜底 (断网时的防线)
            # ==========================================================
            expiry_str = local_data.get('expiry_date')
            if expiry_str:
                try:
                    # 截取日期部分 yyyy-mm-dd
                    exp_date_str = str(expiry_str)[:10]
                    exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d")

                    # 优先拿百度时间，拿不到才用系统时间
                    current_time = SystemManager.get_network_time()

                    # 🔥 强制联网模式：如果拿不到网络时间，直接杀（可选）
                    # if not current_time: return False, {"msg": "请连接互联网验证"}

                    if not current_time:
                        current_time = datetime.now()  # 宽松模式：允许离线

                    # 对比：给1天宽限期
                    if current_time > exp_date + timedelta(days=1):
                        return False, {"msg": f"授权已于 {exp_date_str} 过期"}

                    return True, local_data
                except Exception as e:
                    return False, {"msg": f"时间数据错误: {e}"}

            return False, {"msg": "授权数据丢失"}

        except Exception as e:
            return False, {"msg": f"验证异常: {e}"}


# ================= 4. 空间管理 (dynamicSpaces) =================
# ... (dynamicSpaces 类保持原样) ...
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

    @classmethod
    def get_project_root(cls, project_name, project_type="二创动态漫"):
        root = SystemManager.get_root_workspace()
        if project_type in ["二创动态漫", "secondary"]:
            folder_name = "SpaceDongSecondTaiMan"
        else:
            folder_name = "SpaceDongYuanChuangTaiMan"
        safe_name = cls._make_safe_name(project_name)
        return os.path.join(root, folder_name, safe_name)

    @classmethod
    def save_analysis_result(cls, project_name, data):
        try:
            project_root = cls.get_project_root(project_name)
            save_dir = os.path.join(project_root, "frameExtractions")
            os.makedirs(save_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = cls._make_safe_name(project_name)
            filename = f"{safe_name}_analysis_{timestamp}.dat"
            file_path = os.path.join(save_dir, filename)

            if "created_at" not in data:
                data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            json_str = json.dumps(data, ensure_ascii=False)
            storage_key = SystemManager.get_storage_key()
            encrypted_content = CryptoUtils.encrypt_aes(json_str, storage_key)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)

            return True, file_path
        except Exception as e:
            return False, str(e)



import os
import json
import shutil
from datetime import datetime


# 假设 SystemManager 和 CryptoUtils 已经在上下文中或已导入
# from xxx import SystemManager, CryptoUtils

class videosSecondSpaces:
    """
    专门管理二创动态漫工作台的实时编辑数据
    保存路径: 项目根目录/videosSecondSpaces/data.dat
    """

    FOLDER_NAME = "videosSecondSpaces"
    FILE_NAME = "data.dat"

    @staticmethod
    def _make_safe_name(name):
        """处理文件名，保持与 dynamicSpaces 一致"""
        return "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name]).strip()

    @classmethod
    def _get_storage_path(cls, project_name, project_type="二创动态漫"):
        """获取数据文件的绝对路径"""
        root = SystemManager.get_root_workspace()

        # 确定父级目录 (与 dynamicSpaces 逻辑保持一致)
        if project_type in ["二创动态漫", "secondary"]:
            parent_folder = "SpaceDongSecondTaiMan"
        else:
            parent_folder = "SpaceDongYuanChuangTaiMan"

        safe_name = cls._make_safe_name(project_name)

        # 构建完整路径: root/Category/ProjectName/videosSecondSpaces/
        directory = os.path.join(root, parent_folder, safe_name, cls.FOLDER_NAME)

        # 确保目录存在
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        return os.path.join(directory, cls.FILE_NAME)

    @classmethod
    def save_project_data(cls, project_name, clips_data, project_type="二创动态漫"):
        """
        实时保存项目的所有分镜数据
        :param project_name: 项目名称
        :param clips_data: list, 分镜列表数据 (包含原文、润色文、提示词、视频路径等)
        :param project_type: 项目类型
        """
        try:
            file_path = cls._get_storage_path(project_name, project_type)

            # 构造要保存的完整数据包
            save_payload = {
                "project_name": project_name,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_clips": len(clips_data),
                "clips": clips_data
            }

            # 序列化并加密
            json_str = json.dumps(save_payload, ensure_ascii=False)
            storage_key = SystemManager.get_storage_key()
            encrypted_content = CryptoUtils.encrypt_aes(json_str, storage_key)

            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)

            return True, "保存成功"
        except Exception as e:
            print(f"Save Error: {str(e)}")
            return False, str(e)

    @classmethod
    def load_project_data(cls, project_name, project_type="二创动态漫"):
        """
        加载项目数据，用于软件打开时恢复工作区
        """
        try:
            file_path = cls._get_storage_path(project_name, project_type)

            # 1. 优先尝试读取编辑过的 data.dat
            if os.path.exists(file_path):
                storage_key = SystemManager.get_storage_key()
                with open(file_path, 'r', encoding='utf-8') as f:
                    encrypted_content = f.read().strip()

                if not encrypted_content:
                    return cls._init_from_analysis(project_name, project_type)

                try:
                    json_str = CryptoUtils.decrypt_aes(encrypted_content, storage_key)
                    if json_str:
                        data = json.loads(json_str)
                        return True, data.get("clips", [])
                except Exception as e:
                    print(f"Decrypt Error: {e}, attempting to fallback.")

            # 2. 如果没有编辑记录，则尝试从最初的拆帧分析结果初始化
            return cls._init_from_analysis(project_name, project_type)

        except Exception as e:
            return False, str(e)

    @classmethod
    def _init_from_analysis(cls, project_name, project_type):
        """
        内部方法：如果还没有 videosSecondSpaces 数据 (即从未手动保存过)，
        尝试从 dynamicSpaces 生成的 frameExtractions 目录读取最新的分析结果。
        """
        try:
            # 1. 获取项目根目录 (利用 dynamicSpaces 的现成方法)
            project_root = dynamicSpaces.get_project_root(project_name, project_type)
            analysis_dir = os.path.join(project_root, "frameExtractions")

            # 2. 如果目录不存在，说明还没进行过拆帧分析
            if not os.path.exists(analysis_dir):
                print(f"⚠️ [Init] No analysis directory found for {project_name}")
                return True, []

            # 3. 找到最新的 .dat 文件 (按文件名排序，因为文件名包含时间戳)
            files = [f for f in os.listdir(analysis_dir) if f.endswith('.dat')]
            if not files:
                print(f"⚠️ [Init] No analysis .dat files found in {analysis_dir}")
                return True, []

            # 倒序排列，取第一个即为最新的
            files.sort(reverse=True)
            latest_file = files[0]
            file_path = os.path.join(analysis_dir, latest_file)
            print(f"📂 [Init] Loading initial data from analysis: {latest_file}")

            # 4. 读取并解密
            storage_key = SystemManager.get_storage_key()
            with open(file_path, 'r', encoding='utf-8') as f:
                encrypted_content = f.read().strip()

            json_str = CryptoUtils.decrypt_aes(encrypted_content, storage_key)
            if not json_str:
                return False, "初始分析文件解密失败"

            data = json.loads(json_str)

            # 5. 返回分镜列表
            # 注意：取决于 dynamicSpaces.save_analysis_result 保存时的结构
            # 通常保存的是 {"clips": [...], "scenes": [...]} 或者直接是 [...]
            # 这里做个兼容处理：
            if isinstance(data, list):
                return True, data
            elif isinstance(data, dict):
                # 优先取 clips，没有则取 scenes，再没有则返回空
                return True, data.get("clips") or data.get("scenes") or []

            return True, []

        except Exception as e:
            print(f"❌ [Init Error] Failed to init from analysis: {e}")
            return False, str(e)

    @classmethod
    def update_single_clip(cls, project_name, clip_index, update_fields, project_type="二创动态漫"):
        """
        更新单个分镜的特定字段 (改文案、更新生成的视频URL等)
        :param clip_index: 分镜的 index (0-based 或 id)
        :param update_fields: dict, 例如 {"script_polished": "新文案", "prompt": "..."}
        """
        success, clips = cls.load_project_data(project_name, project_type)
        if not success:
            return False, "无法加载项目数据"

        # 找到对应的分镜并更新
        updated = False
        for clip in clips:
            # 假设每个clip都有一个 index 字段
            if clip.get('index') == clip_index:
                clip.update(update_fields)
                updated = True
                break

        if updated:
            return cls.save_project_data(project_name, clips, project_type)
        else:
            return False, "未找到指定分镜索引"


import os
import json
import shutil
from datetime import datetime


# 假设 SystemManager 和 CryptoUtils 已经在上下文中
# from xxx import SystemManager, CryptoUtils

class VideosCharacter:
    """
    专门管理项目中的【角色库】数据
    保存路径: 项目根目录/videosCharacter/data.dat
    """

    FOLDER_NAME = "videosCharacter"
    FILE_NAME = "data.dat"

    @staticmethod
    def _make_safe_name(name):
        return "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name]).strip()

    @classmethod
    def _get_storage_path(cls, project_name, project_type="二创动态漫"):
        """获取角色数据文件的绝对路径"""
        root = SystemManager.get_root_workspace()

        if project_type in ["二创动态漫", "secondary"]:
            parent_folder = "SpaceDongSecondTaiMan"
        else:
            parent_folder = "SpaceDongYuanChuangTaiMan"

        safe_name = cls._make_safe_name(project_name)

        # 路径: .../ProjectName/videosCharacter/
        directory = os.path.join(root, parent_folder, safe_name, cls.FOLDER_NAME)

        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        return os.path.join(directory, cls.FILE_NAME)

    @classmethod
    def save_characters(cls, project_name, characters_data, project_type="二创动态漫"):
        """
        保存角色列表
        :param characters_data: List[dict] 角色数据列表
        """
        try:
            file_path = cls._get_storage_path(project_name, project_type)

            save_payload = {
                "project_name": project_name,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_chars": len(characters_data),
                "characters": characters_data
            }

            json_str = json.dumps(save_payload, ensure_ascii=False)
            storage_key = SystemManager.get_storage_key()
            encrypted_content = CryptoUtils.encrypt_aes(json_str, storage_key)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)

            return True, "角色库保存成功"
        except Exception as e:
            print(f"Character Save Error: {str(e)}")
            return False, str(e)

    @classmethod
    def load_characters(cls, project_name, project_type="二创动态漫"):
        """
        加载角色列表
        """
        try:
            file_path = cls._get_storage_path(project_name, project_type)

            if os.path.exists(file_path):
                storage_key = SystemManager.get_storage_key()
                with open(file_path, 'r', encoding='utf-8') as f:
                    encrypted_content = f.read().strip()

                if not encrypted_content:
                    return True, []

                try:
                    json_str = CryptoUtils.decrypt_aes(encrypted_content, storage_key)
                    if json_str:
                        data = json.loads(json_str)
                        # 返回 characters 列表，默认为空
                        return True, data.get("characters", [])
                except Exception as e:
                    print(f"Decrypt Error: {e}")
                    return False, "数据损坏"

            # 如果文件不存在，返回空列表
            return True, []

        except Exception as e:
            return False, str(e)

# =========================================================
# 👇👇👇 必须把这段代码粘贴到 config.py 文件的最末尾 👇👇👇
# =========================================================
class CharacterLibraryStorage:
    """
    【风格角色档案库】管理 (跟随项目存储)
    保存路径: 项目根目录/CharacterLibraryModal/data.dat
    """

    FOLDER_NAME = "CharacterLibraryModal"
    FILE_NAME = "data.dat"

    @staticmethod
    def _make_safe_name(name):
        return "".join([c if c.isalnum() or c in (' ', '_', '-') else '_' for c in name]).strip()

    @classmethod
    def _get_storage_path(cls, project_name, project_type="二创动态漫"):
        root = SystemManager.get_root_workspace()

        # 确定父级目录
        if project_type in ["二创动态漫", "secondary"]:
            parent_folder = "SpaceDongSecondTaiMan"
        else:
            parent_folder = "SpaceDongYuanChuangTaiMan"

        safe_name = cls._make_safe_name(project_name)

        # 拼接完整目录
        directory = os.path.join(root, parent_folder, safe_name, cls.FOLDER_NAME)

        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        return os.path.join(directory, cls.FILE_NAME)

    @classmethod
    def save_library(cls, project_name, characters_data, project_type="二创动态漫"):
        try:
            file_path = cls._get_storage_path(project_name, project_type)

            save_payload = {
                "project_name": project_name,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(characters_data),
                "characters": characters_data
            }

            json_str = json.dumps(save_payload, ensure_ascii=False)
            storage_key = SystemManager.get_storage_key()
            encrypted_content = CryptoUtils.encrypt_aes(json_str, storage_key)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)

            return True, f"档案库已保存"
        except Exception as e:
            print(f"Library Save Error: {str(e)}")
            return False, str(e)

    @classmethod
    def load_library(cls, project_name, project_type="二创动态漫"):
        try:
            file_path = cls._get_storage_path(project_name, project_type)

            if not os.path.exists(file_path):
                return True, []

            storage_key = SystemManager.get_storage_key()
            with open(file_path, 'r', encoding='utf-8') as f:
                encrypted_content = f.read().strip()

            if not encrypted_content:
                return True, []

            try:
                json_str = CryptoUtils.decrypt_aes(encrypted_content, storage_key)
                if json_str:
                    data = json.loads(json_str)
                    return True, data.get("characters", [])
            except Exception as e:
                return True, []

            return True, []

        except Exception as e:
            return False, str(e)