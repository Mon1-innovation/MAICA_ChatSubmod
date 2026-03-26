import json
import os

from .cp936_map import CP936_MAP as _CP936_MAP

def decode_cp936(data):
    """
    data: str (Python 2 bytes)
    return: unicode
    """
    out = []
    i = 0
    length = len(data)

    while i < length:
        b1 = ord(data[i])

        # ASCII（单字节）
        if b1 < 0x80:
            key = "0x%02X" % b1
            out.append(unichr(int(_CP936_MAP.get(key, "0xFFFD"), 16)))
            i += 1
            continue

        # 双字节（CP936 / GBK）
        if i + 1 >= length:
            out.append(u"\ufffd")
            break

        b2 = ord(data[i + 1])
        key = "0x%02X%02X" % (b1, b2)

        out.append(unichr(int(_CP936_MAP.get(key, "0xFFFD"), 16)))
        i += 2

    return u"".join(out)