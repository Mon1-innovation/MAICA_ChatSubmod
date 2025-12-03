# -*- coding: utf-8 -*-
import sys
import ctypes

def get_system_locale_name():

    """提取系统非Unicode语言设置项, 仅Windows生效.

    Args:
        无

    Returns: 

        Win32平台: 
            语言名称(字符串), 格式范例: 'zh-CN', 'ja-JP', 'en-US'. 
        非win32平台: None.

    """

    if sys.platform != "win32":
        return None
    

    kernel32 = ctypes.windll.kernel32

    # 常量：获取 locale 名称的 flag
    LOCALE_SNAME = 0x0000005c

    # 获取系统默认 LCID（对应“非 Unicode 程序的语言”）
    lcid = kernel32.GetSystemDefaultLCID()

    # 预分配缓冲区（一般 85 足够）
    buf = ctypes.create_unicode_buffer(85)

    # 调用 GetLocaleInfoW 取出 locale 名称
    if kernel32.GetLocaleInfoW(lcid, LOCALE_SNAME, buf, len(buf)) == 0:
        return None

    return buf.value


def is_zhcn():

    '''确定是否为zh-CN.

    Args:
        无
    
    Returns: 
        Bool:
            False: 非zh-CN
            True: zh-CN
    
    '''

    name = get_system_locale_name()
    if name != "zh-CN":
        return False

    return True

