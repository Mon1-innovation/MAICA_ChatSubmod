# -*- coding: utf-8 -*-

import os, json, math, random
from bot_interface import PY2, PY3, logger
def sort_by_val(ele):
    key = list(ele.keys())[0]
    return ele[key]


class EmoSelector:
    def __init__(self, selector, storage, sentiment, eoc=None):
        self.selector = selector
        self.storage = storage
        self.sentiment = sentiment
        self.affection = 100
        self.eoc = eoc
        self.main_strength = 0.0
        self.repeat_strength = 0.0
        self.pre_mood = u"微笑"
        self.pre_emotes = []
        self.emote = ""
        self.pre_pos = 0
    def get_emote(self, idle = False):
        def idle_pos(pos):
            if pos == 3:
                return 1
            elif pos == 4:
                return 2
            elif pos == 7:
                pos = 6
            return pos
        def idle_emo():
            emo = random.choice(['eua_follow', 'eua_follow', 'eua_follow', 'dua', 'esa_follow', 'esa_follow', 'esa_follow', 'tuu', 'hua', 'huu'])
            return emo
        self.pre_pos = get_pos(self.repeat_strength, self.pre_pos if self.pre_pos != 0 else random.randint(1, 7))
        if self.emote != "":
            return "{}{}".format(get_pos(self.main_strength, self.pre_pos)if not idle else idle_pos(self.pre_pos), idle_emo())
        else:
            return "idle"

    def analyze(self, message):
        import re
        # 正则表达式模式
        pattern = r'\[(.*?)\]'

        # 查找所有匹配的内容
        matches = re.findall(pattern, message)
        m = 0.25
        emo = self.pre_mood
        # 处理每个匹配的内容
        for match in matches:
            # 如果匹配内容在字典的键中，去除匹配的字符串
            if match == "player":
                continue
            message = message.replace('[{}]'.format(match), '')
            if match == u"很开心":
                match = u"开心"
            
            m = 0.7
            emo = match
        self.process_strength(emo, m)
        self.pre_mood = emo
        return message

    def process_strength(self, emote, multi=0.7):
        res = get_sequence_emo(self.main_strength, self.selector[emote], self.storage, eoc=self.eoc, excepted=self.pre_emotes)
        self.main_strength += multi * self.sentiment[emote] * res[1] * self.main_strength if self.sentiment[emote] <= 0 else 1
        self.emote = res[0]
        self.pre_emotes.append(self.emote)
        if self.pre_emotes.__len__() > 1:
            self.pre_emotes = self.pre_emotes[-1:]
        if self.pre_mood == emote:
            self.repeat_strength += 0.2 
        else:
            self.repeat_strength = 0
        self._fix_strength()
    def reset(self):
        self.pre_mood = u"微笑"
        self.main_strength = 0.0
        self.repeat_strength = 0.0
        self.pre_emotes = []
    def _fix_strength(self):
        if self.repeat_strength > 1.0:
            self.repeat_strength = 1.0
        if self.repeat_strength < 0.0:
            self.repeat_strength = 0.0
        if self.main_strength > 1.0:
            self.main_strength = 1.0
        if self.main_strength < 0.0:
            self.main_strength = 0.0


def get_sequence_emo(strength, emotion, storage, eoc, excepted=[], centralization=1.0):
    # strength = total accumulated emotion tendency
    # emotion = selector[emotion]
    # excepted = rejected emos, like last used: ['eka']
    # centralization = higher for lower randomness
    weight_sel = []
    weight_accum = 0
    eoc_sig = 0
    if eoc:
        for emotion_eoc_checked in excepted:
            if not eoc[emotion_eoc_checked]:
                eoc_sig += 1
    # if eoc then filter eyes-closed emotions
    # if eoc list not given, fall back automatically to non-filter mode
    for emotion_code in emotion:
        key = list(emotion_code.keys())[0]
        if eoc_sig and not eoc[key]:
            continue
        if not key in excepted:
            power = float(emotion_code[key])
            weight = math.exp(-(power - strength)**2 / (2 * pow(centralization, 2)))
            weight_accum += weight
            weight_sel.append({key: weight_accum})
    rand = random.random() * weight_accum
    pointer = {"placeholder": rand}
    weight_sel.insert(0, pointer)
    weight_sel.sort(key=sort_by_val)
    seq = weight_sel.index(pointer)
    emo_final = list(weight_sel[seq + 1].keys())[0]
    emo_final_power = storage[emo_final]
    #emo_final_power = list([x for x in storage if {i: j for i, j in x.items() if i == emo_final}][0].keys())[0]
    # Notice this is a low-performance way! Consider adding a pure dict addressing all emocodes with their power
    # emo_final_power = [x for x in emotion if {i: j for i, j in x.items() if i == emo_final}][0].keys()[0]
    # emo_final_power is returned for affecting accumulation
    # emo_final like 'eka', emo_final_power like 0.6
    return emo_final, emo_final_power

import random

def get_pos(strength=0.0, last=None):
    if last is None:
        last = random.randint(1, 7)
    # Use every step. doesn't always switch pose
    # strength = 0.0~1.0
    # last = 1~7
    # 1 resting on hands
    # 2 crossed
    # 3 rest left point right
    # 4 point right
    # 5 leaning
    # 6 down
    # 7 down left point right
    
    f = random.random()

    if last == 1:
        # pos1 is a calm pose. Tends to switch away and to point for stronger emotions
        if 0 <= f < 0.5 - 0.2 * strength:
            next_pos = 1
        elif 0.5 - 0.2 * strength <= f < 0.7 - 0.25 * strength:
            next_pos = 5
        elif 0.7 - 0.25 * strength <= f < 0.85 - 0.2 * strength:
            next_pos = random.choice([2, 2, 6])
        elif 0.85 - 0.2 * strength <= f < 1:
            next_pos = random.choice([3, 3, 3, 3, 3, 4, 7])

    elif last == 2:
        # pos2 is a calm pose. Tends to switch away and to point for stronger emotions
        if 0 <= f < 0.5 - 0.2 * strength:
            next_pos = 2
        elif 0.5 - 0.2 * strength <= f < 0.75 - 0.25 * strength:
            next_pos = 5
        elif 0.75 - 0.25 * strength <= f < 0.85 - 0.2 * strength:
            next_pos = random.choice([1, 1, 6])
        elif 0.85 - 0.2 * strength <= f < 1:
            next_pos = random.choice([3, 3, 4, 4, 7])

    elif last == 3:
        # pos3 is a pointing pose. Tends to keep or to point for stronger emotions
        if 0 <= f < 0.1 + 0.3 * strength:
            next_pos = 3
        elif 0.1 + 0.3 * strength <= f < 0.1 + 0.7 * strength:
            next_pos = 4
        elif 0.1 + 0.7 * strength <= f < 0.9 - 0.1 * strength:
            next_pos = random.choice([1, 1, 1, 1, 1, 2, 4, 5, 6])
        elif 0.9 - 0.1 * strength <= f < 1:
            next_pos = 7

    elif last == 4:
        # pos4 is a tiring pose. Tends to switch away
        if 0 <= f < 0.1 + 0.1 * strength:
            next_pos = 4
        elif 0.1 + 0.1 * strength <= f < 0.1 + 0.7 * strength:
            next_pos = random.choice([3, 7])
        elif 0.1 + 0.7 * strength <= f < 0.9:
            next_pos = random.choice([2, 2, 5, 5, 6])
        elif 0.9 <= f < 1:
            next_pos = 1

    elif last == 5:
        # pos5 is a relaxing pose. Tends to switch away and to point for stronger emotions
        if 0 <= f < 0.7 - 0.4 * strength:
            next_pos = 5
        elif 0.7 - 0.4 * strength <= f < 0.7 + 0.1 * strength:
            next_pos = random.choice([3, 4, 7])
        elif 0.7 + 0.1 * strength <= f < 0.9:
            next_pos = 1
        elif 0.9 <= f < 1:
            next_pos = random.choice([2, 2, 6])

    elif last == 6:
        # pos6 seldom happens
        if 0 <= f < 0.5 - 0.4 * strength:
            next_pos = 6
        elif 0.5 - 0.4 * strength <= f < 0.6 - 0.1 * strength:
            next_pos = random.choice([3, 4, 4, 7, 7])
        elif 0.6 - 0.1 * strength <= f < 1:
            next_pos = random.choice([1, 1, 1, 2, 2, 2, 5])

    elif last == 7:
        # pos7 seldom happens
        if 0 <= f < 0.1 + 0.4 * strength:
            next_pos = 7
        elif 0.1 + 0.4 * strength <= f < 0.6 + 0.3 * strength:
            next_pos = random.choice([1, 1, 2, 2, 2, 5, 5])
        elif 0.6 + 0.3 * strength <= f < 1:
            next_pos = 6
    
    return next_pos
