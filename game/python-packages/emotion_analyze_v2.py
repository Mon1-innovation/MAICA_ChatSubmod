import os, json, math, random

def sort_by_val(ele):
    key = ele.keys()[0]
    return ele[key]

def init_selector():
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion_selector.json"), "r") as emos:
        selector = json.loads(emos.read())
    return selector

def init_storage():
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion_power_storage.json"), "r") as emops:
        storage = json.loads(emops.read())
    return storage

def get_sequence_emo(strength, emotion, excepted=''):
    # emotion = selector[emotion]
    # excepted = "last used emocode like eka"
    weight_sel = []
    weight_accum = 0
    for emotion_code in emotion:
        key = emotion_code.keys()[0]
        if key != excepted:
            power = emotion_code[key]
            weight = math.exp(-(power - strength)**2/2)
            weight_accum += weight
            weight_sel.extend({key: weight_accum})
    rand = random() * weight_accum
    pointer = {"placeholder": rand}
    weight_sel.insert(0, pointer)
    weight_sel.sort(key=sort_by_val)
    seq = weight.sel.index(pointer)
    emo_final = weight_sel[seq + 1].keys()[0]
    emo_final_power = init_storage()[emo_final]
    # Notice this is a low-performance way! Consider adding a pure dict addressing all emocodes with their power
    # emo_final_power = [x for x in emotion if {i: j for i, j in x.items() if i == emo_final}][0].keys()[0]
    return emo_final, emo_final_power

