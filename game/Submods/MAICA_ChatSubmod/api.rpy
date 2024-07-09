init 5 python in maica:
    import store
    import maica, os, json
    maica.basedir = os.path.join(renpy.config.basedir, "game\Submods\MAICA_ChatSubmod")
    
    maica.logger = store.mas_submod_utils.submod_log
    data = {}
    def change_token(content):
        if store.maica.maica.wss_session is not None and store.maica.maica.wss_session.keep_running:
            return False, _("MAICA仍在连接中, 请先断开连接")
        store.maica.maica.ciphertext = content.strip()
        renpy.notify(_("请在子模组界面使用已保存的令牌重新连接"))
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        _("MAICA令牌"),
        on_change=change_token
    )
    maica = maica.MaicaAi("", "", store.mas_getAPIKey("Maica_Token"))
    #maica.update_screen_func = renpy.pause
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
    
    def init_eoc():
        with(open(os.path.join(basedir, "game\Submods\MAICA_ChatSubmod", "emotion_eoc.json"), "r")) as eocs:
            eoc = json.loads(eocs.read())
        return eoc

    maica.MoodStatus.selector = init_selector()
    maica.MoodStatus.storage = init_storage()
    maica.MoodStatus.sentiment = init_sentiment()
    maica.MoodStatus.eoc = init_eoc()

    @store.mas_submod_utils.functionplugin("_quit", )
    def clear_maica():
        maica.auto_reconnect = False
        maica.close_wss_session()
        store.persistent.maica_stat = maica.stat.copy()


    @store.mas_submod_utils.functionplugin("ch30_preloop")
    def start_maica():
        if store.mas_getAPIKey("Maica_Token") == "":
            return
        store.maica.maica.ciphertext = store.mas_getAPIKey("Maica_Token")

init -700 python:
    try:
        screen_data = store.mas_api_keys.MASUpdateCertScreenData()
        screen_data.start()
    except:
        store.mas_submod_utils.submod_log.warning("MAICA call MASUpdateCertScreenData.start() failed")


    import hashlib

    def calculate_sha256(file_path):
        """
        计算文件的SHA-256哈希值。

        :param file_path: 文件路径
        :return: 文件的SHA-256哈希值
        """
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                # 读取文件并更新哈希对象
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        except IOError as e:
            store.mas_submod_utils.submod_log.error("无法打开或读取文件: {}".format(e) )
            return None
        return sha256_hash.hexdigest()

    def check_sha256(file_path, expected_sha256):
        """
        检查文件的SHA-256哈希值是否等于给定值。

        :param file_path: 文件路径
        :param expected_sha256: 预期的SHA-256哈希值
        :return: 如果哈希值匹配则返回True，否则返回False
        """
        calculated_sha256 = calculate_sha256(file_path)
        if calculated_sha256 is None:
            return False
        return calculated_sha256 != expected_sha256
    
    maica_chr_exist = os.path.exists(os.path.join(renpy.config.basedir, "characters", "HeavenForest.sce"))
    if maica_chr_exist:
        maica_chr_changed = check_sha256(os.path.join(renpy.config.basedir, "characters", "HeavenForest.sce"), '35b4a17edbb003014fa93168e0c93df3149e82a4d46f16a0eec295a2d9b02d59')
    else:
        maica_chr_changed = None
