# main.py
import tkinter as tk
from tkinter import ttk, messagebox

from gui_views import (
    AppContext,
    LoginFrame,
    RegisterFrame,
    HomeFrame,
    PublishProductFrame,
    ProductDetailFrame,
    ComplaintFrame,
    AdminFrame,
)
from models import UserRole


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("网络商场系统")
        self.geometry("700x600")

        self.app_ctx = AppContext(self)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # ⭐ 关键修复：把 MainApp 的页面切换方法挂到 container 上
        for name in (
            "show_login",
            "show_register",
            "show_home",
            "show_publish",
            "show_product_detail",
            "show_complaint",
            "show_admin",
        ):
            setattr(self.container, name, getattr(self, name))

        self.current_frame = None

        self.create_menu()
        self.show_login()


    # ========== 菜单 ==========

    def create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        m_user = tk.Menu(menubar, tearoff=0)
        m_user.add_command(label="登录", command=self.show_login)
        m_user.add_command(label="注册", command=self.show_register)
        menubar.add_cascade(label="用户", menu=m_user)

        m_market = tk.Menu(menubar, tearoff=0)
        m_market.add_command(label="首页", command=self.show_home)
        m_market.add_command(label="发布商品", command=self.show_publish)
        menubar.add_cascade(label="商城", menu=m_market)

        m_admin = tk.Menu(menubar, tearoff=0)
        m_admin.add_command(label="后台管理", command=self.show_admin)
        menubar.add_cascade(label="管理员", menu=m_admin)

    # ========== Frame 切换辅助 ==========

    def _set_frame(self, frame_cls, *args, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_cls(self.container, *args, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    # ========== 各页面入口 ==========

    def show_login(self, prefill_phone: str = ""):
        def on_login_success():
            messagebox.showinfo("成功", "登录成功")
            self.show_home()

        self._set_frame(LoginFrame, self.app_ctx, on_login_success)
        if prefill_phone:
            self.current_frame.phone_var.set(prefill_phone)

    def show_register(self, prefill_phone: str = ""):
        self._set_frame(RegisterFrame, self.app_ctx)
        if prefill_phone:
            self.current_frame.phone_var.set(prefill_phone)

    def show_home(self):
        self._set_frame(HomeFrame, self.app_ctx)

    def show_publish(self):
        user = self.app_ctx.current_user
        if not user or user.role not in (UserRole.SELLER, UserRole.ADMIN):
            messagebox.showerror("错误", "只有卖家/管理员可以发布商品")
            return

        def on_published():
            self.show_home()

        self._set_frame(PublishProductFrame, self.app_ctx, on_published)

    def show_product_detail(self, product):
        self._set_frame(ProductDetailFrame, self.app_ctx, product)

    def show_complaint(self, product_id=None, order_id=None):
        self._set_frame(ComplaintFrame, self.app_ctx, product_id=product_id, order_id=order_id)

    def show_admin(self):
        user = self.app_ctx.current_user
        if not user or user.role != UserRole.ADMIN:
            messagebox.showerror("错误", "仅管理员可访问后台")
            return
        self._set_frame(AdminFrame, self.app_ctx)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()

