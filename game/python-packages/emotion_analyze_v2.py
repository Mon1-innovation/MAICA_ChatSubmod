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

def init_sentiment():
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion_sentiment.json"), "r") as emost:
        sentiment = json.loads(emost.read())
    return sentiment

def get_sequence_emo(strength, emotion, excepted=[], centralization=1.0):
    # strength = total accumulated emotion tendency
    # emotion = selector[emotion]
    # excepted = rejected emos, like last used: ['eka']
    # centralization = higher for lower randomness
    weight_sel = []
    weight_accum = 0
    for emotion_code in emotion:
        key = emotion_code.keys()[0]
        if not key in excepted:
            power = emotion_code[key]
            weight = math.exp(-(power - strength)**2 / (2 * pow(centralization, 2)))
            weight_accum += weight
            weight_sel.extend({key: weight_accum})
    rand = random.random() * weight_accum
    pointer = {"placeholder": rand}
    weight_sel.insert(0, pointer)
    weight_sel.sort(key=sort_by_val)
    seq = weight.sel.index(pointer)
    emo_final = weight_sel[seq + 1].keys()[0]
    emo_final_power = init_storage()[emo_final]
    # Notice this is a low-performance way! Consider adding a pure dict addressing all emocodes with their power
    # emo_final_power = [x for x in emotion if {i: j for i, j in x.items() if i == emo_final}][0].keys()[0]
    # emo_final_power is returned for affecting accumulation
    # emo_final like 'eka', emo_final_power like 0.6
    return emo_final, emo_final_power

def get_pos(strength=0.0, last=random.randint(1, 7)):
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
    match last:
        case 1:
            # pos1 is a calm pose. Tends to switch away and to point for stronger emotions
            match random.random():
                case f if 0 <= f < 0.5 - 0.2 * strength:
                    next_pos = 1
                case f if 0.5 - 0.2 * strength <= f < 0.7 - 0.25 * strength:
                    next_pos = 5
                case f if 0.7 - 0.25 * strength <= f < 0.85 - 0.2 * strength:
                    next_pos = random.choice([2,2,6])
                case f if 0.85 - 0.2 * strength <= f < 1:
                    next_pos = random.choice([3,3,3,3,3,4,7])
        case 2:
            # pos2 is a calm pose. Tends to switch away and to point for stronger emotions
            match random.random():
                case f if 0 <= f < 0.5 - 0.2 * strength:
                    next_pos = 2
                case f if 0.5 - 0.2 * strength <= f < 0.75 - 0.25 * strength:
                    next_pos = 5
                case f if 0.75 - 0.25 * strength <= f < 0.85 - 0.2 * strength:
                    next_pos = random.choice([1,1,6])
                case f if 0.85 - 0.2 * strength <= f < 1:
                    next_pos = random.choice([3,3,4,4,7])
        case 3:
            # pos3 is a pointing pose. Tends to keep or to point for stronger emotions
            match random.random():
                case f if 0 <= f < 0.1 + 0.3 * strength:
                    next_pos = 3
                case f if 0.1 + 0.3 * strength <= f < 0.1 + 0.7 * strength:
                    next_pos = 4
                case f if 0.1 + 0.7 * strength <= f < 0.9 - 0.1 * strength:
                    next_pos = random.choice([1,1,1,1,1,2,4,5,6])
                case f if 0.9 - 0.1 * strength <= f < 1:
                    next_pos = 7
        case 4:
            # pos4 is a tiring pose. Tends to switch away
            match random.random():
                case f if 0 <= f < 0.1 + 0.1 * strength:
                    next_pos = 4
                case f if 0.1 + 0.1 * strength <= f < 0.1 + 0.7 * strength:
                    next_pos = random.choice([3,7])
                case f if 0.1 + 0.7 * strength <= f < 0.9:
                    next_pos = random.choice([2,2,5,5,6])
                case f if 0.9 <= f < 1:
                    next_pos = 1
        case 5:
            # pos5 is a relaxing pose. Tends to switch away and to point for stronger emotions
            match random.random():
                case f if 0 <= f < 0.7 - 0.4 * strength:
                    next_pos = 5
                case f if 0.7 - 0.4 * strength <= f < 0.7 + 0.1 * strength:
                    next_pos = random.choice([3,4,7])
                case f if 0.7 + 0.1 * strength <= f < 0.9:
                    next_pos = 1
                case f if 0.9 <= f < 1:
                    next_pos = random.choice([2,2,6])
        case 6:
            # pos6 seldom happens
            match random.random():
                case f if 0 <= f < 0.5 - 0.4 * strength:
                    next_pos = 6
                case f if 0.5 - 0.4 * strength <= f < 0.6 - 0.1 * strength:
                    next_pos = random.choice([3,4,4,7,7])
                case f if 0.6 - 0.1 * strength <= f < 1:
                    next_pos = random.choice([1,1,1,2,2,2,5])
        case 7:
            # pos7 seldom happens
            match random.random():
                case f if 0 <= f < 0.1 + 0.4 * strength:
                    next_pos = 7
                case f if 0.1 + 0.4 * strength <= f < 0.6 + 0.3 * strength:
                    next_pos = random.choice([1,1,2,2,2,5,5])
                case f if 0.6 + 0.3 * strength <= f < 1:
                    next_pos = 6
    return next_pos