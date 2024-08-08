# -*- coding: utf-8 -*-

import emotion_analyze_v2, os, json
basedir = ""
def init_selector():
    selector = {}
    power={}
    eoc={}
    # dkbfsdlc:担心:0.45
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion.txt"), "r", encoding="utf-8") as emos:
        for item in emos.readlines():
            if item[0] == "#":
                continue
            i = item.strip().split(":")
            i[0]=i[0][1:]
            if i[1] not in selector:
                selector[i[1]]=[]
            selector[i[1]].append({i[0]: float(i[2])})
            power[i[0]] = float(i[2])
            eoc[i[0]] = 0 if i[0][0] in ("h", "d", "k", "n") else 1
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_selector.json"), "w", encoding="utf-8") as emos:
            emos.write(json.dumps(selector, ensure_ascii=False))
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_power_storage.json"), "w", encoding="utf-8") as emos:
            emos.write(json.dumps(power, ensure_ascii=False))
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_eoc.json"), "w", encoding="utf-8") as emos:
            emos.write(json.dumps(eoc, ensure_ascii=False))
        
    return selector

def init_storage():
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_power_storage.json"), "r", encoding="utf-8") as emops:
        storage = json.loads(emops.read())
    return storage

def init_sentiment():
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_sentiment.json"), "r", encoding="utf-8") as emost:
        sentiment = json.loads(emost.read())
    return sentiment
def init_eoc():
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_eoc.json"), "r", encoding="utf-8") as emoe:
        eoc = json.loads(emoe.read())
    return eoc

selector = emotion_analyze_v2.EmoSelector(init_selector(), init_storage(), init_sentiment())
selector.selector = init_selector()
selector.storage = init_storage()
selector.sentiment = init_sentiment()
selector.eoc = init_eoc()
selector.affection = 500

def print_info(data = ""):
    selector.analyze(data)
    print(selector.get_emote())
    print("strength m{} r{}".format(selector.main_strength, selector.repeat_strength))
    print("期望表情: {}:{}".format(selector.pre_mood,selector.selector.get(selector.pre_mood, None)))

print_info("[脸红]")
print_info("")
print_info("")
print_info("")
print_info("[意味深长]")
print_info("")
print_info("")
print_info("")