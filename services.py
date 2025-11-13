# services.py
from typing import List, Optional

from models import (
    User,
    UserRole,
    UserStatus,
    Product,
    ProductStatus,
    ConditionLevel,
    ComplaintStatus,
)
from storage import DataStore


class AuthService:
    def __init__(self, store: DataStore):
        self.store = store

    def register(self, username: str, phone: str, role_str: str) -> User:
        existing = self.store.find_user_by_phone(phone)
        if existing:
            raise ValueError("该手机号已注册")
        role = UserRole.BUYER
        if role_str == "卖家":
            role = UserRole.SELLER
        return self.store.add_user(username=username, phone=phone, role=role)

    def login(self, phone: str) -> User:
        user = self.store.find_user_by_phone(phone)
        if not user:
            raise ValueError("账号未注册")
        if user.status == UserStatus.BANNED:
            raise ValueError("账号已被封禁")
        return user


class ProductService:
    def __init__(self, store: DataStore):
        self.store = store

    def publish_product(
        self,
        seller: User,
        title: str,
        category: str,
        condition: str,
        price: float,
        stock: int,
        description: str,
        contact: str,
        image_count: int = 1,
    ) -> Product:
        if image_count < 1:
            raise ValueError("至少需要 1 张图片（可用数字模拟）")
        if not title.strip():
            raise ValueError("商品标题不能为空")
        if len(description.strip()) < 10:
            raise ValueError("商品描述至少 10 字")
        return self.store.add_product(
            seller_id=seller.id,
            title=title.strip(),
            image_count=image_count,
            category=category,
            condition=condition,
            price=price,
            stock=stock,
            description=description.strip(),
            contact=contact.strip(),
        )

    def list_all(self) -> List[Product]:
        return self.store.list_products()

    def search(
        self,
        keyword: str = "",
        category: str = "全部",
        condition_filter: str = "全部",
        price_filter: str = "全部",
    ) -> List[Product]:
        products = [p for p in self.store.list_products() if p.status == ProductStatus.ON_SALE]

        if keyword:
            kw = keyword.strip().lower()
            products = [p for p in products if kw in p.title.lower()]

        if category != "全部":
            products = [p for p in products if p.category == category]

        if condition_filter != "全部":
            if condition_filter == "全新":
                products = [p for p in products if p.condition == ConditionLevel.NEW]
            elif condition_filter == "95新及以上":
                products = [
                    p
                    for p in products
                    if p.condition in (ConditionLevel.NEW, ConditionLevel.NINE_NINE, ConditionLevel.NINE_FIVE)
                ]

        if price_filter != "全部":
            if price_filter == "0-500元":
                products = [p for p in products if 0 <= p.price <= 500]
            elif price_filter == "500-1000元":
                products = [p for p in products if 500 < p.price <= 1000]
            elif price_filter == "1000元以上":
                products = [p for p in products if p.price > 1000]

        return products

    def takedown(self, pid: int):
        self.store.update_product_status(pid, ProductStatus.TAKEDOWN)

    def off_shelf(self, pid: int):
        self.store.update_product_status(pid, ProductStatus.OFF_SHELF)


class OrderService:
    def __init__(self, store: DataStore):
        self.store = store

    def create_order(self, buyer: User, product: Product, quantity: int = 1):
        if quantity <= 0:
            raise ValueError("数量至少为 1")
        if product.stock < quantity:
            raise ValueError("库存不足")
        amount = product.price * quantity
        order = self.store.add_order(
            buyer_id=buyer.id,
            product_id=product.id,
            quantity=quantity,
            amount=amount,
        )
        # 简单扣库存
        for p in self.store.data["products"]:
            if p["id"] == product.id:
                p["stock"] = int(p["stock"]) - quantity
                break
        self.store._save()
        return order


class ComplaintService:
    def __init__(self, store: DataStore):
        self.store = store

    def submit_complaint(
        self,
        complainant: User,
        type_value: str,
        reason: str,
        evidence_count: int = 0,
        product_id: Optional[int] = None,
        order_id: Optional[int] = None,
    ):
        if not reason.strip():
            raise ValueError("请填写投诉原因")
        if evidence_count < 0 or evidence_count > 3:
            raise ValueError("证据图片数量 0~3 张")
        return self.store.add_complaint(
            complainant_id=complainant.id,
            product_id=product_id,
            order_id=order_id,
            type_value=type_value,
            evidence_count=evidence_count,
            reason=reason.strip(),
        )


class AdminService:
    def __init__(self, store: DataStore):
        self.store = store

    def list_users(self) -> List[User]:
        return self.store.list_users()

    def ban_user(self, user_id: int, reason: str):
        # reason 暂时只展示，不做存储
        self.store.update_user_status(user_id, UserStatus.BANNED)

    def list_products(self) -> List[Product]:
        return self.store.list_products()

    def takedown_product(self, pid: int, reason: str):
        self.store.update_product_status(pid, ProductStatus.TAKEDOWN)

    def list_orders(self):
        return self.store.list_orders()

    def list_complaints(self):
        return self.store.list_complaints()

    def handle_complaint(self, cid: int, status_value: str, result: str):
        self.store.update_complaint_status(cid, ComplaintStatus(status_value), result)

