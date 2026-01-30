# -*- coding: utf-8 -*-

from bot_interface import *
import bot_interface
import emotion_analyze_v2
import maica_tasker, maica_tasker_sub, maica_tasker_sub_sessionsender, maica_vista_files_manager
import maica_provider_manager

# Import LoggerManager for injection point registration
from logger_manager import get_logger_manager, MultiLoggerWrapper

import websocket
import maica_mtrigger
from maica_mtrigger import MTriggerAction

# Initialize injection point registration
_logger_manager = get_logger_manager()

# Register initial injection points
maica_tasker.default_logger = logger
_logger_manager.register_injected_reference('maica_tasker.default_logger', maica_tasker, 'default_logger')

websocket._logging._logger = logger
_logger_manager.register_injected_reference('websocket._logging._logger', websocket._logging, '_logger')

# Register bot_interface logger for centralized management
_logger_manager.register_injected_reference('bot_interface.logger', bot_interface, 'logger')

# Register emotion_analyze_v2 logger for centralized management
_logger_manager.register_injected_reference('emotion_analyze_v2.logger', emotion_analyze_v2, 'logger')

# Register maica_provider_manager logger for centralized management
_logger_manager.register_injected_reference('maica_provider_manager.logger', maica_provider_manager, 'logger')

websocket._logging.enableTrace(False)
import datetime

def seconds_to_hms(timestamp_ms):
    # 将毫秒转换为秒
    timestamp_s = timestamp_ms
    # 获取系统本地时区
    dt = datetime.datetime.fromtimestamp(timestamp_s)
    return dt.strftime("%H:%M:%S")

class MaicaAi(ChatBotInterface):
    SUPPORT_BACKEND = "1.2.000.rc10"
    ascii_icon = """                                                             

    __  ___ ___     ____ ______ ___ 
   /  |/  //   |   /  _// ____//   |
  / /|_/ // /| |   / / / /    / /| |
 / /  / // ___ | _/ / / /___ / ___ |
/_/  /_//_/  |_|/___/ \____//_/  |_| v
                                    
"""
    class MaicaAiLang:
        zh_cn = "zh"
        en = "en"
    class MaicaMSpiretype:
        percise_page = "percise_page"
        fuzzy_page = "fuzzy_page"
        in_percise_category = "in_percise_category"
        in_fuzzy_category = "in_fuzzy_category"
        in_fuzzy_all = "in_fuzzy_all"

    class MaicaAiStatus:
        # 未准备好
        NOT_READY = 10000
        # websocket正在连接
        WEBSOCKET_CONNECTING = 10020
        # 账户信息已准备好，准备令牌验证
        WAIT_AUTH = 10100
        # 等待令牌验证结果
        WAIT_SERVER_TOKEN = 10101
        # 传入令牌
        WAIT_USE_TOKEN = 10102
        # 令牌已传入，session已开启，应该选择模型了
        SESSION_CREATED = 10106
        # 等待模型信息
        WAIT_MODEL_INFOMATION = 10110
        # maica 已准备好，等待玩家输入
        MESSAGE_WAIT_INPUT = 10302
        # ssl证书获取错误, 但使用plain能够连接
        SSL_FAILED_BUT_OKAY = 10322
        # 已输入消息，等待消息发送
        MESSAGE_WAIT_SEND = 10300
        # 发送MSpire请求
        MESSAGE_WAIT_SEND_MSPIRE = 10304
        # 发送MPostal请求
        MESSAGE_WAIT_SEND_MPOSTAL = 10305
        # 已发送消息，等待MAICA回应
        MESSAGE_WAITING_RESPONSE = 10301
        # MAICA 已经输出完毕
        MESSAGE_DONE = 10303

        # 请求重置session
        REQUEST_RESET_SESSION = 11000

        # session已重置，websocket已关闭
        SESSION_RESETED = 12000

        # 请求心跳包
        REQUEST_PING = 11100
        # 发送设置项
        SEND_SETTING = 11200
        # 等待设置结果
        WAIT_SETTING_RESPONSE = 11201
        #############################Submod 错误状态码
        # 疑似网络问题
        # 令牌验证失败
        TOKEN_FAILED = 13400
        # 选择的 model 不正确
        MODEL_NOT_FOUND = 13401
        # wss异常关闭
        WSS_CLOSED_UNEXCEPTED = 13402
        # 玩家数据未找到
        SAVEFILE_NOTFOUND = 13403
        # 网络问题
        CONNECT_PROBLEM = 13404
        # 服务器维护中
        SERVER_MAINTAIN = 13405
        # 错误的输入
        WRONE_INPUT = 13406
        # 证书模块损坏
        CERTIFI_BROKEN = 13407
        # 证书模块损坏, 但是自动修复成功, 需要重启
        CERTIFI_AUTO_FIX = 13408
        # 等待可用性验证
        WAIT_AVAILABILITY = 13409
        # 获取节点失败
        FAILED_GET_NODE = 13410
        # 版本过旧
        VERSION_OLD = 13411
        # 发送内容过长
        TOOLONG_CONTENT_LENGTH = 13412
        # 无网络
        NO_INTERTENT = 13413
        # 非发行版本
        IS_SOURCECODE = 13414
        ######################### MAICA 服务器状态码
        MAIKA_PREFIX = 5000
        @classmethod
        def is_1xx(cls, code):
            return 100 <= int(code) - cls.MAIKA_PREFIX <= 199

        @classmethod
        def is_submod_exception(cls, code):
            return 13400 <= code <= 13499
        
        # session 已超过 32768token
        TOKEN_MAX_EXCEEDED = MAIKA_PREFIX + 204
        # session > 24000token
        TOKEN_24000_EXCEEDED = MAIKA_PREFIX + 200

        _descriptions = {
            NOT_READY: u"未准备好, 等待配置账户信息",
            WAIT_AVAILABILITY:u"需要验证可用性, 请重启. 若问题仍然存在则检查mas.log",
            WAIT_AUTH: u"账户信息已确认，连接MAICA服务器验证中",
            WAIT_SERVER_TOKEN: u"等待令牌验证结果",
            WAIT_USE_TOKEN: u"等待传入令牌",
            SESSION_CREATED: u"令牌已传入，session已开启，应该选择模型了",
            WAIT_MODEL_INFOMATION: u"等待模型信息",
            MESSAGE_WAIT_INPUT: u"maica 已准备好，等待玩家输入",
            SSL_FAILED_BUT_OKAY: u"maica 未能获取设备根证书, 已回退到无加密模式. 这一般不会影响正常功能",
            MESSAGE_WAIT_SEND: u"已输入消息，等待消息发送",
            MESSAGE_WAITING_RESPONSE: u"已发送消息，等待MAICA回应",
            MESSAGE_WAIT_SEND_MSPIRE: u"等待发送 MSpire 请求",
            MESSAGE_WAIT_SEND_MPOSTAL: u"等待发送 MPostal 请求",
            MESSAGE_DONE: u"MAICA 已经输出完毕",
            REQUEST_RESET_SESSION: u"请求重置 session",
            SESSION_RESETED: u"session 已重置，websocket 已关闭",
            REQUEST_PING: u"请求心跳包",
            TOKEN_FAILED: u"令牌验证失败",
            CONNECT_PROBLEM: u"无法连接服务器, 请检查网络, 查看submod_log以获取详细信息",
            MODEL_NOT_FOUND: u"选择的 model 不正确",
            TOKEN_MAX_EXCEEDED:u"session 已超过 28672 token, 对话已被裁剪",
            TOKEN_24000_EXCEEDED:u"session 已超过 24576 token, 如需要历史记录请及时保存, 对话将很快被裁剪",
            WSS_CLOSED_UNEXCEPTED:u"websocket 异常关闭, 查看submod_log以获取详细信息" if PY2 else u"websocket 异常关闭, 请确认已安装数据包, 查看submod_log以获取详细信息",
            SAVEFILE_NOTFOUND:u"玩家存档未找到, 请确保当前对话会话已经上传存档",
            SERVER_MAINTAIN:u"服务器维护中, 请关注相关通知",
            WRONE_INPUT:u"错误的输入, 请检查输入内容",
            CERTIFI_BROKEN:u"证书模块损坏, 请重新安装MAS",
            CERTIFI_AUTO_FIX:u"证书模块损坏, 已尝试自动修复, 若重启无效请干净安装",
            SEND_SETTING:u"上传设置中",
            FAILED_GET_NODE:u"获取服务节点失败, 服务器可能维护或离线",
            WEBSOCKET_CONNECTING:u"websocket 正在连接（这应该很快）",
            VERSION_OLD:u"子模组版本过旧, 请升级至最新版",
            TOOLONG_CONTENT_LENGTH:u"发送内容过长, 请查看 MTrigger 列表并关闭不需要的触发器",
            NO_INTERTENT:u"子模组未能联网, 根据 Readme 说明检查安装和网络连接",
            IS_SOURCECODE:u"你不应从源码直接安装, 请从Releases界面下载最新发行版."
        }

        @classmethod
        def get_description(cls, code):
            return cls._descriptions.get(code, u"未知状态码: {}".format(code))
            
        
        #@classmethod
        #def add_status_code(cls, name, code, description):
        #    if code in cls._descriptions:
        #        raise ValueError("状态码 {} 已存在，不能重复添加。".format(code))
        #    cls._descriptions[code] = description
        #    setattr(cls, "{}".format(name), code)
    class ExternalLoggingHandler(logging.Handler):
        def __init__(self, maica_console_log_func):
            self.maica_console_log_func = maica_console_log_func
            self.leveling_filter = re.compile(r'^.*?<DISABLE_VERBOSITY>')
            super(MaicaAi.ExternalLoggingHandler, self).__init__()
        def emit(self, record):
            log_message = self.format(record)
            log_message = self.leveling_filter.sub('', log_message, re.I)
            self.maica_console_log_func(log_message)

    MAX_CHATSESSION = 9

    def __init__(self, account, pwd, token = ""):
        """
        初始化函数，用于创建MaicaAI对象
        
        Args:
            account (str): MaicaAI账号
            pwd (str): MaicaAI密码
            token (str, optional): MaicaAI的token，默认为空字符串
        
        Returns:
            None
        """
        import threading
        self.__accessable = False
        self._ignore_accessable = False
        self._serving_status = ""
        self.stat = {}
        self.multi_lock = threading.Lock()
        self.MoodStatus = emotion_analyze_v2.EmoSelector(None, None, None, self.get_emotion)
        self.public_key = None
        self.ciphertext = None
        self.chat_session = 1
        self.wss_session = None
        self.wss_thread = None
        self.enable_mf = True
        self.enable_mt = True
        self.sf_extraction = False
        self.stream_output = True
        self.content_func = None
        # 待发送消息队列
        self.senddata_queue = Queue() if not PY3 else bot_interface.Queue()
        self.TalkSpilter = bot_interface.TalkSplitV2()
        self.status = self.MaicaAiStatus.WAIT_AVAILABILITY
        self.target_lang = self.MaicaAiLang.zh_cn        
        self.modelconfig = {}
        self.reset_stat()
        self._auto_reconnect = False
        self._auto_resume = False
        self._keep_alive = False
        self.mspire_category = []
        self.mspire_session = 0
        self.mspire_sample = 250
        self.mspire_type = self.MaicaMSpiretype.in_fuzzy_all
        self.pprt=False
        self.in_mas = True
        self.provider_manager = maica_provider_manager.MaicaProviderManager()
        self.is_outdated = None
        self.max_history_token = 28672
        self._in_mspire = False
        self.mspire_use_cache = False
        self.mtrigger_manager = maica_mtrigger.MTriggerManager()
        self.tz = "Asia/Shanghai"
        self.dscl_pvn = False
        self.__ws_cookie = ""
        self._enable_strict_mode = False
        self.default_setting = {
            "amt_aggressive": True,
            "deformation": False,
            "enable_mf": True,
            "enable_mt": True,
            "esc_aggressive": True,
            "frequency_penalty": 0.44,
            "max_length": 8192,
            "max_tokens": 1600,
            "mf_aggressive": False,
            "mt_extraction": True,
            "nsfw_acceptive": True,
            "post_additive": 1,
            "pre_additive": 0,
            "presence_penalty": 0.34,
            "seed": None,
            "sf_extraction": True,
            "sfe_aggressive": False,
            "stream_output": True,
            "target_lang": "zh",
            "temperature": 0.22,
            "tnd_aggressive": 1,
            "top_p": 0.7,
            "tz": None
        }
        self.workload_raw = {
            "None":{
                "0": {
                    "name": "Super PP 0",
                    "vram": "100000 MiB",
                    "mean_utilization": 100,
                    "mean_memory": 21811,
                    "mean_consumption": 100,
                    "tflops": 400,
                },                
                "1": {
                    "name": "if you see this, requests workload is failed",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "tflops": 400,
                    "mean_consumption": 100
                },
            },
            "None2":{
                "0": {
                    "name": "Super PP 2",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "tflops": 400,
                    "mean_consumption": 100
                    
                },                
                "1": {
                    "name": "Super PP 3",
                    "vram": "100000 MiB",
                    "mean_utilization": 0,
                    "mean_memory": 21811,
                    "tflops": 400,
                    "mean_consumption": 100
                },
            },
            "onliners":0
        }
        self.console_logger = logging.getLogger(name="mas_console_logger")
        self.console_logger.setLevel(logging.DEBUG)
        h = self.ExternalLoggingHandler(self.send_to_outside_func)
        h.setFormatter(logging.Formatter("<%(levelname)s>|%(message)s"))
        self.console_logger.addHandler(h)

        # Create optimized logger_both using MultiLoggerWrapper
        from logger_manager import MultiLoggerWrapper
        self.logger_both_wrapper = MultiLoggerWrapper([logger, self.console_logger])

        # For backward compatibility, also create the legacy logger_both class
        class logger_both:
            def __init__(self, wrapper):
                self.wrapper = wrapper
            def info(self, msg):
                self.wrapper.info(msg)
            def error(self, msg):
                self.wrapper.error(msg)
            def warning(self, msg):
                self.wrapper.warning(msg)
            def debug(self, msg):
                self.wrapper.debug(msg)

        maica_mtrigger.logger = logger_both(self.logger_both_wrapper)

        # Register the third injection point
        _logger_manager.register_injected_reference('maica_mtrigger.logger', maica_mtrigger, 'logger')

        self.vista_manager = maica_vista_files_manager.MAICAVistaFilesManager(
            base_url=self.provider_manager.get_api_url(),
            access_token=self.ciphertext,
        )

        #task
        self.task_manager = maica_tasker.MaicaTaskManager()


        maica_tasker_sub.GeneralTaskEventLogger(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_NORMAL,
            name="general_task_event_logger",
            manager=self.task_manager
        )

        maica_tasker_sub.GeneralWsErrorHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="general_ws_error_handler",
            manager=self.task_manager,
            except_ws_status=[]
        )
        maica_tasker_sub.GeneralWsLogger(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="general_ws_logger",
            manager=self.task_manager,
            except_ws_status=[]
        )

        self.WSConsoleLogger = maica_tasker_sub.GeneralWsConsoleLogger(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="general_ws_console_logger",
            manager=self.task_manager,
            except_ws_status=[],
            console_logger=self.console_logger
        )

        maica_tasker_sub.MAICALoopWarnHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="maicaloop_warn_handler",
            manager=self.task_manager,
            except_ws_status=['maica_loop_warn_finished']
        )

        self.HistoryStatus = maica_tasker_sub.HistoryStatusHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="history_status_handler",
            manager=self.task_manager
        )
        self.UserData = maica_tasker_sub.MAICAUserDataHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="maica_user_data_handler",
            manager=self.task_manager
        )

        self.MTriggerTasker = maica_tasker_sub.MTriggerWsHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="mtrigger_ws_handler",
            manager=self.task_manager,
            except_ws_status=[
                'maica_mtrigger_trigger',
                'maica_dscl_status'
            ]
        )
        self.MTriggerTasker.set_trigger_function(self.mtrigger_manager.triggered)

        self.WSCookiesTask = maica_tasker_sub.MAICAWSCookiesHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="maica_ws_cookies_handler",
            manager=self.task_manager,
            except_ws_status=['maica_connection_security_cookie']
        )

        self.Loginer = maica_tasker_sub.MAICALoginTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="login_task",
            manager=self.task_manager,
            except_ws_status=['maica_connection_established', 'maica_connection_initiated', 'maica_unidentified_warning']
        )

        self.SessionReseter = maica_tasker_sub.MAICASessionResetTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="session_reset_task",
            manager=self.task_manager
        )

        self.SettingSender = maica_tasker_sub.MAICASettingSendTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="setting_send_task",
            manager=self.task_manager,
            except_ws_status=['maica_params_accepted']
        )
        self.SettingSender.set_generate_setting_func(self.build_setting_config)

        self.ChatProcessor = maica_tasker_sub_sessionsender.MAICAGeneralChatProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="general_chat_processor",
            manager=self.task_manager,
            except_ws_status=['maica_core_streaming_continue', 'maica_chat_loop_finished']
        )
        self.ChatProcessor._external_callback = self.general_chat_callback
        self.MSpireProcessor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="mspire_processor",
            manager=self.task_manager,
            except_ws_status=['maica_core_streaming_continue', 'maica_chat_loop_finished']
        )
        self.MSpireProcessor._external_callback = self.general_chat_callback
        self.MPostalProcessor = maica_tasker_sub_sessionsender.MAICAMPostalProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="mpostal_processor",
            manager=self.task_manager,
            except_ws_status=['maica_core_nostream_reply', 'maica_chat_loop_finished']
        )
        self.MPostalProcessor._external_callback = self.mpostal_callback

        self.AutoReconnector = maica_tasker_sub.AutoReconnector(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="auto_reconnector",
            manager=self.task_manager
        )
        self.AutoReconnector.set_reconnect_func(self.init_connect)
        self.AutoReconnector._reconnect_delay = 0.5

        self.AutoResumeTasker = maica_tasker_sub.AutoResumeTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="auto_resume_tasker",
            manager=self.task_manager,
        )
        self.AutoResumeTasker.set_should_resume_func(self._should_resume())

        self.KeepAliveTasker = maica_tasker_sub.KeepWsAliveTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="keep_ws_alive",
            manager=self.task_manager,
            ping_interval=150.0
        )

        self.StreamingPacketValidator = maica_tasker_sub.StreamingPacketValidator(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="streaming_packet_validator",
            manager=self.task_manager,
            except_ws_status=['maica_core_streaming_continue', 'maica_core_complete']
        )

    def _should_resume(self):
        return len(self.TalkSpilter.sentence_present) or len(self.message_list)

    @property
    def user_acc(self):
        return self.UserData.account

    @property
    def gen_time(self):
        return maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.occupied_time

    @property
    def enable_strict_mode(self):
        return self._enable_strict_mode

    @enable_strict_mode.setter
    def enable_strict_mode(self, value):
        if value:
            self.WSCookiesTask.enable_cookie()
        else:
            self.WSCookiesTask.disable_cookie()
        self._enable_strict_mode = value

    @property
    def auto_reconnect(self):
        return self._auto_reconnect

    @auto_reconnect.setter
    def auto_reconnect(self, value):
    #    if value:
    #        self.AutoReconnector.enable()
    #    else:
    #        self.AutoReconnector.disable()
        self._auto_reconnect = value

    @property
    def auto_resume(self):
        return self._auto_resume

    @auto_resume.setter
    def auto_resume(self, value):
    #    if self._auto_resume:
    #        self.AutoResumeTasker.enable()
    #    else:
    #        self.AutoResumeTasker.disable()
        self._auto_resume = value

    @property
    def keep_alive(self):
        return self._keep_alive

    @keep_alive.setter
    def keep_alive(self, value):
        self._keep_alive = bool(value)
    #    if self._keep_alive:
    #        self.KeepAliveTasker.enable()
    #    else:
    #        self.KeepAliveTasker.disable()

    @property
    def provider_id(self):
        return self.provider_manager.get_provider_id()

    @provider_id.setter
    def provider_id(self, value):
        self.provider_manager.set_provider_id(value)

    def reset_stat(self):
        self.stat = {
            "message_count":0,
            "received_token":0,
            "mspire_count":0,
            "received_token_by_session":[0] * (self.MAX_CHATSESSION+1),
            "mpostal_count":0
        }
    def send_to_outside_func(self, content):
        content = key_replace(content, bot_interface.renpy_symbol_percentage)
        content = u"{}".format(content)
        import unicodedata
        if self.content_func is None:
            return
        max_len = 33 * 2
        content = content.replace("\"", "").replace("'", "")
        l = content.split("\n")
        def calculate_length(s):
            
            length = 0
            for char in s:
                # 使用unicodedata模块判断字符宽度
                if unicodedata.east_asian_width(char) in ('F', 'W'):
                    length += 2
                else:
                    length += 1
            return length

        def split_string(s, max_len):
            result = []
            current_str = ""
            current_len = 0

            for char in s:
                char_len = 2 if unicodedata.east_asian_width(char) in ('F', 'W') else 1

                if current_len + char_len > max_len:
                    result.append(current_str)
                    current_str = char
                    current_len = char_len
                else:
                    current_str += char
                    current_len += char_len

            if current_str:
                result.append(current_str)

            return result
        def process_lines(l, max_len):
            processed_list = []
            for line in l:
                if calculate_length(line) > max_len:
                    processed_list.extend(split_string(line, max_len))
                else:
                    processed_list.append(line)
            return processed_list
        for i in process_lines(l, max_len):
            if PY2:
                self.content_func(str(key_replace(i.replace("\n", ""), bot_interface.renpy_symbol)).decode())
            elif PY3:
                self.content_func(str(key_replace(i.replace("\n", ""), bot_interface.renpy_symbol)))

    def update_stat(self, new):
        self.stat.update(new)
    def generate_vista_url(self, uuid):
        return self.provider_manager.get_api_url() + "vista?content={}".format(uuid)

    def add_ana(self, ana_input):
        emote_talk_zipped = self.MoodStatus.analyze(ana_input)
        for index, pair in enumerate(emote_talk_zipped):
            self._append_to_message_list(*pair, extend=False if index == 0 else True)

    def get_message(self, add_pause = True):
        res = self.message_list.get()
        if len(self.message_list) < 1:
            talk = self.TalkSpilter.split_present_sentence()
            if talk:
                self.add_ana(talk)

        return (res[0], self.TalkSpilter.add_pauses(res[1]) if add_pause else res[1], res[2] if len(res) >= 3 else False)
    def _gen_token(self, account, pwd, token = "", email = None):
        if token != "":
            self.ciphertext = token
            return
        if not self.__accessable and token == "":
            return logger.error("_gen_token:Maica server not serving.")
        import requests
        data = {
            "username":account,
            "password":pwd
        }
        if email:
            data = {
            "email":email,
            "password":pwd
        }
        try:
            import json
            response = requests.get(self.provider_manager.get_api_url() + "register", params={"content":json.dumps(data)}, timeout=5)
            if (response.status_code != 200): 
                raise Exception("Maica::_gen_token response process failed because server return {}".format(response.status_code))
        except Exception as e:
            import traceback
            self.status = self.MaicaAiStatus.CONNECT_PROBLEM
            logger.error("Maica::_gen_token requests.post failed because can't connect to server: {}".format(e))
            return
        try:
            response_data = response.json()
            if response_data.get("success"):
                self.ciphertext = response_data.get("content")
            else:
                self.status = self.MaicaAiStatus.CONNECT_PROBLEM,
                logger.error("Maica::_gen_token response process failed because server response failed: {}".format(response_data))
        except Exception:
            self.status = self.MaicaAiStatus.CONNECT_PROBLEM
            logger.error("Maica::_gen_token response process failed because server return {}".format(response.status_code))
        return
    
    def has_token(self):
        return len(self.ciphertext) > 5

    def _verify_token(self):
        """
        验证token是否有效。
        
        Returns:
            bool: 验证结果。
        
        """
        import requests
        try:
            res = requests.get(self.provider_manager.get_api_url() + "legality", params={"access_token": self.ciphertext})
            try:
                res = res.json()
                if res.get("success", False):
                    return res
                else:
                    logger.warning("Maica::_verify_token not passed: {}".format(res))
                    return res
            except Exception:
                logger.error("Maica::_verify_token requests.post failed because can't connect to server: {}".format(res.text))
                return {"success":False, "exception": "Maica::_verify_token requests.post failed"}

        except Exception as e:
            import traceback
            logger.error("Maica::_verify_token requests.post failed because can't connect to server: {}".format(traceback.format_exc()))
            return {"success":False, "exception": "Maica::_verify_token failed"}

    def get_version(self):
        import requests
        import traceback

        try:
            res = requests.get(self.provider_manager.get_api_url() + "version")
            try:
                res_data = res.json()
                if res_data.get("success", False):
                    return res_data
                else:
                    logger.warning("Get version failed: {}".format(res_data))
                    return res_data
            except Exception:
                logger.error("Get version request failed: Server returned {} - {}".format(res.status_code, res.text))
                return {"success": False, "exception": "Get version request failed"}

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("Get version request encountered an error: {}".format(error_msg))
            return {"success": False, "exception": "Get version request failed"}

    def get_emotion(self, type, text):
        import requests
        import json
        import traceback

        try:
            res = requests.get(self.provider_manager.get_api_url() + "emotion",
                               params={
                                   "access_token": self.ciphertext,
                                   "content": json.dumps({
                                       "type": type,
                                       "text": text,
                                       "target_lang": self.target_lang
                                   })
                                }
                               )
            try:
                res_data = res.json()
                if res_data.get("success", False):
                    return res_data
                else:
                    logger.warning("Emotion analysis failed: {}".format(res_data))
                    return res_data
            except Exception:
                logger.error("Emotion analysis request failed: Server returned {} - {}".format(res.status_code, res.text))
                return {"success": False, "exception": "Emotion analysis request failed"}

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("Emotion analysis request encountered an error: {}".format(error_msg))
            return {"success": False, "exception": "Emotion analysis request failed"}

    def verify_legality(self, verification_object=None, verification_value=None):
        """
        进行在线执行验证。

        Args:
            verification_object (str, optional): 验证项目，目前只支持 "geolocation"。
            verification_value (str, optional): 待验证内容。

        Returns:
            dict: 验证结果。如果验证成功，返回包含验证信息的字典；
                  如果只验证令牌，返回用户名；
                  如果验证失败，返回包含错误信息的字典。

        Notes:
            - 如果不提供 content 参数，则只验证令牌合法性
            - 如果提供 content 参数，则还验证对应内容的合法性
            - 目前验证项目只支持 "geolocation"，用于查询地理位置是否规范可用
        """
        import requests
        import json
        import traceback

        if not self.__accessable:
            logger.error("verify_legality: Maica server not serving.")
            return {"success": False, "exception": "Maica server not serving"}

        if not self.ciphertext:
            logger.error("verify_legality: access_token is null")
            return {"success": False, "exception": "Access token is null"}

        try:
            # 构建请求参数
            params = {"access_token": self.ciphertext}

            # 如果提供了验证内容，添加到参数中
            if verification_object and verification_value:
                content = {
                    "object": verification_object,
                    "value": verification_value
                }
                params["content"] = json.dumps(content)

            res = requests.get(
                self.provider_manager.get_api_url() + "legality",
                params=params
            )

            try:
                res_data = res.json()
                if res_data.get("success", False):
                    logger.debug("Legality verification successful: {}".format(res_data))
                    return res_data
                else:
                    logger.warning("Legality verification failed: {}".format(res_data))
                    return res_data
            except Exception:
                logger.error("Legality verification request failed: Server returned {} - {}".format(res.status_code, res.text))
                return {"success": False, "exception": "Legality verification request failed"}

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("Legality verification request encountered an error: {}".format(error_msg))
            return {"success": False, "exception": "Legality verification request failed"}


    def init_connect(self):
        import threading
        threading.Thread(target=self._init_connect).start()
        
    def _init_ws_client(self):
        if self.task_manager.ws_client:
            if self.task_manager.ws_client.url == self.provider_manager.get_wssurl():
                return
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if self.multi_lock.locked():
            return logger.warning("Maica::_init_connect try to create multi connection")
        self.status = self.MaicaAiStatus.WEBSOCKET_CONNECTING
        self.multi_lock.acquire()
        import websocket
        url = self.provider_manager.get_wssurl()
        self.vista_manager.base_url = self.provider_manager.get_api_url()
        self.vista_manager.access_token = self.ciphertext
        logger.debug("_init_connect to {}".format(url))
        self.task_manager.ws_client = websocket.WebSocketApp(url, on_message=self.task_manager._ws_onmessage, on_error=self._on_error
                                                  , on_close=self._on_close)
        self.wss_session = self.task_manager.ws_client
        self.wss_session.ping_payload = "PING"
        self.WSConsoleLogger.ovr_welcomemessage = self.target_lang == self.MaicaAiLang.en
        return True

    def _init_connect(self):
        self._init_ws_client()
        self.Loginer.set_token(self.ciphertext)
        self.task_manager.reset_all_task()
        if self.auto_reconnect:
            self.AutoReconnector.enable()
        try:
            self.task_manager.ws_client.run_forever()
        except Exception as e:
            import traceback
            self.console_logger.error("wss_session.run_forever() failed: {}".format(e))
            logger.error("Maica::_init_connect wss_session.run_forever() failed: {}".format(traceback.format_exc()))
        finally:
            if self.multi_lock.locked():
                self.multi_lock.release()
                logger.info("Maica::_init_connect released lock because wss closed")
        
        
    def is_responding(self):
        """返回maica是否正在返回消息"""
        #return self.status in (self.MaicaAiStatus.MESSAGE_WAITING_RESPONSE, self.MaicaAiStatus.MESSAGE_WAIT_SEND, self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE, self.MaicaAiStatus.MESSAGE_WAIT_SEND_MPOSTAL)
        return maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.locked()

    def is_ready_to_input(self):
        """返回maica是否可以接受输入消息了"""
        #return self.status in (self.MaicaAiStatus.MESSAGE_WAIT_INPUT, self.MaicaAiStatus.SSL_FAILED_BUT_OKAY, self.MaicaAiStatus.MESSAGE_DONE) and self.is_connected()
        return not maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.locked() and self.Loginer.success

    def is_accessable(self):
        """返回maica是否可用"""
        return self.__accessable

    
    def is_failed(self):
        """返回maica是否处于异常状态"""
        return self.task_manager.is_task_failed()\
            or not self.is_connected()

    def is_in_exception(self):
        return self.task_manager.is_task_failed()

    def is_connected(self):
        """返回maica是否连接服务器, 不检查状态码"""
        return self.task_manager.ws_client.keep_running if self.task_manager.ws_client else False #\
            #or self.wss_thread.is_alive() if self.wss_thread else False

    def get_status_description(self):
        """返回maica当前状态描述"""
        return self.MaicaAiStatus.get_description(self.status)

    def len_message_queue(self):
        """返回maica已接收并完成分句的台词数"""
        return self.message_list.size()
    
    def start_MSpire(self):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.stat['mspire_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE
        self.MSpireProcessor.start_request(
            category=self.mspire_category,
            session=self.mspire_session,
            pprt=self.pprt,
            flush=self.chat_session != self.mspire_session # Leave the zero detection to later procedure
        )
        self._in_mspire = True
    
    def start_MPostal(self, content, title="", visions=None):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.stat['mpostal_count'] += 1
        self.MPostalProcessor.start_request(
            query = {
                "header": title,
                "content": key_replace(content, chinese_to_english_punctuation),
                "bypass_mt": True,
                "bypass_mf": False
            },
            visions=visions
        )
    _pos = 0
    def build_setting_config(self):
        data = {
            "type": "params",
            "chat_params": {}
        }
        data["chat_params"].update({"enable_mf": self.enable_mf, "enable_mt": self.enable_mt, "sf_extraction":self.sf_extraction, "mt_extraction":True, "stream_output":self.stream_output, "target_lang":self.target_lang, "max_length":self.max_history_token, "tz": self.tz, "dscl_pvn":self.dscl_pvn})
        data['chat_params'].update(self.modelconfig)
        if self.enable_strict_mode and self.__ws_cookie != "":
            data['cookie'] = self.__ws_cookie
        return data

    def send_settings(self):
        self.send_mtrigger()
        import json
        data = self.build_setting_config()
        if self.is_connected() and self.Loginer.success:
            logger.debug("send_settings: {}".format(json.dumps(self.build_setting_config())))
            self.SettingSender.start_event(
                self.build_setting_config()
            )
            return data
        else:
            logger.warning("You should connected to send settings")
            return {}
    def _on_message(self, wsapp, message):
        try:
            self.task_manager._ws_onmessage(wsapp, message)
        except Exception as e:
            import traceback
            self.console_logger.debug("!!SUBMOD ERROR when on_message: {}".format(e))
            logger.error("exception is ocurrred: \n{}".format(traceback.format_exc()))
            logger.error("when processing context: {}".format(message))
    def general_chat_callback(self, processor, event):
        if event.data.status == "maica_core_streaming_continue":
            self.stat["received_token"] += 1
            self.stat["received_token_by_session"][self.chat_session if not self._in_mspire else self.mspire_session] += 1
            if self.pprt:
                self.add_ana(event.data.content)
            else:
                self.TalkSpilter.add_part(event.data.content)
                if len(self.message_list) == 0:
                    res = self.TalkSpilter.split_present_sentence()
                    if res:
                        self.add_ana(res)

        elif event.data.status == "maica_chat_loop_finished":
            self._in_mspire = False
            if self.pprt:
                talks = []
            else:
                talks = self.TalkSpilter.announce_stop()
            for item in talks:
                self.add_ana(item)
            self.status = self.MaicaAiStatus.MESSAGE_DONE
            self.MoodStatus.reset()
            # 释放聊天锁，允许下一个聊天请求
            processor.reset()
    
    def mpostal_callback(self, processor, event):
        if event.data.status == "maica_core_nostream_reply":
            message = ''.join([i[1] for i in self.MoodStatus.analyze(event.data.content)])
            if len(message) > 0 and message[0] == " ":
                message = message[1:]
            message_step1 = key_replace(str(message), bot_interface.renpy_symbol_big_bracket_only, bot_interface.renpy_symbol_percentage)
            self.message_list.put(('1eua', message_step1))
        elif event.data.status == "maica_chat_loop_finished":
            processor.reset()

    def _on_error(self, wsapp, error):
        self.task_manager._ws_onerror(wsapp, error)
        self.task_manager.ws_client.close()

    def _on_close(self, wsapp, close_status_code=None, close_msg=None):
        logger.debug("MaicaAi::_on_close {}|{}".format(close_status_code, close_msg))
        self.__ws_cookie = ""
        if self.multi_lock.locked():
            self.multi_lock.release()
        self.task_manager.ws_client.close()
        self.task_manager._ws_onclose(wsapp, close_status_code, close_msg)

        
    def chat(self, message, visions = None, session=None):
        from maica_mtrigger import MTriggerMethod
        if not self.__accessable:
            return logger.error("Maica is not serving")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        message = str(message)
        self.ChatProcessor.start_request(
            query=message,
            session = session if session == None else self.chat_session,
            trigger = self.mtrigger_manager.build_data(MTriggerMethod.request),
            taskowner = self.task_manager,
            visions = visions,
            pprt = self.pprt
        )
        self.stat['message_count'] += 1

    def _append_to_message_list(self, emote, message, extend=False):
        if len(message) == 0:
            return
        elif message[0] == " ":
            message = message[1:]
        message_step1 = key_replace(str(message), bot_interface.renpy_symbol_big_bracket_only, bot_interface.renpy_symbol_percentage, bot_interface.renpy_symbol_enter)
        self.message_list.put((emote, message_step1, extend))
    def upload_save(self, dict):
        """
        向Maica服务上传并保存存档数据。
        
        Args:
            dict (dict): 要上传的数据，必须为字典类型。
            session (int, optional): 会话ID。默认为1。
        
        Returns:
            dict: 如果上传成功，则返回Maica服务返回的JSON响应；否则返回空字典。
        
        """

        if not self.__accessable:
            logger.error("upload_save::Maica is not serving")
            return {}
        if self.ciphertext in ("", None):
            logger.error("upload_save:: token is null")
            return {}
        import requests, json
        content = {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "content": dict
                }
        res = requests.post(
            self.provider_manager.get_api_url() + "savefile",
            json = content,
            headers = {"Content-Type": "application/json"}
        )
        try:
            return res.json()
        except Exception:
            logger.error("upload_save:: return non json:: {}".format(res.text))
            return {}

    def get_history(self, lines = 0):
        """
        获取与Maica的历史聊天记录
        
        Args:
            lines (int, optional): 需要获取的聊天记录条数
                当lines为正整数n时, 接口只返回对话历史的前n项, 应注意其中第一项为最后一次生效的system字段.
                当lines为负整数-n时, 接口只返回对话历史的后n项, 此时返回的对话历史仍然以正序排列.
                当lines为0时, 接口返回全部对话历史--可能会很长.
        
        Returns:
            dict: 包含历史聊天记录的字典。
        
        Raises:
            无
        
        """
        
        if not self.__accessable:
            return logger.error("Maica is not serving")
        import requests, json
        res = requests.get(
            self.provider_manager.get_api_url() + "history",
            params =
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "content": lines
                }
        )

        try:
            return res.json()
        except Exception as e:
            logger.error("get_history:: {}".format(e))
            return []

    def upload_history(self, history):
        """
        将历史记录上传到Maica服务器
        
        Args:
            history (dict): 
        
        Returns:
            dict: Maica服务器返回的JSON响应
        
        """

        if not self.__accessable:
            logger.error("Maica is not serving")
            return {}
        if self.ciphertext in ("", None):
            logger.error("upload_history:: token is null")
            return {}
        import requests, json
        content = {
            "access_token": self.ciphertext,
            "chat_session": self.chat_session,
            "content": history
        }
        res = requests.put(
            self.provider_manager.get_api_url() + "history",
            json = content,
            headers = {"Content-Type": "application/json"}
        )
        try:
            return res.json()
        except Exception:
            logger.error("upload_history:: return non json:: {}".format(res.text))
            return {}
        
    def reset_chat_session(self):
        """
        重置当前聊天会话。
        
        Args:
            无。
        
        Returns:
            无返回值。
        
        Raises:
            无。
        
        """

        if not self.__accessable:
            return logger.error("Maica is not serving")
        import json
        self.SessionReseter.start_event(chat_session = self.chat_session)
        self.message_list.clear()
        self.stat["received_token_by_session"][self.chat_session] = 0
        self.HistoryStatus.reset()

    def update_workload(self):
        """
        更新工作负载信息（后台执行）。

        Args:
            无。

        Returns:
            threading.Thread对象，可以用于检查线程的状态。
        """
        import requests
        import threading
        if not self.__accessable:
            logger.error("Maica is not serving")
            return None

        def task():
            res = requests.get(self.provider_manager.get_api_url() + "workload")
            try:
                data = res.json()
                if data["success"]:
                    self.workload_raw = data["content"]
                    #logger.debug("Workload updated successfully.")
                else:
                    logger.error("Failed to update workload: {}".format(data))
            except Exception:
                logger.error("Failed to update workload.")

        thread = threading.Thread(target=task)
        thread.daemon = True  # Optional: allow the program to exit even if the thread is running
        thread.start()
        return thread

    def get_workload_lite(self):
        """
        获取最高负载设备的占用

        Args:
            无。

        Returns:
            工作负载信息简化版。

        """

        data = {
            "avg_usage": 0,
            "max_usage": 0,
            "total_vmem": 0,
            "total_inuse_vmem": 0,
            "total_w": 0,
            "mem_pencent":0,
            "max_tflops":0,
            "cur_tflops":0,
            "onliners":0
        }
        if not self.__accessable:
            return data
    # Use iteritems() for Python 2
        avgcount = 0
        if PY2:
            # 处理 onliners 键
            if isinstance(self.workload_raw.get('onliners'), (int, float)):
                data['onliners'] = int(self.workload_raw['onliners'])

            for group_name, group in self.workload_raw.iteritems():
                if group_name == 'onliners':
                    continue
                for card in group.itervalues():
                    if card["mean_utilization"] > data["max_usage"]:
                        data["max_usage"] = card["mean_utilization"]
                    data["avg_usage"] += card["mean_utilization"]
                    avgcount+=1
                    data["total_vmem"] += int(card["vram"][:-4].strip())
                    data["total_inuse_vmem"] += card["mean_memory"]
                    data["total_w"] += card["mean_consumption"]
                    data["max_tflops"] += int(card["tflops"])
                    data["cur_tflops"] += int(card["tflops"]) * card["mean_utilization"] * 0.01
        elif PY3:
            # 处理 onliners 键
            if isinstance(self.workload_raw.get('onliners'), (int, float)):
                data['onliners'] = int(self.workload_raw['onliners'])

            for group_name, group in self.workload_raw.items():
                if group_name == 'onliners':
                    continue
                for card in group.values():
                    if card["mean_utilization"] > data["max_usage"]:
                        data["max_usage"] = card["mean_utilization"]
                    data["avg_usage"] += card["mean_utilization"]
                    avgcount+=1
                    data["total_vmem"] += int(card["vram"][:-4].strip())
                    data["total_inuse_vmem"] += card["mean_memory"]
                    data["total_w"] += card["mean_consumption"]
                    data["max_tflops"] += int(card["tflops"])
                    data["cur_tflops"] += int(card["tflops"]) * card["mean_utilization"] * 0.01

        if avgcount > 0:
            data["avg_usage"] /= avgcount
        return data

    

    def close_wss_session(self):
        """
        关闭WebSocket会话。这会自动关闭自动重连。

        Args:
            无参数。

        Returns:
            无返回值。

        """
        self.AutoReconnector.disable()
        if self.task_manager.ws_client:
            self.task_manager.close_ws()
    def del_mtrigger(self):
        import requests
        requests.delete(self.provider_manager.get_api_url()+"trigger", json={"access_token": self.ciphertext, "chat_session": self.chat_session}, headers={'Content-Type': 'application/json'})

    def send_mtrigger(self):
        try:
            import time
            if not self.__accessable:
                logger.error("Maica is not serving")
                return
            if self.ciphertext in ("", None):
                logger.error("send_mtrigger:: token is null")
                return
            
            from maica_mtrigger import MTriggerMethod
            import requests
            content = {
                "access_token": self.ciphertext,
                "chat_session": self.chat_session,
                "content": self.mtrigger_manager.build_data(MTriggerMethod.table)
            }
            #requests.delete(self.provider_manager.get_api_url()+"trigger", json={"access_token": self.ciphertext, "chat_session": self.chat_session})
            res = requests.post(
                self.provider_manager.get_api_url() + "trigger",
                json = content,
                headers = {"Content-Type": "application/json"}
            )
            
            try:
                response_data = res.json()
                if response_data.get('success', False):
                    logger.debug("send_mtrigger success")
                else:
                    logger.error("send_mtrigger failed: {}".format(response_data))
            except Exception:
                logger.error("send_mtrigger:: return non json:: {}".format(res.text))

        except Exception as e:
            import traceback
            logger.error("send_mtrigger error: {}".format(traceback.format_exc()))



    def ping(self, host, port=80, timeout=2):
        """通过 TCP 连接检测主机可达性，成功返回 True，否则返回 False"""
        import socket
        try:
            socket.create_connection((host, port), timeout=timeout).close()
            return True
        except:
            return False

    def can_access_internet(self):
        """
        Check if either Baidu or Google is reachable.
        Returns True if at least one is reachable, False otherwise.
        """
        baidu_reachable = self.ping("www.baidu.com")
        google_reachable = self.ping("www.google.com")
        
        return baidu_reachable or google_reachable
    def accessable(self):
        """
        检查Maica服务是否可访问
        注意, 在开始使用前, 必须先使用该函数来检查MAICA服务器是否可用
        
        Args:
            无
        
        Returns:
            无返回值，该函数主要用于更新类的状态
        
        Raises:
            无
        """
        #self.__accessable = True
        #self.status = self.MaicaAiStatus.NOT_READY
        #return
        if not self.can_access_internet():
            self.status = self.MaicaAiStatus.NO_INTERTENT
            logger.error("accessable(): no internet connection")
            self.__accessable = False
            return
        if self.status == self.MaicaAiStatus.CERTIFI_AUTO_FIX:
            logger.error("accessable(): certifi auto fix, need restart")
            self.__accessable = False
            return
        try:
            if not self.provider_manager.get_provider():
                if self.provider_id != 9999:
                    self.status = self.MaicaAiStatus.FAILED_GET_NODE
                    self.__accessable = False
                    return

        except Exception as e:
            logger.error("accessable(): Maica get Service Provider Error: {}".format(e))
            if self.provider_id != 9999:
                self.status = self.MaicaAiStatus.FAILED_GET_NODE
                self.__accessable = False
                return

        if self.in_mas:
            try:
                import certifi
                certifi.set_parent_dir
            except AttributeError:
                logger.error("accessable(): certifi is broken")
                self.status = self.MaicaAiStatus.CERTIFI_BROKEN
                self.__accessable = False
                return
                
        import requests, json
        res = requests.get(self.provider_manager.get_api_url() + "accessibility")
        logger.debug("accessable(): try get accessibility from {}".format(self.provider_manager.get_api_url() + "accessibility"))
        d = res.json()
        if d.get(u"success", False):
            self._serving_status = d["content"]
            if self._serving_status != "serving" and not self._ignore_accessable:
                self.status = self.MaicaAiStatus.SERVER_MAINTAIN
                self.__accessable = False
                logger.error("accessable(): Maica is not serving: {}".format(d["content"]))
            else:
                self.__accessable = True
                self.status = self.MaicaAiStatus.NOT_READY
        else:
            self.status = self.MaicaAiStatus.SERVER_MAINTAIN
            self.__accessable = False
            logger.error("accessable(): Maica is not serving: request failed: {}".format(d))
        
        # 写下版本检测
        # 后端返回示例：{"content":{"curr_version":"1.2.000.post3","fe_blessland_version":"1.5.0","legc_version":"1.2.000.rc10"},"exception":null,"success":true}
        if self.__accessable:
            version_info = self.get_version()
            self.version_info = version_info
            if version_info.get("success", False):
                legc_version = version_info.get("content", {}).get("legc_version", "")
                try:
                    from packaging import version
                    if version.parse(legc_version) > version.parse(self.SUPPORT_BACKEND):
                        self.status = self.MaicaAiStatus.VERSION_OLD
                        self.__accessable = False
                        logger.error("accessable(): Backend version {} is newer than supported version {}".format(legc_version, self.SUPPORT_BACKEND))
                        return
                except:
                    pass
            try:
                res = requests.get(self.provider_manager.get_api_url() + "defaults").json()["content"]
                if type(res) == dict:
                    self.default_setting.update(res)
            except Exception as e:
                logger.error("accessable(): Maica get default setting error: {}".format(e))
        


    def disable(self):
        self.__accessable = False



            

        


