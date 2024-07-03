# -*- coding: utf-8 -*-

WRITING = 1
END = 0
import ast
import sys

import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
chlr.setLevel(logging.DEBUG)  # 也可以不设置，不设置就默认用logger的level
fhlr = logging.FileHandler('example.log')
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)
logger.info('正在使用logging')

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    from queue import Queue
else:
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
        for case_data, key_dict in zip(str_main, rep_info):
            for key_, value in key_dict.items():  # 遍历字典中的所有键值对
                case_data = str(case_data).replace(key_, str(value))  # 替换指定的关键词
            try:
                ast.literal_eval(case_data)  # 尝试将替换后的字符串解析为对应数据类型
            except Exception:  # 如果解析失败，则将字符串加入到case_list中
                case_list.append(case_data)
            else:  # 如果解析成功，则将解析后的结果加入到case_list中
                case_list.append(ast.literal_eval(case_data))
 
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
        for s in signal:
            if strs[index:index+len(s)] == s:
                return index + 1
    return 0



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

    # 从message_list获取消息('renpy表情', 'message')，如果已经阅读完已经生成的句子，但是还在生成返回WRITING,如果已经结束生成并且全部阅读完毕返回END(同时清空),如果有异常则抛出异常
    def get_message(self):
        raise Exception("该类未实现get_message()")

