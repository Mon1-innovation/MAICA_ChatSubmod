# -*- coding: utf-8 -*-

import emotion_analyze_v2, os, json, json_exporter
basedir = ""


def init_storage():
    return json_exporter.emotion_selector

def init_sentiment():
    return json_exporter.emotion_sentiment
def init_eoc():
    return json_exporter.emotion_eoc

selector = emotion_analyze_v2.EmoSelector(None, None, None)
def init_selector():
    import json_exporter
    sentiment = json_exporter.emotion_selector
    return sentiment
def init_storage():
    import json_exporter
    storage = json_exporter.emotion_power_storage
    return storage
def init_sentiment():
    import json_exporter
    sentiment = json_exporter.emotion_sentiment
    return sentiment
def init_eoc():
    import json_exporter
    eoc = json_exporter.emotion_eoc
    return eoc

selector.selector = init_selector()
selector.storage = init_storage()
selector.sentiment = init_sentiment()
selector.eoc = init_eoc()
selector.affection = 500
selector.emote_translate = {
    "smile": u"微笑",
    "worry": u"担心",
    "grin": u"笑",
    "think": u"思考",
    "happy": u"开心",
    "angry": u"生气",
    "blush": u"脸红",
    "gaze": u"凝视",
    "upset": u"沉重",
    "daydreaming": u"憧憬",
    "surprise": u"惊喜",
    "awkward": u"尴尬",
    "meaningful": u"意味深长",
    "unexpected": u"惊讶",
    "relaxed": u"轻松",
    "shy": u"害羞",
    "eagering": u"急切",
    "proud": u"得意",
    "dissatisfied": u"不满",
    "serious": u"严肃",
    "touched": u"感动",
    "excited": u"激动",
    "love": u"宠爱",
    "wink": u"眨眼",
    "sad": u"伤心",
    "disgust": u"厌恶",
    "fear": u"害怕",
    "kawaii": u"可爱",
    "smiling": u"微笑",
    "worrying": u"担心",
    "grinning": u"笑",
    "thinking": u"思考",
    "gazing": u"凝视",
    "surprised": u"惊喜",
    "relaxing": u"轻松",
    "eager": u"急切",
    "winking": u"眨眼",
    "disgusting": u"厌恶",
    "fearing": u"害怕"
}

def print_info(data = ""):
    print(selector.analyze(data))
    #print(selector.get_emote())
    #print("strength m{} r{}".format(selector.main_strength, selector.repeat_strength))
    #print("期望表情: {}:{}".format(selector.pre_emote,selector.selector.get(selector.pre_emote, None)))

print_info("[smile]My favorite book? There's a lot of books I like.[smile]If you ask me what my favorite book is, I'd say it's the one you're reading right now, [player].[grin]Ahaha~")
