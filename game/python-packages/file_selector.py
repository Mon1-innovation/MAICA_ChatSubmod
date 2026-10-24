# -*- coding: utf-8 -*-
import sys
import os
import subprocess

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    class OPENFILENAME(ctypes.Structure):
        _fields_ = [
            ('lStructSize', wintypes.DWORD),
            ('hwndOwner', wintypes.HWND),
            ('hInstance', wintypes.HINSTANCE),
            ('lpstrFilter', wintypes.LPCWSTR),
            ('lpstrCustomFilter', wintypes.LPWSTR),
            ('nMaxCustFilter', wintypes.DWORD),
            ('nFilterIndex', wintypes.DWORD),
            ('lpstrFile', wintypes.LPWSTR),
            ('nMaxFile', wintypes.DWORD),
            ('lpstrFileTitle', wintypes.LPWSTR),
            ('nMaxFileTitle', wintypes.DWORD),
            ('lpstrInitialDir', wintypes.LPCWSTR),
            ('lpstrTitle', wintypes.LPCWSTR),
            ('Flags', wintypes.DWORD),
            ('nFileOffset', wintypes.WORD),
            ('nFileExtension', wintypes.WORD),
            ('lpstrDefExt', wintypes.LPCWSTR),
            ('lCustData', wintypes.LPARAM),
            ('lpfnHook', wintypes.LPVOID),
            ('lpTemplateName', wintypes.LPCWSTR),
            ('pvReserved', wintypes.LPVOID),
            ('dwReserved', wintypes.DWORD),
            ('FlagsEx', wintypes.DWORD),
        ]


def _build_filter_string(file_types):
    """
    构建 Windows 文件过滤字符串

    Args:
        file_types (list): 文件类型列表，格式为 [('描述', '扩展名'), ...]
                          例如: [('文本文件', '*.txt'), ('所有文件', '*.*')]

    Returns:
        str: Windows文件对话框所需的过滤字符串
    """
    filter_str = u""
    for description, extension in file_types:
        filter_str += description + u"\0" + extension + u"\0"
    return filter_str


def _select_file_windows(title=None, file_types=None):
    if title is None:
        title = u"选择文件"

    if file_types is None:
        file_types = [(u"所有文件", u"*.*"), (u"文本文件", u"*.txt")]

    buffer = ctypes.create_unicode_buffer(260)
    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 260
    ofn.lpstrFilter = _build_filter_string(file_types)
    ofn.lpstrTitle = title
    ofn.Flags = 0x00001000

    if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return u""


def _select_file_macos(title=None, file_types=None):
    if title is None:
        title = u"选择文件"

    type_clause = ""
    if file_types:
        exts = []
        has_wildcard = False
        for _, pattern in file_types:
            parts = pattern.replace(";", " ").replace(",", " ").split()
            for part in parts:
                ext = part.strip().lstrip("*.").lower()
                if ext == "" or ext == "*":
                    has_wildcard = True
                    break
                if ext:
                    exts.append(ext)
            if has_wildcard:
                break
        if not has_wildcard and exts:
            unique_exts = []
            for ext in exts:
                if ext not in unique_exts:
                    unique_exts.append(ext)
            if unique_exts:
                type_clause = ' of type {%s}' % ", ".join(['"%s"' % e for e in unique_exts])

    safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
    script = 'POSIX path of (choose file%s with prompt "%s")' % (type_clause, safe_title)
    try:
        try:
            unicode_type = unicode
        except NameError:
            unicode_type = str

        if isinstance(script, unicode_type):
            script_bytes = script.encode("utf-8")
        else:
            script_bytes = script

        p = subprocess.Popen(
            ["osascript", "-e", script_bytes],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = p.communicate()
        if p.returncode == 0:
            result = stdout.decode("utf-8").strip()
            return result
    except Exception:
        pass
    return u""


def _select_file_linux(title=None, file_types=None):
    if title is None:
        title = u"选择文件"

    # 尝试使用 zenity
    try:
        cmd = ["zenity", "--file-selection", "--title=%s" % title]
        if file_types:
            for desc, pat in file_types:
                cmd.append("--file-filter=%s | %s" % (desc, pat))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = p.communicate()
        if p.returncode == 0:
            return stdout.decode("utf-8").strip()
    except Exception:
        pass

    # 尝试使用 kdialog
    try:
        patterns = " ".join(pat for _, pat in file_types) if file_types else "*"
        cmd = ["kdialog", "--getopenfilename", ".", patterns, "--title", title]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, _ = p.communicate()
        if p.returncode == 0:
            return stdout.decode("utf-8").strip()
    except Exception:
        pass

    # 尝试使用 tkinter
    try:
        try:
            import Tkinter as tk
            import tkFileDialog as filedialog
        except ImportError:
            import tkinter as tk
            from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        types_arg = [(desc, pat) for desc, pat in file_types] if file_types else [("All Files", "*.*")]
        selected = filedialog.askopenfilename(title=title, filetypes=types_arg)
        root.destroy()
        if selected:
            return selected
    except Exception:
        pass

    return u""


def select_file(title=None, file_types=None):
    """
    打开跨平台文件选择对话框

    Args:
        title (str): 对话框标题，默认为"选择文件"
        file_types (list): 文件类型列表，格式为 [('描述', '扩展名'), ...]
                          默认为 [('所有文件', '*.*'), ('文本文件', '*.txt')]

    Returns:
        str: 选中的文件路径，未选择则返回空字符串
    """
    if sys.platform == "win32":
        return _select_file_windows(title, file_types)
    elif sys.platform == "darwin":
        return _select_file_macos(title, file_types)
    else:
        return _select_file_linux(title, file_types)


if __name__ == "__main__":
    selected = select_file()
    print(u"选择的文件:", selected if selected else u"未选择")
