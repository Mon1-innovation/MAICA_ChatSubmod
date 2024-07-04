init 5 python in maica:
    import store
    import maica, os, emotion_analyze
    maica.basedir = os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod")
    
    maica.logger = store.mas_submod_utils.submod_log
    data = {}
    def change_token(content):
        if store.maica.maica.wss_session is not None and store.maica.maica.wss_session.keep_running:
            return False, "MAICA 仍在连接中, 请先断开连接"
        store.maica.maica.ciphertext = content.strip()
        renpy.notify("请在子模组界面使用已保存的令牌重新连接")
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        "Maica 令牌",
        on_change=change_token
    )
    maica = maica.MaicaAi("", "", store.mas_getAPIKey("Maica_Token"))


    basedir = renpy.config.basedir #"e:\GithubKu\MAICA_ChatSubmod"
    # 表情代码
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion.txt"), "r") as e:
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
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_sentiment.txt"), "r") as s:
        for i in s.readlines():
            line = i.split(":")
            if len(line) != 2:
                continue
            line[1] = line[1].strip()
            if line[0] in data:
                data[line[0]]["sentiment"] = [line[1]]
    emotion_analyze.add_emotedata(data)
    
    # 表情相关性
    import json
    with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_influence.json"), "r") as s:
        emotion_analyze.add_emoteeffectdata(
            json.load(s)
        )

    import emotion_analyze
    mood = emotion_analyze.MoodStatus()
    mood.get_emote()
    #set: store.mas_api_keys.api_keys |= {"Maica_Token":token}
    # store.mas_api_keys.save_keys()