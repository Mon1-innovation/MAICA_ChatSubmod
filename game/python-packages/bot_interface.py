# -*- coding: utf-8 -*-

WRITING = 1
END = 0
import ast
import sys
import re
import math
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel(logging.DEBUG)  # 也可以不设置，不设置就默认用logger的level
#fhlr = logging.FileHandler('example.log')
#fhlr.setFormatter(formatter)
logger.addHandler(chlr)
#logger.addHandler(fhlr)
logger.info('正在使用logging')

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

import warnings
import sys

def deprecated(message=None):
    """
    装饰器：标记某个方法已被弃用，使用logger.warning记录

    Args:
        message: 可选的自定义弃用消息

    Usage:
        @deprecated()
        def old_method(self):
            pass

        @deprecated("Use new_method instead")
        def old_method(self):
            pass
    """
    def decorator(func):
        if PY2:
            # Python 2 compatible wrapper
            def wrapper(*args, **kwargs):
                default_msg = "Call to deprecated function {}.".format(func.__name__)
                warning_msg = message if message else default_msg
                logger.warning(warning_msg)
                return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            wrapper.__doc__ = func.__doc__
            return wrapper
        else:
            # Python 3 compatible wrapper using functools
            import functools
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                default_msg = "Call to deprecated function {}.".format(func.__name__)
                warning_msg = message if message else default_msg
                logger.warning(warning_msg)
                return func(*args, **kwargs)
            return wrapper
    return decorator
class Queue(object):
    def __init__(self):
        self.items = []

    def put(self, item):
        """将元素加入队列"""
        self.items.append(item)
    
    def get(self):
        """从队列中取出元素"""
        if not self.is_empty():
            return self.items.pop(0)
        else:
            raise IndexError("get from empty queue")

    def is_empty(self):
        """检查队列是否为空"""
        return len(self.items) == 0
    
    def size(self):
        """返回队列的大小"""
        return len(self.items)
    def clear(self):
        """清空队列"""
        self.items = []
    def __len__(self):
        return self.size()

chinese_to_english_punctuation = {
    '，': ', ',
    '。': '. ',
    '？': '? ',
    '！': '! ',
    '：': ': ',
    '；': '; ',
    '（': '( ',
    '）': ') ',
    '【': '[ ',
    '】': '] ',
    '「': '" ',
    '」': '" ',
    '《': '< ',
    '》': '> ',
    '、': ', ',
}
renpy_symbol = {
    "[": "",
    "]": "",
    "{": "",
    "}": ""
}
renpy_symbol_big_bracket_only = {
    "{": "",
    "}": ""
}
renpy_symbol_percentage = {
    "%": r"%%"
}
renpy_symbol_enter = {
    "\n": ""
}
# 关键字替换字符串:

def key_replace(*args):
        """
        传入格式说明：key_replace(原始字符串，{'关键字':'新数据'})
        可变传参说明：key_replace(原始字符串1,原始字符串2,{'关键字1':'新数据1','关键字2':'新数据2'},{'关键字':'新数据'})
        PS： 一个(原始字符串)对应一个字典，一个字典可以传入多个关键字替换
        :return:
        """
        str_main = []  # 用于存储传入的字符串主体
        rep_info = []  # 用于存储传入替换关键字信息
        for key_info in args:  # 遍历传入的参数
            if isinstance(key_info, dict):  # 如果是字典格式，则代表是(替换关键字信息)
                rep_info.append(key_info)
            else:  # 如果是字符串或其它，则将其添加到字符串列表中
                str_main.append(key_info)

        case_list = []  # 用于存储替换后的结果
        # 遍历传入的字符串和字典，分别进行替换操作
def key_replace(*args):
        """
        传入格式说明：key_replace(原始字符串，{'关键字':'新数据'})
        可变传参说明：key_replace(原始字符串1,原始字符串2,{'关键字1':'新数据1','关键字2':'新数据2'},{'关键字':'新数据'})
        PS： 一个(原妼字符串)对应一个字典，一个字典可以传入多个关键字替换
        :return:
        """
        str_main = []  # 用于存储传入的字符串主体
        rep_info = []  # 用于存储传入替换关键字信息
        for key_info in args:  # 遍历传入的参数
            if isinstance(key_info, dict):  # 如果是字典格式，则代表是(替换关键字信息)
                rep_info.append(key_info)
            else:  # 如果是字符串或其它，则将其添加到字符串列表中
                str_main.append(key_info)

        case_list = []  # 用于存储替换后的结果
        for case_data in str_main:
            # 将所有字典应用到当前字符串
            for key_dict in rep_info:
                for key_, value in key_dict.items():  # 遍历字典中的所有键值对
                    case_data = str(case_data).replace(key_, str(value))  # 替换指定的关键词

            try:
                result = ast.literal_eval(case_data)  # 尝试将替换后的字符串解析为对应数据类型
            except Exception:  # 如果解析失败，则将字符串加入到case_list中
                case_list.append(case_data)
            else:  # 如果解析成功，则将解析后的结果加入到case_list中
                case_list.append(result)

        if len(case_list) == 1:  # 如果case_list中元素个数为1，则返回该元素(而不是一个列表)
            return case_list[0]
        return case_list  # 否则，整体返回case_list

        if len(case_list) == 1:  # 如果case_list中元素个数为1，则返回该元素(而不是一个列表)
            return case_list[0]
        return case_list  # 否则，整体返回case_list

def is_multiple(n, base):
    if base == 0:  # 如果base是0，无法判断是否是倍数
        return False
    elif n % base == 0:  # 如果n能够整除base，说明n是base的倍数
        return True
    else:  # 其他情况下，n不是base的倍数
        return False
signal = ['。', '！', '~', ".", "!", "?"]
def is_a_talk(strs):
    if '...' in strs:
        return strs.find('...') + len("...")
    
    length = len(strs)
    for index in range(length):
        index = length - index
        for s in signal:
            if not s == "." or not len(re.findall(r"\.", strs)) == len(re.findall(r"[0-9]\s*\.\s*[0-9]", strs)):
                if strs[index:index+len(s)] == s:
                    return index + 1
    return 0

def fuckprint(*args, **kwargs):
    return

def is_precisely_a_talk(strin, debug_printfunc=fuckprint):

    def get_pos(relpos):
        # This method added 1
        pos = 0
        for chopls in allset[:relpos+1]:
            if PY2:
                if isinstance(chopls[1], bytes):
                    # 如果是字节串，使用 UTF-8 解码
                    try:
                        decoded_str = chopls[1].decode('utf-8')
                    except UnicodeDecodeError as e:
                        # 处理解码错误，比如记录错误日志或其他处理逻辑
                        raise Exception("Decode Error: {}".format(e))
                        continue  # 或者根据需要跳过当前循环
                elif isinstance(chopls[1], str) or isinstance(chopls[1], unicode):
                    # Python 2 中，如果是 Unicode 字符串，则不需要解码
                    decoded_str = chopls[1]
                else:
                    # 处理其他数据类型的情况
                    raise ValueError("Unknown type: {}".format(type(chopls[1])))
                    continue
                pos += len(decoded_str)
            else:
                pos += len(str(chopls[1]))
        return pos
    allset = []; wordset = []; puncset = []; critset = []; excritset = []
    pattern_common_punc = r'(\s*[.。!！?？；;，,~]+\s*)'
    pattern_crit = r'[.。!！?？~]'
    pattern_excrit = r'[~!！]'
    str_split = re.split(pattern_common_punc,strin)
    relpos = 0
    for chop in str_split:
        if chop != '':
            if re.findall(pattern_common_punc, chop):
                puncset.append([relpos, chop])
                if re.search(pattern_crit, chop):
                    critset.append([relpos, chop])
                    if re.search(pattern_excrit, chop):
                        excritset.append([relpos, chop])
            else:
                wordset.append([relpos, chop])
            allset.append([relpos, chop])
            relpos += 1
    debug_printfunc(allset, puncset, critset, excritset)
    if strin[-1] == '.':
        # In case unfinished
        return 0
    if len(critset) <= 2 and len(strin.encode()) <= 30:
        # Likely too short to break
        if len(excritset) < 2:
            return 0
        else:
            return get_pos(excritset[1][0])
    if len(strin.encode()) <= 100:
        # Making chops long as possible. It's short now
        if critset != [] and re.search(r'\.\.\.', critset[-1][1]):
            return 0
        if len(excritset) >= 2:
            pnum = int(math.floor((len(excritset)*(2/3))))
            return get_pos(excritset[pnum][0])
        if len(critset) >= 2:
            return get_pos(critset[-1][0])
        else:
            return 0
    elif len(strin.encode()) <= 140:
        if excritset:
            pnum = int(math.floor((len(excritset)*(1/3))))
            return get_pos(excritset[pnum][0])
        if critset:
            return get_pos(critset[-1][0])
        else:
            return 0
    elif len(strin.encode()) <= 180:
        # Something may went wrong, just break
        if excritset:
            return get_pos(excritset[-1][0])
        if critset:
            return get_pos(critset[-1][0])
        if puncset:
            return get_pos(puncset[-1][0])
        else:
            return 0
    else:
        # Breakin
        if not len(re.findall(r'\[', allset[-1][1])) == len(re.findall(r'\]', allset[-1][1])):
            return 0
        else:
            return len(strin)-1


class AiException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
    def __str__(self):
        return super().__str__()
# 接口类
class ChatBotInterface():
    WRITING = 1
    END = 0

    # 单次聊天，但是按is_a_talk分句子
    message_list = Queue()
    # 完整的消息。
    full_message = ""

    # 账密/token登录
    def __init__(self, account, pwd, token):
        pass

    # 发送消息，同时接受消息到一个Queue队列
    # Queue队列消息的格式：('renpy表情', 'message')
    def chat(self, message):
        raise Exception("该类未实现chat()")

    # 删除conversation
    def del_conversation(self):
        raise Exception("该类未实现del_conversation()")

    # 从message_list获取消息('renpy表情', 'message')
    def get_message(self):
        raise Exception("该类未实现get_message()")
    
class TalkSplitV2():

    # 简单文档:
    # 先实例化. 一个实例原理上可以用到连接死为止, 也可以每轮对话重建
    # 每次收到消息片段时, 调用instance.add_part(str(消息片段))
    # 这个断句方法是"已知消息越长, 判断越准". 尽可能拖延时间, 最好不要每次收到片段都尝试断句
    # 当然我做了节流阀, 每次收到都断也行
    # 当已收到消息总长达到180字节(60汉字)时达到完整精度且不可能返回None, 具体的缓冲区大小由开发者决定
    # 当需要执行一次断句时, 调用instance.split_present_sentence(), 返回值是断句产生的句子(str)
    # 每次调用断句方法都会返回断句产生的下一个句子. 如果当前字数太少导致无法决定断句, 则会返回None.
    # 当收到1000 streaming_done时, 调用instance.announce_stop(), 注意其输出是一个list! 是一个list! 是一个list!
    # 这个list会包含所有剩余部分的断句. 如果断句调用得频繁, 这里一般就一项. 如果不用流式输出, 也可以直接用这个功能全部断完
    # 这个方法会自动重置实例. 也可以调用instance.init1()手动重置实例, 比直接重建实例省一套编译正则的计算量
    # 我知道你懒得做优化, 所以随你的便吧. 我能替你优化的部分基本都优化到最佳了
    # 理论上能规避小数点, 也会尽可能避免拆括号, 还有未封闭就不是我的锅了

    def __init__(self, print_func = fuckprint):
        self.sentence_present = ''
        if PY3:
            self.pattern_all_punc = re.compile(r'[.。!！?？；;，,—~-]+')
            self.pattern_uncrit_punc = re.compile(r'[.。!！?？；;，,~]+')
            self.pattern_subcrit_punc = re.compile(r'[.。!！?？；;~]+')
            self.pattern_crit_punc = re.compile(r'[.。!！?？~]+')
            self.pattern_excrit_punc = re.compile(r'[!！~]+')
            self.pattern_numeric = re.compile(r'[0-9]')
            self.pattern_content = re.compile(r'[一-龥A-Za-z]')
            self.pattern_semileft = re.compile(r'[(（\[]')
            self.pattern_semiright = re.compile(r'[)）\]]')
        elif PY2:
            import datapy2
            self.pattern_all_punc = datapy2.pattern_all_punc
            self.pattern_uncrit_punc = datapy2.pattern_uncrit_punc
            self.pattern_subcrit_punc = datapy2.pattern_subcrit_punc
            self.pattern_crit_punc = datapy2.pattern_crit_punc
            self.pattern_excrit_punc = datapy2.pattern_excrit_punc
            self.pattern_numeric = datapy2.pattern_numeric
            self.pattern_content = datapy2.pattern_content
            self.pattern_semileft = datapy2.pattern_semileft
            self.pattern_semiright = datapy2.pattern_semiright

        self.list_uncrit_punc = '.。!！?？；;，,~'
        self.list_subcrit_punc = '.。!！?？；;~'
        self.list_crit_punc = '.。!！?？~'
        self.list_excrit_puc = '!！~'

        self.print_func = print_func

    def test_patterns(self, text):
        self.print_func("test_patterns text: {}".format(text))
        results = {
            "all_punc": self.pattern_all_punc.findall(text),
            "crit_punc": self.pattern_crit_punc.findall(text),
            "excrit_punc": self.pattern_excrit_punc.findall(text),
            "numeric": self.pattern_numeric.findall(text),
            "semileft": self.pattern_semileft.findall(text),
            "semiright": self.pattern_semiright.findall(text)
        }

        for pattern_name, matches in results.items():
            self.print_func("{}: {}".format(pattern_name, matches))

    @staticmethod
    def check_has(string, l):
        for i in l:
            if i in string:
                return True
        return False

    def is_decimal(self, five_related_cells):

        def num_amount(text):
            i = 0
            for c in text:
                if c.isdigit():
                    i += 1
            return i

        if five_related_cells[2] == '.':
            cnts = len(self.pattern_content.findall(five_related_cells))
            if (num_amount(five_related_cells[0:2]) and num_amount(five_related_cells[3:5])) or (cnts<=1 and num_amount(five_related_cells[0:2]) != 2) or five_related_cells[1].isupper():
                return True
        return False
    
    @staticmethod
    def insert_string(original_str, insert_str, index):
        return original_str[:index] + insert_str + original_str[index:]

    def init1(self):
        self.sentence_present = ''

    def add_part(self, part):
        self.sentence_present += part

    def split_present_sentence(self):
        apc=[]; upc=[]; spc=[]; cpc=[]; epc=[]; slc=[]; src=[]
        length_present = len(self.sentence_present.encode())
        self.print_func("length_present: {}".format(length_present))

        if length_present <= 60:
            return None
    
        def get_real_len(pos):
            sce = self.sentence_present[0:pos]
            return len(sce.encode())
        
        def check_sanity_pos(pos):
            if slc:
                lc = 0
                for l in slc:
                    lc += 1
                    if l[0] > pos:
                        lc -= 1
                        break
            else:
                lc = 0
            if src:
                rc = 0
                for r in src:
                    rc += 1
                    if r[0] > pos:
                        rc -= 1
                        break
            else:
                rc = 0
            if lc <= rc:
                return True
            else:
                return False
            
        def split_at_pos(pos):
            sce = self.sentence_present[0:pos]
            self.sentence_present = self.sentence_present[pos:]
            if len(sce) > 1 and not sce.isspace():
                return sce.lstrip()
            else:
                return None
        
        # We're doing v2.5 overhaul from here

        matches = self.pattern_all_punc.finditer(self.sentence_present)
        for match in matches:
            pos = match.end(); content = match.group()
            match_tuple = (pos, content)
            apc.append(match_tuple)
            if len(content) > 1 or not self.is_decimal(('   ' + self.sentence_present + ' ')[pos:pos+5]):
                if self.check_has(content, self.list_uncrit_punc):
                    upc.append(match_tuple)
                    if self.check_has(content, self.list_subcrit_punc):
                        spc.append(match_tuple)
                        if self.check_has(content, self.list_crit_punc):
                            cpc.append(match_tuple)
                            if self.check_has(content, self.list_excrit_puc):
                                epc.append(match_tuple)
        slc_matches = self.pattern_semileft.finditer(self.sentence_present)
        for match in slc_matches:
            slc.append((match.end(), match.group()))
        src_matches = self.pattern_semiright.finditer(self.sentence_present)
        for match in src_matches:
            src.append((match.end(), match.group()))

        # self.print_func(apc); self.print_func(upc); self.print_func(cpc); self.print_func(epc); self.print_func(length_present)
        # if length_present <= 60:
        #     return None
        if epc:
            for char in reversed(epc):
                if 30 <= get_real_len(char[0]) <= 180 and check_sanity_pos(char[0]):
                    return split_at_pos(char[0])
        # No epc or none fits
        if length_present <= 100:
            return None
        if cpc:
            for char in reversed(cpc):
                if 30 <= get_real_len(char[0]) <= 180 and check_sanity_pos(char[0]):
                    return split_at_pos(char[0])
        # No cpc or still none fits
        if length_present <= 120:
            return None
        if spc:
            for char in reversed(spc):
                if 20 <= get_real_len(char[0]) <= 180 and check_sanity_pos(char[0]):
                    return split_at_pos(char[0])
        # No spc or still none fits
        if length_present <= 140:
            return None
        if upc:
            for char in reversed(upc):
                if 10 <= get_real_len(char[0]) <= 180 and check_sanity_pos(char[0]):
                    return split_at_pos(char[0])
        # No upc or still none fits
        if length_present <= 160:
            return None
        if apc:
            for char in reversed(apc):
                if 3 <= get_real_len(char[0]) <= 180 and check_sanity_pos(char[0]):
                    return split_at_pos(char[0])
        # Falling back -- sanity given up
            if length_present <= 180:
                return None
            for char in reversed(apc):
                if 3 <= get_real_len(char[0]) <= 200:
                    return split_at_pos(char[0])
        return split_at_pos(get_real_len(200))
    def announce_stop(self):
        sce = []
        res = True
        while res:
            res = self.split_present_sentence()
            if res:
                sce.append(res)
        if self.sentence_present and len(self.sentence_present) > 1 and not self.sentence_present.isspace():
            sce.append(self.sentence_present)
        self.init1()
        return sce


    def add_pauses(self, strin):
        if PY2:
            if not isinstance(strin, (str, unicode)):
                raise TypeError("Input should be a string or unicode, get {}".format(type(strin)))
        else:
            if not isinstance(strin, str):
                raise TypeError("Input should be a string, get {}".format(type(strin)))
        
        def get_pre_i_space(ele, list):
            pre_index = list.index(ele) - 1
            pre_pos = list[pre_index][3] if pre_index >= 0 else 0
            return ele[3] - pre_pos

        iupc=[]; icpc=[]; iepc=[]
        
        matches = self.pattern_all_punc.finditer(strin)
        lmatch = None; i = 0 
        # This is a iterator but we need a list
        matches = list(matches)
        for match in matches:
            # No pause needed for last punc
            i += 1
            if i == len(matches):
                break
            pos = match.end(); content = match.group()
            if not lmatch:
                preseq = strin[:match.start()]
            else:
                preseq = strin[lmatch.end():match.start()]
            prelen = len(preseq.encode('utf-8'))
            alllen = len(strin[:match.start()].encode('utf-8'))
            lmatch = match
            match_tuple_b = (pos, content, prelen, alllen)
            # print(('   ' + strin + ' ')[pos:pos+5])
            if len(content) > 1 or not self.is_decimal(('   ' + strin + ' ')[pos:pos+5]):
                if self.check_has(content, self.list_excrit_puc):
                    iepc.append(match_tuple_b)
                elif self.check_has(content, self.list_crit_punc):
                    icpc.append(match_tuple_b)
                elif self.check_has(content, self.list_uncrit_punc):
                    iupc.append(match_tuple_b)

        pending_insert = []

        for mb in iupc:
            if prelen > 80:
                pending_insert.append(('{w=0.3}', mb[0]))

        for mb in icpc:
            if len(mb[1]) > 1:
                # ellipsis?
                if get_pre_i_space(mb, icpc) > 30:
                    pending_insert.append(('{w=0.5}', mb[0]))
            elif get_pre_i_space(mb, icpc) > 45:
                pending_insert.append(('{w=0.3}', mb[0]))

        for mb in iepc:
            if prelen > 45:
                pending_insert.append(('{w=0.2}', mb[0]))

        for tup in pending_insert[::-1]:
            strin = self.insert_string(strin, *tup)
                
        return strin
