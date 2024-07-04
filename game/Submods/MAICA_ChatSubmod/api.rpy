init 5 python in maica:
    import store
    import maica, os, json
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
    if store.persistent.maica_stat is None:
        store.persistent.maica_stat = maica.stat.copy()
    else:    
        maica.update_stat(store.persistent.maica_stat)


    basedir = renpy.config.basedir #"e:\GithubKu\MAICA_ChatSubmod"
    def init_selector():
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_selector.json"), "r") as emost:
            sentiment = json.loads(emost.read())
        return sentiment
    def init_storage():
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_power_storage.json"), "r") as emops:
            storage = json.loads(emops.read())
        return storage

    def init_sentiment():
        with open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_sentiment.json"), "r") as emost:
            sentiment = json.loads(emost.read())
        return sentiment

    maica.MoodStatus.selector = init_selector()
    maica.MoodStatus.storage = init_storage()
    maica.MoodStatus.sentiment = init_sentiment()

    