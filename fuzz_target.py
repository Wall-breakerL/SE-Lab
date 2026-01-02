import atheris
import sys
import os

# ==================== 1. 环境配置 ====================
# 将 project 目录加入路径，否则 import 找不到
print(os.path.join(os.path.dirname(__file__), "project"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "project")))

# 导入你的业务代码
from services import AuthService
from storage import DataStore
from models import UserRole

# ==================== 2. Mock 存储层 (关键！) ====================
# 继承 DataStore，重写读写方法，避免 Fuzz 时疯狂操作硬盘
class MockDataStore(DataStore):
    def __init__(self):
        # 初始化内存数据，不读文件
        self.data = {
            "users": [],
            "products": [],
            "_id_counters": {"users": 1, "products": 1}
        }
        self.path = "mock_path" # 假路径

    def _save(self):
        pass # 禁止写文件，什么都不做

    def _load(self):
        pass # 禁止读文件

# ==================== 3. 定义 Fuzz 目标函数 ====================
def TestOneInput(data):
    """
    这是 Atheris 会反复调用的函数。
    data 是 Atheris 生成的随机字节流。
    """
    # 使用 FuzzedDataProvider 将随机字节转换为字符串
    fdp = atheris.FuzzedDataProvider(data)
    
    # 生成随机输入
    try:
        random_phone = fdp.ConsumeUnicodeNoSurrogates(11)
        random_name = fdp.ConsumeUnicodeNoSurrogates(10)
    except Exception:
        return # 忽略编码错误生成的非法字符串

    # 准备测试环境 (使用纯内存存储)
    store = MockDataStore()
    #print("Fuzzing with phone:", random_phone, "name:", random_name)
    auth = AuthService(store)

    try:
        # === 这里是你要攻击的逻辑 ===
        # 尝试用随机乱码注册用户
        auth.register(random_name, random_phone, "买家")
        
    except ValueError:
        # ValueError 是我们代码里主动 raise 的（比如手机号已存在），
        # 这是“预期内”的错误，不算 Bug，所以我们捕获它，不让 Fuzzer 报错。
        return 
    
    except RuntimeError:
        # 也可以忽略特定的运行时错误
        return

    # 如果发生了其他没想到的异常（比如 IndexError, TypeError），
    # 脚本会在这里崩溃，Atheris 就会报告找到了 Bug！

# ==================== 4. 启动 Fuzzing ====================
if __name__ == "__main__":
    # 自动检测 instrument 哪些模块
    atheris.instrument_all()
    # 启动，设置运行次数或时间
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()
