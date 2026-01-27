# -*- coding: utf-8 -*-

import os, json, math, random
from bot_interface import PY2, PY3, logger, Queue

def sort_by_val(ele):
    key = list(ele.keys())[0]
    return ele[key]

def get_encoded_len(str):
    return len(str.encode('utf-8'))

def iterize(dict):
    if PY2:
        return dict.iteritems()
    elif PY3:
        return dict.items()

class FallBackEmo(object):

    EMPTY_EMOTE_FALLBACK = {
        u"开心":[u"笑", u"微笑"],
        u"脸红":[u"脸红", u"微笑"],
        u"意味深长":[u"意味深长", u"微笑"],
        u"生气":[u"不满", u"担心"],
        u"担心":[u"沉重", u"凝视"],
        u"尴尬":[u"尴尬", u"微笑"],
        u"惊喜":[u"开心", u"笑", u"微笑"],
        u"惊讶":[u"尴尬", u"微笑"],
    }

    def __init__(self):
        self._last_known = u"微笑"
        self._pending_seq = []

    @property
    def last(self):
        return self._last_known
    @last.setter
    def last(self, v):
        self._last_known = v
        self._pending_seq = getattr(self.EMPTY_EMOTE_FALLBACK, v, [])

    def predict(self):
        if len(self._pending_seq) > 1:
            return self._pending_seq.pop(0)
        elif len(self._pending_seq) == 1:
            return self._pending_seq[0]
        else:
            return self._last_known

class EmoSelector(object):

    def __init__(self, selector, storage, sentiment, fallback_predictor = None, eoc=None):
        self.selector = selector
        self.storage = storage
        self.sentiment = sentiment
        self.emote_translate = {}
        self.affection = 100
        self.eoc = eoc
        self.main_strength = 0.0
        self.pre_mood = u"微笑"
        self.pre_emotes = []
        self.curr_emotes = []
        self.emote = ""
        self.pre_pos = 0
        self.fallback_predictor = fallback_predictor
        self.fallback_selector = FallBackEmo()

    def reset(self):
        self.pre_mood = u"微笑"
        self.main_strength = 0.0
        self.pre_emotes = []
        self.fallback_selector.__init__()

    def get_emote(self, idle = False):
        """
        获取表情
        
        Args:
            idle (bool, optional): 是否处于空闲状态. 默认为False.
        
        Returns:
            str: 可以直接show的表情代码.
        
        """

        def idle_pos(pos):
            if pos == 3:
                return 1
            elif pos == 4:
                return 2
            elif pos == 7:
                pos = 6
            return pos
        
        def idle_emo():
            emo = random.choice(['eua_follow', 'eua_follow', 'eua_follow', 'dua', 'esa_follow', 'esa_follow', 'esa_follow', 'tuu'])
            return emo
        
        self.pre_pos = get_pos(self.main_strength, self.pre_pos if self.pre_pos != 0 else random.randint(1, 7))
        if self.emote != "":
            return "{}{}".format(get_pos(self.main_strength, self.pre_pos)if not idle else idle_pos(self.pre_pos), self.emote if not idle else idle_emo())
        else:
            return "idle"

    def analyze(self, message, keep_tags=False):
        """
        分析输入消息中的情绪标签，并返回处理后的消息。
        
        Args:
            message (str): 需要进行情绪分析的字符串消息。
        
        Returns:
            list.
        
        """

        import re
        # 正则表达式模式
        # Filter emojis
        if PY3:
            pattern = r'\[(.*?)\]'
            bad_pattern = r'(\ud83c[\udf00-\udfff])|(\ud83d[\udc00-\ude4f\ude80-\udeff])|[\u2600-\u2B55]' 
        else:
            import datapy2
            pattern = datapy2.pattern_emotion
            bad_pattern = datapy2.bad_pattern
        message = re.sub(bad_pattern, '', message)
        # 查找所有匹配的内容
        matches = re.findall(pattern, message)
        rawmatches = []

        # m = 0.25
        # o = -0.1
        emo = self.pre_mood

        new_matches = []
        # new_rawmatches = []

        message_cuttingmat = message
        message_pieces = []
        
        # This part sanitizes matches
        for index, match in enumerate(matches):
            rawmatch = match

            # 可能是有句子被套上了
            if get_encoded_len(match) >= 16 and not '[' in match and not ']' in match:
                message = message.replace('[{}]'.format(rawmatch), rawmatch)
                continue

            if ' ' in match:
                match = match.replace(' ', '')

            # 如果匹配内容在字典的键中，去除匹配的字符串
            if match == "player":
                continue
            if match in [u"感动", u"憧憬", u"脸红"] and self.main_strength > 0.7:
                message = message.replace('[player]', '[mas_get_player_nickname()]')

            if match == u"很开心":
                match = u"开心"

            if index == 0:
                randf = random.random()
                if len(self.pre_emotes) and self.pre_emotes[-1] in self.selector[u'微笑'].keys() and match == u'微笑':
                    if 0 <= randf < 0.25:
                        match = u'笑'
                    elif 0.25 <= randf < 0.5:
                        match = u'开心'
                elif len(self.pre_emotes) and self.pre_emotes[-1] in self.selector[u'笑'].keys() and match == u'笑':
                    if 0 <= randf < 0.25:
                        match = u'微笑'
                    elif 0.25 <= randf < 0.75:
                        match = u'开心'
                elif len(self.pre_emotes) and self.pre_emotes[-1] in self.selector[u'开心'].keys() and match == u'开心':
                    if 0 <= randf < 0.25:
                        match = u'微笑'
                    elif 0.25 <= randf < 0.75:
                        match = u'笑'

            rawmatches.append(rawmatch)

            if new_matches and match == new_matches[-1]:
                # This is a repetition, treat as null
                continue

            new_matches.append(match) # new_rawmatches.append(rawmatch)
            pre_piece, post_piece = message_cuttingmat.split('[{}]'.format(rawmatch), 1)
            message_pieces.append(pre_piece); message_cuttingmat = post_piece

        message_pieces.append(message_cuttingmat)

        emos = []

        # Then this part processes
        for index, match in enumerate(new_matches):
            match = new_matches[index] = self.emote_translate.get(match, match)
            # rawmatch = new_rawmatches[index]

            if not match in self.selector:
                temp_match = None
                result = self.fallback_predictor('norm', match)
                if result.get('success'):
                    content = result['content']
                    if content[1] >= 0.5:
                        temp_match = content[0]

                if temp_match:
                    # message = message.replace('[{}]'.format(rawmatch), temp_match)
                    logger.warning("[Maica::EmoSelector] {} is not in selector, normalized to {}".format(match, temp_match))
                    if temp_match[0] != '[':
                        continue
                    match = new_matches[index] = temp_match.strip('[').strip(']')

            if match in self.selector:
                emo = match
                # m = 0.7
                # o = 0.0
                self.fallback_selector.last = emo
            else:
                emo = self.fallback_selector.predict()
                logger.warning("[Maica::EmoSelector] {} is not in selector".format(match))

            emos.append(emo)

        if not keep_tags:
            for index, piece in enumerate(message_pieces):
                for rawmatch in rawmatches:
                    message_pieces[index] = piece.replace('[{}]'.format(rawmatch), '')

        # So now len(message_pieces) should equal to len(emos) + 1
        # Now we check if the first piece is empty. If it isn't, this talk does not begin with a match
        # We fix that by adding a fallback prediction.

        if not message_pieces[0].strip():
            message_pieces.pop(0)

        if len(emos) < len(message_pieces):
            emos.insert(0, self.fallback_selector.predict())

        emo_codes = []

        for emo in emos:
            self.process_strength(emo)
            self.pre_mood = emo
            emo_codes.append(self.get_emote())

        return list(zip(emo_codes, message_pieces))

    def process_strength(self, emote, multi=0.7, offset=0.0):
        res = get_sequence_emo(self.main_strength, self.selector[emote], self.storage, eoc=self.eoc, excepted=self.pre_emotes)
        strength_diff = res[1] - self.main_strength
        self.main_strength += min(0.15, max(-0.15, multi * strength_diff + offset)) if self.sentiment[emote] == self.sentiment[self.pre_mood] else 0.1
        self.emote = res[0]
        self.pre_emotes.append(self.emote)
        if self.pre_emotes.__len__() > 1:
            self.pre_emotes = self.pre_emotes[-1:]
        if self.sentiment[self.pre_mood] == self.sentiment[emote]:
            if self.pre_mood != emote:
                if self.main_strength <= 0.3:
                    self.main_strength += 0.2
                elif self.main_strength <= 0.6:
                    self.main_strength += 0.1
                else:
                    self.main_strength += 0.05
            else:
                self.main_strength += 0.05
        self._fix_strength()

    def _fix_strength(self):
        self.main_strength = min(1.0, max(0.0, self.main_strength))

def get_sequence_emo(strength, emotion, storage, eoc, excepted=[], centralization=1.0):
    """
    strength = total accumulated emotion tendency
    emotion = selector[emotion]
    excepted = rejected emos, like last used: ['eka']
    centralization = higher for lower randomness
    """    

    weight_sel = []
    weight_rnd = []
    weight_accum = 0.0
    crucial_weight = 0.0
    eoc_overall_amount = 0
    bypass_eoc = False
    emotion_filter1 = {}
    emotion_new = emotion
    # if eoc then filter eyes-closed emotions
    # if eoc list not given, fall back automatically to non-filter mode
    for k, v in iterize(emotion_new):
        if eoc[k]:
            eoc_overall_amount += 1
    # We bypass eoc if there are no or too little eyes opened emotions
    if eoc_overall_amount <= 1:
        bypass_eoc = True
    for k, v in iterize(emotion_new):
        if not eoc[k] and not bypass_eoc:
            continue
        elif not k in excepted:
            emotion_filter1[k] = v
    # We bypass all limits if no appropriate emotion provided at all
    if len(emotion_filter1) < 1:
        emotion_filter1 = emotion_new
    for k, v in iterize(emotion_filter1):
        power = float(v)
        weight_rnd.append(abs(power - strength))
    weight_rnd.sort()
    crucial_weight = weight_rnd[min(6, max(int(len(weight_rnd)/2), 2), len(weight_rnd)-1)]
    for k, v in iterize(emotion_filter1):
        power = float(v)
        if abs(power - strength) <= crucial_weight:
            weight = math.exp(-(power - strength)**2 / (2 * pow(centralization, 2)))
            weight_accum += weight
            weight_sel.append({k: weight_accum})

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
