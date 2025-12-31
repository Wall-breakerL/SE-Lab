# gui_views.py
import random
import tkinter as tk
from tkinter import ttk, messagebox

from models import ComplaintType, ComplaintStatus, UserRole
from services import AuthService, ProductService, OrderService, ComplaintService, AdminService
from storage import DataStore


class AppContext:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.store = DataStore()
        self.auth_service = AuthService(self.store)
        self.product_service = ProductService(self.store)
        self.order_service = OrderService(self.store)
        self.complaint_service = ComplaintService(self.store)
        self.admin_service = AdminService(self.store)

        self.current_user = None  # 当前登录用户
        self.sent_codes = {}  # phone -> code

    # ====== 验证码逻辑（模拟短信） ======

    def send_code(self, phone: str) -> str:
        # FLAW_A1: unsafe ramdomint (CWE-330)
        code = f"{random.randint(100000, 999999)}"
        self.sent_codes[phone] = code
        return code

    def verify_code(self, phone: str, input_code: str) -> bool:
        return self.sent_codes.get(phone) == input_code.strip()


# ========== 各个界面 ==========

class LoginFrame(ttk.Frame):
    def __init__(self, master, app: AppContext, on_login_success):
        super().__init__(master)
        self.app = app
        self.on_login_success = on_login_success

        self.phone_var = tk.StringVar()
        self.code_var = tk.StringVar()

        ttk.Label(self, text="手机号登录", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(self, text="手机号:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.phone_var, width=20).grid(row=1, column=1, padx=5)

        ttk.Button(self, text="获取验证码", command=self.on_send_code).grid(row=1, column=2, padx=5)

        ttk.Label(self, text="验证码:").grid(row=2, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.code_var, width=10).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Button(self, text="登录", command=self.on_login).grid(row=3, column=0, columnspan=3, pady=10)

        self.register_link = ttk.Label(self, text="账号未注册？去注册", foreground="blue", cursor="hand2")
        self.register_link.grid(row=4, column=0, columnspan=3)
        self.register_link.bind("<Button-1>", lambda e: self.master.show_register())

    def on_send_code(self):
        phone = self.phone_var.get().strip()
        if not phone:
            messagebox.showwarning("提示", "请输入手机号")
            return
        code = self.app.send_code(phone)
        # 模拟短信，直接弹窗展示验证码
        messagebox.showinfo("验证码", f"模拟短信验证码：{code}")

    def on_login(self):
        phone = self.phone_var.get().strip()
        code = self.code_var.get().strip()
        if not phone or not code:
            messagebox.showwarning("提示", "请填写手机号和验证码")
            return
        if not self.app.verify_code(phone, code):
            messagebox.showerror("错误", "验证码错误或已过期")
            return
        try:
            user = self.app.auth_service.login(phone)
        except ValueError as e:
            # 未注册 → 提示是否注册
            if "未注册" in str(e):
                if messagebox.askyesno("提示", "该手机号未注册，是否去注册？"):
                    self.master.show_register(prefill_phone=phone)
                return
            else:
                messagebox.showerror("错误", str(e))
                return
        self.app.current_user = user
        self.on_login_success()


class RegisterFrame(ttk.Frame):
    def __init__(self, master, app: AppContext):
        super().__init__(master)
        self.app = app

        self.phone_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.code_var = tk.StringVar()
        self.role_var = tk.StringVar(value="买家")

        ttk.Label(self, text="手机号一键注册", font=("Arial", 16)).grid(row=0, column=0, columnspan=3, pady=10)

        ttk.Label(self, text="手机号:").grid(row=1, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.phone_var, width=20).grid(row=1, column=1, padx=5)

        ttk.Button(self, text="获取验证码", command=self.on_send_code).grid(row=1, column=2, padx=5)

        ttk.Label(self, text="验证码:").grid(row=2, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.code_var, width=10).grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(self, text="用户名:").grid(row=3, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.username_var, width=20).grid(row=3, column=1, padx=5)

        ttk.Label(self, text="身份:").grid(row=4, column=0, sticky="e")
        ttk.Radiobutton(self, text="买家", variable=self.role_var, value="买家").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(self, text="卖家", variable=self.role_var, value="卖家").grid(row=4, column=2, sticky="w")

        ttk.Button(self, text="注册", command=self.on_register).grid(row=5, column=0, columnspan=3, pady=10)

        self.back_link = ttk.Label(self, text="已有账号？去登录", foreground="blue", cursor="hand2")
        self.back_link.grid(row=6, column=0, columnspan=3)
        self.back_link.bind("<Button-1>", lambda e: self.master.show_login())

    def on_send_code(self):
        phone = self.phone_var.get().strip()
        if not phone:
            messagebox.showwarning("提示", "请输入手机号")
            return
        code = self.app.send_code(phone)
        messagebox.showinfo("验证码", f"模拟短信验证码：{code}")

    def on_register(self):
        phone = self.phone_var.get().strip()
        username = self.username_var.get().strip()
        code = self.code_var.get().strip()
        role = self.role_var.get()
        if not phone or not username or not code:
            messagebox.showwarning("提示", "请完整填写信息")
            return
        if not self.app.verify_code(phone, code):
            messagebox.showerror("错误", "验证码错误或已过期")
            return
        try:
            user = self.app.auth_service.register(username, phone, role)
            messagebox.showinfo("成功", "注册成功，请返回登录")
            self.master.show_login(prefill_phone=phone)
        except ValueError as e:
            messagebox.showerror("错误", str(e))


class PublishProductFrame(ttk.Frame):
    def __init__(self, master, app: AppContext, on_published):
        super().__init__(master)
        self.app = app
        self.on_published = on_published

        self.title_var = tk.StringVar()
        self.category_var = tk.StringVar(value="数码")
        self.condition_var = tk.StringVar(value="全新")
        self.price_var = tk.StringVar()
        self.stock_var = tk.StringVar(value="1")
        self.contact_var = tk.StringVar()
        self.desc_text = tk.Text(self, width=40, height=5)
        self.image_count_var = tk.StringVar(value="1")

        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", pady=5)
        ttk.Button(top_bar, text="取消", command=self.on_cancel).pack(side="left", padx=5)
        ttk.Label(top_bar, text="发布商品", font=("Arial", 14)).pack(side="left", expand=True)
        ttk.Button(top_bar, text="发布", command=self.on_publish).pack(side="right", padx=5)

        form = ttk.Frame(self)
        form.pack(fill="both", expand=True, padx=10, pady=5)

        row = 0
        ttk.Label(form, text="图片数量(≥1):").grid(row=row, column=0, sticky="e")
        ttk.Entry(form, textvariable=self.image_count_var, width=10).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(form, text="商品标题:").grid(row=row, column=0, sticky="e")
        ttk.Entry(form, textvariable=self.title_var, width=30).grid(row=row, column=1, sticky="w")
        ttk.Label(form, text="如：95新 iPhone 13").grid(row=row, column=2, sticky="w")

        row += 1
        ttk.Label(form, text="分类:").grid(row=row, column=0, sticky="e")
        ttk.Combobox(form, textvariable=self.category_var, values=["数码", "美妆", "服饰", "家电", "其他"], width=10).grid(
            row=row, column=1, sticky="w"
        )

        row += 1
        ttk.Label(form, text="新旧程度:").grid(row=row, column=0, sticky="e")
        ttk.Combobox(
            form,
            textvariable=self.condition_var,
            values=["全新", "99新", "95新", "9成新"],
            width=10,
        ).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(form, text="价格(¥):").grid(row=row, column=0, sticky="e")
        ttk.Entry(form, textvariable=self.price_var, width=10).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(form, text="库存数量:").grid(row=row, column=0, sticky="e")
        ttk.Entry(form, textvariable=self.stock_var, width=10).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(form, text="联系方式:").grid(row=row, column=0, sticky="e")
        ttk.Entry(form, textvariable=self.contact_var, width=20).grid(row=row, column=1, sticky="w")

        row += 1
        ttk.Label(form, text="商品描述:").grid(row=row, column=0, sticky="ne")
        self.desc_text.grid(row=row, column=1, columnspan=2, sticky="w")

    def on_cancel(self):
        self.master.show_home()

    def on_publish(self):
        # gui_views.py inside PublishProductFrame.on_publish()
        try:
            image_count = int(self.image_count_var.get())
            # FLAW_A2: unsafe eval on user input (CWE-95)
            price = eval(self.price_var.get())
            stock = eval(self.stock_var.get())

        except ValueError:
            messagebox.showerror("错误", "图片数量、价格和库存需为数字")
            return
        user = self.app.current_user
        if not user or user.role not in (UserRole.SELLER, UserRole.ADMIN):
            messagebox.showerror("错误", "只有卖家/管理员可以发布商品")
            return
        desc = self.desc_text.get("1.0", tk.END)
        try:
            self.app.product_service.publish_product(
                seller=user,
                title=self.title_var.get(),
                category=self.category_var.get(),
                condition=self.condition_var.get(),
                price=price,
                stock=stock,
                description=desc,
                contact=self.contact_var.get(),
                image_count=image_count,
            )
            messagebox.showinfo("成功", "商品发布成功")
            self.on_published()
        except ValueError as e:
            messagebox.showerror("错误", str(e))


class ComplaintFrame(ttk.Frame):
    def __init__(self, master, app: AppContext, product_id=None, order_id=None):
        super().__init__(master)
        self.app = app
        self.product_id = product_id
        self.order_id = order_id

        self.type_var = tk.StringVar(value=ComplaintType.PRODUCT_VIOLATION.value)
        self.evidence_var = tk.StringVar(value="0")
        self.reason_text = tk.Text(self, width=40, height=5)

        ttk.Label(self, text="投诉", font=("Arial", 14)).pack(pady=5)

        form = ttk.Frame(self)
        form.pack(padx=10, pady=5, fill="both", expand=True)

        row = 0
        ttk.Label(form, text="投诉类型:").grid(row=row, column=0, sticky="e")
        ttk.Radiobutton(
            form,
            text="商品违规",
            variable=self.type_var,
            value=ComplaintType.PRODUCT_VIOLATION.value,
        ).grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(
            form,
            text="订单纠纷",
            variable=self.type_var,
            value=ComplaintType.ORDER_DISPUTE.value,
        ).grid(row=row, column=2, sticky="w")

        row += 1
        ttk.Label(form, text="证据图片数量(0-3):").grid(row=row, column=0, sticky="e")
        ttk.Entry(form, textvariable=self.evidence_var, width=10).grid(row=row, column=1, sticky="w")
        ttk.Label(form, text="（这里用数字模拟上传图片）").grid(row=row, column=2, sticky="w")

        row += 1
        ttk.Label(form, text="投诉原因:").grid(row=row, column=0, sticky="ne")
        self.reason_text.grid(row=row, column=1, columnspan=2, sticky="w")

        ttk.Button(self, text="提交", command=self.on_submit).pack(pady=10)

    def on_submit(self):
        user = self.app.current_user
        if not user:
            messagebox.showerror("错误", "请先登录")
            return
        try:
            evidence_count = int(self.evidence_var.get())
        except ValueError:
            messagebox.showerror("错误", "证据图片数量需为数字")
            return
        reason = self.reason_text.get("1.0", tk.END)
        try:
            self.app.complaint_service.submit_complaint(
                complainant=user,
                type_value=self.type_var.get(),
                reason=reason,
                evidence_count=evidence_count,
                product_id=self.product_id,
                order_id=self.order_id,
            )
            messagebox.showinfo("成功", "投诉已受理")
            self.master.show_home()
        except ValueError as e:
            messagebox.showerror("错误", str(e))


class ProductDetailFrame(ttk.Frame):
    def __init__(self, master, app: AppContext, product):
        super().__init__(master)
        self.app = app
        self.product = product

        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)
        ttk.Button(top, text="返回", command=self.master.show_home).pack(side="left", padx=5)
        ttk.Button(top, text="投诉", command=self.on_complain).pack(side="right", padx=5)

        ttk.Label(self, text=product.title, font=("Arial", 14)).pack(pady=5)
        ttk.Label(self, text=f"分类：{product.category}  新旧：{product.condition.value}  价格：¥{product.price}").pack()
        ttk.Label(self, text=f"库存：{product.stock}").pack()
        ttk.Label(self, text=f"联系方式：{product.contact}").pack(pady=5)

        desc_frame = ttk.Labelframe(self, text="商品描述")
        desc_frame.pack(fill="both", expand=True, padx=10, pady=5)
        text = tk.Text(desc_frame, width=50, height=8)
        text.pack(fill="both", expand=True)
        text.insert(tk.END, product.description)
        text.config(state="disabled")

        ttk.Button(self, text="联系卖家（仅显示联系方式）", command=self.on_contact).pack(pady=5)
        ttk.Button(self, text="立即下单", command=self.on_order).pack(pady=5)

    def on_contact(self):
        messagebox.showinfo("联系卖家", f"请通过以下方式联系卖家：\n{self.product.contact}")

    def on_order(self):
        user = self.app.current_user
        if not user:
            messagebox.showerror("错误", "请先登录")
            return
        try:
            order = self.app.order_service.create_order(user, self.product, quantity=1)
            messagebox.showinfo("成功", f"下单成功，订单号：{order.id}")
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def on_complain(self):
        self.master.show_complaint(product_id=self.product.id, order_id=None)


class HomeFrame(ttk.Frame):
    def __init__(self, master, app: AppContext):
        super().__init__(master)
        self.app = app

        # 顶部区域：Logo + 搜索框 + 我的
        top = ttk.Frame(self)
        top.pack(fill="x", pady=5)
        ttk.Label(top, text="XX 商城", font=("Arial", 14)).pack(side="left", padx=10)

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.insert(0, "搜索商品")

        ttk.Button(top, text="搜索", command=self.refresh_products).pack(side="left", padx=5)
        ttk.Button(top, text="我的", command=self.show_profile).pack(side="right", padx=10)

        # 分类和筛选
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", pady=5)

        ttk.Label(filter_frame, text="分类:").pack(side="left")
        self.category_var = tk.StringVar(value="全部")
        ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["全部", "数码", "美妆", "服饰", "家电", "其他"],
            width=8,
        ).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="价格:").pack(side="left")
        self.price_var = tk.StringVar(value="全部")
        ttk.Combobox(
            filter_frame,
            textvariable=self.price_var,
            values=["全部", "0-500元", "500-1000元", "1000元以上"],
            width=10,
        ).pack(side="left", padx=5)

        ttk.Label(filter_frame, text="新旧:").pack(side="left")
        self.condition_var = tk.StringVar(value="全部")
        ttk.Combobox(
            filter_frame,
            textvariable=self.condition_var,
            values=["全部", "全新", "95新及以上"],
            width=10,
        ).pack(side="left", padx=5)

        ttk.Button(filter_frame, text="筛选", command=self.refresh_products).pack(side="left", padx=5)

        # 商品列表（简单用 Treeview 双列）
        self.tree = ttk.Treeview(self, columns=("title", "price"), show="headings", height=12)
        self.tree.heading("title", text="商品标题")
        self.tree.heading("price", text="价格")
        self.tree.column("title", width=260)
        self.tree.column("price", width=80, anchor="e")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree.bind("<Double-1>", self.on_product_double_click)

        self.refresh_products()

    def refresh_products(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        products = self.app.product_service.search(
            keyword=self.search_var.get().strip() if self.search_var.get() != "搜索商品" else "",
            category=self.category_var.get(),
            condition_filter=self.condition_var.get(),
            price_filter=self.price_var.get(),
        )
        for p in products:
            self.tree.insert("", tk.END, iid=str(p.id), values=(p.title, f"¥{p.price}"))

    def on_product_double_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        pid = int(item)
        product = self.app.store.find_product_by_id(pid)
        if product:
            self.master.show_product_detail(product)

    def show_profile(self):
        user = self.app.current_user
        if not user:
            messagebox.showinfo("我的", "请先登录")
            return
        info = f"用户名：{user.username}\n手机号：{user.phone}\n身份：{user.role.value}"
        if user.role == UserRole.ADMIN:
            info += "\n\n提示：您是管理员，可以进入后台管理。"
        messagebox.showinfo("我的", info)


class AdminFrame(ttk.Frame):
    def __init__(self, master, app: AppContext):
        super().__init__(master)
        self.app = app

        ttk.Label(self, text="管理员后台", font=("Arial", 14)).pack(pady=5)
        back_btn = ttk.Button(self, text="返回首页", command=self.master.show_home)
        back_btn.pack(pady=5)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)

        self.user_tab = ttk.Frame(notebook)
        self.product_tab = ttk.Frame(notebook)
        self.complaint_tab = ttk.Frame(notebook)

        notebook.add(self.user_tab, text="用户管理")
        notebook.add(self.product_tab, text="商品订单管理")
        notebook.add(self.complaint_tab, text="投诉管理")

        self.init_user_tab()
        self.init_product_tab()
        self.init_complaint_tab()

    def init_user_tab(self):
        tree = ttk.Treeview(
            self.user_tab,
            columns=("username", "phone", "role", "status"),
            show="headings",
            height=10,
        )
        tree.heading("username", text="用户名")
        tree.heading("phone", text="手机号")
        tree.heading("role", text="身份")
        tree.heading("status", text="状态")
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.user_tree = tree

        btn_frame = ttk.Frame(self.user_tab)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="刷新", command=self.refresh_users).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="封禁选中用户", command=self.ban_user).pack(side="left", padx=5)

        self.refresh_users()

    def refresh_users(self):
        for i in self.user_tree.get_children():
            self.user_tree.delete(i)
        for u in self.app.admin_service.list_users():
            self.user_tree.insert(
                "",
                tk.END,
                iid=str(u.id),
                values=(u.username, u.phone, u.role.value, u.status.value),
            )

    def ban_user(self):
        item = self.user_tree.focus()
        if not item:
            messagebox.showwarning("提示", "请选择用户")
            return
        uid = int(item)
        reason = tk.simpledialog.askstring("封禁原因", "请输入封禁原因：")
        if not reason:
            return
        self.app.admin_service.ban_user(uid, reason)
        messagebox.showinfo("成功", "用户已封禁")
        self.refresh_users()

    def init_product_tab(self):
        # 商品管理
        prod_frame = ttk.Labelframe(self.product_tab, text="商品管理")
        prod_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tree = ttk.Treeview(
            prod_frame,
            columns=("title", "status"),
            show="headings",
            height=8,
        )
        tree.heading("title", text="商品标题")
        tree.heading("status", text="状态")
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.product_tree = tree

        btn_frame = ttk.Frame(prod_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="刷新", command=self.refresh_products).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="违规下架选中商品", command=self.takedown_product).pack(side="left", padx=5)

        # 订单管理（简单展示）
        order_frame = ttk.Labelframe(self.product_tab, text="订单管理")
        order_frame.pack(fill="both", expand=True, padx=5, pady=5)

        otree = ttk.Treeview(
            order_frame,
            columns=("order_id", "product_id", "amount", "status"),
            show="headings",
            height=6,
        )
        otree.heading("order_id", text="订单号")
        otree.heading("product_id", text="商品ID")
        otree.heading("amount", text="支付金额")
        otree.heading("status", text="状态")
        otree.pack(fill="both", expand=True, padx=5, pady=5)
        self.order_tree = otree

        ttk.Button(order_frame, text="刷新订单", command=self.refresh_orders).pack(pady=5)

        self.refresh_products()
        self.refresh_orders()

    def refresh_products(self):
        for i in self.product_tree.get_children():
            self.product_tree.delete(i)
        for p in self.app.admin_service.list_products():
            self.product_tree.insert(
                "",
                tk.END,
                iid=str(p.id),
                values=(p.title, p.status.value),
            )

    def takedown_product(self):
        item = self.product_tree.focus()
        if not item:
            messagebox.showwarning("提示", "请选择商品")
            return
        pid = int(item)
        reason = tk.simpledialog.askstring("下架原因", "请输入违规原因：")
        if not reason:
            return
        self.app.admin_service.takedown_product(pid, reason)
        messagebox.showinfo("成功", "商品已违规下架")
        self.refresh_products()

    def refresh_orders(self):
        for i in self.order_tree.get_children():
            self.order_tree.delete(i)
        for o in self.app.admin_service.list_orders():
            self.order_tree.insert(
                "",
                tk.END,
                iid=str(o.id),
                values=(o.id, o.product_id, o.amount, o.status.value),
            )

    def init_complaint_tab(self):
        tree = ttk.Treeview(
            self.complaint_tab,
            columns=("complainant", "product", "type", "status", "result"),
            show="headings",
            height=10,
        )
        tree.heading("complainant", text="投诉人ID")
        tree.heading("product", text="商品ID/订单ID")
        tree.heading("type", text="投诉类型")
        tree.heading("status", text="状态")
        tree.heading("result", text="处理结果")
        tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.complaint_tree = tree

        btn_frame = ttk.Frame(self.complaint_tab)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="刷新", command=self.refresh_complaints).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="标记为已解决", command=lambda: self.handle_complaint(ComplaintStatus.RESOLVED)).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="标记为已驳回", command=lambda: self.handle_complaint(ComplaintStatus.REJECTED)).pack(
            side="left", padx=5
        )

        self.refresh_complaints()

    def refresh_complaints(self):
        for i in self.complaint_tree.get_children():
            self.complaint_tree.delete(i)
        for c in self.app.admin_service.list_complaints():
            product_info = c.product_id or c.order_id or "-"
            self.complaint_tree.insert(
                "",
                tk.END,
                iid=str(c.id),
                values=(
                    c.complainant_id,
                    product_info,
                    c.type.value,
                    c.status.value,
                    c.result,
                ),
            )

    def handle_complaint(self, status: ComplaintStatus):
        item = self.complaint_tree.focus()
        if not item:
            messagebox.showwarning("提示", "请选择投诉记录")
            return
        cid = int(item)
        result = tk.simpledialog.askstring("处理结果", "请输入处理结果：")
        if not result:
            return
        self.app.admin_service.handle_complaint(cid, status.value, result)
        messagebox.showinfo("成功", "已更新投诉状态")
        self.refresh_complaints()

