init -1500 python:
    if not config.language:
        config.language = "english"
    maica_ver = '1.2.3'
    try:
        import maica_rss_provider
        maica_rss_provider.set_ua(maica_ver)
    except:
        pass

    cn_mas_mobile_min_timescamp = 1733179724

    def get_build_timescamp():
        try:
            return build.time
        except:
            return 0.0

default persistent._maica_updatelog_version_seen = 0
default persistent._maica_last_version = "0.0.1"
default persistent._maica_send_or_received_mpostals = []
#{
#    "raw_title":"",
#    "raw_content":"",
#    "responsed_content": "",
#    "responsed_status":"notupload|delaying|received|readed|failed"
#}

init 5 python in maica:
    try:
        import maica_rss_provider
        update_info = maica_rss_provider.get_log()
    except:
        pass
    import store, chardet
    class MaicaInputValue(store.InputValue):
        """
        Our subclass of InputValue for internal use
        Allows us to manipulate the user input
        For more info read renpy docs (haha yeah...docs...renpy...)
        """
        def __init__(self):
            self.default = True
            self.input_value = ""
            self.editable = True
            self.returnable = True
    
        def get_text(self):
            return self.input_value
        
        def process_str(self, s):
            res = ""
            if isinstance(s, unicode):
                # 's' is already Unicode
                res = s
            else:
                # Detect encoding and decode to Unicode
                encoding_info = chardet.detect(s)
                encoding = encoding_info['encoding']
                if encoding is not None:
                    res = s.decode(encoding)
                else:
                    res = s.decode('utf-8', errors='replace')
            if len(res) > 375:
                res = res[:375]
            return res


        def set_text(self, s):
            self.input_value = self.process_str(s)

        def add_text(self, s):
            self.input_value += self.process_str(s)



    import store
    import maica, os, json
    maica.basedir = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod"))
    
    maica.logger = store.mas_submod_utils.submod_log
    data = {}
    def change_token(content):
        if store.maica.maica.wss_session is not None and store.maica.maica.is_connected():
            return False, _("MAICA仍在连接中, 请先断开连接")
        store.maica.maica.ciphertext = content.strip()
        renpy.notify(_("MAICA: 请在子模组界面使用已保存的令牌重新连接"))
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        _("MAICA令牌"),
        on_change=change_token,
    )
    maica = maica.MaicaAi("", "", store.mas_getAPIKey("Maica_Token"))
    maica.ascii_icon = """                                                             
    __  ___ ___     ____ ______ ___ 
   /  |/  //   |   /  _// ____//   |
  / /|_/ // /| |   / / / /    / /| |
 / /  / // ___ | _/ / / /___ / ___ |
/_/  /_//_/  |_|/___/ \____//_/  |_|  v{}

""".format(store.maica_ver)

    #maica.update_screen_func = renpy.pause
    if store.persistent.maica_stat is None:
        store.persistent.maica_stat = maica.stat.copy()
    else:    
        maica.update_stat(store.persistent.maica_stat)
    
    if store.persistent.maica_mtrigger_status is None:
        store.persistent.maica_mtrigger_status = maica.mtrigger_manager.output_settings()
    else:
        maica.mtrigger_manager.import_settings(store.persistent.maica_mtrigger_status)



    maica_basedir = renpy.config.basedir #"e:\GithubKu\MAICA_ChatSubmod"
    def init_selector():
        with open(os.path.normpath(os.path.join(maica_basedir, "game", "Submods", "MAICA_ChatSubmod", "emotion_selector.json")), "r") as emost:
            sentiment = json.loads(emost.read())
        return sentiment
    def init_storage():
        with open(os.path.normpath(os.path.join(maica_basedir, "game", "Submods", "MAICA_ChatSubmod", "emotion_power_storage.json")), "r") as emops:
            storage = json.loads(emops.read())
        return storage

    def init_sentiment():
        with open(os.path.normpath(os.path.join(maica_basedir, "game", "Submods", "MAICA_ChatSubmod", "emotion_sentiment.json")), "r") as emost:
            sentiment = json.loads(emost.read())
        return sentiment
    
    def init_eoc():
        with(open(os.path.normpath(os.path.join(maica_basedir, "game", "Submods", "MAICA_ChatSubmod", "emotion_eoc.json")), "r")) as eocs:
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
        store.persistent.maica_mtrigger_status = maica.mtrigger_manager.output_settings()

    def check_is_outdated(version_local):
        url = "http://sp2.0721play.icu/d/MAS/%E6%89%A9%E5%B1%95%E5%86%85%E5%AE%B9/%E5%AD%90%E6%A8%A1%E7%BB%84/0.12/Github%E5%AD%90%E6%A8%A1%E7%BB%84/MAICA%20%E5%85%89%E8%80%80%E4%B9%8B%E5%9C%B0/version_data.json"
        import requests, store
        try:
            r = requests.get(url)
            version_remote = r.json().get("min_version")
            return store.mas_utils._is_downgrade(version_remote, version_local)
        except:
            store.mas_submod_utils.submod_log.warning("MAICA: Check Version Failed")
            return None

    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def start_maica():
        import time
        store.mas_submod_utils.submod_log.info("MAICA: Game build timescamp: {}/{}".format(store.get_build_timescamp(), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(store.get_build_timescamp())))))
        if renpy.android and store.get_build_timescamp() < store.cn_mas_mobile_min_timescamp:
            store.mas_submod_utils.submod_log.warning("MAICA: Your game maybe too old!")
        if store.mas_submod_utils.isSubmodInstalled("Better Loading"):
            store.mas_submod_utils.submod_log.warning("MAICA: Better Loading detected, this may cause MAICA not work")
        if store.mas_getAPIKey("Maica_Token") != "":
            store.maica.maica.ciphertext = store.mas_getAPIKey("Maica_Token")
        if not store.mas_can_import.certifi() or store.maica_can_update_cacert:
            import requests
            if not store.mas_can_import.certifi():
                try:
                    store.mas_submod_utils.submod_log.warning("Certifi broken, try to fix it")
                    try:
                        res = requests.get("https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/06baf319a34c2ef585bc7c0a1e969a7eaa894b35/Monika%20After%20Story/game/python-packages/certifi/core.py", verify=False)
                        res2 = requests.get("https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/06baf319a34c2ef585bc7c0a1e969a7eaa894b35/Monika%20After%20Story/game/python-packages/certifi/__init__.py", verify=False)
                    except:
                        res = requests.get("https://mirror.ghproxy.com/" + "https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/06baf319a34c2ef585bc7c0a1e969a7eaa894b35/Monika%20After%20Story/game/python-packages/certifi/core.py", verify=False)
                        res2 = requests.get("https://mirror.ghproxy.com/" + "https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/06baf319a34c2ef585bc7c0a1e969a7eaa894b35/Monika%20After%20Story/game/python-packages/certifi/__init__.py", verify=False)

                    if res.status_code == 200 and res2.status_code == 200:
                        with open(os.path.normpath(os.path.join(renpy.config.basedir, "game", "python-packages", "certifi","core.py")), "wb") as file:
                            file.write(res.content)
                            store.maica.maica.status = 13408
                            store.mas_submod_utils.submod_log.info("MAICA: certifi core.py fixed")
                    
                        with open(os.path.normpath(os.path.join(renpy.config.basedir, "game", "python-packages", "certifi", "__init__.py")), "wb") as file:
                            file.write(res2.content)
                            store.maica.maica.status = 13408
                            store.mas_submod_utils.submod_log.info("MAICA: certifi __init__.py fixed")
                    else:
                        store.mas_submod_utils.submod_log.error("MAICA: certifi core.py download failed, HTTP code：core{} init{}", res.status_code, res2.status_code)
                except Exception as e:
                    store.mas_submod_utils.submod_log.error("MAICA: certifi core.py download failed: {}".format(e))
            
            url = "https://gitee.com/mirrors/python-certifi/raw/master/certifi/cacert.pem"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                # 将文件保存到本地
                with open(os.path.join(renpy.config.basedir, "game", "python-packages", "certifi", "cacert.pem"), "wb") as file:
                    file.write(response.content)
                store.mas_submod_utils.submod_log.info("MAICA: cacert.pem downloaded use gitee mirror")
            else:
                store.mas_submod_utils.submod_log.error("MAICA: cacert download failed with gitee mirror, HTTP code：{}", response.status_code)
            
        store.maica.maica.accessable()
        store.maica.maica.is_outdated = check_is_outdated(store.maica_ver)
        if store.maica.maica.is_outdated:
            store.maica.maica.disable(store.maica.maica.MaicaAiStatus.VERSION_OLD)

        if not renpy.seen_label("maica_greeting"):
            store.mas_submod_utils.submod_log.info("MAICA: maica_main locked because it should not be unlocked now")
            store.mas_lockEVL("maica_main", "EVE")
        else:
            store.mas_unlockEVL("maica_greeting", "GRE")
                

init -700 python:
    maica_can_update_cacert = False
    try:
        import os
        if not os.path.exists(os.path.normpath(os.path.join(renpy.config.basedir, "game", "python-packages", "certifi", "cacert.pem"))):
            res = mas_can_import.certifi._update_cert(force=True)
            if res is None or res < 0:
                raise Exception("fuck")
    except:
        maica_can_update_cacert = True
        store.mas_submod_utils.submod_log.warning("MAS native function update cacert failed")


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

    maica_chr_exist = os.path.exists(os.path.normpath(os.path.join(renpy.config.basedir, "characters", "HeavenForest.sce")))
    if maica_chr_exist:
        maica_chr_changed = check_sha256(os.path.normpath(os.path.join(renpy.config.basedir, "characters", "HeavenForest.sce")), '35b4a17edbb003014fa93168e0c93df3149e82a4d46f16a0eec295a2d9b02d59')
    else:
        maica_chr_changed = None

    def mail_exist():
        basedir = os.path.join(renpy.config.basedir, "characters")
        mail_files = []

        # 遍历目录中的文件
        for filename in os.listdir(basedir):
            if filename.endswith('.mail'):
                return True

    import os
    import chardet

    def find_mail_files():
        """
        查找邮件文件。

        :return: 邮件文件列表，(title, content)
        """

        basedir = os.path.join(renpy.config.basedir, "characters")
        mail_files = []

        # 遍历目录中的文件
        for filename in os.listdir(basedir):
            if filename.endswith('.mail'):
                # 获取完整文件路径
                file_path = os.path.join(basedir, filename)
                
                # 读取文件内容并检测编码
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    encoding = chardet.detect(raw_data)['encoding']
                    
                    # 如果chardet未能检测到编码，则使用默认编码（如utf-8）
                    if encoding is None:
                        encoding = 'utf-8'
                    
                    # 解码文件内容
                    content = raw_data.decode(encoding)
                
                # 去掉后缀添加到结果列表
                file_name_without_extension = os.path.splitext(filename)[0]
                mail_files.append((file_name_without_extension, content))
                
                # 删除文件
                os.remove(file_path)

        return mail_files
    def has_mail_waitsend():
        for i in persistent._maica_send_or_received_mpostals:
            if i["responsed_status"] == "notupload":
                return True
        return False

init 999 python:
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=0)
    def maica_migration():
        def migration_1_2_0():
            if renpy.android:
                persistent.maica_setting_dict['provider_id'] = 2
            if persistent.maica_setting_dict['max_history_token'] > 4096:
                persistent.maica_setting_dict['max_history_token'] = 4096
            maica_reset_setting()
        import migrations
        migration = migrations.migration_instance(persistent._maica_last_version, store.maica_ver)
        migration.migration_queue = [
            ("1.2.0", migration_1_2_0),
        ]
        migration.migrate()
        persistent._maica_last_version = store.maica_ver
