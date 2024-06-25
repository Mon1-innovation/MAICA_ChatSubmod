WRITING = 1
END = 0

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
        return strs.find('...') + 1
    
    length = len(strs)
    for index in range(length):
        for s in signal:
            if strs[index:index+len(s)] == s:
                return index + 1
    return 0

from queue import Queue

class AiException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
    def __str__(self) -> str:
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
    def __init__(self, account, pwd, token) -> None:
        pass

    # 发送消息，同时接受消息到一个Queue队列
    # Queue队列消息的格式：('renpy表情', 'message')
    def chat(self, message):
        raise Exception("该类未实现chat()")

    # 删除conversation
    def del_conversation(self):
        raise Exception("该类未实现del_conversation()")

    # 从message_list获取消息，如果已经阅读完已经生成的句子，但是还在生成返回WRITING,如果已经结束生成并且全部阅读完毕返回END(同时清空),如果有异常则抛出异常
    def get_message(self):
        raise Exception("该类未实现get_message()")

