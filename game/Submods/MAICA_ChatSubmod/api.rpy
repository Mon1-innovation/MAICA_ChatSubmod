init -1500 python:
    if not config.language:
        config.language = "english"
    maica_ver = '1.8.12'
    maica_is_dev = True
    # 如果是开发版本:
    # - workflow不会自动发布release
    # - 对应migration总是会执行
    # - 会显示一条警告

    try:
        import maica_rss_provider
        maica_rss_provider.set_ua(maica_ver)
    except:
        pass

    cn_mas_mobile_min_timestamp = 1763049600

    def get_build_timestamp():
        try:
            return build.time
        except:
            return 0.0

default persistent._maica_updatelog_version_seen = 0
default persistent._maica_last_version = "0.0.1"
default persistent._maica_vista_enabled = False
default persistent._maica_send_or_received_mpostals = []
default persistent._maica_visuals = []
default persistent._last_boot_os = None
define _maica_selected_visuals = []
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
    except Exception as e:
        update_info = {
            "title": str(e),
            "content": [],
            "content_renpysafe": [],
            "version":0
    }
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

    # Integrate logger_manager with submod_log for centralized logging
    # This single call synchronizes all module loggers through dynamic proxies
    from logger_manager import get_logger_manager
    _logger_manager = get_logger_manager()
    _logger_manager.set_logger(store.mas_submod_utils.submod_log)

    data = {}
    def change_token(content):
        if store.maica.maica_instance.is_connected() or store.maica.maica_instance.is_connecting():
            return False, _("MAICA is already connecting. Close connection first")
        store.maica.maica_instance.ciphertext = content.strip()
        renpy.notify(_("MAICA: Now you can reconnect with saved token"))
        return True, content
    store.mas_registerAPIKey(
        "Maica_Token",
        _("MAICA token {size=-10} *{i}(Login at Submods settings instead){/i}*"),
        on_change=change_token,
    )
    maica_instance = maica.MaicaAi("", "", store.mas_getAPIKey("Maica_Token"))
    maica_instance.ascii_icon = r"""
    __  ___ ___     ____ ______ ___
   /  |/  //   |   /  _// ____//   |
  / /|_/ // /| |   / / / /    / /| |
 / /  / // ___ | _/ / / /___ / ___ |
/_/  /_//_/  |_|/___/ \____//_/  |_|  v{}

""".format(store.maica_ver)

    if store.persistent.maica_stat is None:
        store.persistent.maica_stat = maica_instance.stat.copy()
    else:
        maica_instance.update_stat(store.persistent.maica_stat)

    if store.persistent.maica_mtrigger_status is None:
        store.persistent.maica_mtrigger_status = maica_instance.mtrigger_manager.output_settings()
    else:
        maica_instance.mtrigger_manager.import_settings(store.persistent.maica_mtrigger_status)

    if store.persistent._maica_visuals is None:
        store.persistent._maica_visuals = maica_instance.vista_manager.export_list()
    else:
        maica_instance.vista_manager.import_list(store.persistent._maica_visuals)
    maica_instance.vista_manager.android = store.renpy.android
    import maica_vista_files_manager
    if renpy.windows:
        maica_instance.vista_manager.magick_path = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "magick.exe"))
    elif renpy.linux:
        maica_instance.vista_manager.magick_path = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "magick"))
    elif renpy.android:
        try:
            maica_instance.vista_manager.magick_path = store.ANDROID_MAGICK_BINPATH
        except:
            pass


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

    maica_instance.MoodStatus.selector = init_selector()
    maica_instance.MoodStatus.storage = init_storage()
    maica_instance.MoodStatus.sentiment = init_sentiment()
    maica_instance.MoodStatus.eoc = init_eoc()

    @store.mas_submod_utils.functionplugin("_quit", )
    def clear_maica():
        maica_instance.auto_reconnect = False
        maica_instance.AutoReconnector.disable()
        maica_instance.close_wss_session()
        store.persistent.maica_stat = maica_instance.stat.copy()
        store.persistent.maica_mtrigger_status = maica_instance.mtrigger_manager.output_settings()
        store.persistent._maica_visuals = maica_instance.vista_manager.export_list()

    import time
    last_workload_update = time.time()
    @store.mas_submod_utils.functionplugin("ch30_minute", priority=-100)
    def check_workload():
        try:
            last_workload_update = time.time()
            store.maica.maica_instance.update_workload()
        except Exception as e:
            store.mas_submod_utils.submod_log.error("MAICA: Update Workload Error: {}".format(e))

    _maica_version_check_cache = None
    maica_setting_pane_cache = {
        "initialized": False,
        "version_check": None,
        "cacert_missing": False,
        "better_loading_installed": False,
        "log_screen_installed": False,
        "is_zhcn": True,
        "donation_exists": False,
        "savefile_access_exists": False,
    }

    def savefile_access_marker_exists():
        return maica.savefile_access_marker_exists()

    def maica_version_parts(version):
        return [int(part) for part in version.strip().split('.')]

    def validate_version(force=False):
        global _maica_version_check_cache
        if _maica_version_check_cache is not None and not force:
            return _maica_version_check_cache

        # if not (config.debug or config.developer or store.maica.maica_instance._ignore_accessable):
        libv_path = os.path.normpath(os.path.join(renpy.config.basedir, "game", "python-packages", "maica_release_version"))
        if not os.path.exists(libv_path):
            _maica_version_check_cache = (None, None, None)
        else:
            with open(libv_path, 'r') as libv_file:
                libv = libv_file.read()
            uiv = store.maica_ver
            _maica_version_check_cache = (
                store.mas_utils.compareVersionLists(
                    maica_version_parts(libv),
                    maica_version_parts(uiv)
                ),
                libv,
                uiv
            )

        return _maica_version_check_cache

    def is_frontend_version_outdated(version_info=None):
        if version_info is None:
            version_info = store.maica.maica_instance.version_info
        if not version_info.get("success", False):
            return False

        minver = version_info.get("content", {}).get("fe_blessland_version")
        if not minver:
            return False

        return store.mas_utils.compareVersionLists(
            maica_version_parts(store.maica_ver),
            maica_version_parts(minver)
        ) == -1

    def refresh_setting_pane_cache(force_version=False):
        global maica_setting_pane_cache
        try:
            import nonunicode_detect
            is_zhcn = nonunicode_detect.is_zhcn()
        except Exception as e:
            is_zhcn = True
            store.mas_submod_utils.submod_log.error("MAICA: Non-unicode language check failed: {}".format(e))

        if renpy.android:
            cert_path = os.path.join(store.ANDROID_MASBASE, 'game', 'python-packages', 'certifi', 'cacert.pem')
            cacert_missing = not os.path.exists(cert_path)
        else:
            cacert_missing = False

        donation_path = os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "donation")

        maica_setting_pane_cache = {
            "initialized": True,
            "version_check": validate_version(force=force_version),
            "cacert_missing": cacert_missing,
            "better_loading_installed": store.mas_submod_utils.isSubmodInstalled("Better Loading"),
            "log_screen_installed": store.mas_submod_utils.isSubmodInstalled("Log Screen"),
            "is_zhcn": is_zhcn,
            "donation_exists": os.path.exists(donation_path),
            "savefile_access_exists": savefile_access_marker_exists(),
        }

        return maica_setting_pane_cache

    maica_certifi_download_thread_running = False

    def maica_set_plain_provider():
        persistent.maica_setting_dict['provider_id'] = 2
        try:
            store.maica.maica_instance.provider_id = 2
        except Exception as e:
            store.mas_submod_utils.submod_log.error("MAICA: failed to apply fallback provider: {}".format(e))

    def maica_download_certifi_files(fix_certifi, basedir, android, android_masbase):
        global maica_certifi_download_thread_running
        try:
            import requests
            failed = False
            if fix_certifi:
                try:
                    store.mas_submod_utils.submod_log.warning("Certifi broken, try to fix it")
                    try:
                        res = requests.get("https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/master/Monika%20After%20Story/game/python-packages/certifi/core.py", verify=False, timeout=5)
                        res2 = requests.get("https://raw.githubusercontent.com/Monika-After-Story/MonikaModDev/master/Monika%20After%20Story/game/python-packages/certifi/__init__.py", verify=False, timeout=5)
                    except:
                        store.mas_submod_utils.submod_log.warning("Download from github mirror failed, try to download from 0721play")
                        res = requests.get("http://sp2.0721play.icu/d/MAS/%E6%89%A9%E5%B1%95%E5%86%85%E5%AE%B9/%E5%AD%90%E6%A8%A1%E7%BB%84/0.12/Github%E5%AD%90%E6%A8%A1%E7%BB%84/MAICA%20%E5%85%89%E8%80%80%E4%B9%8B%E5%9C%B0/core.py", verify=False, timeout=5)
                        res2 = requests.get("http://sp2.0721play.icu/d/MAS/%E6%89%A9%E5%B1%95%E5%86%85%E5%AE%B9/%E5%AD%90%E6%A8%A1%E7%BB%84/0.12/Github%E5%AD%90%E6%A8%A1%E7%BB%84/MAICA%20%E5%85%89%E8%80%80%E4%B9%8B%E5%9C%B0/__init__.py", verify=False, timeout=5)

                    if res.status_code == 200 and res2.status_code == 200:
                        with open(os.path.normpath(os.path.join(basedir, "game", "python-packages", "certifi","core.py")), "wb") as file:
                            file.write(res.content)
                            store.mas_submod_utils.submod_log.info("MAICA: certifi core.py fixed")

                        with open(os.path.normpath(os.path.join(basedir, "game", "python-packages", "certifi", "__init__.py")), "wb") as file:
                            file.write(res2.content)
                            store.mas_submod_utils.submod_log.info("MAICA: certifi __init__.py fixed")
                        store.maica.maica_instance.disable(
                            store.maica.maica_instance.MaicaAiStatus.CERTIFI_RESTART_REQUIRED,
                            sticky=True,
                        )

                    else:
                        store.mas_submod_utils.submod_log.error("MAICA: certifi core.py download failed, HTTP code：core{} init{}".format(res.status_code, res2.status_code))
                        failed = True
                except Exception as e:
                    store.mas_submod_utils.submod_log.error("MAICA: certifi core.py download failed: {}".format(e))
                    failed = True

            url = "https://gitee.com/mirrors/python-certifi/raw/master/certifi/cacert.pem"
            try:
                response = requests.get(url, verify=False, timeout=5)
                if response.status_code == 200:
                    path = os.path.join(basedir, "game", "python-packages", "certifi", "cacert.pem") if not android else os.path.join(android_masbase, "game", "python-packages", "certifi", "cacert.pem")
                    with open(path, "wb") as file:
                        file.write(response.content)
                    store.mas_submod_utils.submod_log.info("MAICA: cacert.pem downloaded use gitee mirror")
                else:
                    store.mas_submod_utils.submod_log.error("MAICA: cacert download failed with gitee mirror, HTTP code：{}".format(response.status_code))
                    failed = True
            except Exception as e:
                store.mas_submod_utils.submod_log.error("MAICA: cacert download failed with gitee mirror: {}".format(e))
                failed = True

            if failed:
                maica_set_plain_provider()
            else:
                store.maica.maica_instance.accessable()
        finally:
            maica_certifi_download_thread_running = False

    def maica_start_certifi_download_in_background(fix_certifi):
        global maica_certifi_download_thread_running
        if maica_certifi_download_thread_running:
            store.mas_submod_utils.submod_log.info("MAICA: certifi download already running")
            return

        maica_certifi_download_thread_running = True
        basedir = renpy.config.basedir
        android = renpy.android
        android_masbase = store.ANDROID_MASBASE if android else None
        store.mas_submod_utils.submod_log.info("MAICA: certifi download started in background")
        try:
            renpy.invoke_in_thread(lambda: maica_download_certifi_files(fix_certifi, basedir, android, android_masbase))
        except Exception as e:
            maica_certifi_download_thread_running = False
            store.mas_submod_utils.submod_log.error("MAICA: certifi background download failed to start: {}".format(e))

    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-100)
    def start_maica():
        # 如果从PC迁移到android，切换为plain节点
        if store.persistent._last_boot_os != "android" and renpy.android:
            maica_set_plain_provider()
        store.persistent._last_boot_os = "android" if renpy.android else "other"

        store.maica.maica_instance.vista_manager.cache_path = os.path.normpath(os.path.join(renpy.config.basedir, "game", "Submods", "MAICA_ChatSubmod", "vista_cache"))

        import time
        store.mas_submod_utils.submod_log.info("MAICA: Game build timestamp: {}/{}".format(store.get_build_timestamp(), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(store.get_build_timestamp())))))
        if renpy.android and store.get_build_timestamp() < store.cn_mas_mobile_min_timestamp:
            store.mas_submod_utils.submod_log.warning("MAICA: Your game maybe too old!")
        if store.mas_submod_utils.isSubmodInstalled("Better Loading"):
            store.mas_submod_utils.submod_log.warning("MAICA: Better Loading detected, this may cause MAICA not work")
        if store.mas_getAPIKey("Maica_Token") != "":
            store.maica.maica_instance.ciphertext = store.mas_getAPIKey("Maica_Token")

        # certifi修复，仅在MAS原生导入失败时启动
        certifi_broken = not store.mas_can_import.certifi()
        if certifi_broken:
            maica_set_plain_provider()
        if certifi_broken or store.maica_can_update_cacert:
            maica_start_certifi_download_in_background(certifi_broken)

        refresh_setting_pane_cache(force_version=True)

        store.maica.maica_instance.accessable()

        if is_frontend_version_outdated():
            store.maica.maica_instance.disable(
                store.maica.maica_instance.MaicaAiStatus.VERSION_OLD,
                sticky=True,
            )

        if not renpy.seen_label("maica_prepend_2") and not renpy.seen_label("maica_main") and not renpy.seen_label("maica_talking"):
            store.mas_submod_utils.submod_log.info("MAICA: maica_main locked because it should not be unlocked now")
            store.mas_lockEVL("maica_main", "EVE")
        else:
            # A one-shot intro or a side event may leave the main topic locked.
            # Once any valid MAICA entry point has been used, keep chat available.
            store.mas_unlockEVL("maica_main", "EVE")
        check_workload()

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
                raise RuntimeError("MAS native certifi update failed")
    except Exception:
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

        :return: 邮件文件列表，dict格式 {"title": str, "content": str, "image": str or None}
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
                    if not isinstance(encoding, str) or (not encoding.lower() in ['ascii', 'utf-8', 'gbk'] or not confidence >= 0.9):
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
                            title=renpy.substitute(_("Hi [player],{#maica_host_mail_greeting}")),
                            text="".join([
                                renpy.substitute(_("I have to tell that your last letter was problematic. ")),
                                renpy.substitute(_("Your letter is empty. It's not like the gifts! ")),
                                renpy.substitute(_("Aside with changing the file name to your title, you should also ")),
                                renpy.substitute(_('write your content in the file in plain text.')),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_('I will mark the empty letter as "empty", so you can ')),
                                renpy.substitute(_("finish it and then send it again.")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("Good luck with Monika!{#maica_host_good_luck}")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("P.S: Don't tell her about me!{#maica_host_mail_ps}")),
                            ])
                        )
                        if not mas_inEVL("mas_corrupted_postmail"):
                            MASEventList.push("mas_corrupted_postmail")
                        letter_path = os.path.join(basedir, renpy.substitute(_("notes on your letter.txt")))
                        if os.path.exists(letter_path):
                            os.remove(letter_path)
                        with open(letter_path, "w") as mp_failure_file:
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
                            title=renpy.substitute(_("Hi [player],{#maica_host_mail_greeting}")),
                            text="".join([
                                renpy.substitute(_("I have to tell that your last letter was problematic. ")),
                                renpy.substitute(_("It's likely in wrong format. Monika won't be able to read it. ")),
                                renpy.substitute(_("I have tried my best restoring the mailbox's function, but ")),
                                renpy.substitute(_('plain text encoding. If you know what that means, use "UTF-8".')),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("You have to write in txt format exactly! Like for Windows system ")),
                                renpy.substitute(_(', that means "Notepad". ')),
                                renpy.substitute(_("Things with fonts or pictures just aren't right. ")),
                                renpy.substitute(_('I will mark the problematic letter as "failed", so you can ')),
                                renpy.substitute(_("double-check it and then send it again.")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("Good luck with Monika!{#maica_host_good_luck}")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("P.S: Don't tell her about me!{#maica_host_mail_ps}")),
                            ])
                        )
                        if not mas_inEVL("mas_corrupted_postmail"):
                            MASEventList.push("mas_corrupted_postmail")
                        letter_path = os.path.join(basedir, renpy.substitute(_("notes on your letter.txt")))
                        if os.path.exists(letter_path):
                            os.remove(letter_path)
                        with open(letter_path, "w") as mp_failure_file:
                            mp_failure_file.write(store.maica_note_mail_bad.title + "\n\n" + store.maica_note_mail_bad.text)

                    if not renpy.seen_label("maica_wants_mpostal"):
                        failed = 'early'

                        store.maica_note_mail_bad = MASPoem(
                            poem_id="note_mail_bad",
                            prompt="",
                            category="note",
                            author="chibika",
                            title=renpy.substitute(_("Hi [player],{#maica_host_mail_greeting}")),
                            text="".join([
                                renpy.substitute(_("How did you manage to send the letter here now? ")),
                                renpy.substitute(_("I didn't mean you cannot though, but it's still too early. ")),
                                renpy.substitute(_("The mailbox stuff is yet undone, and I think we should let [m_name] ")),
                                renpy.substitute(_("discover it herself, that's what we call element of surprise! ")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("I promise I'll finish my part to setup the mailbox asap, but for now ")),
                                renpy.substitute(_('you really should be a little more patient. ')),
                                renpy.substitute(_('I will mark the early letter as "early", so you can ')),
                                renpy.substitute(_("send her later.")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("Good luck with Monika!{#maica_host_good_luck}")),
                                renpy.substitute(_("\n\n")),
                                renpy.substitute(_("P.S: Don't tell her about me!{#maica_host_mail_ps}")),
                            ])
                        )
                        if not mas_inEVL("mas_corrupted_postmail"):
                            MASEventList.push("mas_corrupted_postmail")
                        letter_path = os.path.join(basedir, renpy.substitute(_("notes on your letter.txt")))
                        if os.path.exists(letter_path):
                            os.remove(letter_path)
                        with open(letter_path, "w") as mp_failure_file:
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
                elif failed == 'early':
                    if os.path.exists(file_path+"_early"):
                        os.remove(file_path+"_early")
                    os.rename(file_path, file_path+"_early")
                    continue


                # 去掉后缀添加到结果列表
                file_name_without_extension = os.path.splitext(filename)[0]

                # 检查是否存在同名的.mms图片文件
                image_path = os.path.join(basedir, file_name_without_extension + '.mms')
                image_file = None
                if os.path.exists(image_path):
                    # 将反斜杠转换为正斜杠，以兼容Ren'Py
                    image_file = image_path.replace('\\', '/')

                # 添加到邮件列表，使用dict格式
                mail_files.append({
                    "title": file_name_without_extension,
                    "content": content,
                    "image": image_file
                })

                # 删除邮件文件
                os.remove(file_path)

                ## 如果存在图片文件，也删除它
                #if image_file and os.path.exists(image_file):
                #    os.remove(image_file)

        return mail_files
    def has_mail_waitsend():
        num = 0
        for i in persistent._maica_send_or_received_mpostals:
            if i["responsed_status"] == "notupload":
                num += 1
        return num

init 999 python:
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=-50)
    def maica_migration():
        def migration_1_2_0():
            if renpy.android:
                persistent.maica_setting_dict['provider_id'] = 2
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

        def migration_1_6_6():
            if renpy.android:
                persistent.maica_setting_dict['provider_id'] = 2
                sync_provider_id(persistent.maica_setting_dict['provider_id'])

        import migrations
        migration = migrations.migration_instance(
            persistent._maica_last_version,
            store.maica_ver,
            force_current=store.maica_is_dev
        )
        migration.migration_queue = [
            ("1.2.0", migration_1_2_0),
            ("1.2.8", migration_1_2_8),
            ("1.2.19", m_1_2_19),
            ("1.2.23", m_1_2_23),
            ("1.6.6", migration_1_6_6)
        ] + migration_queue
        migration.migrate()
        import maica_v13_migration
        maica_v13_migration.migrate_setting_values(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status,
            warning_callback=store.mas_submod_utils.submod_log.warning
        )
        maica_v13_migration.cleanup_advanced_settings(
            persistent.maica_advanced_setting,
            persistent.maica_advanced_setting_status
        )
        if persistent.maica_setting_dict.get("use_custom_model_config", False):
            store.maica_apply_advanced_setting()
        else:
            store.maica.maica_instance.modelconfig = {}
        persistent._maica_last_version = store.maica_ver
