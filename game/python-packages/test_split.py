def calculate_length(s):
    import unicodedata
    length = 0
    for char in s:
        # 使用unicodedata模块判断字符宽度
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            length += 2
        else:
            length += 1
    return length


def split_long_strings(l, max_len):
    result = []
    for item in l:
        while calculate_length(item) > max_len:
            cut_index = max_len // 2  # 初步估计切割位置
            current_len = 0
            for i, char in enumerate(item):
                if '\u4e00' <= char <= '\u9fff':
                    current_len += 2
                else:
                    current_len += 1
                if current_len >= max_len:
                    cut_index = i + 1
                    break
            result.append(item[:cut_index])
            item = item[cut_index:]
        result.append(item)
    return result

# 示例
content = "HelloWDADFAWDASFSEGSDRGDRESGHTDRRHGSDRFDXG FDHFDTHGFTDV GFTDVGHTDGDG RGD GRDTGCSRE你好\n这是一段测试文本\n这个字符串长度超过了最大限制，需要被切割这个字符串长度超过了最大限制，需要被切割"
l = content.split("\n")
max_len = 33 * 2

split_result = split_long_strings(l, max_len)
for line in split_result:
    print(line, "|" ,calculate_length(line))
