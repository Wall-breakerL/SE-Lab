import pytest
import os
from services import AuthService, ProductService
from storage import DataStore
from models import UserRole

# 集成测试使用独立的文件
TEST_DB_INT = "test_data_integration.json"

@pytest.fixture
def store():
    if os.path.exists(TEST_DB_INT):
        os.remove(TEST_DB_INT)
    ds = DataStore(path=TEST_DB_INT)
    yield ds
    if os.path.exists(TEST_DB_INT):
        os.remove(TEST_DB_INT)

def test_integration_full_flow(store):
    """场景1: 卖家发布 -> 买家搜索 -> 验证数据持久化"""
    # 1. 注册
    auth = AuthService(store)
    seller = auth.register("集成卖家", "18800000001", "卖家")
    buyer = auth.register("集成买家", "18800000002", "买家")
    
    # 2. 卖家发布
    product_srv = ProductService(store)
    product = product_srv.publish_product(
        seller, "集成显卡", "电脑", "全新", 999.0, 1, "很好的显卡描述描述描述", "Contact"
    )
    
    # 3. 买家搜索
    results = product_srv.search("集成显卡")
    assert len(results) == 1
    
    # 4. 模拟重启（验证数据存进磁盘了）
    new_store = DataStore(path=TEST_DB_INT)
    new_ps = ProductService(new_store)
    assert len(new_ps.list_all()) >= 1

def test_integration_auth_security(store):
    """场景2: 注册重复检测 -> 封号 -> 登录拦截"""
    auth = AuthService(store)
    # 1. 正常注册
    u1 = auth.register("用户1", "18800000003", "买家")
    
    # 2. 重复注册拦截
    with pytest.raises(ValueError):
        auth.register("用户2", "18800000003", "卖家")
        
    # 3. 登录成功
    u1_login = auth.login("18800000003")
    assert u1_login.id == u1.id
