# -*- coding: utf-8 -*-

from bot_interface import PY2, PY3, logger

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
    if PY2:
        return EMOTE_DICT.update(dict)
    EMOTE_DICT |= dict

# EMOTE_EFFECT: 心情相关度
# 请查看emotion_influence.json
def add_emoteeffectdata(dict):
    global EMOTE_EFFECT
    if PY2:
        return EMOTE_EFFECT.update(dict)
    EMOTE_EFFECT |= dict

class MoodStatus(object):
    
    
    def __init__(self):
        self.EmotionalStatus = {}
        self.EmotionalStatus = EMOTE_DICT.copy()
        self.init_emotional_status()

    def init_emotional_status(self):
        for i in self.EmotionalStatus:
            self.EmotionalStatus[i] = 0.0
        self.EmotionalStatus["微笑"]=1

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
            if match not in self.EmotionalStatus:
                logger.warning("MoodStatus::analyze {} not in EmotionalStatus".format(match))
            # 如果匹配内容在字典的键中，去除匹配的字符串
            message = message.replace('[{}]'.format(match), '')
            #self.add_emotional(match)

        return message
    # 增加心情值
    def add_emotional(self, emote, value=3.0):
        logger.debug("MoodStatus::add_emotional {}: {}".format(emote, value))
        if emote not in self.EmotionalStatus:
            return
        add_value = value * (1 - self.EmotionalStatus[emote] / MAX_EMOTE_EFFECT)
        self.EmotionalStatus[emote] += add_value
        # 统计相关影响值
        if emote in EMOTE_EFFECT:
            for i in EMOTE_EFFECT[emote]:
                if i in self.EmotionalStatus:
                    self.EmotionalStatus[i] += add_value * EMOTE_EFFECT[emote][i]
        for i in self.EmotionalStatus:
            self.EmotionalStatus[i] *= 0.87 if emote != "微笑" else 0.95
        self.EmotionalStatus["微笑"] *= 0.75
        # 处理负面影响值
        s = EMOTE_DICT[emote]["sentiment"]
        for i in self.EmotionalStatus:
            if EMOTE_DICT[i]["sentiment"] != s:
                self.EmotionalStatus[i] /= add_value 
        logger.debug(self.EmotionalStatus)
    
    # 获取表情
    def get_emote(self):
        return "1eua"
        max_key = max(self.EmotionalStatus, key=self.EmotionalStatus.get)
        max_value = self.EmotionalStatus[max_key]
        emotes = EMOTE_DICT[max_key].copy() 
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


