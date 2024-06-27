# -*- coding: utf-8 -*-

EMOTE_DICT = {}
EMOTE_EFFECT = {}

MAX_EMOTE_EFFECT = 15

# EMOTE_DICT: 表情代码选择
# "心情":{
#   1:["1eua","2eua"]
#   2:["3eua"]
#   "sentiment":-1/0/1
#}
# key越大，说明心情程度越高
# sentiment表示该心情的偏好 坏/中/好
def set_emotedata(dict):
    global EMOTE_DICT
    EMOTE_DICT = dict
def add_emotedata(dict):
    global EMOTE_DICT
    EMOTE_DICT |= dict

# EMOTE_EFFECT: 心情相关度
# 请查看emotion_influence.json
def add_emoteeffectdata(dict):
    global EMOTE_EFFECT
    EMOTE_EFFECT |= dict

class MoodStatus(object):
    
    
    def __init__(self):
        self.EmotionalStatus = {}
        self.init_emotional_status()
        self.EmotionalStatus["微笑"]=1

    def init_emotional_status(self):
        for i in EMOTE_DICT:
            if i not in self.EmotionalStatus:
                self.EmotionalStatus[i] = 0.0

    def reset(self):
        self.__init__()
        
    # 分析该句对话
    def analyze(self, message):
        import re
        # 正则表达式模式
        pattern = r'\[(.*?)\]'

        # 查找所有匹配的内容
        matches = re.findall(pattern, message)

        # 处理每个匹配的内容
        for match in matches:
            if match in self.EmotionalStatus:
                # 如果匹配内容在字典的键中，去除匹配的字符串
                result = message.replace('[{}]'.format(match), '')
                self.add_emotional(match)
        return result
    # 增加心情值
    def add_emotional(self, emote, value=3.0):
        if emote not in self.EmotionalStatus:
            return
        add_value = value * (1 - self.EmotionalStatus[emote] / MAX_EMOTE_EFFECT)
        # 统计相关影响值
        for i in EMOTE_EFFECT[emote]:
            if i in self.EmotionalStatus:
                self.EmotionalStatus[i] += add_value * EMOTE_EFFECT[emote][i]
        for i in self.EmotionalStatus:
            if i not in EMOTE_EFFECT[emote] or i != emote:
                self.EmotionalStatus[i] *= 0.75
        # 处理负面影响值
        s = EMOTE_DICT[emote]["sentiment"]
        for i in self.EmotionalStatus:
            if EMOTE_DICT[i]["sentiment"] != s:
                self.EmotionalStatus[i] /= add_value 
    
    # 获取表情
    def get_emote(self):
        max_key = max(self.EmotionalStatus, key=self.EmotionalStatus.get)
        max_value = self.EmotionalStatus[max_key]

        emotes = EMOTE_DICT[max_key]
        del emotes["sentiment"]

        def select_code(data, ratio):
            if ratio > 1:
                ratio = 1
            import random
            # 按键排序
            keys = sorted(data.keys())
            # 计算选择的键
            cumulative_ratio = 0
            for key in keys:
                cumulative_ratio += key / sum(keys)
                if ratio <= cumulative_ratio:
                    # 从相应的列表中随机选择一个值
                    return random.choice(data[key])
            # 如果比例超出范围，默认返回最大键
            return random.choice(data[keys[-1]])
        

        return select_code(emotes, max_value / MAX_EMOTE_EFFECT)

        



