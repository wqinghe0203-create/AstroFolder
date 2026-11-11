"""
Windows 资源管理器活动路径与选中项嗅探模块
利用 Windows Shell COM 自动化接口探测当前活动资源管理器会话及文件项
"""
import os
import sys

def get_active_explorer_paths():
    """
    获取当前系统中所有打开的资源管理器窗口及其选中的路径
    返回列表: [{"hwnd": int, "path": str, "selected": list[str]}]
    """
    results = []
    try:
        import win32com.client
        shell = win32com.client.Dispatch("Shell.Application")
        for window in shell.Windows():
            try:
                # 过滤 IE/Edge 等旧 COM 窗口，只保留本地文件浏览
                doc = getattr(window, "Document", None)
                if not doc:
                    continue
                
                folder = getattr(doc, "Folder", None)
                if not folder or not hasattr(folder, "Self"):
                    continue
                
                curr_path = folder.Self.Path
                if not curr_path or not os.path.exists(curr_path):
                    continue
                
                selected_paths = []
                sel = getattr(doc, "SelectedItems", None)
                if sel and callable(sel):
                    selected_items = sel()
                    for i in range(selected_items.Count):
                        try:
                            selected_paths.append(selected_items.Item(i).Path)
                        except Exception:
                            pass
                
                results.append({
                    "hwnd": getattr(window, "HWND", 0),
                    "path": curr_path,
                    "selected": selected_paths
                })
            except Exception:
                continue
    except Exception as e:
        print(f"[ExplorerHook] 无法初始化 COM 接口: {e}", file=sys.stderr)
        
    return results

def get_best_target_path(fallback_path=None):
    """
    获取最适合透视的路径：
    1. 优先获取当前处于前台/正在操作的活跃资源管理器窗口
    2. 过滤掉系统内部虚拟路径（如 QTTabBar, .workbuddy 等）
    3. 如果没有检测到明确的前台窗口，且传入了 fallback_path，优先返回 fallback_path
    4. 兜底返回最近的有效工作目录
    """
    windows = get_active_explorer_paths()

    # 过滤掉系统内部缓存或插件特殊路径
    valid_windows = []
    for w in windows:
        p = w.get("path", "")
        if not p or p.startswith("::{") or "QTTabBar" in p or "\\.workbuddy" in p:
            continue
        valid_windows.append(w)

    if valid_windows:
        # 1. 尝试检测当前处于前台（Foreground）的资源管理器窗口
        try:
            import ctypes
            user32 = ctypes.windll.user32
            fg_hwnd = user32.GetForegroundWindow()
            for win in valid_windows:
                if win["hwnd"] == fg_hwnd or user32.GetAncestor(fg_hwnd, 2) == win["hwnd"]:
                    if win["selected"]:
                        first_sel = win["selected"][0]
                        return first_sel if os.path.isdir(first_sel) else os.path.dirname(first_sel)
                    return win["path"]
        except Exception:
            pass

        # 2. 如果提供了 fallback_path，且当前没有前台活动窗口，优先保持 fallback_path（防止误入后台陈旧窗口）
        if fallback_path and os.path.exists(fallback_path):
            return fallback_path

        # 3. 兜底取最近有效窗口
        for win in reversed(valid_windows):
            if win["selected"]:
                first_sel = win["selected"][0]
                return first_sel if os.path.isdir(first_sel) else os.path.dirname(first_sel)
        return valid_windows[-1]["path"]

    if fallback_path and os.path.exists(fallback_path):
        return fallback_path

    cwd = os.getcwd()
    if cwd and os.path.exists(cwd):
        return cwd

    return os.path.expanduser("~")

if __name__ == "__main__":
    print("=== 正在扫描当前 Windows 资源管理器窗口 ===")
    wins = get_active_explorer_paths()
    if not wins:
        print("未检测到打开的资源管理器窗口。")
    else:
        for idx, w in enumerate(wins):
            print(f"[{idx+1}] HWND: {w['hwnd']} | 路径: {w['path']}")
            if w["selected"]:
                print(f"    └── 选中项目: {w['selected']}")
    print("\n建议透视起点路径:", get_best_target_path())
