"""
Radial Folder Peek - 苹果级文件夹星系透视 (生产级客户端)
基于 Python + Tkinter + Win32 Shell API
符合 frontend-design 规范：
- 苹果精工白净设计规范 (Apple Studio Precision)
- 极坐标星系拓扑与空间深度层次
- 自适应星系半径 (根治少项空旷、多项重叠)
- 像素级保后缀智能截断 (剧本宣创科技...docx)
- 精致文件格式微标与分类容器色彩
- 交互式面包屑导航与极简悬浮 HUD
"""
import os
import sys
import math
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox

# 导入 Windows 资源管理器嗅探模块
try:
    from explorer_hook import get_best_target_path
except ImportError:
    try:
        from scripts.explorer_hook import get_best_target_path
    except ImportError:
        get_best_target_path = lambda fallback=None: os.getcwd()


# Apple Studio Precision 设计规范 Token Sheet
STYLE = {
    # 基础底色与画布
    "bg": "#f8fafc",
    "topbar_bg": "#ffffff",
    "topbar_border": "#e2e8f0",
    
    # 极坐标雷达与星系氛围 (肉眼清晰可辨的高质感灰色虚线)
    "orbit_primary": "#cbd5e1",
    "orbit_secondary": "#e2e8f0",
    "orbit_glow": "#f1f5f9",
    "grid_tick": "#cbd5e1",
    "grid_text": "#64748b",
    
    # 平滑导引流线 (Bezier Curves - 清晰度优化，杜绝肉眼难以看清的问题)
    "line_default": "#cbd5e1",
    "line_active": "#2563eb",
    "line_active_glow": "#dbeafe",
    "line_l2_default": "#94a3b8",
    "line_l2_hover": "#2563eb",
    
    # 中心核心节点 (Linear / Vercel Modern Nucleus)
    "center_bg": "#ffffff",
    "center_border": "#93c5fd",
    "center_border_glow": "#eff6ff",
    "center_halo": "#dbeafe",
    "center_shadow": "#e2e8f0",
    "center_title": "#0f172a",
    "center_sub": "#64748b",
    
    # 项目卡片 (Card Nodes)
    "card_bg": "#ffffff",
    "card_border": "#e2e8f0",
    "card_border_hover": "#60a5fa",
    "card_border_active": "#3b82f6",
    "card_shadow_1": "#f1f5f9",
    "card_shadow_2": "#e2e8f0",
    "text_main": "#0f172a",
    "text_hover": "#1d4ed8",
    
    # 底部 HUD
    "hud_bg": "#ffffff",
    "hud_border": "#e2e8f0",
    "hud_text": "#475569",
    
    # 全息悬浮气泡
    "tooltip_bg": "#0f172a",
    "tooltip_fg": "#ffffff",
    "tooltip_border": "#334155"
}


class RoundedButton(tk.Canvas):
    """现代微圆角交互按钮 (Linear / Vercel Rounded Button)"""
    def __init__(self, parent, text, command=None, bg_color="#ffffff", fg_color="#334155",
                 hover_bg="#f8fafc", hover_fg="#0f172a", border_color="#cbd5e1", hover_border="#94a3b8",
                 radius=8, font=("Microsoft YaHei UI", 9), padx=12, pady=5):
        self.command = command
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_bg = hover_bg
        self.hover_fg = hover_fg
        self.border_color = border_color
        self.hover_border = hover_border
        self.radius = radius

        # 测算文本物理像素宽度与行高
        f = tkfont.Font(family=font[0], size=font[1], weight=font[2] if len(font) > 2 else "normal")
        text_w = f.measure(text)
        text_h = f.metrics("linespace")

        w = text_w + padx * 2
        h = max(30, text_h + pady * 2)

        super().__init__(parent, width=w, height=h, bg=parent["bg"], highlightthickness=0, bd=0, cursor="hand2")
        self.w = w
        self.h = h

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self._draw(self.bg_color, self.fg_color, self.border_color)

    def _draw_round_rect(self, x1, y1, x2, y2, r, fill, outline):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, fill=fill, outline=outline, width=1)

    def _draw(self, fill, fg, outline):
        self.delete("all")
        self._draw_round_rect(1, 1, self.w - 1, self.h - 1, self.radius, fill, outline)
        self.create_text(self.w // 2, self.h // 2, text=self.text, fill=fg, font=self.font)

    def _on_enter(self, e):
        self._draw(self.hover_bg, self.hover_fg, self.hover_border)

    def _on_leave(self, e):
        self._draw(self.bg_color, self.fg_color, self.border_color)

    def _on_press(self, e):
        self._draw(self.hover_bg, self.hover_fg, self.hover_border)

    def _on_release(self, e):
        self._draw(self.hover_bg, self.hover_fg, self.hover_border)
        if self.command and 0 <= e.x <= self.w and 0 <= e.y <= self.h:
            self.command()

    def set_text(self, new_text):
        self.text = new_text
        f = tkfont.Font(family=self.font[0], size=self.font[1], weight=self.font[2] if len(self.font) > 2 else "normal")
        self.w = f.measure(new_text) + 24
        self.config(width=self.w)
        self._draw(self.bg_color, self.fg_color, self.border_color)


class RoundedPill(tk.Canvas):
    """现代胶囊指示条与徽章 (Linear / Vercel Rounded Capsule Pill)"""
    def __init__(self, parent, text, bg_color="#f8fafc", fg_color="#475569", border_color="#e2e8f0",
                 radius=10, font=("Microsoft YaHei UI", 8), padx=10, pady=4):
        f = tkfont.Font(family=font[0], size=font[1], weight=font[2] if len(font) > 2 else "normal")
        text_w = f.measure(text)
        text_h = f.metrics("linespace")

        w = text_w + padx * 2
        h = max(26, text_h + pady * 2)

        super().__init__(parent, width=w, height=h, bg=parent["bg"], highlightthickness=0, bd=0)
        self.w = w
        self.h = h

        points = [
            1 + radius, 1, w - 1 - radius, 1, w - 1, 1, w - 1, 1 + radius,
            w - 1, h - 1 - radius, w - 1, h - 1, w - 1 - radius, h - 1, 1 + radius, h - 1,
            1, h - 1, 1, h - 1 - radius, 1, 1 + radius, 1, 1
        ]
        self.create_polygon(points, smooth=True, fill=bg_color, outline=border_color, width=1)
        self.create_text(w // 2, h // 2, text=text, fill=fg_color, font=font)


class RadialFolderPeekApp:
    def __init__(self, root, initial_path=None):
        self.root = root
        self.root.title("AstroFolder - 星图视界 (文件夹星系透视)")
        self.root.geometry("1240x860+80+30")
        self.root.minsize(980, 700)

        self.style = STYLE
        self.current_path = initial_path or self._detect_initial_path()
        self.history_stack = []

        # 字体系统（支持中英文抗锯齿字重测算）
        self.font_logo = tkfont.Font(family="Microsoft YaHei UI", size=10, weight="bold")
        self.font_main = tkfont.Font(family="Microsoft YaHei UI", size=9)
        self.font_main_bold = tkfont.Font(family="Microsoft YaHei UI", size=9, weight="bold")
        self.font_badge = tkfont.Font(family="Segoe UI", size=8, weight="bold")
        self.font_micro = tkfont.Font(family="Segoe UI", size=7, weight="bold")
        self.font_tooltip = tkfont.Font(family="Microsoft YaHei UI", size=8)

        # 交互与缓存状态
        self.layout_mode = "tree"  # "tree" (思维导图模式) | "orbit" (星轨雷达模式)
        self.camera_x = None
        self.camera_y = None
        self.is_panning = False
        self.has_panned = False
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.pan_cam_x = 0
        self.pan_cam_y = 0

        self.hovered_node = None
        self.active_l1_node = None
        self.nodes_data = {}
        self.l1_items = []
        self.l2_cache = {}

        self._setup_ui()
        self._bind_events()
        self.render_path(self.current_path)

    def _detect_initial_path(self):
        # 1. 命令行参数优先 (例如 run.bat 传参)
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            return os.path.abspath(sys.argv[1])

        # 2. 记忆恢复优先 (恢复上次正常浏览查看的路径，如 E:\project)
        cache_file = os.path.join(os.path.dirname(__file__), ".last_viewed_path.txt")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    last_path = f.read().strip()
                if last_path and os.path.exists(last_path):
                    return last_path
            except Exception:
                pass

        # 3. 当前运行工作区目录 (run.bat 所在工程目录)
        cwd = os.getcwd()
        if cwd and os.path.exists(cwd):
            return cwd

        # 4. 兜底获取前台活动资源管理器
        target = get_best_target_path(cwd)
        if target and os.path.exists(target):
            return target

        return os.path.expanduser("~")

    def _setup_ui(self):
        self.root.configure(bg=self.style["bg"])

        # 顶部精致导航栏 (Apple Studio Frosted Top Bar)
        self.top_bar = tk.Frame(self.root, bg=self.style["topbar_bg"], height=58, padx=16, pady=8)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)
        self.top_bar.pack_propagate(False)

        # 1. 品牌微标 (Brand Logo - 圆角徽章 8px)
        self.logo_badge = RoundedPill(
            self.top_bar, text="✦ RadialPeek", bg_color="#eff6ff", fg_color="#2563eb",
            border_color="#bfdbfe", radius=8, font=("Microsoft YaHei UI", 9, "bold"), padx=10, pady=5
        )
        self.logo_badge.pack(side=tk.LEFT, padx=(0, 8))

        # 分割竖线
        self.sep1 = tk.Frame(self.top_bar, bg="#e2e8f0", width=1, height=22)
        self.sep1.pack(side=tk.LEFT, padx=(0, 8))

        # 2. 核心操作按钮组 (全量配置精致圆弧微圆角 radius=8)
        self.btn_sniff = RoundedButton(
            self.top_bar, text="⚡ 嗅探资源管理器", command=self.sniff_active_explorer,
            bg_color="#2563eb", fg_color="#ffffff", hover_bg="#1d4ed8", hover_fg="#ffffff",
            border_color="#2563eb", hover_border="#1d4ed8", radius=8,
            font=("Microsoft YaHei UI", 9, "bold"), padx=12, pady=5
        )
        self.btn_sniff.pack(side=tk.LEFT, padx=3)

        self.btn_browse = RoundedButton(
            self.top_bar, text="📂 选择文件夹", command=self.browse_folder,
            bg_color="#ffffff", fg_color="#334155", hover_bg="#f8fafc", hover_fg="#0f172a",
            border_color="#cbd5e1", hover_border="#94a3b8", radius=8,
            font=("Microsoft YaHei UI", 9), padx=10, pady=5
        )
        self.btn_browse.pack(side=tk.LEFT, padx=3)

        self.btn_up = RoundedButton(
            self.top_bar, text="⬆ 上一级", command=self.navigate_up,
            bg_color="#ffffff", fg_color="#334155", hover_bg="#f8fafc", hover_fg="#0f172a",
            border_color="#cbd5e1", hover_border="#94a3b8", radius=8,
            font=("Microsoft YaHei UI", 9), padx=10, pady=5
        )
        self.btn_up.pack(side=tk.LEFT, padx=3)

        self.btn_open = RoundedButton(
            self.top_bar, text="↗ 系统打开", command=self.open_current_in_explorer,
            bg_color="#ffffff", fg_color="#64748b", hover_bg="#f8fafc", hover_fg="#0f172a",
            border_color="#cbd5e1", hover_border="#94a3b8", radius=8,
            font=("Microsoft YaHei UI", 9), padx=10, pady=5
        )
        self.btn_open.pack(side=tk.LEFT, padx=3)

        self.btn_layout = RoundedButton(
            self.top_bar, text="🧠 树状导图", command=self.toggle_layout_mode,
            bg_color="#ffffff", fg_color="#2563eb", hover_bg="#eff6ff", hover_fg="#1d4ed8",
            border_color="#bfdbfe", hover_border="#93c5fd", radius=8,
            font=("Microsoft YaHei UI", 9, "bold"), padx=10, pady=5
        )
        self.btn_layout.pack(side=tk.LEFT, padx=3)

        self.btn_reset_view = RoundedButton(
            self.top_bar, text="🎯 居中", command=self.reset_camera,
            bg_color="#ffffff", fg_color="#334155", hover_bg="#f8fafc", hover_fg="#0f172a",
            border_color="#cbd5e1", hover_border="#94a3b8", radius=8,
            font=("Microsoft YaHei UI", 9), padx=8, pady=5
        )
        self.btn_reset_view.pack(side=tk.LEFT, padx=3)

        # 分割竖线
        self.sep2 = tk.Frame(self.top_bar, bg="#e2e8f0", width=1, height=22)
        self.sep2.pack(side=tk.LEFT, padx=(8, 8))

        # 4. 右侧就绪状态胶囊 (Live Status Badge - 圆弧胶囊 10px)
        self.status_badge = RoundedPill(
            self.top_bar, text="● 实时就绪", bg_color="#ecfdf5", fg_color="#059669",
            border_color="#a7f3d0", radius=10, font=("Segoe UI", 8, "bold"), padx=10, pady=4
        )
        self.status_badge.pack(side=tk.RIGHT, padx=(6, 2))

        # 5. 顶部操作指南 HUD 胶囊 (圆弧胶囊 10px，清晰易读)
        self.hud_frame = RoundedPill(
            self.top_bar, text="🖱️ 悬停发散  ·  👈 单击进入  ·  👆 双击打开  ·  🖐 拖拽/滚轮平移  ·  ⌫ 返回",
            bg_color="#f8fafc", fg_color="#64748b", border_color="#cbd5e1",
            radius=10, font=("Microsoft YaHei UI", 8), padx=12, pady=4
        )
        self.hud_frame.pack(side=tk.RIGHT, padx=(0, 6))

        # 3. 动态交互式面包屑导航条 (Interactive Segmented Breadcrumbs)
        self.breadcrumb_container = tk.Frame(self.top_bar, bg=self.style["topbar_bg"])
        self.breadcrumb_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 主画布 (消除边缘边框)
        self.canvas = tk.Canvas(self.root, bg=self.style["bg"], highlightthickness=0, bd=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _bind_events(self):
        self.canvas.bind("<Configure>", lambda e: self.redraw())
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Leave>", self._on_canvas_leave)
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_b1_down)
        self.canvas.bind("<B1-Motion>", self._on_canvas_b1_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_b1_up)
        self.canvas.bind("<ButtonPress-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_move)
        self.canvas.bind("<ButtonPress-3>", self._on_pan_start)
        self.canvas.bind("<B3-Motion>", self._on_pan_move)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.root.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<BackSpace>", lambda e: self.navigate_up())
        self.root.bind("<F5>", lambda e: self.render_path(self.current_path))

    def reset_camera(self):
        w = self.canvas.winfo_width() or 1240
        h = self.canvas.winfo_height() or 860
        if self.layout_mode == "tree":
            self.camera_x = 160
            self.camera_y = h // 2
        else:
            self.camera_x = w // 2
            self.camera_y = h // 2
        self.redraw()

    def toggle_layout_mode(self):
        if self.layout_mode == "tree":
            self.layout_mode = "orbit"
            self.btn_layout.set_text("🪐 星轨雷达")
        else:
            self.layout_mode = "tree"
            self.btn_layout.set_text("🧠 树状导图")
        self.reset_camera()

    def _on_canvas_b1_down(self, event):
        items_under = self.canvas.find_overlapping(event.x - 2, event.y - 2, event.x + 2, event.y + 2)
        has_node = False
        for i_id in items_under:
            tags = self.canvas.gettags(i_id)
            for t in tags:
                if t in self.nodes_data or t == "center":
                    has_node = True
                    break
            if has_node:
                break

        if not has_node:
            self.is_panning = True
            self.has_panned = False
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.pan_cam_x = self.camera_x if self.camera_x is not None else event.x
            self.pan_cam_y = self.camera_y if self.camera_y is not None else event.y
            self.canvas.config(cursor="fleur")
        else:
            self.is_panning = False
            self.has_panned = False

    def _on_canvas_b1_drag(self, event):
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            if abs(dx) > 3 or abs(dy) > 3:
                self.has_panned = True
            self.camera_x = self.pan_cam_x + dx
            self.camera_y = self.pan_cam_y + dy
            self.redraw()

    def _on_canvas_b1_up(self, event):
        if self.is_panning:
            self.is_panning = False
            self.canvas.config(cursor="")
            if self.has_panned:
                return

        # 点击节点
        if not self.has_panned:
            self._on_single_click(event)

    def _on_pan_start(self, event):
        self.is_panning = True
        self.has_panned = False
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_cam_x = self.camera_x if self.camera_x is not None else event.x
        self.pan_cam_y = self.camera_y if self.camera_y is not None else event.y
        self.canvas.config(cursor="fleur")

    def _on_pan_move(self, event):
        if self.is_panning:
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.camera_x = self.pan_cam_x + dx
            self.camera_y = self.pan_cam_y + dy
            self.redraw()

    def _on_mouse_wheel(self, event):
        delta = event.delta
        if self.camera_y is None:
            self.camera_y = self.canvas.winfo_height() // 2
        self.camera_y += delta
        self.redraw()

    def _update_breadcrumbs(self):
        """生成支持逐级点击跳转的高交互圆角面包屑组件"""
        for child in self.breadcrumb_container.winfo_children():
            child.destroy()

        path = os.path.abspath(self.current_path)
        parts = []
        cur = path
        while True:
            parent, tail = os.path.split(cur)
            if tail:
                parts.append((tail, cur))
                cur = parent
            elif parent:
                parts.append((parent, parent))
                break
            else:
                break
        parts.reverse()

        # 最多显示末尾 4 级，前置加省略
        if len(parts) > 5:
            display_parts = [parts[0], ("...", None)] + parts[-3:]
        else:
            display_parts = parts

        for i, (name, target_path) in enumerate(display_parts):
            is_last = (i == len(display_parts) - 1)
            
            if target_path:
                btn = RoundedButton(
                    self.breadcrumb_container, text=name,
                    command=lambda p=target_path: self.render_path(p),
                    bg_color="#eff6ff" if is_last else "#f8fafc",
                    fg_color="#2563eb" if is_last else "#475569",
                    hover_bg="#dbeafe" if is_last else "#f1f5f9",
                    hover_fg="#1d4ed8" if is_last else "#0f172a",
                    border_color="#bfdbfe" if is_last else "#e2e8f0",
                    hover_border="#93c5fd" if is_last else "#cbd5e1",
                    radius=6, font=("Microsoft YaHei UI", 8, "bold" if is_last else "normal"),
                    padx=7, pady=2
                )
                btn.pack(side=tk.LEFT, padx=1)
            else:
                lbl = tk.Label(self.breadcrumb_container, text="...", bg=self.style["topbar_bg"], fg="#94a3b8", font=("Segoe UI", 8))
                lbl.pack(side=tk.LEFT, padx=1)

            if not is_last:
                sep = tk.Label(self.breadcrumb_container, text="/", bg=self.style["topbar_bg"], fg="#cbd5e1", font=("Segoe UI", 8))
                sep.pack(side=tk.LEFT, padx=1)

    def sniff_active_explorer(self):
        target = get_best_target_path(self.current_path)
        if target and os.path.exists(target):
            self.render_path(target)
        else:
            messagebox.showinfo("提示", "未检测到活跃的资源管理器窗口，仍保持当前路径。")

    def browse_folder(self):
        selected = filedialog.askdirectory(parent=self.root, initialdir=self.current_path)
        if selected:
            self.history_stack.append(self.current_path)
            self.render_path(selected)

    def open_current_in_explorer(self):
        if os.path.exists(self.current_path):
            os.startfile(self.current_path)

    def navigate_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path and os.path.exists(parent):
            self.history_stack.append(self.current_path)
            self.render_path(parent)
            self.reset_camera()

    def render_path(self, path):
        if not os.path.exists(path):
            return
        self.current_path = os.path.abspath(path)
        self._update_breadcrumbs()
        self.active_l1_node = None
        self.hovered_node = None
        self.l1_items = self._scan_directory(self.current_path)

        # 记忆当前浏览路径，下次启动时自动恢复用户最后停留的目录
        try:
            cache_file = os.path.join(os.path.dirname(__file__), ".last_viewed_path.txt")
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(self.current_path)
        except Exception:
            pass

        # 默认自动展开首个有子项的文件夹
        for itm in self.l1_items:
            if itm["is_dir"] and itm.get("count", 0) > 0:
                self.active_l1_node = itm
                break

        self.redraw()

    def _scan_directory(self, path):
        """扫描真实文件系统"""
        folders, files = [], []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                        item = {"name": entry.name, "path": entry.path, "is_dir": is_dir, "count": 0}
                        if is_dir:
                            try:
                                item["count"] = len(os.listdir(entry.path))
                            except Exception:
                                item["count"] = 0
                            folders.append(item)
                        else:
                            try:
                                item["size"] = entry.stat().st_size
                            except Exception:
                                item["size"] = 0
                            files.append(item)
                    except Exception:
                        continue
        except Exception as e:
            print(f"扫描出错: {e}", file=sys.stderr)

        folders.sort(key=lambda x: x["name"].lower())
        files.sort(key=lambda x: x["name"].lower())
        return folders + files


    def _measure_card_dimensions(self, item, level):
        """精准测算卡片物理像素宽度，让长文件名100%完整展示，绝不出现省略号截断"""
        box_h = 44 if level == 1 else 38
        icon_box_size = 26 if level == 1 else 22
        _, _, _, type_tag = self._get_item_icon_theme(item)

        badge_w = 0
        if item["is_dir"]:
            count = item.get("count", 0)
            if count > 0:
                badge_w = max(24, len(str(count)) * 7 + 12)
        else:
            badge_w = max(34, len(type_tag) * 6 + 10)

        name_w = self.font_main.measure(item["name"])
        min_w = 150 if level == 1 else 135
        # 9 (左边距) + icon_box_size + 8 (间隙) + name_w + (badge_w + 10 if badge_w > 0 else 0) + 12 (右边距)
        box_w = max(min_w, 9 + icon_box_size + 8 + name_w + (badge_w + 10 if badge_w > 0 else 0) + 12)
        return box_w, box_h, badge_w, icon_box_size

    def _calculate_mindmap_layout(self, w, h):
        """思维导图树状布局计算引擎 (Mind Map Strict Vertical Non-Overlap)"""
        gap_y = 14
        col_dist = 76
        folder_name = os.path.basename(self.current_path) or self.current_path
        root_w = max(204, self.font_main_bold.measure(folder_name) + 90)
        root_h = 62

        cx = self.camera_x if self.camera_x is not None else 160
        cy = self.camera_y if self.camera_y is not None else h // 2

        l1_nodes = []
        total_l1_h = 0
        for item in self.l1_items:
            is_expanded = (self.active_l1_node and self.active_l1_node.get("path") == item.get("path"))
            box_w, box_h, badge_w, ib_size = self._measure_card_dimensions(item, level=1)
            subtree_h = box_h
            children_nodes = []
            if is_expanded:
                sub_items = self._scan_directory(item["path"])
                item["children"] = sub_items
                if sub_items:
                    total_child_h = 0
                    for c in sub_items:
                        cw, ch, c_badge_w, c_ib_size = self._measure_card_dimensions(c, level=2)
                        children_nodes.append({
                            "item": c,
                            "w": cw,
                            "h": ch,
                            "badge_w": c_badge_w,
                            "ib_size": c_ib_size
                        })
                        total_child_h += ch
                    total_child_h += (len(children_nodes) - 1) * gap_y
                    subtree_h = max(box_h, total_child_h)

            l1_nodes.append({
                "item": item,
                "w": box_w,
                "h": box_h,
                "badge_w": badge_w,
                "ib_size": ib_size,
                "subtree_h": subtree_h,
                "is_expanded": is_expanded,
                "children": children_nodes
            })
            total_l1_h += subtree_h

        total_l1_h += max(0, len(l1_nodes) - 1) * gap_y

        cur_y = cy - total_l1_h // 2
        l1_start_x = cx + root_w // 2 + col_dist
        all_l2 = []

        for n in l1_nodes:
            item = n["item"]
            item["level"] = 1
            node_center_y = cur_y + n["subtree_h"] // 2
            item["x"] = l1_start_x + n["w"] // 2
            item["y"] = node_center_y
            item["w"] = n["w"]
            item["h"] = n["h"]
            item["badge_w"] = n["badge_w"]
            item["ib_size"] = n["ib_size"]

            if n["is_expanded"] and n["children"]:
                total_child_h = sum(c["h"] for c in n["children"]) + (len(n["children"]) - 1) * gap_y
                child_cur_y = node_center_y - total_child_h // 2
                l2_start_x = item["x"] + n["w"] // 2 + col_dist
                for c_obj in n["children"]:
                    child = c_obj["item"]
                    child["level"] = 2
                    child["x"] = l2_start_x + c_obj["w"] // 2
                    child["y"] = child_cur_y + c_obj["h"] // 2
                    child["w"] = c_obj["w"]
                    child["h"] = c_obj["h"]
                    child["badge_w"] = c_obj["badge_w"]
                    child["ib_size"] = c_obj["ib_size"]
                    child["parent"] = item
                    all_l2.append(child)
                    child_cur_y += c_obj["h"] + gap_y

            cur_y += n["subtree_h"] + gap_y

        return all_l2, cx, cy, root_w, root_h

    def _draw_tree_branch(self, p1, p2, is_hovered=False, is_active=False, is_dimmed=False):
        """绘制思维导图 S 型水平平滑贝塞尔曲线 (Mind Map Horizontal S-Curve)"""
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        cp1x, cp1y = x1 + dx * 0.5, y1
        cp2x, cp2y = x1 + dx * 0.5, y2

        pts = []
        for step in range(21):
            t = step / 20.0
            u = 1.0 - t
            px = u*u*u*x1 + 3*u*u*t*cp1x + 3*u*t*t*cp2x + t*t*t*x2
            py = u*u*u*y1 + 3*u*u*t*cp1y + 3*u*t*t*cp2y + t*t*t*y2
            pts.extend([px, py])

        if is_hovered or is_active:
            self.canvas.create_line(pts, fill="#bfdbfe", width=3.5, tags="conn")
            self.canvas.create_line(pts, fill="#2563eb", width=1.6, tags="conn")
            mid_idx = 10 * 2
            mx, my = pts[mid_idx], pts[mid_idx + 1]
            self.canvas.create_oval(mx - 2.5, my - 2.5, mx + 2.5, my + 2.5, fill="#2563eb", outline="#ffffff", width=1.0, tags="conn")
        elif is_dimmed:
            self.canvas.create_line(pts, fill="#f1f5f9", width=1.0, tags="conn")
        else:
            self.canvas.create_line(pts, fill="#cbd5e1", width=1.2, tags="conn")

    def redraw(self):
        self.canvas.delete("all")
        self.nodes_data.clear()

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 10 or h <= 10:
            return

        if self.camera_x is None:
            if self.layout_mode == "tree":
                self.camera_x = 160
                self.camera_y = h // 2
            else:
                self.camera_x = w // 2
                self.camera_y = h // 2

        hovered_path = self.hovered_node.get("path") if self.hovered_node else None
        is_any_hovered = bool(hovered_path)

        if self.layout_mode == "tree":
            # === 思维导图模式 (零重叠，全称直显) ===
            l2_nodes, cx, cy, root_w, root_h = self._calculate_mindmap_layout(w, h)

            # 1. 连线层 (低于节点卡片)
            for item in self.l1_items:
                is_hovered = (hovered_path and hovered_path == item["path"])
                is_active = (self.active_l1_node and self.active_l1_node.get("path") == item["path"])
                is_dimmed = False
                if is_any_hovered:
                    is_parent_of_hovered = (is_active and any(c.get("path") == hovered_path for c in l2_nodes))
                    if not is_hovered and not is_parent_of_hovered:
                        is_dimmed = True
                p1 = (cx + root_w // 2, cy)
                p2 = (item["x"] - item["w"] // 2, item["y"])
                self._draw_tree_branch(p1, p2, is_hovered, is_active, is_dimmed)

            for child in l2_nodes:
                is_hovered = (hovered_path and hovered_path == child["path"])
                is_dimmed = (is_any_hovered and not is_hovered)
                parent = child["parent"]
                p1 = (parent["x"] + parent["w"] // 2, parent["y"])
                p2 = (child["x"] - child["w"] // 2, child["y"])
                self._draw_tree_branch(p1, p2, is_hovered, False, is_dimmed)

            # 2. 二级节点卡片
            for child in l2_nodes:
                is_hovered = (hovered_path and hovered_path == child["path"])
                self._render_modern_card(child["x"], child["y"], child, level=2, is_active=False, is_hovered=is_hovered)

            # 3. 一级节点卡片
            for item in self.l1_items:
                is_active = (self.active_l1_node and self.active_l1_node.get("path") == item["path"])
                is_hovered = (hovered_path and hovered_path == item["path"])
                self._render_modern_card(item["x"], item["y"], item, level=1, is_active=is_active, is_hovered=is_hovered)

            # 4. 根工作区卡片
            self._draw_center_card(cx, cy, root_w, root_h)

        else:
            # === 星轨雷达模式 ===
            cx = self.camera_x
            cy = self.camera_y
            self._draw_ambient_orbits(w, h, cx, cy)
            self._calculate_l1_positions(cx, cy)

            l2_nodes = []
            if self.active_l1_node and "x" in self.active_l1_node:
                l2_nodes = self._calculate_l2_nodes_anti_overlap(cx, cy)

            self._draw_all_connections(cx, cy, l2_nodes)

            for child in l2_nodes:
                is_hovered = (hovered_path and hovered_path == child["path"])
                self._render_modern_card(child["x"], child["y"], child, level=2, is_active=False, is_hovered=is_hovered)

            for item in self.l1_items:
                is_active = (self.active_l1_node and self.active_l1_node.get("path") == item["path"])
                is_hovered = (hovered_path and hovered_path == item["path"])
                self._render_modern_card(item["x"], item["y"], item, level=1, is_active=is_active, is_hovered=is_hovered)

            self._draw_center_card(cx, cy)

    def _draw_ambient_orbits(self, w, h, cx, cy):
        """绘制清晰度提升的极坐标同心圆虚线 (Slate-300 #cbd5e1 与 #e2e8f0, 肉眼清晰可见)"""
        n = len(self.l1_items)

        # 1. 中心柔和光晕 (Focal Glow)
        self.canvas.create_oval(cx - 140, cy - 90, cx + 140, cy + 90, fill="", outline="#e2e8f0", width=1)
        self.canvas.create_oval(cx - 80, cy - 50, cx + 80, cy + 50, fill="#f8fafc", outline="#dbeafe", width=1)

        # 2. 自适应星系轨道半径标尺 (清晰明朗的灰色虚线 #cbd5e1 与 #e2e8f0，杜绝看不清)
        if n > 8:
            r_in = min(w, h) * 0.23
            r_out = min(w, h) * 0.38
            self.canvas.create_oval(cx - r_in * 1.05, cy - r_in * 0.72, cx + r_in * 1.05, cy + r_in * 0.72, outline=self.style["orbit_primary"], width=1.2, dash=(4, 6))
            self.canvas.create_oval(cx - r_out * 1.05, cy - r_out * 0.72, cx + r_out * 1.05, cy + r_out * 0.72, outline=self.style["orbit_secondary"], width=1.0, dash=(3, 5))
        else:
            r1 = min(w, h) * (0.22 if n <= 4 else 0.26)
            r2 = min(w, h) * (0.36 if n <= 4 else 0.40)
            self.canvas.create_oval(cx - r1 * 1.05, cy - r1 * 0.72, cx + r1 * 1.05, cy + r1 * 0.72, outline=self.style["orbit_primary"], width=1.2, dash=(4, 6))
            self.canvas.create_oval(cx - r2 * 1.05, cy - r2 * 0.72, cx + r2 * 1.05, cy + r2 * 0.72, outline=self.style["orbit_secondary"], width=1.0, dash=(3, 5))

        # 3. 极简中心十字准星
        cross_len = 22
        self.canvas.create_line(cx - cross_len, cy, cx + cross_len, cy, fill="#cbd5e1", width=1)
        self.canvas.create_line(cx, cy - cross_len, cx, cy + cross_len, fill="#cbd5e1", width=1)

    def _draw_center_card(self, cx, cy, custom_w=None, custom_h=None):
        """绘制中心核心工作区卡片 (Linear / Vercel Modern Nucleus: 全称直显，自适应动态宽度)"""
        folder_name = os.path.basename(self.current_path) or self.current_path
        name_w = self.font_main_bold.measure(folder_name)
        w_box = custom_w or max(204, name_w + 90)
        h_box = custom_h or 62
        x1, y1 = cx - w_box // 2, cy - h_box // 2
        x2, y2 = cx + w_box // 2, cy + h_box // 2

        # 1. 柔和蓝色微发光光晕 (Diffuse Ambient Glow - 去除生硬单色粗框)
        self._draw_rounded_rect(x1 - 4, y1 - 4, x2 + 4, y2 + 4, radius=18, fill="", outline="#eff6ff", width=4, tags="center")
        self._draw_rounded_rect(x1 - 2, y1 - 2, x2 + 2, y2 + 2, radius=16, fill="", outline="#dbeafe", width=2, tags="center")

        # 2. 现代弥散柔和多层底影
        self.canvas.create_rectangle(x1 + 1, y1 + 3, x2 + 1, y2 + 6, fill="#e2e8f0", outline="", tags="center")
        self.canvas.create_rectangle(x1 + 2, y1 + 5, x2 + 2, y2 + 9, fill="#f1f5f9", outline="", tags="center")

        # 3. 纯白立体主卡片 (半透明渐变蓝微边框 1px)
        self._draw_rounded_rect(x1, y1, x2, y2, radius=14, fill="#ffffff", outline=self.style["center_border"], width=1, tags="center")

        # 4. 顶部极光微发光顶线 (Top Hairline Glow)
        self.canvas.create_line(x1 + 22, y1 + 1, x2 - 22, y1 + 1, fill="#3b82f6", width=2, tags="center")

        # 5. 左侧专属徽章容器 (微圆角 9px + 低饱和品牌蓝)
        badge_size = 32
        bx1 = x1 + 14
        by1 = cy - badge_size // 2
        bx2 = bx1 + badge_size
        by2 = by1 + badge_size
        self._draw_rounded_rect(bx1, by1, bx2, by2, radius=9, fill="#eff6ff", outline="#bfdbfe", width=1, tags="center")
        self.canvas.create_text((bx1 + bx2)//2, cy, text="📁", font=("Segoe UI", 12), tags="center")

        # 6. 右侧信息层级结构
        info_x = bx2 + 12
        # 上层精致胶囊徽章 Badge (Linear 风格: bg-slate-100 text-slate-500 rounded-full)
        badge_w = 118
        badge_h = 16
        self._draw_rounded_rect(info_x, cy - 19, info_x + badge_w, cy - 3, radius=8, fill="#f1f5f9", outline="#e2e8f0", width=1, tags="center")
        self.canvas.create_text(info_x + badge_w // 2, cy - 11, text="CURRENT WORKSPACE", fill="#64748b", font=self.font_micro, tags="center")

        # 文件夹主名称
        self.canvas.create_text(info_x, cy + 7, text=folder_name, fill=self.style["center_title"], anchor="w", font=self.font_main_bold, tags="center")

        self.canvas.tag_bind("center", "<Button-1>", lambda e: self.navigate_up())

    def _calculate_l1_positions(self, cx, cy):
        """
        核心自适应布局算法：
        - N <= 4: 精简致密内径 (避免少文件空旷)
        - 5 <= N <= 8: 中等舒适星系轨道
        - N > 8: 【双圈内外交替轨道】(解决多文件堆叠)
        - 配合 6 轮物理斥力防重叠松弛迭代，实现极致几何平衡
        """
        n = len(self.l1_items)
        if n == 0:
            return

        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if n <= 4:
            base_rx = min(w * 0.22, 225)
            base_ry = min(h * 0.22, 150)
            for i, item in enumerate(self.l1_items):
                angle = -math.pi / 2 + (2 * math.pi * i) / n
                item["x"] = int(cx + base_rx * math.cos(angle))
                item["y"] = int(cy + base_ry * math.sin(angle))
                item["angle"] = angle
                item["level"] = 1
        elif n <= 8:
            base_rx = min(w * 0.26, 275)
            base_ry = min(h * 0.26, 185)
            for i, item in enumerate(self.l1_items):
                angle = -math.pi / 2 + (2 * math.pi * i) / n
                item["x"] = int(cx + base_rx * math.cos(angle))
                item["y"] = int(cy + base_ry * math.sin(angle))
                item["angle"] = angle
                item["level"] = 1
        else:
            rx_inner = min(w * 0.23, 245)
            ry_inner = min(h * 0.23, 165)
            rx_outer = min(w * 0.37, 390)
            ry_outer = min(h * 0.37, 265)

            for i, item in enumerate(self.l1_items):
                angle = -math.pi / 2 + (2 * math.pi * i) / n
                curr_rx = rx_inner if i % 2 == 0 else rx_outer
                curr_ry = ry_inner if i % 2 == 0 else ry_outer

                item["x"] = int(cx + curr_rx * math.cos(angle))
                item["y"] = int(cy + curr_ry * math.sin(angle))
                item["angle"] = angle
                item["level"] = 1

        # 智能互斥松弛迭代 (Relaxation Repulsion)
        card_w, card_h = 176, 44
        center_w, center_h = 196, 68
        for _ in range(6):
            # 1. 避让中心卡片
            for item in self.l1_items:
                dx = item["x"] - cx
                dy = item["y"] - cy
                overlap_x = (card_w / 2 + center_w / 2 + 14) - abs(dx)
                overlap_y = (card_h / 2 + center_h / 2 + 14) - abs(dy)
                if overlap_x > 0 and overlap_y > 0:
                    dist = math.hypot(dx, dy) or 1
                    push = min(overlap_x, overlap_y)
                    item["x"] = int(item["x"] + (dx / dist) * push)
                    item["y"] = int(item["y"] + (dy / dist) * push)

            # 2. 节点之间互斥避让
            for i in range(n):
                for j in range(i + 1, n):
                    n1, n2 = self.l1_items[i], self.l1_items[j]
                    dx = n2["x"] - n1["x"]
                    dy = n2["y"] - n1["y"]
                    min_dx = card_w + 12
                    min_dy = card_h + 8
                    overlap_x = min_dx - abs(dx)
                    overlap_y = min_dy - abs(dy)
                    if overlap_x > 0 and overlap_y > 0:
                        if overlap_x < overlap_y:
                            shift = int(overlap_x * 0.55)
                            sgn = 1 if dx >= 0 else -1
                            n2["x"] += shift * sgn
                            n1["x"] -= shift * sgn
                        else:
                            shift = int(overlap_y * 0.55)
                            sgn = 1 if dy >= 0 else -1
                            n2["y"] += shift * sgn
                            n1["y"] -= shift * sgn

            # 3. 严格视口边缘夹紧
            pad_x = card_w // 2 + 10
            pad_y = card_h // 2 + 10
            for item in self.l1_items:
                item["x"] = max(pad_x, min(w - pad_x, item["x"]))
                item["y"] = max(pad_y, min(h - pad_y, item["y"]))

    def _get_card_boundary_point(self, cx, cy, w, h, target_x, target_y, padding=5):
        """计算卡片边界点并留出 5px 的呼吸间距 (Padding，避免硬连到文字或边框边缘)"""
        dx = target_x - cx
        dy = target_y - cy
        if abs(dx) < 1e-4 and abs(dy) < 1e-4:
            return cx, cy
        half_w = w / 2.0
        half_h = h / 2.0
        scale_x = half_w / abs(dx) if abs(dx) > 1e-4 else 1e4
        scale_y = half_h / abs(dy) if abs(dy) > 1e-4 else 1e4
        scale = min(scale_x, scale_y)

        edge_x = cx + dx * scale
        edge_y = cy + dy * scale

        dist = math.hypot(dx, dy) or 1.0
        return edge_x + (dx / dist) * padding, edge_y + (dy / dist) * padding

    def _draw_all_connections(self, cx, cy, l2_nodes):
        """绘制高阶三阶贝塞尔平滑流线 (Cubic Bezier: 切线发散引导、1px细线、关联高亮与非关联虚化)"""
        if not self.l1_items:
            return

        hovered_path = self.hovered_node.get("path") if self.hovered_node else None
        is_any_hovered = bool(hovered_path)

        # 1. 一级平滑三阶贝塞尔曲线 (从中心卡片向外发散)
        for item in self.l1_items:
            is_hovered = (hovered_path and hovered_path == item["path"])
            is_active = (self.active_l1_node and self.active_l1_node.get("path") == item["path"])

            # 关联连线高亮与非关联虚化判定
            is_dimmed = False
            if is_any_hovered:
                is_parent_of_hovered = (is_active and any(c.get("path") == hovered_path for c in l2_nodes))
                if not is_hovered and not is_parent_of_hovered:
                    is_dimmed = True

            # 计算留出 5px padding 的边界端点
            p1_x, p1_y = self._get_card_boundary_point(cx, cy, 204, 62, item["x"], item["y"], padding=5)
            p2_x, p2_y = self._get_card_boundary_point(item["x"], item["y"], 176, 44, cx, cy, padding=5)

            dist = math.hypot(p2_x - p1_x, p2_y - p1_y)
            if dist < 4:
                continue

            ray_angle = math.atan2(item["y"] - cy, item["x"] - cx)
            tangent_len = dist * 0.40
            curve_offset = math.sin(ray_angle * 2) * (dist * 0.05)
            perp_x = -math.sin(ray_angle) * curve_offset
            perp_y = math.cos(ray_angle) * curve_offset

            cp1x = p1_x + math.cos(ray_angle) * tangent_len + perp_x
            cp1y = p1_y + math.sin(ray_angle) * tangent_len + perp_y
            cp2x = p2_x - math.cos(ray_angle) * tangent_len + perp_x
            cp2y = p2_y - math.sin(ray_angle) * tangent_len + perp_y

            if is_hovered or is_active:
                # 关联高亮：1.5px 发光曲线 + 发光外晕
                self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#dbeafe", width=4)
                self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#3b82f6", width=1.5)
                # 贝塞尔中点发光光斑
                mid_t = 0.5
                u = 1 - mid_t
                mx = u**3 * p1_x + 3 * u**2 * mid_t * cp1x + 3 * u * mid_t**2 * cp2x + mid_t**3 * p2_x
                my = u**3 * p1_y + 3 * u**2 * mid_t * cp1y + 3 * u * mid_t**2 * cp2y + mid_t**3 * p2_y
                self.canvas.create_oval(mx - 2.5, my - 2.5, mx + 2.5, my + 2.5, fill="#3b82f6", outline="#ffffff", width=1.0)
            elif is_dimmed:
                # 其余非关联连线进一步虚化 (极淡灰 #f1f5f9)
                self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#f1f5f9", width=1)
            else:
                # 普通连线：1px 细线 #cbd5e1，三阶贝塞尔平滑流线，绝不抢占视觉焦点
                self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#cbd5e1", width=1)

        # 2. 二级与深层导引连线 (三阶贝塞尔：起点沿父节点朝向平滑发散进入子节点，杜绝密集处线条过粗过硬)
        parent = self.active_l1_node
        if parent and l2_nodes:
            px, py = parent["x"], parent["y"]
            p_heading = parent.get("angle", math.atan2(py - cy, px - cx))

            for child in l2_nodes:
                is_hovered = (hovered_path and hovered_path == child["path"])
                is_dimmed = (is_any_hovered and not is_hovered)

                # 两端卡片边界点，留出 5px padding
                p1_x, p1_y = self._get_card_boundary_point(px, py, 176, 44, child["x"], child["y"], padding=5)
                p2_x, p2_y = self._get_card_boundary_point(child["x"], child["y"], 158, 38, px, py, padding=5)

                dist = math.hypot(p2_x - p1_x, p2_y - p1_y)
                if dist < 4:
                    continue

                tangent_len = dist * 0.44
                enter_angle = math.atan2(p2_y - p1_y, p2_x - p1_x)

                cp1x = p1_x + math.cos(p_heading) * tangent_len
                cp1y = p1_y + math.sin(p_heading) * tangent_len
                cp2x = p2_x - math.cos(enter_angle) * tangent_len
                cp2y = p2_y - math.sin(enter_angle) * tangent_len

                if is_hovered:
                    # 悬停连线高亮 (1.5px 发光蓝)
                    self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#dbeafe", width=4)
                    self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#3b82f6", width=1.5)
                    mid_t = 0.5
                    u = 1 - mid_t
                    mx = u**3 * p1_x + 3 * u**2 * mid_t * cp1x + 3 * u * mid_t**2 * cp2x + mid_t**3 * p2_x
                    my = u**3 * p1_y + 3 * u**2 * mid_t * cp1y + 3 * u * mid_t**2 * cp2y + mid_t**3 * p2_y
                    self.canvas.create_oval(mx - 2.5, my - 2.5, mx + 2.5, my + 2.5, fill="#3b82f6", outline="#ffffff", width=1.0)
                elif is_dimmed:
                    # 非关联连线虚化 (极淡灰 #f1f5f9)
                    self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#f1f5f9", width=1)
                else:
                    # 默认 1px 细线 #cbd5e1，三阶贝塞尔平滑流线，消除网状直插感
                    self.canvas.create_line(p1_x, p1_y, cp1x, cp1y, cp2x, cp2y, p2_x, p2_y, smooth=True, fill="#cbd5e1", width=1)

    def _calculate_l2_nodes_anti_overlap(self, cx, cy):
        parent = self.active_l1_node
        if not parent or not parent["is_dir"]:
            return []

        if "x" not in parent or "y" not in parent or "angle" not in parent:
            return []

        path = parent["path"]
        if path not in self.l2_cache:
            self.l2_cache[path] = self._scan_directory(path)

        children = self.l2_cache[path]
        if not children:
            return []

        px, py = parent["x"], parent["y"]
        parent_angle = parent["angle"]
        m = len(children)

        cone_span = math.radians(min(110, max(50, m * 18)))
        r_inner = 160
        r_outer = 245

        l2_nodes = []
        for j, child in enumerate(children):
            if m == 1:
                sub_angle = parent_angle
            else:
                sub_angle = parent_angle - (cone_span / 2) + (cone_span * j) / (m - 1)

            dist = (r_inner if (j % 2 == 0) else r_outer) if m >= 4 else 175

            c_x = int(px + dist * math.cos(sub_angle))
            c_y = int(py + dist * math.sin(sub_angle))

            child["x"] = c_x
            child["y"] = c_y
            child["angle"] = sub_angle
            child["parent_x"] = px
            child["parent_y"] = py
            child["level"] = 2
            l2_nodes.append(child)

        # L2 节点间防重叠与边界约束
        l2_card_w, l2_card_h = 158, 38
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for _ in range(5):
            for i in range(len(l2_nodes)):
                for j in range(i + 1, len(l2_nodes)):
                    n1, n2 = l2_nodes[i], l2_nodes[j]
                    dx = n2["x"] - n1["x"]
                    dy = n2["y"] - n1["y"]
                    min_dx = l2_card_w + 10
                    min_dy = l2_card_h + 6
                    overlap_x = min_dx - abs(dx)
                    overlap_y = min_dy - abs(dy)
                    if overlap_x > 0 and overlap_y > 0:
                        if overlap_x < overlap_y:
                            shift = int(overlap_x * 0.55)
                            sgn = 1 if dx >= 0 else -1
                            n2["x"] += shift * sgn
                            n1["x"] -= shift * sgn
                        else:
                            shift = int(overlap_y * 0.55)
                            sgn = 1 if dy >= 0 else -1
                            n2["y"] += shift * sgn
                            n1["y"] -= shift * sgn

            pad_x = l2_card_w // 2 + 12
            pad_y_min = 65 + l2_card_h // 2
            pad_y_max = h - l2_card_h // 2 - 12
            for child in l2_nodes:
                child["x"] = max(pad_x, min(w - pad_x, child["x"]))
                child["y"] = max(pad_y_min, min(pad_y_max, child["y"]))

        return l2_nodes

    def _get_item_icon_theme(self, item):
        """根据真实文件类型匹配高质感专属微标与类型标签"""
        if item["is_dir"]:
            return "📁", "#eff6ff", "#2563eb", "DIR"

        name_lower = item["name"].lower()
        if name_lower.endswith((".docx", ".doc")):
            return "📝", "#eff6ff", "#1d4ed8", "DOCX"
        elif name_lower.endswith((".xlsx", ".xls", ".csv")):
            return "📊", "#ecfdf5", "#059669", "XLSX"
        elif name_lower.endswith((".pdf",)):
            return "📕", "#fef2f2", "#dc2626", "PDF"
        elif name_lower.endswith((".py", ".ts", ".js", ".json", ".vue", ".html")):
            return "💻", "#f5f3ff", "#7c3aed", "CODE"
        elif name_lower.endswith((".png", ".jpg", ".jpeg", ".svg")):
            return "🖼️", "#fffbeb", "#d97706", "IMG"
        elif name_lower.endswith((".zip", ".rar", ".7z", ".tar")):
            return "📦", "#fff7ed", "#ea580c", "ZIP"
        return "📄", "#f8fafc", "#64748b", "FILE"

    def _truncate_text_to_width(self, text, max_pixel_width, font, is_dir=False):
        """
        核心防溢出算法：基于物理像素宽度严格剪裁文字。
        - 对文件：智能保留扩展名（如 '剧本宣创科技...docx'），杜绝粗暴截断产生 'd..'
        - 对文件夹：优雅添加 '..'
        - 确保 100% 绝对不超出可用物理像素范围！
        """
        if font.measure(text) <= max_pixel_width:
            return text, False

        ellipsis = ".."
        if is_dir:
            stem = text
            ext = ""
        else:
            stem, ext = os.path.splitext(text)
            if len(ext) > 7 or not ext:
                stem, ext = text, ""

        fixed_w = font.measure(ellipsis + ext)
        if fixed_w >= max_pixel_width:
            avail = max_pixel_width - font.measure(ellipsis)
            t = text
            while t and font.measure(t) > avail:
                t = t[:-1]
            return t + ellipsis, True

        avail_stem = max_pixel_width - fixed_w
        trimmed_stem = stem
        while trimmed_stem and font.measure(trimmed_stem) > avail_stem:
            trimmed_stem = trimmed_stem[:-1]

        return trimmed_stem + ellipsis + ext, True

    def _render_modern_card(self, x, y, item, level, is_active, is_hovered):
        # 尺寸根据全文件名动态计算包裹
        box_w = item.get("w", 176 if level == 1 else 158)
        box_h = item.get("h", 44 if level == 1 else 38)
        card_r = 14 if level == 1 else 12

        # 悬停微上浮态
        draw_y = y - 2 if is_hovered else y
        x1, y1 = x - box_w // 2, draw_y - box_h // 2
        x2, y2 = x + box_w // 2, draw_y + box_h // 2

        tag = f"node_{id(item)}"
        self.nodes_data[tag] = item

        border_col = self.style["card_border_hover"] if is_hovered else (self.style["card_border_active"] if is_active else self.style["card_border"])
        border_w = 1.5 if (is_hovered or is_active) else 1.0

        # 1. 弥散阴影
        if is_hovered or is_active:
            self.canvas.create_rectangle(x1 + 1, y1 + 3, x2 + 1, y2 + 6, fill="#e2e8f0", outline="", tags=(tag, "node"))
            self.canvas.create_rectangle(x1 + 2, y1 + 5, x2 + 2, y2 + 9, fill="#cbd5e1", outline="", tags=(tag, "node"))
        else:
            self.canvas.create_rectangle(x1 + 1, y1 + 2, x2 + 1, y2 + 4, fill="#f1f5f9", outline="", tags=(tag, "node"))
            self.canvas.create_rectangle(x1 + 1, y1 + 1, x2 + 1, y2 + 2, fill="#e2e8f0", outline="", tags=(tag, "node"))

        # 2. 纯白主体微毛玻璃卡片
        self._draw_rounded_rect(x1, y1, x2, y2, radius=card_r, fill="#ffffff", outline=border_col, width=border_w, tags=(tag, "node"))

        # 3. 左侧矢量微标容器
        icon_box_size = item.get("ib_size", 26 if level == 1 else 22)
        ib_x1 = x1 + 9
        ib_y1 = draw_y - icon_box_size // 2
        ib_x2 = ib_x1 + icon_box_size
        ib_y2 = ib_y1 + icon_box_size

        icon_char, icon_bg, icon_fg, type_tag = self._get_item_icon_theme(item)
        self._draw_rounded_rect(ib_x1, ib_y1, ib_x2, ib_y2, radius=8 if level == 1 else 6, fill=icon_bg, outline=border_col if is_hovered else "#e2e8f0", width=1, tags=(tag, "node"))
        self.canvas.create_text(ib_x1 + icon_box_size//2, draw_y, text=icon_char, font=("Segoe UI", 10 if level == 1 else 9), tags=(tag, "node"))

        # 4. 右侧圆角胶囊角标
        badge_w = item.get("badge_w", 0)
        bx2 = x2 - 8
        bx1 = bx2 - badge_w
        if item["is_dir"]:
            count = item.get("count", 0)
            if count > 0:
                count_str = str(count)
                badge_h = 18
                by1 = draw_y - badge_h // 2
                by2 = by1 + badge_h
                self._draw_rounded_rect(bx1, by1, bx2, by2, radius=9, fill="#f1f5f9", outline="#e2e8f0", width=1, tags=(tag, "node"))
                self.canvas.create_text((bx1 + bx2)//2, draw_y, text=count_str, fill="#64748b", font=self.font_badge, tags=(tag, "node"))
        else:
            fmt_str = type_tag
            badge_h = 16
            by1 = draw_y - badge_h // 2
            by2 = by1 + badge_h
            self._draw_rounded_rect(bx1, by1, bx2, by2, radius=8, fill="#f8fafc", outline="#e2e8f0", width=1, tags=(tag, "node"))
            self.canvas.create_text((bx1 + bx2)//2, draw_y, text=fmt_str, fill="#64748b", font=self.font_micro, tags=(tag, "node"))

        # 5. 中间文件名：100% 完整直接呈现，绝不截断或显示省略号
        text_start_x = ib_x2 + 8
        font_used = self.font_main_bold if (is_active or is_hovered) else self.font_main
        text_color = self.style["text_hover"] if (is_hovered or is_active) else self.style["text_main"]
        item["is_truncated"] = False
        self.canvas.create_text(text_start_x, draw_y, text=item["name"], fill=text_color, anchor="w", font=font_used, tags=(tag, "node"))

    def _draw_hover_tooltip(self, item):
        """当长文件名截断时，悬停在其上方浮现精致全名全息气泡"""
        full_name = item["name"]
        w = self.canvas.winfo_width()

        text_w = self.font_tooltip.measure(full_name) + 24
        tooltip_w = min(max(text_w, 120), 480)
        tooltip_h = 28

        tx = item["x"]
        ty = item["y"] - 34
        tx1 = max(10, min(w - tooltip_w - 10, tx - tooltip_w // 2))
        tx2 = tx1 + tooltip_w
        ty1 = max(10, ty - tooltip_h // 2)
        ty2 = ty1 + tooltip_h

        # 柔和底影
        self.canvas.create_rectangle(tx1 + 1, ty1 + 2, tx2 + 1, ty2 + 2, fill="#cbd5e1", outline="", tags="tooltip")
        # 绘制黑曜石气泡
        self._draw_rounded_rect(tx1, ty1, tx2, ty2, radius=6, fill=self.style["tooltip_bg"], outline=self.style["tooltip_border"], width=1, tags="tooltip")
        self.canvas.create_text((tx1 + tx2) // 2, (ty1 + ty2) // 2, text=full_name, fill=self.style["tooltip_fg"], font=self.font_tooltip, tags="tooltip")

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius=6, fill="", outline="", width=1, tags=None):
        r = radius
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, fill=fill, outline=outline, width=width, tags=tags)

    def _on_canvas_motion(self, event):
        items_under = self.canvas.find_overlapping(event.x - 2, event.y - 2, event.x + 2, event.y + 2)
        matched = None
        for i_id in items_under:
            tags = self.canvas.gettags(i_id)
            for t in tags:
                if t in self.nodes_data:
                    matched = self.nodes_data[t]
                    break
            if matched:
                break

        need_redraw = False
        if matched != self.hovered_node:
            self.hovered_node = matched
            need_redraw = True

        if matched and matched.get("level") == 1 and matched.get("is_dir"):
            if self.active_l1_node != matched:
                self.active_l1_node = matched
                need_redraw = True

        if need_redraw:
            self.redraw()

    def _on_canvas_leave(self, event):
        if self.hovered_node:
            self.hovered_node = None
            self.redraw()

    def _on_single_click(self, event):
        if self.hovered_node:
            item = self.hovered_node
            if item.get("is_center"):
                self.navigate_up()
                return
            if item.get("is_dir"):
                self.history_stack.append(self.current_path)
                self.render_path(item["path"])
                self.reset_camera()

    def _on_double_click(self, event):
        if self.hovered_node:
            if self.hovered_node.get("is_center"):
                self.navigate_up()
                return
            if self.hovered_node.get("is_dir"):
                self.history_stack.append(self.current_path)
                self.render_path(self.hovered_node["path"])
                self.reset_camera()
                return
            try:
                os.startfile(self.hovered_node["path"])
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开项: {e}")


def main():
    root = tk.Tk()
    initial = sys.argv[1] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else None
    app = RadialFolderPeekApp(root, initial_path=initial)
    root.mainloop()


if __name__ == "__main__":
    main()
