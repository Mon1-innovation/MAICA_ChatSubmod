init 5 python in maica:
    import store
    import maica, os, emotion_analyze
    maica.basedir = os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod")
    
    maica.logger = store.mas_submod_utils.submod_log
    data = {}
    def change_token(content):
        if maica.keep_running:
            return False, "MAICA 仍在连接中, 请先断开连接"
        maica = maica.MaicaAi("", "", content)
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        "Maica 令牌",
        on_change=change_token
    )
    maica = maica.MaicaAi("", "", store.mas_getAPIKey("Maica_Token"))


    # 表情代码
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion.txt"), "r") as e:
        for i in e.readlines():
            line = i.split(":")
            if len(line) != 2:
                continue
            line[1] = line[1].strip()
            if line[1] not in data:
                data[line[1]] = {"sentiment":-2}
            if not len(line[0]) in data[line[1]]:
                data[line[1]][len(line[0])] = []
            data[line[1]][len(line[0])].append(line[0])
    
        for i in data:
            for n in i:
                n = set(n)
    # 表情正负性
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion_sentiment.txt"), "r") as s:
        for i in s.readlines():
            line = i.split(":")
            if len(line) != 2:
                continue
            line[1] = line[1].strip()
            if line[0] in data:
                data[line[0]]["sentiment"] = [line[1]]
    emotion_analyze.add_emotedata(data.__dict__)

    # 表情相关性
    import json
    with open(os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod", "emotion_influence.json"), "r") as s:
        emotion_analyze.add_emoteeffectdata(
            json.load(s)
        )



    #set: store.mas_api_keys.api_keys |= {"Maica_Token":token}
    # store.mas_api_keys.save_keys()