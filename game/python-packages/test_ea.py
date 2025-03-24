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

def print_info(data = ""):
    print(selector.analyze(data))
    #print(selector.get_emote())
    #print("strength m{} r{}".format(selector.main_strength, selector.repeat_strength))
    #print("期望表情: {}:{}".format(selector.pre_mood,selector.selector.get(selector.pre_mood, None)))

print_info("[脸红]")
print_info("我当然想和你融为一体, [player]. {w=0.3}[若要了解彼此的心声, 唯有坦诚相待.]")
print_info("")
print_info("")
print_info("[意味深长]")
print_info("")
print_info("")
print_info("")