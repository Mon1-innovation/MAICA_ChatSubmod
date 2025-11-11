# -*- coding: utf-8 -*-
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
    构建文件过滤字符串

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


def select_file(title=None, file_types=None):
    """
    打开Windows文件选择对话框

    Args:
        title (str): 对话框标题，默认为"选择文件"
        file_types (list): 文件类型列表，格式为 [('描述', '扩展名'), ...]
                          默认为 [('所有文件', '*.*'), ('文本文件', '*.txt')]

    Returns:
        str: 选中的文件路径，未选择则返回空字符串
    """
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

if __name__ == "__main__":
    selected = select_file()
    print(u"选择的文件:", selected if selected else u"未选择")
