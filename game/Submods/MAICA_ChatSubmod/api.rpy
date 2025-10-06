init -1500 python:
    if not config.language:
        config.language = "english"
    maica_ver = '1.4.7'
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
#    "responsed_status":"delaying|notupload|received|readed|failed|fatal"
#}

init 5 python in maica:
    try:
        import maica_rss_provider
        update_info = maica_rss_provider.get_log()
    except:
        pass
    import store, chardet
    import bot_interface
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
        _("MAICA令牌{size=-10} *{i}(在子模组处登录后自动生成){/i}*"),
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
        import json_exporter
        sentiment = json_exporter.emotion_selector
        return sentiment
    def init_storage():
        import json_exporter
        storage = json_exporter.emotion_power_storage
        return storage
    def init_sentiment():
        import json_exporter
        sentiment = json_exporter.emotion_sentiment
        return sentiment
    def init_eoc():
        import json_exporter
        eoc = json_exporter.emotion_eoc
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
        mas_rmEVL("mas_corrupted_persistent")

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
    import time
    last_workload_update = time.time()
    @store.mas_submod_utils.functionplugin("ch30_minute", priority=-100)
    def check_workload():
        try:
            last_workload_update = time.time()
            store.maica.maica.update_workload()
        except Exception as e:
            store.mas_submod_utils.submod_log.error("MAICA: Update Workload Error: {}".format(e))
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def start_maica():
        import time
        failed = False
        store.mas_submod_utils.submod_log.info("MAICA: Game build timescamp: {}/{}".format(store.get_build_timescamp(), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(store.get_build_timescamp())))))
        if renpy.android and store.get_build_timescamp() < store.cn_mas_mobile_min_timescamp:
            store.mas_submod_utils.submod_log.warning("MAICA: Your game maybe too old!")
        if store.mas_submod_utils.isSubmodInstalled("Better Loading"):
            store.mas_submod_utils.submod_log.warning("MAICA: Better Loading detected, this may cause MAICA not work")
        if store.mas_getAPIKey("Maica_Token") != "":
            store.maica.maica.ciphertext = store.mas_getAPIKey("Maica_Token")
        if not store.mas_can_import.certifi() or store.maica_can_update_cacert:
            import requests
            canwhere = False
            if not store.mas_can_import.certifi():
                try:
                    store.mas_submod_utils.submod_log.warning("Certifi broken, try to fix it")
                    try:
                        res = requests.get("https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/master/Monika%20After%20Story/game/python-packages/certifi/core.py", verify=False)
                        res2 = requests.get("https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/master/Monika%20After%20Story/game/python-packages/certifi/__init__.py", verify=False)
                    except:
                        store.mas_submod_utils.submod_log.warning("Download from github mirror failed, try to download from 0721play")
                        res = requests.get("http://sp2.0721play.icu/d/MAS/%E6%89%A9%E5%B1%95%E5%86%85%E5%AE%B9/%E5%AD%90%E6%A8%A1%E7%BB%84/0.12/Github%E5%AD%90%E6%A8%A1%E7%BB%84/MAICA%20%E5%85%89%E8%80%80%E4%B9%8B%E5%9C%B0/core.py", verify=False)
                        res2 = requests.get("http://sp2.0721play.icu/d/MAS/%E6%89%A9%E5%B1%95%E5%86%85%E5%AE%B9/%E5%AD%90%E6%A8%A1%E7%BB%84/0.12/Github%E5%AD%90%E6%A8%A1%E7%BB%84/MAICA%20%E5%85%89%E8%80%80%E4%B9%8B%E5%9C%B0/__init__.py", verify=False)


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
                        failed = True
                except Exception as e:
                    store.mas_submod_utils.submod_log.error("MAICA: certifi core.py download failed: {}".format(e))
                    failed = True

            
            url = "https://gitee.com/mirrors/python-certifi/raw/master/certifi/cacert.pem"
            response = requests.get(url, verify=False)
            if response.status_code == 200:
                path = os.path.join(renpy.config.basedir, "game", "python-packages", "certifi", "cacert.pem") if not renpy.android else os.path.join(ANDROID_MASBASE, "game", "python-packages", "certifi", "cacert.pem")
                # 将文件保存到本地
                with open(path, "wb") as file:
                    file.write(response.content)
                store.mas_submod_utils.submod_log.info("MAICA: cacert.pem downloaded use gitee mirror")
            else:
                store.mas_submod_utils.submod_log.error("MAICA: cacert download failed with gitee mirror, HTTP code：{}", response.status_code)
                failed = True
        if failed:
            persistent.maica_setting_dict['provider_id'] = 2
        store.maica.maica.accessable()
        store.maica.maica.is_outdated = check_is_outdated(store.maica_ver)
        if store.maica.maica.is_outdated:
            store.maica.maica.disable(store.maica.maica.MaicaAiStatus.VERSION_OLD)

        if not renpy.seen_label("maica_greeting") and not renpy.seen_label("maica_main"):
            store.mas_submod_utils.submod_log.info("MAICA: maica_main locked because it should not be unlocked now")
            store.mas_lockEVL("maica_main", "EVE")
        else:
            store.mas_unlockEVL("maica_greeting", "GRE")
        check_workload()
        if not config.debug or not config.developer or store.maica.maica._ignore_accessable:
            if not os.path.exists(os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "release_version")))
                store.maica.maica.disable(13414)

    def progress_bar(percentage, current=None, total=None, bar_length=20, unit=None):
        # Calculate the number of filled positions in the progress bar
        filled_length = int(round(bar_length * percentage / 100.0))
        
        # Generate the progress bar string
        bar = '▇' * filled_length + '▁' * (bar_length - filled_length)
        
        # Format the output string based on the presence of total
        if total is not None:
            if not current:
                current = total * percentage / 100.0
            if unit:
                return '|{}| {}% | {}{} / {}{}'.format(bar, int(percentage), int(current), unit, total, unit)
            else:
                return '|{}| {}% | {} / {}'.format(bar, int(percentage), int(current), total)
        elif current is not None:
            if unit:
                return '|{}| {}% | {}{}'.format(bar, int(percentage), current, unit)
            else:
                return '|{}| {}% | {}'.format(bar, int(percentage), current)
        else:
            return '|{}| {}%'.format(bar, int(percentage))


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
        maica_chr_changed = check_sha256(os.path.normpath(os.path.join(renpy.config.basedir, "characters", "HeavenForest.sce")), '7164588cda6dcd4dee5268faa3ee143a45a085a93fe663cd91542f84279e0431')
    else:
        maica_chr_changed = None

    def mail_exist():
        basedir = os.path.join(renpy.config.basedir if not renpy.android else ANDROID_MASBASE , "characters")
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

        basedir = os.path.join(renpy.config.basedir if not renpy.android else ANDROID_MASBASE , "characters")
        mail_files = []

        # 遍历目录中的文件
        for filename in os.listdir(basedir):
            if filename.endswith('.mail'):
                # 获取完整文件路径
                file_path = os.path.join(basedir, filename)
                failed = False
                # 读取文件内容并检测编码
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    encoding, confidence = chardet.detect(raw_data)['encoding'], chardet.detect(raw_data)['confidence']
                    if not isinstance(encoding, str) or (not encoding.lower() in ['ascii', 'utf-8', 'gbk'] and not confidence >= 0.95):
                        # The detection might be wrong!
                        try:
                            raw_data.decode('utf-8')
                            encoding = 'utf-8'
                        except:
                            encoding = None
                    if not raw_data:
                        failed = 'empty'

                        store.maica_note_mail_bad = MASPoem(
                            poem_id="note_mail_empty",
                            prompt="",
                            category="note",
                            author="chibika",
                            title=renpy.substitute(_("[player]你好,")),
                            text="".join([
                                renpy.substitute(_("我得告诉你, 你写给莫妮卡的上一封信是有问题的. ")),
                                renpy.substitute(_("你的信里面没有内容. 这些信和礼物是不一样的! ")),
                                renpy.substitute(_("除了把标题写在文件名里, 你还得用纯文本的格式, ")),
                                renpy.substitute(_('在文件里写下信的正文.')),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_('我会把空的信标记为"empty", 这样你就可以')),
                                renpy.substitute(_("写好再发给她了.")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("祝你和莫妮卡好运!")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("P.S: 不要告诉她是我写的!")),
                            ])
                        )
                        if not mas_inEVL("mas_corrupted_postmail"):
                            MASEventList.push("mas_corrupted_postmail")
                        if not os.path.exists(os.path.join(basedir, renpy.substitute(_("关于你的信.txt")))):
                            with open(os.path.join(basedir, renpy.substitute(_("关于你的信.txt"))), "w") as mp_failure_file:
                                mp_failure_file.write(store.maica_note_mail_bad.title + "\n\n" + store.maica_note_mail_bad.text)
                    
                    # 如果chardet未能检测到编码，则使用默认编码（如utf-8）
                    elif encoding is None:
                        #encoding = 'utf-8'
                        failed = 'corrupt'

                        store.maica_note_mail_bad = MASPoem(
                            poem_id="note_mail_bad",
                            prompt="",
                            category="note",
                            author="chibika",
                            title=renpy.substitute(_("[player]你好,")),
                            text="".join([
                                renpy.substitute(_("我得告诉你, 你写给莫妮卡的上一封信是有问题的. ")),
                                renpy.substitute(_("你用的格式可能错了, 莫妮卡没法读出上面的内容. ")),
                                renpy.substitute(_("虽然我尽可能收拾好了这个邮箱, 但它只能读取纯")),
                                renpy.substitute(_('文字的文本. 如果你了解的话, 就是"UTF-8".')),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("你得用一个编写txt文件的工具写信! 在Windows系统")),
                                renpy.substitute(_('上的话, 就是"记事本". ')),
                                renpy.substitute(_("能够插入图片或者修改格式的工具都是不对的. ")),
                                renpy.substitute(_('我会把有问题的信标记为"failed", 这样你就可以')),
                                renpy.substitute(_("改好再发给她了.")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("祝你和莫妮卡好运!")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("P.S: 不要告诉她是我写的!")),
                            ])
                        )
                        if not mas_inEVL("mas_corrupted_postmail"):
                            MASEventList.push("mas_corrupted_postmail")
                        if not os.path.exists(os.path.join(basedir, renpy.substitute(_("关于你的信.txt")))):
                            with open(os.path.join(basedir, renpy.substitute(_("关于你的信.txt"))), "w") as mp_failure_file:
                                mp_failure_file.write(store.maica_note_mail_bad.title + "\n\n" + store.maica_note_mail_bad.text)
                    
                    # 解码文件内容
                if not failed:
                    content = raw_data.decode(encoding)
                elif failed == 'corrupt':
                    if os.path.exists(file_path+"_failed"):
                        os.remove(file_path+"_failed")
                    os.rename(file_path, file_path+"_failed")
                    continue
                elif failed == 'empty':
                    if os.path.exists(file_path+"_empty"):
                        os.remove(file_path+"_empty")
                    os.rename(file_path, file_path+"_empty")
                    continue

                
                # 去掉后缀添加到结果列表
                file_name_without_extension = os.path.splitext(filename)[0]
                mail_files.append((file_name_without_extension, content))
                
                # 删除文件
                os.remove(file_path)

        return mail_files
    def has_mail_waitsend():
        num = 0
        for i in persistent._maica_send_or_received_mpostals:
            if i["responsed_status"] == "notupload":
                num += 1
        return num

init 999 python:
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=0)
    def maica_migration():
        def migration_1_2_0():
            if renpy.android:
                persistent.maica_setting_dict['provider_id'] = 2
            if persistent.maica_setting_dict['max_history_token'] > 4096:
                persistent.maica_setting_dict['max_history_token'] = 4096
            maica_reset_setting()

        def migration_1_2_8():
            import logging
            persistent.maica_setting_dict['log_level'] = logging.DEBUG
        def m_1_2_19():
            if renpy.seen_label("maica_greeting"):
                store.mas_unlockEVL("maica_greeting", "GRE")
        def m_1_2_23():
            import bot_interface
            for item in persistent._maica_send_or_received_mpostals:
                item["responsed_content"] = bot_interface.key_replace(item["responsed_content"], bot_interface.renpy_symbol_big_bracket_only)
        import migrations
        migration = migrations.migration_instance(persistent._maica_last_version, store.maica_ver)
        migration.migration_queue = [
            ("1.2.0", migration_1_2_0),
            ("1.2.8", migration_1_2_8),
            ("1.2.19", m_1_2_19),
            ("1.2.23", m_1_2_23),
        ]
        migration.migrate()
        persistent._maica_last_version = store.maica_ver
