import os, json, math, random

def sort_by_val(ele):
    key = ele.keys()[0]
    return ele[key]

def first_init():
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion_selector.json"), "r") as emos:
        selector = json.loads(emos.read())
    return selector

def get_sequence(strength, emotion):
    # emotion = selector[emotion]
    weight_sel = []
    weight_accum = 0
    for emotion_code in emotion:
        key = emotion_code.keys()[0]
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
    return emo_final

