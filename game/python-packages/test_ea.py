import emotion_analyze_v2, os, json
basedir = "E:\GithubKu\MAICA_ChatSubmod"
def init_selector():
    selector = {}
    power={}
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion.txt"), "r", encoding='utf-8') as emos:
        for item in emos.readlines():
            if item[0] == "#":
                continue
            i = item.strip().split(":")
            i[0]=i[0][1:]
            if i[1] not in selector:
                selector[i[1]]=[]
            selector[i[1]].append({i[0]: float(i[2])})
            power[i[0]] = float(i[2])
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_selector.json"), "w") as emos:
            emos.write(json.dumps(selector, ensure_ascii=False))
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_power_storage.json"), "w") as emos:
            emos.write(json.dumps(power, ensure_ascii=False))
    return selector

def init_storage():
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_power_storage.json"), "r", encoding='utf-8') as emops:
        storage = json.loads(emops.read())
    return storage

def init_sentiment():
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_sentiment.json"), "r", encoding='utf-8') as emost:
        sentiment = json.loads(emost.read())
    return sentiment

selector = emotion_analyze_v2.EmoSelector(init_selector(), init_storage(), init_sentiment())
selector.selector = init_selector()
selector.storage = init_storage()
selector.sentiment = init_sentiment()

selector.analyze("[很开心]")
print(selector.get_emote())
