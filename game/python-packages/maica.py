# -*- coding: utf-8 -*-

from bot_interface import *
import bot_interface
import emotion_analyze_v2
import maica_tasker, maica_tasker_sub, maica_tasker_sub_sessionsender, maica_vista_files_manager, maica_context_query
import maica_provider_manager

# Import LoggerManager for injection point registration
from logger_manager import get_logger_manager, MultiLoggerWrapper

import websocket
import maica_mtrigger
import maica_v13_migration
import os
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

MAX_SESSION_LEN_LIMIT = 28672


def savefile_access_marker_exists():
    marker_root = globals().get("basedir")
    return bool(
        marker_root
        and os.path.isfile(os.path.join(marker_root, "savefile_access"))
    )


def normalize_chat_params(params):
    normalized = dict(params or {})
    for legacy_key in maica_v13_migration.SETTING_RENAMES:
        normalized.pop(legacy_key, None)
    normalized.pop("mt_extraction", None)
    maica_v13_migration.remove_retired_persistent_settings(normalized)
    maica_v13_migration.normalize_tristate_values(
        normalized,
        fill_missing=False,
    )
    if normalized.get("mf_const_tools") == 3:
        normalized["mf_const_tools"] = 2
    if normalized.get("mf_const_tools", 0) > 2:
        normalized["mf_const_tools"] = 2
    if normalized.get("session_len_limit", 0) > MAX_SESSION_LEN_LIMIT:
        normalized["session_len_limit"] = MAX_SESSION_LEN_LIMIT
    return normalized

def seconds_to_hms(timestamp_ms):
    # 将毫秒转换为秒
    timestamp_s = timestamp_ms
    # 获取系统本地时区
    dt = datetime.datetime.fromtimestamp(timestamp_s)
    return dt.strftime("%H:%M:%S")

class MaicaAi(ChatBotInterface):
    SUPPORT_BACKEND = "1.3.000"
    HTTP_TIMEOUT = (5.0, 30.0)
    CONNECTION_TIMEOUT = 30.0
    RESPONSE_TIMEOUT = 300.0
    ascii_icon = """                                                             

    __  ___ ___     ____ ______ ___ 
   /  |/  //   |   /  _// ____//   |
  / /|_/ // /| |   / / / /    / /| |
 / /  / // ___ | _/ / / /___ / ___ |
/_/  /_//_/  |_|/___/ \____//_/  |_| v
                                    
"""
    class MaicaAiLang:
        auto = "auto"
        zh_cn = "zh"
        en = "en"
    class MaicaMSpiretype:
        precise_page = "precise_page"
        fuzzy_page = "fuzzy_page"
        in_precise_category = "in_precise_category"
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
        # 等待可用性验证
        WAIT_AVAILABILITY = 10010
        #############################Submod 错误状态码
        TOKEN_MISSING = 13400
        TOKEN_CORRUPTED = 13401
        TOKEN_INVALID = 13402
        LOGIN_BLOCKED = 13403
        ACCOUNT_BANNED = 13404
        EMAIL_UNVERIFIED = 13405
        TOS_UNACCEPTED = 13406
        CONNECTION_REUSE_DENIED = 13407
        SERVER_REJECTED = 13408
        SERVER_ERROR = 13409
        TOKEN_GENERATION_FAILED = 13410
        CONNECT_PROBLEM = 13411
        RESPONSE_INVALID = 13412
        SERVER_MAINTAIN = 13413
        CERTIFI_BROKEN = 13414
        FAILED_GET_NODE = 13415
        VERSION_OLD = 13416
        NO_INTERNET = 13417
        ######################### MAICA 服务器状态码
        MAIKA_PREFIX = 5000
        @classmethod
        def is_1xx(cls, code):
            return 100 <= int(code) - cls.MAIKA_PREFIX <= 199

        @classmethod
        def is_submod_exception(cls, code):
            try:
                return 13400 <= int(code) <= 13499
            except (TypeError, ValueError):
                return False

        _protocol_error_map = {
            "maica_login_token_corrupted": TOKEN_CORRUPTED,
            "maica_login_token_invalid": TOKEN_INVALID,
            "maica_login_f2b": LOGIN_BLOCKED,
            "maica_login_banned": ACCOUNT_BANNED,
            "maica_login_email_unchecked": EMAIL_UNVERIFIED,
            "maica_login_tos_unaccepted": TOS_UNACCEPTED,
            "maica_connection_reuse_denied": CONNECTION_REUSE_DENIED,
            "maica_unified_warning": SERVER_REJECTED,
            "maica_unified_error": SERVER_ERROR,
            "client_token_generation_failed": TOKEN_GENERATION_FAILED,
            "client_server_unavailable": SERVER_MAINTAIN,
            "client_availability_failed": CONNECT_PROBLEM,
            "client_network_error": CONNECT_PROBLEM,
            "client_response_timeout": CONNECT_PROBLEM,
            "client_response_invalid": RESPONSE_INVALID,
            "client_auth_failed": TOKEN_INVALID,
        }

        @classmethod
        def from_protocol_status(cls, status, fallback=None):
            return cls._protocol_error_map.get(
                status,
                cls.SERVER_REJECTED if fallback is None else fallback,
            )
        
        # session 已超过 32768token
        TOKEN_MAX_EXCEEDED = MAIKA_PREFIX + 204
        # session > 24000token
        TOKEN_WARN_EXCEEDED = MAIKA_PREFIX + 200

        _descriptions = {
            NOT_READY: u"Waiting for account configuration",
            WAIT_AVAILABILITY:u"Core is not initialized. If the problem persists, check mas.log",
            WAIT_AUTH: u"Account details received, validating",
            WAIT_SERVER_TOKEN: u"Waiting for token validation",
            WAIT_USE_TOKEN: u"Waiting for token",
            SESSION_CREATED: u"Session started, waiting for model selection",
            WAIT_MODEL_INFOMATION: u"Waiting for model information",
            MESSAGE_WAIT_INPUT: u"MAICA is ready to receive queries",
            SSL_FAILED_BUT_OKAY: u"MAICA is falling back to a normal connection. This can usually be considered normal",
            MESSAGE_WAIT_SEND: u"Message received, waiting to send",
            MESSAGE_WAITING_RESPONSE: u"Message sent, waiting for the server response",
            MESSAGE_WAIT_SEND_MSPIRE: u"Waiting to send MSpire request",
            MESSAGE_WAIT_SEND_MPOSTAL: u"Waiting to send MPostal request",
            MESSAGE_DONE: u"MAICA streaming transfer has ended",
            REQUEST_RESET_SESSION: u"Requesting session reset",
            SESSION_RESETED: u"Session reset, connection closed",
            REQUEST_PING: u"Sending PING",
            TOKEN_MISSING: u"No token is configured",
            TOKEN_CORRUPTED: u"The token is corrupted",
            TOKEN_INVALID: u"The account or password is invalid",
            LOGIN_BLOCKED: u"Login is temporarily blocked",
            ACCOUNT_BANNED: u"The account is suspended",
            EMAIL_UNVERIFIED: u"The account email is not verified",
            TOS_UNACCEPTED: u"The latest terms are not accepted",
            CONNECTION_REUSE_DENIED: u"The account already has an active connection",
            SERVER_REJECTED: u"An user level exception happened",
            SERVER_ERROR: u"An server level exception happened",
            TOKEN_GENERATION_FAILED: u"Token generation failed",
            CONNECT_PROBLEM: u"Unable to connect to the server",
            RESPONSE_INVALID: u"The server returned an invalid response",
            TOKEN_MAX_EXCEEDED:u"Session length has exceeded limit; part of the conversation truncated",
            TOKEN_WARN_EXCEEDED:u"Session length is approaching limit and will be truncated once exceeded",
            SERVER_MAINTAIN:u"The server is unavailable or under maintenance",
            CERTIFI_BROKEN:u"SSL/TLS support is not working correctly",
            SEND_SETTING:u"Uploading settings",
            FAILED_GET_NODE:u"Failed to retrieve an available service provider",
            WEBSOCKET_CONNECTING:u"WebSocket is connecting (this should finish quickly)",
            VERSION_OLD:u"The submod version is outdated",
            NO_INTERNET:u"No internet connection is available"
        }

        @classmethod
        def get_description(cls, code):
            return cls._descriptions.get(code, u"Unknown status code: {}".format(code))
            
        
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
        self.version_info = {"success": False, "content": {}}
        self.stat = {}
        self.multi_lock = threading.Lock()
        self.MoodStatus = emotion_analyze_v2.EmoSelector(None, None, None)
        self.public_key = None
        self.ciphertext = None
        self.error_protocol_status = None
        self.error_message = None
        self.error_protocol_code = None
        self.chat_session = 1
        self.wss_session = None
        self.wss_thread = None
        self._intentional_ws_closes = set()
        self.enable_mf = True
        self.enable_mt = True
        self.savefile_access = True
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
        self.mspire_weight = 10
        self.mspire_type = self.MaicaMSpiretype.in_fuzzy_all
        self.pprt=False
        self.in_mas = True
        self.provider_manager = maica_provider_manager.MaicaProviderManager()
        self.is_outdated = None
        self.max_history_token = 8192
        self._in_mspire = False
        self.mspire_use_cache = False
        self.mtrigger_manager = maica_mtrigger.MTriggerManager()
        self.tz = "Asia/Shanghai"
        self.gen_quality_chk = False
        self.default_setting = {
            "deformation": False,
            "enable_mf": True,
            "enable_mt": True,
            "esearch_llm_concl": True,
            "frequency_penalty": 0.44,
            "gen_enforce_lang": True,
            "gen_quality_chk": True,
            "max_tokens": 1600,
            "mf_const_sf_access": 0,
            "mf_const_tools": 1,
            "mf_context_rnds": 1,
            "mf_disable_loop": True,
            "mf_llm_concl": False,
            "mf_precheck_mt": True,
            "mf_sf_access_impl": 1,
            "memory_concl_arc": 1,
            "mt_context_rnds": 1,
            "mt_disable_loop": True,
            "nsfw_acceptive": True,
            "presence_penalty": 0.34,
            "prompt_allow_nickname": True,
            "prompt_pname_repl": False,
            "savefile_access": True,
            "seed": None,
            "session_len_limit": 8192,
            "stream_output": True,
            "target_lang": "zh",
            "temperature": 0.22,
            "top_p": 0.7,
            "tz": None,
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

        self.WsErrorHandler = maica_tasker_sub.GeneralWsErrorHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="general_ws_error_handler",
            manager=self.task_manager,
            except_ws_status=[]
        )
        self.WsErrorHandler.set_error_callback(self._handle_ws_failure)
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
            except_ws_status=['maica_loop_warn_reset']
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
            except_ws_status=['maica_mtrigger_trigger']
        )
        self.MTriggerTasker.set_trigger_function(self.mtrigger_manager.triggered)

        self.QualityStatusTasker = maica_tasker_sub.QualityStatusWsHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="quality_status_ws_handler",
            manager=self.task_manager,
            except_ws_status=['maica_quality_status']
        )

        self.Loginer = maica_tasker_sub.MAICALoginTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="login_task",
            manager=self.task_manager,
            except_ws_status=(
                ['maica_connection_established', 'maica_connection_initiated']
                + list(maica_tasker_sub.MAICALoginTasker.LOGIN_FAILURE_STATUSES)
                + list(maica_tasker_sub.MAICALoginTasker.PREAUTH_FAILURE_STATUSES)
            )
        )
        self.Loginer.set_result_callback(self._handle_login_result)

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
            except_ws_status=['maica_core_streaming_continue', 'maica_chat_loop_finished']
        )
        self.MPostalProcessor._external_callback = self.mpostal_callback
        self.RawContextProcessor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="raw_context_processor",
            manager=self.task_manager,
            except_ws_status=['maica_core_streaming_continue', 'maica_chat_loop_finished']
        )
        self.RawContextProcessor._external_callback = self.general_chat_callback
        for processor in (
            self.ChatProcessor,
            self.MSpireProcessor,
            self.MPostalProcessor,
            self.RawContextProcessor,
        ):
            processor.set_timeout_callback(self._handle_response_timeout)

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
            except_ws_status=['maica_mcore_gen_start', 'maica_chat_loop_finished'],
        )

        self.KeepAliveTasker = maica_tasker_sub.KeepWsAliveTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="keep_ws_alive",
            manager=self.task_manager,
            ping_interval=150.0
        )

    @property
    def user_acc(self):
        return self.UserData.account

    @property
    def gen_time(self):
        return maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.occupied_time

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
        self.vista_manager.base_url = self.provider_manager.get_api_url()

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
        return self.provider_manager.get_api_url() + "/vista?content={}".format(uuid)

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
        try:
            if type(res[1]) == ellipsis:
                res[1] = "..."
            if type(res[1]) in (int, float):
                res[1] = str(res[1])
        except Exception:
            pass
        return (res[0], self.TalkSpilter.add_pauses(res[1]) if add_pause else res[1], res[2] if len(res) >= 3 else False)

    def clear_error(self, status=None):
        """Clear protocol failure details and move to a non-error status."""
        self.error_protocol_status = None
        self.error_message = None
        self.error_protocol_code = None
        if status is not None:
            self.status = status
        elif self.MaicaAiStatus.is_submod_exception(getattr(self, "status", None)):
            self.status = self.MaicaAiStatus.NOT_READY

    def set_error(self, status, message=None, code=None, fallback=None):
        self.error_protocol_status = status
        self.error_message = message
        self.error_protocol_code = code
        self.status = self.MaicaAiStatus.from_protocol_status(status, fallback)

    def _handle_login_result(self, success, status=None, message=None, code=None):
        if success:
            self.clear_error()
            self.status = self.MaicaAiStatus.MESSAGE_WAIT_INPUT
        else:
            self.set_error(status, message, code, self.MaicaAiStatus.TOKEN_INVALID)

    def _handle_ws_failure(self, status, message=None, code=None):
        login_failures = (
            self.Loginer.LOGIN_FAILURE_STATUSES + self.Loginer.PREAUTH_FAILURE_STATUSES
        )
        if not self.Loginer.success and status in login_failures:
            return False
        self.set_error(status, message, code, self.MaicaAiStatus.SERVER_ERROR)
        return True

    def _handle_response_timeout(self, processor_name, timeout):
        self.set_error(
            "client_response_timeout",
            "{} timed out after {:.1f} seconds".format(processor_name, timeout),
            fallback=self.MaicaAiStatus.CONNECT_PROBLEM,
        )

    def get_error_result(self):
        return {
            "success": False,
            "status": getattr(self, "error_protocol_status", None),
            "exception": getattr(self, "error_message", None),
            "code": getattr(self, "error_protocol_code", None),
        }

    def _preserve_or_set_availability_error(self, message):
        availability_failures = (
            self.MaicaAiStatus.SERVER_MAINTAIN,
            self.MaicaAiStatus.CERTIFI_BROKEN,
            self.MaicaAiStatus.FAILED_GET_NODE,
            self.MaicaAiStatus.VERSION_OLD,
            self.MaicaAiStatus.NO_INTERNET,
            self.MaicaAiStatus.CONNECT_PROBLEM,
        )
        if self.status not in availability_failures:
            self.set_error(
                "client_availability_failed",
                message,
                fallback=self.MaicaAiStatus.CONNECT_PROBLEM,
            )

    def _gen_token(self, account, pwd, token = "", email = None):
        if token != "":
            self.ciphertext = token
            self.clear_error()
            return
        if not self.__accessable and token == "":
            self._preserve_or_set_availability_error(
                "Maica server availability is unknown"
            )
            return logger.error("_gen_token: Maica server is not accessible.")
        self.ciphertext = ""
        self.clear_error()
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
            response = requests.post(
                self.provider_manager.get_api_url() + "/register",
                json={"content": data},
                timeout=self.HTTP_TIMEOUT,
            )
            response_data = response.json()
            if response.status_code != 200 or not response_data.get("success"):
                protocol_status, message = self._normalize_failure(
                    response_data,
                    "client_token_generation_failed",
                )
                self.set_error(protocol_status, message, response.status_code)
                logger.warning("Maica::_gen_token failed: {}".format(response_data))
                return
        except ValueError as e:
            self.set_error(
                "client_response_invalid",
                "Maica::_gen_token response was not valid JSON",
            )
            logger.error("Maica::_gen_token returned non-JSON response: {}".format(e))
            return
        except Exception as e:
            self.set_error("client_network_error", "Maica::_gen_token failed")
            logger.error("Maica::_gen_token requests.post failed because can't connect to server: {}".format(e))
            return
        self.ciphertext = response_data.get("content")
        if not self.ciphertext:
            self.set_error(
                "client_response_invalid",
                "Maica::_gen_token response did not contain a token",
            )
            return
        self.clear_error()
        return
    
    def has_token(self):
        return bool(self.ciphertext) and len(self.ciphertext) > 5

    @staticmethod
    def _normalize_failure(data, fallback_status):
        try:
            string_types = (basestring,)
        except NameError:
            string_types = (str,)
        if not isinstance(data, dict):
            data = {"exception": str(data)}
        exception = data.get("exception")
        status = data.get("status")
        if not status and isinstance(exception, string_types) and ":" in exception:
            candidate, message = exception.split(":", 1)
            if candidate.startswith("maica_"):
                status = candidate.strip()
                exception = message.strip()
        return status or fallback_status, exception

    def _verify_token(self):
        """
        验证token是否有效。
        
        Returns:
            bool: 验证结果。
        
        """
        import requests
        if getattr(self, "error_protocol_status", None) and not self.ciphertext:
            return self.get_error_result()
        if not self.has_token():
            self.set_error("client_token_missing", "Access token is not configured", fallback=self.MaicaAiStatus.TOKEN_MISSING)
            return self.get_error_result()
        try:
            res = requests.get(self.provider_manager.get_api_url() + "/legality", params={"access_token": self.ciphertext}, timeout=self.HTTP_TIMEOUT)
            try:
                result = res.json()
                if result.get("success", False):
                    self.clear_error()
                    return result
                else:
                    protocol_status, message = self._normalize_failure(result, "client_auth_failed")
                    self.set_error(protocol_status, message, getattr(res, "status_code", None))
                    result["status"] = protocol_status
                    result["exception"] = message
                    logger.warning("Maica::_verify_token not passed: {}".format(result))
                    return result
            except Exception:
                logger.error("Maica::_verify_token requests.post failed because can't connect to server: {}".format(res.text))
                self.set_error("client_response_invalid", "Maica::_verify_token response was not valid JSON")
                return self.get_error_result()

        except Exception as e:
            import traceback
            logger.error("Maica::_verify_token requests.post failed because can't connect to server: {}".format(traceback.format_exc()))
            self.set_error("client_network_error", "Maica::_verify_token failed")
            return self.get_error_result()

    def get_version(self):
        import requests
        import traceback

        try:
            res = requests.get(self.provider_manager.get_api_url() + "/version", timeout=self.HTTP_TIMEOUT)
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
        """Return the local emotion fallback for legacy callers."""
        return {
            "success": True,
            "content": [self.MoodStatus.fallback_selector.predict(), 0.0],
        }

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
                self.provider_manager.get_api_url() + "/legality",
                params=params,
                timeout=self.HTTP_TIMEOUT
            )

            try:
                res_data = res.json()
                if res_data.get("success", False):
                    content = res_data.get("content") or {}
                    if isinstance(content, dict):
                        latitude = content.get("latitude", content.get("lat"))
                        longitude = content.get("longitude", content.get("lng", content.get("lon")))
                        if latitude is not None and longitude is not None:
                            content["coordinate_text"] = "Latitude: {0}, Longitude: {1}".format(latitude, longitude)
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
        if not self.__accessable:
            self._preserve_or_set_availability_error(
                "Maica server availability is unknown"
            )
            return False
        if not self.has_token():
            self.set_error(
                "client_token_missing",
                "Access token is not configured",
                fallback=self.MaicaAiStatus.TOKEN_MISSING,
            )
            return False
        self.clear_error(self.MaicaAiStatus.WEBSOCKET_CONNECTING)
        self.wss_thread = threading.Thread(target=self._init_connect)
        self.wss_thread.daemon = True
        self.wss_thread.start()
        return True
        
    def _init_ws_client(self):
        if not self.__accessable:
            self._preserve_or_set_availability_error(
                "Maica server became unavailable before WebSocket initialization"
            )
            logger.error("Maica server is not accessible.")
            return False
        if not self.multi_lock.acquire(False):
            self.set_error(
                "client_connection_in_progress",
                "A connection attempt is already running",
                fallback=self.MaicaAiStatus.CONNECT_PROBLEM,
            )
            logger.warning("Maica::_init_connect try to create multi connection")
            return False
        try:
            self.status = self.MaicaAiStatus.WEBSOCKET_CONNECTING
            import websocket
            url = self.provider_manager.get_wssurl()
            self.vista_manager.base_url = self.provider_manager.get_api_url()
            self.vista_manager.access_token = self.ciphertext
            logger.debug("_init_connect to {}".format(url))
            if not self.task_manager.ws_client or self.task_manager.ws_client.url != url:
                self.task_manager.ws_client = websocket.WebSocketApp(
                    url,
                    on_message=self.task_manager._ws_onmessage,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
            self.wss_session = self.task_manager.ws_client
            self._intentional_ws_closes.discard(self.wss_session)
            self.wss_session.ping_payload = "PING"
            import renpy
            self.WSConsoleLogger.ui_lang_zh = renpy.config.language == "chinese"
            return True
        except Exception:
            import traceback
            self.set_error(
                "client_network_error",
                "Failed to initialize WebSocket client",
            )
            if self.multi_lock.locked():
                self.multi_lock.release()
            logger.error("Maica::_init_ws_client failed: {}".format(traceback.format_exc()))
            return False

    def _init_connect(self):
        import threading
        if not self._init_ws_client():
            return
        self.Loginer.set_token(self.ciphertext)
        self.task_manager.reset_all_task()
        if self.auto_reconnect:
            self.AutoReconnector.enable()
        ws_client = self.task_manager.ws_client
        def connection_timeout():
            if self.Loginer.success or self.task_manager.ws_client is not ws_client:
                return
            self.set_error(
                "client_network_error",
                "Connection timed out after {:.1f} seconds".format(self.CONNECTION_TIMEOUT),
            )
            logger.error(
                "Maica::_init_connect timed out after {:.1f} seconds".format(
                    self.CONNECTION_TIMEOUT
                )
            )
            try:
                self.task_manager.close_ws()
            except Exception as error:
                logger.error("Maica::_init_connect timeout close failed: {}".format(error))
        connection_timer = threading.Timer(self.CONNECTION_TIMEOUT, connection_timeout)
        connection_timer.daemon = True
        connection_timer.start()
        try:
            ws_client.run_forever()
        except Exception as e:
            import traceback
            self.set_error("client_network_error", "WebSocket connection failed")
            self.console_logger.error("wss_session.run_forever() failed: {}".format(e))
            logger.error("Maica::_init_connect wss_session.run_forever() failed: {}".format(traceback.format_exc()))
        finally:
            connection_timer.cancel()
            if not self.Loginer.success and not self.is_failed():
                self.set_error(
                    "client_network_error",
                    "WebSocket closed before authentication completed",
                )
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

    def is_connecting(self):
        return bool(
            not self.is_connected()
            and not self.is_failed()
            and self.wss_thread
            and self.wss_thread.is_alive()
        )

    def is_accessable(self):
        """返回maica是否可用"""
        return self.__accessable

    
    def is_failed(self):
        """返回maica是否处于异常状态"""
        if bool(
            self.MaicaAiStatus.is_submod_exception(self.status)
            or self.task_manager.is_task_failed()
            or self.response_timed_out()
        ):
            return True
        return bool(self.Loginer.success and not self.is_connected())

    def response_timed_out(self):
        return any(
            getattr(processor, "request_timed_out", False)
            for processor in (
                getattr(self, "ChatProcessor", None),
                getattr(self, "MSpireProcessor", None),
                getattr(self, "MPostalProcessor", None),
                getattr(self, "RawContextProcessor", None),
            )
            if processor is not None
        )

    def _clear_response_timeouts(self):
        for processor in (
            getattr(self, "ChatProcessor", None),
            getattr(self, "MSpireProcessor", None),
            getattr(self, "MPostalProcessor", None),
            getattr(self, "RawContextProcessor", None),
        ):
            if processor is not None and hasattr(processor, "_request_timed_out"):
                processor._request_timed_out = False

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
    
    def start_MSpire(self, ctg_weight=None):
        """启动 MSpire；分类权重默认为实例配置的 10。"""
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.QualityStatusTasker.clear()
        self._clear_response_timeouts()
        self.stat['mspire_count'] += 1
        self.status = self.MaicaAiStatus.MESSAGE_WAIT_SEND_MSPIRE
        self.mspire_type = maica_tasker_sub_sessionsender.normalize_mspire_type(
            getattr(self, "mspire_type", self.MaicaMSpiretype.in_fuzzy_all)
        )
        self.MSpireProcessor.start_request(
            category=self.mspire_category,
            session=self.mspire_session,
            pprt=self.pprt,
            ctg_weight=self.mspire_weight if ctg_weight is None else ctg_weight,
            use_cache=self.mspire_use_cache,
            mspire_type=self.mspire_type,
            flush=self.chat_session != self.mspire_session, # Leave the zero detection to later procedure
            core_input_mode=maica_tasker_sub_sessionsender.CORE_INPUT_STREAM,
            core_output_mode=maica_tasker_sub_sessionsender.CORE_OUTPUT_INCREMENTAL,
            request_timeout=self.RESPONSE_TIMEOUT
        )
        self._in_mspire = True
    
    def start_MPostal(self, content, title="", visions=None):
        if not self.__accessable:
            return logger.error("Maica server not serving.")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.QualityStatusTasker.clear()
        self._clear_response_timeouts()
        self.stat['mpostal_count'] += 1
        self.MPostalProcessor.start_request(
            query = {
                "header": title,
                "content": key_replace(content, chinese_to_english_punctuation),
                "bypass_mt": True,
                "bypass_mf": False
            },
            visions=visions,
            core_input_mode=maica_tasker_sub_sessionsender.CORE_INPUT_COMPLETE,
            core_output_mode=maica_tasker_sub_sessionsender.CORE_OUTPUT_COMPLETE,
            request_timeout=self.RESPONSE_TIMEOUT
        )
    _pos = 0
    def build_setting_config(self):
        data = {
            "type": "params",
            "chat_params": {},
            "reset": True,
        }
        data["chat_params"].update({
            "enable_mf": self.enable_mf,
            "enable_mt": self.enable_mt,
            "savefile_access": self.savefile_access,
            "stream_output": self.stream_output,
            "target_lang": self.target_lang,
            "session_len_limit": self.max_history_token,
            "tz": self.tz,
            "gen_quality_chk": self.gen_quality_chk,
        })
        data['chat_params'].update(
            maica_v13_migration.filter_advanced_settings(self.modelconfig)
        )
        data['chat_params'] = normalize_chat_params(data['chat_params'])
        data['chat_params']['savefile_access'] = bool(
            self.savefile_access and savefile_access_marker_exists()
        )
        return data

    def send_settings(self):
        self.send_mtrigger()
        import json
        data = self.build_setting_config()
        if self.is_connected() and self.Loginer.success:
            logger.debug("send_settings: {}".format(json.dumps(data)))
            self.SettingSender.start_event(data)
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
        core_output = processor.consume_core_output(event)
        if event.data.status == "maica_core_streaming_continue":
            for content in core_output:
                self.stat["received_token"] += 1
                self.stat["received_token_by_session"][self.chat_session if not self._in_mspire else self.mspire_session] += 1
                if self.pprt:
                    self.add_ana(content)
                else:
                    self.TalkSpilter.add_part(content)
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
        core_output = processor.consume_core_output(event)
        for content in core_output:
            message = ''.join([i[1] for i in self.MoodStatus.analyze(content)])
            if len(message) > 0 and message[0] == " ":
                message = message[1:]
            message_step1 = key_replace(str(message), bot_interface.renpy_symbol_big_bracket_only, bot_interface.renpy_symbol_percentage)
            self.message_list.put(('1eua', message_step1))
        if event.data.status == "maica_chat_loop_finished":
            processor.reset()

    def _on_error(self, wsapp, error):
        if not self.is_failed():
            self.set_error("client_network_error", u"{}".format(error))
        self.task_manager._ws_onerror(wsapp, error)
        if wsapp:
            wsapp.close()

    def _on_close(self, wsapp, close_status_code=None, close_msg=None):
        logger.debug("MaicaAi::_on_close {}|{}".format(close_status_code, close_msg))
        intentional_close = wsapp in self._intentional_ws_closes
        self._intentional_ws_closes.discard(wsapp)
        if (
            not intentional_close
            and self.Loginer.success
            and not self.MaicaAiStatus.is_submod_exception(self.status)
        ):
            self.set_error(
                "client_connection_closed",
                close_msg or "WebSocket connection closed unexpectedly",
                close_status_code,
                self.MaicaAiStatus.CONNECT_PROBLEM,
            )
        if wsapp:
            wsapp.close()
        self.task_manager._ws_onclose(wsapp, close_status_code, close_msg)

        
    def chat(self, message, visions = None, session=None):
        from maica_mtrigger import MTriggerMethod
        if not self.__accessable:
            return logger.error("Maica is not serving")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.QualityStatusTasker.clear()
        self._clear_response_timeouts()
        self.ChatProcessor.start_request(
            query=message,
            session = self.chat_session if session == None else session,
            triggers = self.mtrigger_manager.build_data(MTriggerMethod.request),
            taskowner = self.task_manager,
            visions = visions,
            pprt = self.pprt,
            core_input_mode=maica_tasker_sub_sessionsender.CORE_INPUT_STREAM,
            core_output_mode=maica_tasker_sub_sessionsender.CORE_OUTPUT_INCREMENTAL,
            request_timeout=self.RESPONSE_TIMEOUT
        )
        self.stat['message_count'] += 1

    def start_raw_context(self, query, visions=None):
        """
        启动 -1 session 原始上下文查询。

        实验性功能，允许用户自行管理对话上下文。

        Args:
            query (list): 消息列表，使用 MAICAContextQueryBuilder.build() 生成:
                [{"role": "system/user/assistant", "content": "..."}, ...]
            visions: 可选，图像数据 (TODO: 尚未实现, 保持此为None)
            pprt (bool): 是否启用自动断句和实时后处理

        Note:
            - 最多 10 条消息，紧凑 JSON 的 UTF-8 编码不超过 16 KiB
            - MFocus 不会介入 (无 trigger)
        """
        if not self.__accessable:
            return logger.error("Maica is not serving")
        if not self.is_ready_to_input():
            return logger.error("Maica is not ready to input")
        self.QualityStatusTasker.clear()
        self._clear_response_timeouts()
        self.RawContextProcessor.start_request(
            query=query,
            taskowner=self.task_manager,
            visions=visions,
            pprt=self.pprt,
            core_input_mode=maica_tasker_sub_sessionsender.CORE_INPUT_STREAM,
            core_output_mode=maica_tasker_sub_sessionsender.CORE_OUTPUT_INCREMENTAL,
            request_timeout=self.RESPONSE_TIMEOUT
        )
        self.stat['message_count'] += 1

    def consume_quality_statuses(self):
        """Return and clear quality results received for the current response."""
        return self.QualityStatusTasker.drain()

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

        if not savefile_access_marker_exists():
            logger.info("upload_save:: savefile_access marker is missing")
            return {
                "success": False,
                "exception": "savefile_access marker is missing"
            }
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
            self.provider_manager.get_api_url() + "/savefile",
            json = content,
            headers = {"Content-Type": "application/json"},
            timeout=self.HTTP_TIMEOUT
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
            self.provider_manager.get_api_url() + "/history",
            params =
                {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "content": lines
                },
            timeout=self.HTTP_TIMEOUT
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
            self.provider_manager.get_api_url() + "/history",
            json = content,
            headers = {"Content-Type": "application/json"},
            timeout=self.HTTP_TIMEOUT
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
            res = requests.get(self.provider_manager.get_api_url() + "/workload", timeout=self.HTTP_TIMEOUT)
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
            self._intentional_ws_closes.add(self.task_manager.ws_client)
            self.task_manager.close_ws()
        self.task_manager.reset_all_task()
        self.clear_error(self.MaicaAiStatus.NOT_READY)
    def del_mtrigger(self):
        import requests
        requests.delete(self.provider_manager.get_api_url()+"/trigger", json={"access_token": self.ciphertext, "chat_session": self.chat_session}, headers={'Content-Type': 'application/json'}, timeout=self.HTTP_TIMEOUT)

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
                self.provider_manager.get_api_url() + "/trigger",
                json = content,
                headers = {"Content-Type": "application/json"},
                timeout=self.HTTP_TIMEOUT
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
        baidu_reachable = self.ping("www.baidu.com", 80)
        google_reachable = self.ping("www.google.com", 80)
            
        return baidu_reachable or google_reachable
    
    def check_certifi(self):
        try:
            import certifi
            import os
            import ssl

            cert_path = certifi.where()
            if not cert_path or not os.path.isfile(cert_path):
                return False

            if not hasattr(ssl, "SSLContext"):
                return False
            protocol = getattr(
                ssl,
                "PROTOCOL_TLS_CLIENT",
                getattr(ssl, "PROTOCOL_TLS", ssl.PROTOCOL_SSLv23),
            )
            context = ssl.SSLContext(protocol)
            context.load_verify_locations(cafile=cert_path)
            return True
        except Exception as e:
            logger.error("check_certifi(): local CA bundle is unusable: {}".format(e))
            return False

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
        self.clear_error(self.MaicaAiStatus.WAIT_AVAILABILITY)

        #self.__accessable = True
        #self.status = self.MaicaAiStatus.NOT_READY
        #return

        # 检测证书是否是MAS版本/证书是否工作正常
        if self.in_mas:
            try:
                import certifi
                certifi.set_parent_dir
            except (ImportError, AttributeError):
                logger.error("accessable(): certifi is broken")
                self.set_error(
                    "client_certifi_broken",
                    "certifi is missing the MAS integration",
                    fallback=self.MaicaAiStatus.CERTIFI_BROKEN,
                )
                self.__accessable = False
                return
            if not self.check_certifi():
                self.set_error(
                    "client_certifi_broken",
                    "SSL/TLS certificate validation is unavailable",
                    fallback=self.MaicaAiStatus.CERTIFI_BROKEN,
                )
                self.__accessable = False
                return

        # 获取服务节点
        try:
            if not self.provider_manager.get_provider():
                if self.provider_id != 9999:
                    if self.can_access_internet():
                        self.set_error(
                            "client_provider_unavailable",
                            "Failed to retrieve a service provider",
                            fallback=self.MaicaAiStatus.FAILED_GET_NODE,
                        )
                    else:
                        self.set_error(
                            "client_no_internet",
                            "External network check failed",
                            fallback=self.MaicaAiStatus.NO_INTERNET,
                        )
                    self.__accessable = False
                    return

        except Exception as e:
            logger.error("accessable(): Maica get Service Provider Error: {}".format(e))
            if self.provider_id != 9999:
                if self.can_access_internet():
                    self.set_error(
                        "client_provider_unavailable",
                        u"{}".format(e),
                        fallback=self.MaicaAiStatus.FAILED_GET_NODE,
                    )
                else:
                    self.set_error(
                        "client_no_internet",
                        u"{}".format(e),
                        fallback=self.MaicaAiStatus.NO_INTERNET,
                    )
                self.__accessable = False
                return

        #获取节点可用性
        import requests, json
        accessibility_url = self.provider_manager.get_api_url() + "/accessibility"
        logger.debug("accessable(): try get accessibility from {}".format(accessibility_url))
        try:
            res = requests.get(accessibility_url, timeout=self.HTTP_TIMEOUT)
            d = res.json()
        except Exception as e:
            self.__accessable = False
            if self.can_access_internet():
                self.set_error("client_network_error", u"{}".format(e))
                logger.error("accessable(): backend is unreachable: {}".format(e))
            else:
                self.set_error(
                    "client_no_internet",
                    u"{}".format(e),
                    fallback=self.MaicaAiStatus.NO_INTERNET,
                )
                logger.error("accessable(): backend and external network checks failed: {}".format(e))
            return
        if d.get(u"success", False):
            self._serving_status = d["content"]
            if self._serving_status != "serving" and not self._ignore_accessable:
                self.set_error(
                    "client_server_unavailable",
                    u"{}".format(d["content"]),
                    fallback=self.MaicaAiStatus.SERVER_MAINTAIN,
                )
                self.__accessable = False
                logger.error("accessable(): Maica is not serving: {}".format(d["content"]))
            else:
                self.__accessable = True
                self.clear_error(self.MaicaAiStatus.NOT_READY)
        else:
            self.set_error(
                "client_availability_failed",
                d.get("exception") or "Accessibility request failed",
                fallback=self.MaicaAiStatus.CONNECT_PROBLEM,
            )
            self.__accessable = False
            logger.error("accessable(): Maica is not serving: request failed: {}".format(d))
        
        # 版本信息获取
        if self.__accessable:
            version_info = self.get_version()
            self.version_info = version_info
            if version_info.get("success", False):
                legc_version = version_info.get("content", {}).get("legc_version", "")
                try:
                    from packaging import version
                    if version.parse(legc_version) > version.parse(self.SUPPORT_BACKEND):
                        self.set_error(
                            "client_version_unsupported",
                            "Backend {} requires a newer client than {}".format(
                                legc_version, self.SUPPORT_BACKEND
                            ),
                            fallback=self.MaicaAiStatus.VERSION_OLD,
                        )
                        self.__accessable = False
                        logger.error("accessable(): Backend version {} is newer than supported version {}".format(legc_version, self.SUPPORT_BACKEND))
                        return
                except:
                    pass
            try:
                res = requests.get(self.provider_manager.get_api_url() + "/defaults", timeout=self.HTTP_TIMEOUT).json()["content"]
                if type(res) == dict:
                    self.default_setting.update(res)
            except Exception as e:
                logger.error("accessable(): Maica get default setting error: {}".format(e))
        


    def disable(self, status=None):
        if status is not None:
            self.status = status
        self.__accessable = False



            

        
