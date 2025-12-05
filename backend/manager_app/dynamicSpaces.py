import os
import shutil
import random
from datetime import datetime

# === 修正引用：直接引用同目录模块 ===
from DecryptorCore import DecryptorCore


class dynamicSpaces:
    """动态空间管理器"""

    @classmethod
    def _get_base_config_dir(cls):
        roaming_path = os.getenv('APPDATA')
        if not roaming_path:
            roaming_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        base_dir = os.path.join(roaming_path, "instpopup_workspaces_man_creator", "SpaceDongSecondTaiMan")
        os.makedirs(base_dir, exist_ok=True)
        return base_dir

    @classmethod
    def _make_safe_filename(cls, filename):
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

    @classmethod
    def create_space(cls, space_name, initial_data):
        base_dir = cls._get_base_config_dir()
        safe_name = cls._make_safe_filename(space_name)

        # 1. 创建项目文件夹
        project_dir = os.path.join(base_dir, safe_name)

        # 2. 创建 creatSpace 子文件夹
        config_dir = os.path.join(project_dir, "creatSpace")
        os.makedirs(config_dir, exist_ok=True)

        # 3. 数据文件路径
        config_path = os.path.join(config_dir, f"{safe_name}.dat")

        if os.path.exists(config_path):
            return False, "空间已存在"

        # 4. 完善数据
        initial_data.update({
            "space_name": space_name,
            "safe_space_name": safe_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            # 确保 ID 存在
            "id": initial_data.get("id", random.randint(10000, 99999))
        })

        # 5. 加密并写入
        encrypted_content = DecryptorCore.encrypt_data(initial_data)
        if not encrypted_content:
            return False, "加密失败"

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)
            print(f"✅ 创建成功: {config_path}")
            return True, "创建成功"
        except Exception as e:
            return False, f"写入失败: {str(e)}"

    @classmethod
    def delete_space(cls, space_name):
        base_dir = cls._get_base_config_dir()
        safe_name = cls._make_safe_filename(space_name)
        space_path = os.path.join(base_dir, safe_name)

        if os.path.exists(space_path):
            try:
                shutil.rmtree(space_path)
                return True, "删除成功"
            except Exception as e:
                return False, str(e)
        return False, "空间不存在"

    @classmethod
    def get_all_projects(cls):
        base_dir = cls._get_base_config_dir()
        projects = []

        if not os.path.exists(base_dir):
            return projects

        for item in os.listdir(base_dir):
            space_path = os.path.join(base_dir, item)
            # 排除非文件夹和 license.sys
            if os.path.isdir(space_path):
                # 尝试寻找 .dat 文件
                config_dir = os.path.join(space_path, "creatSpace")
                target_file = os.path.join(config_dir, f"{item}.dat")

                # 容错：如果找不到标准命名的 dat，找文件夹里第一个 dat
                if not os.path.exists(target_file) and os.path.exists(config_dir):
                    files = [f for f in os.listdir(config_dir) if f.endswith('.dat')]
                    if files:
                        target_file = os.path.join(config_dir, files[0])

                if os.path.exists(target_file):
                    try:
                        with open(target_file, 'r', encoding='utf-8') as f:
                            content = f.read().strip()
                            data = DecryptorCore.decrypt_data(content)
                            if data:
                                projects.append({
                                    "id": data.get("id", 0),
                                    "name": data.get("space_name", item),
                                    "type": data.get("type", "未知"),
                                    "ratio": data.get("ratio", "16:9"),
                                    "created_at": data.get("created_at", ""),
                                    "updated_at": data.get("last_updated", "")
                                })
                    except Exception as e:
                        print(f"❌ 读取 {item} 失败: {e}")

        # 按创建时间倒序
        return sorted(projects, key=lambda x: x['created_at'], reverse=True)