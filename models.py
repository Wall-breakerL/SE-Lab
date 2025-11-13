# models.py
from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
from datetime import datetime


class UserRole(str, Enum):
    BUYER = "BUYER"
    SELLER = "SELLER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    NORMAL = "NORMAL"
    BANNED = "BANNED"


class ConditionLevel(str, Enum):
    NEW = "全新"
    NINE_NINE = "99新"
    NINE_FIVE = "95新"
    NINE = "9成新"


class ProductStatus(str, Enum):
    ON_SALE = "在售"
    OFF_SHELF = "下架"
    DELETED = "删除"
    TAKEDOWN = "违规下架"


class OrderStatus(str, Enum):
    CREATED = "已创建"
    PAID = "已支付"
    COMPLETED = "已完成"
    CANCELLED = "已取消"


class ComplaintType(str, Enum):
    PRODUCT_VIOLATION = "商品违规"
    ORDER_DISPUTE = "订单纠纷"


class ComplaintStatus(str, Enum):
    PENDING = "待处理"
    IN_PROGRESS = "处理中"
    RESOLVED = "已解决"
    REJECTED = "已驳回"


@dataclass
class User:
    id: int
    username: str
    phone: str
    role: UserRole
    status: UserStatus = UserStatus.NORMAL

    def to_dict(self):
        d = asdict(self)
        d["role"] = self.role.value
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(
            id=d["id"],
            username=d["username"],
            phone=d["phone"],
            role=UserRole(d["role"]),
            status=UserStatus(d.get("status", "NORMAL")),
        )


@dataclass
class Product:
    id: int
    seller_id: int
    title: str
    image_count: int
    category: str
    condition: ConditionLevel
    price: float
    stock: int
    description: str
    contact: str
    status: ProductStatus = ProductStatus.ON_SALE

    def to_dict(self):
        d = asdict(self)
        d["condition"] = self.condition.value
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "Product":
        return Product(
            id=d["id"],
            seller_id=d["seller_id"],
            title=d["title"],
            image_count=d.get("image_count", 1),
            category=d.get("category", "未分类"),
            condition=ConditionLevel(d.get("condition", "全新")),
            price=float(d["price"]),
            stock=int(d["stock"]),
            description=d.get("description", ""),
            contact=d.get("contact", ""),
            status=ProductStatus(d.get("status", ProductStatus.ON_SALE.value)),
        )


@dataclass
class Order:
    id: int
    buyer_id: int
    product_id: int
    quantity: int
    amount: float
    status: OrderStatus
    created_at: str  # isoformat

    def to_dict(self):
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "Order":
        return Order(
            id=d["id"],
            buyer_id=d["buyer_id"],
            product_id=d["product_id"],
            quantity=d["quantity"],
            amount=float(d["amount"]),
            status=OrderStatus(d["status"]),
            created_at=d["created_at"],
        )


@dataclass
class Complaint:
    id: int
    complainant_id: int
    product_id: Optional[int]
    order_id: Optional[int]
    type: ComplaintType
    status: ComplaintStatus
    evidence_count: int
    reason: str
    submitted_at: str  # isoformat
    result: str = ""

    def to_dict(self):
        d = asdict(self)
        d["type"] = self.type.value
        d["status"] = self.status.value
        return d

    @staticmethod
    def from_dict(d: dict) -> "Complaint":
        return Complaint(
            id=d["id"],
            complainant_id=d["complainant_id"],
            product_id=d.get("product_id"),
            order_id=d.get("order_id"),
            type=ComplaintType(d["type"]),
            status=ComplaintStatus(d["status"]),
            evidence_count=int(d.get("evidence_count", 0)),
            reason=d.get("reason", ""),
            submitted_at=d["submitted_at"],
            result=d.get("result", ""),
        )


