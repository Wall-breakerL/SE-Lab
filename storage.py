# storage.py
import json
import os
from typing import List, Optional
from datetime import datetime

from models import (
    User,
    Product,
    Order,
    Complaint,
    UserRole,
    UserStatus,
    ProductStatus,
    ComplaintStatus,
)


class DataStore:
    """
    简单文件存储，使用一个 data.json 保存所有数据
    """

    def __init__(self, path: str = "data.json"):
        self.path = path
        self.data = {
            "users": [],
            "products": [],
            "orders": [],
            "complaints": [],
            "_id_counters": {
                "users": 1,
                "products": 1,
                "orders": 1,
                "complaints": 1,
            },
        }
        self._load()
        self._ensure_admin_user()

    # ------------ 基础读写 ------------

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def _save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def _next_id(self, collection: str) -> int:
        current = self.data["_id_counters"].get(collection, 1)
        self.data["_id_counters"][collection] = current + 1
        return current

    # ------------ 用户 ------------

    def _ensure_admin_user(self):
        # 默认 admin 账号：手机号 00000000000
        for u in self.data["users"]:
            if u["role"] == UserRole.ADMIN.value:
                return
        admin = User(
            id=self._next_id("users"),
            username="管理员",
            phone="00000000000",
            role=UserRole.ADMIN,
            status=UserStatus.NORMAL,
        )
        self.data["users"].append(admin.to_dict())
        self._save()

    def add_user(self, username: str, phone: str, role: UserRole) -> User:
        user = User(
            id=self._next_id("users"),
            username=username,
            phone=phone,
            role=role,
            status=UserStatus.NORMAL,
        )
        self.data["users"].append(user.to_dict())
        self._save()
        return user

    def find_user_by_phone(self, phone: str) -> Optional[User]:
        for u in self.data["users"]:
            if u["phone"] == phone:
                return User.from_dict(u)
        return None

    def find_user_by_id(self, uid: int) -> Optional[User]:
        for u in self.data["users"]:
            if u["id"] == uid:
                return User.from_dict(u)
        return None

    def update_user_status(self, user_id: int, status: UserStatus):
        for u in self.data["users"]:
            if u["id"] == user_id:
                u["status"] = status.value
                break
        self._save()

    def list_users(self) -> List[User]:
        return [User.from_dict(u) for u in self.data["users"]]

    # ------------ 商品 ------------

    def add_product(
        self,
        seller_id: int,
        title: str,
        image_count: int,
        category: str,
        condition: str,
        price: float,
        stock: int,
        description: str,
        contact: str,
    ) -> Product:
        from models import ConditionLevel  # 避免循环导入

        product = Product(
            id=self._next_id("products"),
            seller_id=seller_id,
            title=title,
            image_count=image_count,
            category=category,
            condition=ConditionLevel(condition),
            price=price,
            stock=stock,
            description=description,
            contact=contact,
            status=ProductStatus.ON_SALE,
        )
        self.data["products"].append(product.to_dict())
        self._save()
        return product

    def list_products(self) -> List[Product]:
        return [Product.from_dict(p) for p in self.data["products"]]

    def update_product_status(self, pid: int, status: ProductStatus):
        for p in self.data["products"]:
            if p["id"] == pid:
                p["status"] = status.value
                break
        self._save()

    def find_product_by_id(self, pid: int) -> Optional[Product]:
        for p in self.data["products"]:
            if p["id"] == pid:
                return Product.from_dict(p)
        return None

    # ------------ 订单 ------------

    def add_order(
        self,
        buyer_id: int,
        product_id: int,
        quantity: int,
        amount: float,
    ) -> Order:
        order = Order(
            id=self._next_id("orders"),
            buyer_id=buyer_id,
            product_id=product_id,
            quantity=quantity,
            amount=amount,
            status=OrderStatus.PAID,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        self.data["orders"].append(order.to_dict())
        self._save()
        return order

    def list_orders(self) -> List[Order]:
        return [Order.from_dict(o) for o in self.data["orders"]]

    def find_order_by_id(self, oid: int) -> Optional[Order]:
        for o in self.data["orders"]:
            if o["id"] == oid:
                return Order.from_dict(o)
        return None

    # ------------ 投诉 ------------

    def add_complaint(
        self,
        complainant_id: int,
        product_id: Optional[int],
        order_id: Optional[int],
        type_value: str,
        evidence_count: int,
        reason: str,
    ) -> Complaint:
        from models import ComplaintType, ComplaintStatus

        complaint = Complaint(
            id=self._next_id("complaints"),
            complainant_id=complainant_id,
            product_id=product_id,
            order_id=order_id,
            type=ComplaintType(type_value),
            status=ComplaintStatus.PENDING,
            evidence_count=evidence_count,
            reason=reason,
            submitted_at=datetime.now().isoformat(timespec="seconds"),
            result="",
        )
        self.data["complaints"].append(complaint.to_dict())
        self._save()
        return complaint

    def list_complaints(self) -> List[Complaint]:
        return [Complaint.from_dict(c) for c in self.data["complaints"]]

    def update_complaint_status(self, cid: int, status: ComplaintStatus, result: str):
        for c in self.data["complaints"]:
            if c["id"] == cid:
                c["status"] = status.value
                c["result"] = result
                break
        self._save()

