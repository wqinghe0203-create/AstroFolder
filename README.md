# 🌌 AstroFolder (星图视界)

> **像看星轨一样，全景俯瞰你的文件夹与文档。**  
> 告别枯燥扁平的文件树！AstroFolder 是一款将文件夹层级结构转化为 **360° 极坐标辐射星系拓扑** 的新一代文件透视工具。遵循 Linear / Vercel 现代精工设计规范，提供双模式支持（零环境网页免安装版 + 独立免配环境桌面客户端）。

---

## ✨ 核心特性

- 🪐 **极坐标星轨拓扑（Radial Celestial Orbits）**：当前工作区置于中心主核，一级子文件夹/文件呈行星环绕分布，二级子项沿三阶贝塞尔平滑流线辐射展开。
- 🔍 **全深度穿透下钻（Infinite Deep Drill-down）**：支持任意深度的文件夹点击下钻与层级跳转，实时响应，完整呈现深层所有子文件夹与全部文档（`.docx`、`.xlsx`、`.pdf`、代码等）。
- 🎨 **Apple & Linear 现代工程美学**：弥散柔和多层阴影、毛玻璃卡片、微发光渐变微边框、低饱和度格式微标（`DOCX`、`XLSX`、`PDF`、`CODE` 等）。
- 🚀 **双运行形态支持**：
  - **网页极速免安装版 (`AstroFolder.html`)**：单文件纯前端（HTML5 Canvas + File System Access API），任何现代浏览器（Edge / Chrome）双击秒开，0 依赖、0 安装、跨平台！
  - **独立桌面客户端 (`AstroFolder.exe`)**：内置微型 Python 运行时环境，支持双击直接在 Windows 本地 Word/Excel/WPS 中打开原文件并实时编辑保存。
- 👁️ **全息快速预览（Quick Look）**：
  - PDF 文件：原生浏览器阅读器直接打开；
  - 图片文件：高保真灯箱大图无损全屏预览；
  - 文本/代码：等宽字体行号代码阅读器；
  - Office 文档：全息元数据卡片 + 一键呼起本地软件查看。

---

## 🚀 极速上手

### 方式一：网页免安装版（最推荐，零环境配置）
1. 双击运行 `run_web.bat`（或直接双击用 Edge/Chrome 打开 `AstroFolder.html`）；
2. 点击页面顶部导航栏的 **「📂 打开本地文件夹」**；
3. 选入电脑中的任意工程或需求目录，即可享受 360° 星系展开！

### 方式二：独立桌面客户端（绿色免安装）
1. 双击运行根目录下的 `run.bat`（或进入 `bin/AstroFolder` 目录双击 `AstroFolder.exe`）；
2. 客户端秒级弹出，无需安装配置 Python 环境；
3. 双击任何文件，直接调用 Windows 关联的本地应用（如 Word、Excel、VS Code）打开原文件。

---

## 🎮 常用交互手势

| 操作手势 | 触发交互 | 说明 |
| :--- | :--- | :--- |
| **鼠标悬停 (Hover)** | 发散展开二级星轨 | 悬停在一级文件夹上，平滑散开其内部子项；长文件名自动浮现全名气泡 |
| **单击文件夹 (Click)** | 下钻进入目录 | 瞬间进入该目录，中心卡片实时更新为主星核，向外辐射展示其全部直属项 |
| **双击文件 (Double Click)** | 打开/预览文件 | 桌面版直接调起本地软件打开；网页版提供高清预览或一键调起 |
| **单击中心卡片** | 返回上一级 | 快速回到父级目录 |
| **点击顶部面包屑** | 精准路径跳转 | 任意点击上级路径胶囊，快速回溯 |

---

## 📁 目录结构

```text
AstroFolder/
├── AstroFolder.html                # 核心网页版（单文件纯前端，零依赖）
├── AstroFolder_网页免安装版.html    # 中文命名备份
├── run_web.bat                     # 一键唤起网页版
├── run.bat                         # 一键唤起独立桌面版
├── 使用说明_README.txt              # 纯文本使用手册
├── scripts/                        # 桌面客户端源码
│   ├── cyber_radial_peek.py        # 极坐标核心绘制与交互主程序 (Tkinter)
│   └── explorer_hook.py            # Windows 资源管理器前台探测模块
└── bin/                            # 独立绿色免安装运行时 (PyInstaller)
    └── AstroFolder/
        ├── AstroFolder.exe         # Windows 独立引导程序
        └── _internal/              # 内置微型 Python 运行时与依赖库
```

---

## 🛠️ 技术栈

- **前端渲染**：HTML5 Canvas 2D, File System Access API, CSS3 Glassmorphism (Backdrop Filter), Web Audio API (交互声效反馈)
- **桌面客户端**：Python 3.12, Tkinter Canvas Engine, Win32 API, PyWin32 Shell COM
- **构建打包**：PyInstaller Standalone Runtime

---

## 📄 开源许可

本项目遵循 MIT 开源许可证。欢迎提 Issue 与 PR 共建！
