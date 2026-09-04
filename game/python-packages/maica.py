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
    HTTP_TIMEOUT = (5.0, 30.0)
    CONNECTION_TIMEOUT = 30.0
    RESPONSE_TIMEOUT = 300.0
    ascii_icon = r"""

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
        # 空闲，等待建立连接
        IDLE = 10000
        # 等待可用性验证
        WAIT_AVAILABILITY = 10010
        # WebSocket正在连接
        WEBSOCKET_CONNECTING = 10020
        # WebSocket已通过认证，可以接受请求
        CONNECTED = 10302

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
        CERTIFI_RESTART_REQUIRED = 13418

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
            "maica_uncaught_exception": SERVER_ERROR,
            "client_token_generation_failed": TOKEN_GENERATION_FAILED,
            "client_server_unavailable": SERVER_MAINTAIN,
            "client_availability_failed": CONNECT_PROBLEM,
            "client_network_error": CONNECT_PROBLEM,
            "client_response_timeout": CONNECT_PROBLEM,
            "client_response_invalid": RESPONSE_INVALID,
            "client_auth_failed": TOKEN_INVALID,
        }

        @classmethod
        def from_protocol_status(cls, status, fallback=None, code=None):
            mapped_status = cls._protocol_error_map.get(status)
            if mapped_status == cls.SERVER_ERROR:
                return mapped_status
            try:
                if 500 <= int(code) < 600:
                    return cls.SERVER_ERROR
            except (TypeError, ValueError):
                pass
            if mapped_status is not None:
                return mapped_status
            return cls.SERVER_REJECTED if fallback is None else fallback
        _descriptions = {
            IDLE: u"MAICA is idle",
            WAIT_AVAILABILITY: u"Checking service availability",
            WEBSOCKET_CONNECTING: u"WebSocket is connecting (this should finish quickly)",
            CONNECTED: u"MAICA is connected and ready",
            TOKEN_MISSING: u"No token is configured",
            TOKEN_CORRUPTED: u"The token is corrupted",
            TOKEN_INVALID: u"The account or password is invalid",
            LOGIN_BLOCKED: u"Login is temporarily blocked",
            ACCOUNT_BANNED: u"The account is suspended",
            EMAIL_UNVERIFIED: u"The account email is not verified",
            TOS_UNACCEPTED: u"The latest terms are not accepted",
            CONNECTION_REUSE_DENIED: u"The account already has an active connection",
            SERVER_REJECTED: u"A user-level error occurred",
            SERVER_ERROR: u"A server-side error occurred",
            TOKEN_GENERATION_FAILED: u"Token generation failed",
            CONNECT_PROBLEM: u"Unable to connect to the server",
            RESPONSE_INVALID: u"The server returned an invalid response",
            SERVER_MAINTAIN:u"The server is unavailable or under maintenance",
            CERTIFI_BROKEN:u"SSL/TLS support is not working correctly",
            FAILED_GET_NODE:u"Failed to retrieve an available service provider",
            VERSION_OLD:u"Submod version outdated, update required",
            NO_INTERNET:u"No internet connection available",
            CERTIFI_RESTART_REQUIRED:u"A certificate fix was applied; restart the game to apply it",
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
        CONSOLE_LOG_FORMAT = u"<%(levelname)s>|%(message)s"

        def __init__(self, maica_console_log_func):
            self.maica_console_log_func = maica_console_log_func
            self._maica_console_handler = True
            self.leveling_filter = re.compile(r'^.*?<DISABLE_VERBOSITY>')
            super(MaicaAi.ExternalLoggingHandler, self).__init__()
            self.setFormatter(logging.Formatter(self.CONSOLE_LOG_FORMAT))

        def emit(self, record):
            preferred_encoding = (
                bot_interface.sys.getdefaultencoding() if PY2 else None
            )
            try:
                log_message = self.format(record)
            except UnicodeError:
                message = bot_interface.to_unicode(
                    record.msg,
                    preferred_encoding
                )
                if record.args:
                    try:
                        if isinstance(record.args, dict):
                            format_args = dict(
                                (
                                    bot_interface.to_unicode(key, preferred_encoding),
                                    bot_interface.to_unicode(value, preferred_encoding)
                                )
                                for key, value in record.args.items()
                            )
                        else:
                            format_args = tuple(
                                bot_interface.to_unicode(value, preferred_encoding)
                                for value in record.args
                            )
                        message = message % format_args
                    except (TypeError, ValueError, UnicodeError):
                        pass
                log_message = self.CONSOLE_LOG_FORMAT % {
                    "levelname": bot_interface.to_unicode(
                        record.levelname,
                        preferred_encoding,
                    ),
                    "message": message,
                }
            log_message = bot_interface.to_unicode(
                log_message,
                preferred_encoding
            )
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
        self._connection_state_lock = threading.RLock()
        self._availability_check_lock = threading.Lock()
        self._availability_check_in_progress = False
        self._connection_in_progress = False
        self._connection_cancel_requested = False
        self._connection_close_in_progress = False
        # Transport failures are tracked separately from frontend status codes.
        self._connection_interrupted = False
        self._sticky_disable_status = None
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
        self.mspire_type = self.MaicaMSpiretype.in_precise_category
        self.pprt=False
        self.in_mas = True
        self.provider_manager = maica_provider_manager.MaicaProviderManager()
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
            "prompt_monika_nickname": False,
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
        self._workload_failure_state = None
        self.console_logger = logging.getLogger(name="mas_console_logger")
        self.console_logger.setLevel(logging.DEBUG)
        self.console_logger.propagate = False

        # ``logging.getLogger`` returns the same named logger for every
        # MaicaAi instance. Reuse the existing MAICA handler and rebind its
        # output callback instead of stacking one handler per instance.
        maica_handlers = [
            handler for handler in list(self.console_logger.handlers)
            if getattr(handler, "_maica_console_handler", False)
        ]
        if maica_handlers:
            h = maica_handlers[0]
            h.maica_console_log_func = self.send_to_outside_func
            for duplicate in maica_handlers[1:]:
                self.console_logger.removeHandler(duplicate)
                duplicate.close()
        else:
            h = self.ExternalLoggingHandler(self.send_to_outside_func)
            self.console_logger.addHandler(h)

        h.setLevel(logging.NOTSET)
        self._console_handler = h

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

        loop_warn_task = maica_tasker_sub.MAICALoopWarnHandler(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="maicaloop_warn_handler",
            manager=self.task_manager,
            except_ws_status=['maica_loop_warn_reset']
        )
        loop_warn_task.set_reset_callback(self._handle_loop_warn_reset)

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
            except_ws_status=[
                'maica_core_streaming_continue',
                'maica_chat_loop_finished',
                'maica_loop_warn_reset',
            ]
        )
        self.ChatProcessor._external_callback = self.general_chat_callback
        self.MSpireProcessor = maica_tasker_sub_sessionsender.MAICAMSpireProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="mspire_processor",
            manager=self.task_manager,
            except_ws_status=[
                'maica_core_streaming_continue',
                'maica_chat_loop_finished',
                'maica_loop_warn_reset',
            ]
        )
        self.MSpireProcessor._external_callback = self.general_chat_callback
        self.MPostalProcessor = maica_tasker_sub_sessionsender.MAICAMPostalProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="mpostal_processor",
            manager=self.task_manager,
            except_ws_status=[
                'maica_core_streaming_continue',
                'maica_chat_loop_finished',
                'maica_loop_warn_reset',
            ]
        )
        self.MPostalProcessor._external_callback = self.mpostal_callback
        self.RawContextProcessor = maica_tasker_sub_sessionsender.MAICARawContextProcessor(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="raw_context_processor",
            manager=self.task_manager,
            except_ws_status=[
                'maica_core_streaming_continue',
                'maica_chat_loop_finished',
                'maica_loop_warn_reset',
            ]
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
        self.AutoReconnector.set_reconnect_func(self._auto_reconnect_when_idle)
        self.AutoReconnector._reconnect_delay = 0.5

        self.AutoResumeTasker = maica_tasker_sub.AutoResumeTasker(
            task_type=maica_tasker.MaicaTask.MAICATASK_TYPE_WS,
            name="auto_resume_tasker",
            manager=self.task_manager,
            except_ws_status=[
                'maica_mcore_gen_start',
                'maica_chat_loop_finished',
                'maica_loop_warn_reset',
            ],
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
        content = bot_interface.to_unicode(
            key_replace(content, bot_interface.renpy_symbol_percentage)
        )
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
            line = bot_interface.to_unicode(
                key_replace(i.replace("\n", ""), bot_interface.renpy_symbol)
            )
            self.content_func(line)

    def update_stat(self, new):
        self.stat.update(new)
    def generate_vista_url(self, uuid):
        return self.provider_manager.get_api_url() + "/vista?content={}".format(uuid)

    def add_ana(self, ana_input):
        emote_talk_zipped = self.MoodStatus.analyze(
            bot_interface.to_unicode(ana_input)
        )
        for index, pair in enumerate(emote_talk_zipped):
            self._append_to_message_list(*pair, extend=False if index == 0 else True)

    @staticmethod
    def _prepare_message_for_renpy(message):
        if message is Ellipsis:
            message = "..."
        elif type(message) in (int, float):
            message = str(message)
        message = bot_interface.to_unicode(message)
        return message

    def prepare_message_for_renpy(
        self,
        message,
        add_pause=True,
        escape_for_renpy=True,
    ):
        """Normalize a message and optionally escape it for Ren'Py display.

        Display mode applies glyph fallbacks before escaping and pause
        insertion. Raw mode only retains the shared value normalization.
        """
        message = self._prepare_message_for_renpy(message)

        if escape_for_renpy:
            for source, replacement in bot_interface.RENPY_DISPLAY_REPLACEMENTS.items():
                message = message.replace(source, replacement)
            message = bot_interface.escape_renpy_text(
                message,
                bot_interface.RENPY_DIALOGUE_SUBSTITUTIONS
            )
            if add_pause:
                message = self.TalkSpilter.add_pauses(message)
        return message

    def get_message(self):
        res = self.message_list.get()
        if len(self.message_list) < 1:
            talk = self.TalkSpilter.split_present_sentence()
            if talk:
                self.add_ana(talk)
        message = self._prepare_message_for_renpy(res[1])
        return (res[0], message, res[2] if len(res) >= 3 else False)

    def _clear_error_unlocked(self, status=None):
        self.error_protocol_status = None
        self.error_message = None
        self.error_protocol_code = None
        sticky_status = getattr(self, "_sticky_disable_status", None)
        if sticky_status is not None:
            self.status = sticky_status
        elif status is not None:
            self.status = status
        elif self.MaicaAiStatus.is_submod_exception(getattr(self, "status", None)):
            self.status = self.MaicaAiStatus.IDLE

    def clear_error(self, status=None):
        """Clear protocol failure details and move to a non-error status."""
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            return self._clear_error_unlocked(status)
        with connection_lock:
            return self._clear_error_unlocked(status)

    def _set_error_unlocked(self, status, message=None, code=None, fallback=None):
        sticky_status = getattr(self, "_sticky_disable_status", None)
        if sticky_status is not None:
            self.status = sticky_status
            return
        self.error_protocol_status = status
        self.error_message = message
        self.error_protocol_code = code
        self.status = self.MaicaAiStatus.from_protocol_status(status, fallback, code)

    def set_error(self, status, message=None, code=None, fallback=None):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            return self._set_error_unlocked(status, message, code, fallback)
        with connection_lock:
            return self._set_error_unlocked(status, message, code, fallback)

    def _handle_loop_warn_reset(self, event):
        """Convert a backend loop reset into a one-shot frontend operation error."""
        if self._is_login_rejection():
            return
        packet = event.data
        self.set_error(
            getattr(packet, "status", "maica_loop_warn_reset"),
            getattr(packet, "content", None),
            getattr(packet, "code", None),
            fallback=self.MaicaAiStatus.SERVER_REJECTED,
        )

    def _handle_login_result(self, success, status=None, message=None, code=None):
        if self._connection_cancelled() or self.is_connection_interrupted():
            self.Loginer.success = False
            return
        if success:
            self._set_connection_interrupted(False)
            self.clear_error(self.MaicaAiStatus.CONNECTED)
        else:
            # A rejected login is an intentional policy decision, not a
            # transport failure.  The login task closes this socket itself.
            self._set_connection_interrupted(False)
            self.set_error(status, message, code, self.MaicaAiStatus.TOKEN_INVALID)
        self._mark_connection_handshake_complete()

    def _handle_ws_failure(self, status, message=None, code=None):
        if self._connection_cancelled() or status == "maica_loop_warn_reset":
            return False
        login_failures = (
            self.Loginer.LOGIN_FAILURE_STATUSES + self.Loginer.PREAUTH_FAILURE_STATUSES
        )
        if not self.Loginer.success and status in login_failures:
            return False
        self._set_connection_interrupted(True)
        self.set_error(status, message, code, self.MaicaAiStatus.SERVER_ERROR)
        return True

    def _handle_response_timeout(self, processor_name, timeout):
        self._set_connection_interrupted(True)
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
            self.MaicaAiStatus.CERTIFI_RESTART_REQUIRED,
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
            self._log_operation_skipped(
                "_gen_token",
                "service availability has not been established",
            )
            return
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
            logger.error(
                "Maica::_gen_token POST /register failed: {}".format(e)
            )
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

    @staticmethod
    def _response_json(response):
        try:
            data = response.json()
        except Exception:
            return None
        return data if isinstance(data, dict) else None

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
                logger.error(
                    "Maica::_verify_token GET /legality returned a non-JSON response "
                    "(HTTP {}): {}".format(res.status_code, res.text)
                )
                self.set_error("client_response_invalid", "Maica::_verify_token response was not valid JSON")
                return self.get_error_result()

        except Exception as e:
            import traceback
            logger.error(
                "Maica::_verify_token GET /legality failed: {}".format(
                    traceback.format_exc()
                )
            )
            self.set_error("client_network_error", "Maica::_verify_token failed")
            return self.get_error_result()

    def get_version(self):
        import requests
        import traceback

        try:
            response = requests.get(
                self.provider_manager.get_api_url() + "/version",
                timeout=self.HTTP_TIMEOUT,
            )
            result = self._response_json(response)
            if result is None:
                logger.error("MAICA: Get version returned an invalid response")
                return {
                    "success": False,
                    "status": "client_response_invalid",
                    "exception": "Version response was not valid JSON",
                    "code": getattr(response, "status_code", None),
                }
            if response.status_code == 200 and result.get("success", False):
                return result

            status, message = self._normalize_failure(
                result,
                "client_server_unavailable",
            )
            logger.warning("MAICA: Get version failed: {}".format(result))
            return {
                "success": False,
                "status": status,
                "exception": message,
                "code": response.status_code,
            }

        except Exception as e:
            error_msg = traceback.format_exc()
            logger.error("MAICA: Get version request encountered an error: {}".format(error_msg))
            return {
                "success": False,
                "status": "client_network_error",
                "exception": "Version request failed",
                "code": None,
            }

    def get_emotion(self, type, text):
        """Return the local emotion fallback for legacy callers."""
        return {
            "success": True,
            "content": [self.MoodStatus.fallback_selector.predict(), 0.0],
        }

    def extract_legality_coordinates(self, result):
        """Return the canonical latitude/longitude pair from a legality result."""
        if not isinstance(result, dict):
            return None

        content = result.get("content")
        if not isinstance(content, dict):
            return None

        latitude = content.get("latitude")
        longitude = content.get("longitude")
        if latitude is None or longitude is None:
            return None

        return latitude, longitude

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
            return self._unavailable_result("verify_legality")

        if not self.ciphertext:
            logger.error("verify_legality: access_token is null")
            return {"success": False, "exception": "Access token is null"}

        token_only = verification_object is None and verification_value is None
        if not token_only:
            try:
                string_types = (basestring,)
            except NameError:
                string_types = (str,)

            if (
                not isinstance(verification_object, string_types)
                or not isinstance(verification_value, string_types)
                or not verification_object.strip()
                or not verification_value.strip()
            ):
                logger.warning("verify_legality: object and value must be non-empty strings")
                return {
                    "success": False,
                    "exception": "Legality verification requires non-empty object and value",
                }

        try:
            # 构建请求参数
            params = {"access_token": self.ciphertext}

            # 如果提供了验证内容，添加到参数中
            if not token_only:
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
                    if (
                        not token_only
                        and verification_object == "geolocation"
                        and self.extract_legality_coordinates(res_data) is None
                    ):
                        logger.warning(
                            "Legality verification response missing latitude/longitude: {}".format(
                                res_data
                            )
                        )
                        return {
                            "success": False,
                            "exception": "Legality verification response missing latitude/longitude",
                        }
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


    def _connection_cancelled(self):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            return False
        with connection_lock:
            return self._connection_cancel_requested

    def _set_connection_interrupted(self, interrupted=True):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            previous = bool(getattr(self, "_connection_interrupted", False))
            self._connection_interrupted = bool(interrupted)
            return previous
        with connection_lock:
            previous = bool(getattr(self, "_connection_interrupted", False))
            self._connection_interrupted = bool(interrupted)
            return previous

    def is_connection_interrupted(self):
        """Return whether the authenticated transport needs to be reopened."""
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            interrupted = bool(getattr(self, "_connection_interrupted", False))
            closing = bool(getattr(self, "_connection_close_in_progress", False))
            cancelled = bool(getattr(self, "_connection_cancel_requested", False))
        else:
            with connection_lock:
                interrupted = bool(getattr(self, "_connection_interrupted", False))
                closing = bool(getattr(self, "_connection_close_in_progress", False))
                cancelled = bool(getattr(self, "_connection_cancel_requested", False))
        if interrupted or closing or cancelled:
            return interrupted
        # Keep the predicate correct if a driver dies before its callback runs.
        return bool(
            getattr(getattr(self, "Loginer", None), "success", False)
            and not self.is_connected()
        )

    def _is_login_rejection(self):
        loginer = getattr(self, "Loginer", None)
        if getattr(loginer, "success", False):
            return False
        statuses = tuple(
            getattr(loginer, "LOGIN_FAILURE_STATUSES", ())
        ) + tuple(
            getattr(loginer, "PREAUTH_FAILURE_STATUSES", ())
        )
        if getattr(self, "error_protocol_status", None) in statuses:
            return True
        return getattr(self, "status", None) in (
            self.MaicaAiStatus.TOKEN_CORRUPTED,
            self.MaicaAiStatus.TOKEN_INVALID,
            self.MaicaAiStatus.LOGIN_BLOCKED,
            self.MaicaAiStatus.ACCOUNT_BANNED,
            self.MaicaAiStatus.EMAIL_UNVERIFIED,
            self.MaicaAiStatus.TOS_UNACCEPTED,
            self.MaicaAiStatus.CONNECTION_REUSE_DENIED,
        )

    def _mark_connection_handshake_complete(self):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            return
        with connection_lock:
            self._connection_in_progress = False

    def _run_connection_thread(self):
        import threading
        current_thread = threading.current_thread()
        try:
            self._init_connect()
        finally:
            with self._connection_state_lock:
                if self.wss_thread is current_thread:
                    if self._connection_cancel_requested:
                        self._set_connection_interrupted(False)
                        self.clear_error(self.MaicaAiStatus.IDLE)
                    self._connection_in_progress = False
                    self._connection_cancel_requested = False
                    self.wss_thread = None

    def wait_for_connection_shutdown(self, timeout=None):
        """Wait for the current WebSocket driver thread to finish."""
        import threading
        with self._connection_state_lock:
            connection_thread = self.wss_thread
        if connection_thread is None:
            return True
        if connection_thread is threading.current_thread():
            return False
        connection_thread.join(timeout)
        return not connection_thread.is_alive()

    def _auto_reconnect_when_idle(self):
        if not self.wait_for_connection_shutdown(self.CONNECTION_TIMEOUT):
            logger.warning(
                "Maica auto-reconnect skipped because the previous WebSocket "
                "driver did not stop"
            )
            return False
        if not self.AutoReconnector.is_enabled():
            return False
        return self.init_connect()

    def init_connect(self):
        import threading
        import traceback

        with self._connection_state_lock:
            connection_thread = self.wss_thread
            if (
                self._connection_close_in_progress
                or self._connection_in_progress
                or self.is_connected()
                or (connection_thread and connection_thread.is_alive())
            ):
                logger.debug("Maica::init_connect ignored duplicate connection request")
                return False

        if not self.__accessable:
            if self.is_checking_availability():
                return False
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

        with self._connection_state_lock:
            connection_thread = self.wss_thread
            if (
                self._connection_close_in_progress
                or self._connection_in_progress
                or not self.__accessable
                or self.is_connected()
                or (connection_thread and connection_thread.is_alive())
            ):
                logger.debug("Maica::init_connect ignored duplicate connection request")
                return False

            self._connection_in_progress = True
            self._connection_cancel_requested = False
            try:
                self._set_connection_interrupted(False)
                self.task_manager.reset_all_task()
                self._clear_response_timeouts()
                self.Loginer.set_token(self.ciphertext)
                self.clear_error(self.MaicaAiStatus.WEBSOCKET_CONNECTING)
                connection_thread = threading.Thread(
                    target=self._run_connection_thread
                )
                connection_thread.daemon = True
                self.wss_thread = connection_thread
                connection_thread.start()
            except Exception:
                self._connection_in_progress = False
                self._connection_cancel_requested = False
                self.wss_thread = None
                self._set_connection_interrupted(True)
                self.set_error(
                    "client_network_error",
                    "Failed to start WebSocket connection thread",
                )
                logger.error(
                    "Maica::init_connect failed to start thread: {}".format(
                        traceback.format_exc()
                    )
                )
                return False
        return True
        
    def _init_ws_client(self):
        if self._connection_cancelled():
            return False
        if not self.__accessable:
            if not self._connection_cancelled():
                self._preserve_or_set_availability_error(
                    "Maica server became unavailable before WebSocket initialization"
                )
            self._log_operation_skipped(
                "_init_ws_client",
                "service became unavailable before WebSocket initialization",
            )
            return False
        if not self.multi_lock.acquire(False):
            logger.warning("Maica::_init_connect found an existing connection driver")
            return False
        try:
            if self._connection_cancelled():
                self.multi_lock.release()
                return False
            with self._connection_state_lock:
                if not self.__accessable:
                    self.multi_lock.release()
                    return False
                self.clear_error(self.MaicaAiStatus.WEBSOCKET_CONNECTING)
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
            ui_lang_zh = renpy.config.language == "chinese"
            self.WSConsoleLogger.ui_lang_zh = ui_lang_zh
            self.KeepAliveTasker.ui_lang_zh = ui_lang_zh
            return True
        except Exception:
            import traceback
            if not self._connection_cancelled():
                self._set_connection_interrupted(True)
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
            return False
        ws_client = self.task_manager.ws_client
        def connection_timeout():
            if (
                self._connection_cancelled()
                or self.Loginer.success
                or self.task_manager.ws_client is not ws_client
            ):
                return
            self._set_connection_interrupted(True)
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
        connection_timer = None
        try:
            if self._connection_cancelled():
                return False
            if self.auto_reconnect:
                self.AutoReconnector.enable()
            if self._connection_cancelled():
                self.AutoReconnector.disable()
                return False
            connection_timer = threading.Timer(
                self.CONNECTION_TIMEOUT,
                connection_timeout,
            )
            connection_timer.daemon = True
            connection_timer.start()
            ws_client.run_forever()
        except Exception as e:
            import traceback
            if not self._connection_cancelled():
                self._set_connection_interrupted(True)
                self.set_error("client_network_error", "WebSocket connection failed")
            self.console_logger.error("wss_session.run_forever() failed: {}".format(e))
            logger.error("Maica::_init_connect wss_session.run_forever() failed: {}".format(traceback.format_exc()))
        finally:
            if connection_timer is not None:
                connection_timer.cancel()
            unexpected_close = bool(
                not self._connection_cancelled()
                and not self.is_connected()
                and not self._is_login_rejection()
            )
            if unexpected_close:
                was_interrupted = self._set_connection_interrupted(True)
                if not was_interrupted or not self.error_protocol_status:
                    if self.Loginer.success:
                        self.set_error(
                            "client_connection_closed",
                            "WebSocket connection closed unexpectedly",
                            fallback=self.MaicaAiStatus.CONNECT_PROBLEM,
                        )
                    else:
                        self.set_error(
                            "client_network_error",
                            "WebSocket closed before authentication completed",
                        )
            if self.multi_lock.locked():
                self.multi_lock.release()
                logger.debug("Maica::_init_connect released lock because WebSocket closed")
        return self.Loginer.success
        
        
    def is_responding(self):
        """返回maica是否正在返回消息"""
        return maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.locked()

    def is_ready_to_input(self):
        """返回maica是否可以接受输入消息了"""
        return bool(
            self.is_connected()
            and not self.is_connection_interrupted()
            and self.Loginer.success
            and not maica_tasker_sub_sessionsender.SessionSenderAndReceiver.multi_lock.locked()
        )

    def is_connecting(self):
        with self._connection_state_lock:
            connection_close_in_progress = self._connection_close_in_progress
            connection_in_progress = self._connection_in_progress
            connection_thread = self.wss_thread
        driver_is_stopping = bool(
            connection_thread
            and connection_thread.is_alive()
            and not self.is_connected()
        )
        return bool(
            connection_close_in_progress
            or connection_in_progress
            or driver_is_stopping
        )

    def is_accessable(self):
        """返回maica是否可用"""
        return self.__accessable

    
    def is_failed(self):
        """返回maica是否处于异常状态"""
        task_manager = getattr(self, "task_manager", None)
        return bool(
            self.is_connection_interrupted()
            or bool(task_manager and task_manager.is_task_failed())
            or self.response_timed_out()
            or self.MaicaAiStatus.is_submod_exception(
                getattr(self, "status", None)
            )
        )

    def _prepare_authenticated_operation(self):
        """Clear a retryable operation error immediately before a new request."""
        if getattr(self, "error_protocol_status", None) == "maica_loop_warn_reset":
            self.clear_error(self.MaicaAiStatus.CONNECTED)

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
        task_manager = getattr(self, "task_manager", None)
        return bool(getattr(getattr(task_manager, "ws_client", None), "keep_running", False)) #\
            #or self.wss_thread.is_alive() if self.wss_thread else False

    def get_status_description(self):
        """返回maica当前状态描述"""
        return self.MaicaAiStatus.get_description(self.status)

    def _log_operation_skipped(self, operation, prerequisite):
        """Record a skipped operation without mislabeling the backend state."""
        status = getattr(self, "status", self.MaicaAiStatus.WAIT_AVAILABILITY)
        status_description = self.MaicaAiStatus.get_description(status)
        protocol_status = getattr(self, "error_protocol_status", None)
        protocol_detail = (
            " / protocol_status={}".format(protocol_status)
            if protocol_status else ""
        )
        logger.debug(
            "MaicaAi.{} skipped: {} (status={} / {}{}).".format(
                operation,
                prerequisite,
                status,
                status_description,
                protocol_detail,
            )
        )

    def _unavailable_result(self, operation, content=None):
        """Build the common response for an operation blocked by client state."""
        self._log_operation_skipped(
            operation,
            "the current client state does not permit this request",
        )
        result = {
            "success": False,
            "exception": self.MaicaAiStatus.get_description(
                getattr(self, "status", self.MaicaAiStatus.WAIT_AVAILABILITY)
            ),
        }
        if content is not None:
            result["content"] = content
        return result

    def len_message_queue(self):
        """返回maica已接收并完成分句的台词数"""
        return self.message_list.size()
    
    def start_MSpire(self, ctg_weight=None):
        """启动 MSpire；分类权重默认为实例配置的 10。"""
        if not self.__accessable:
            self._log_operation_skipped(
                "start_MSpire",
                "service availability is not ready",
            )
            return
        if not self.is_ready_to_input():
            self._log_operation_skipped(
                "start_MSpire",
                "the WebSocket is not ready to accept input",
            )
            return
        self._prepare_authenticated_operation()
        self.QualityStatusTasker.clear()
        self._clear_response_timeouts()
        self.stat['mspire_count'] += 1
        self.mspire_type = maica_tasker_sub_sessionsender.normalize_mspire_type(
            getattr(self, "mspire_type", self.MaicaMSpiretype.in_precise_category)
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
            self._log_operation_skipped(
                "start_MPostal",
                "service availability is not ready",
            )
            return
        if not self.is_ready_to_input():
            self._log_operation_skipped(
                "start_MPostal",
                "the WebSocket is not ready to accept input",
            )
            return
        self._prepare_authenticated_operation()
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

    def send_settings(self, send_mtrigger=True):
        data = self.build_setting_config()
        if self.is_connected() and self.Loginer.success:
            self._prepare_authenticated_operation()
            if send_mtrigger:
                self.send_mtrigger()
            self.SettingSender.start_event(data)
            return data
        self._log_operation_skipped(
            "send_settings",
            "the WebSocket is not authenticated",
        )
        return {}
    def _on_message(self, wsapp, message):
        try:
            self.task_manager._ws_onmessage(wsapp, message)
        except Exception as e:
            import traceback
            self.console_logger.error(
                "MAICA message processing failed: {}".format(e)
            )
            logger.error(
                "MaicaAi._on_message failed while processing message {}:\n{}".format(
                    message,
                    traceback.format_exc(),
                )
            )
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
            self.MoodStatus.reset()
            # 释放聊天锁，允许下一个聊天请求
            processor.reset()
        elif event.data.status == "maica_loop_warn_reset":
            self._in_mspire = False
            self.TalkSpilter.init1()
            self.MoodStatus.reset()
            processor.reset()
    
    def mpostal_callback(self, processor, event):
        core_output = processor.consume_core_output(event)
        for content in core_output:
            message = u''.join([
                bot_interface.to_unicode(i[1])
                for i in self.MoodStatus.analyze(bot_interface.to_unicode(content))
            ])
            if len(message) > 0 and message[0] == " ":
                message = message[1:]
            message_step1 = key_replace(message, bot_interface.renpy_symbol_percentage)
            self.message_list.put(('1eua', message_step1))
        if event.data.status in (
            "maica_chat_loop_finished",
            "maica_loop_warn_reset",
        ):
            processor.reset()

    def _on_error(self, wsapp, error):
        if not self._connection_cancelled():
            was_interrupted = self._set_connection_interrupted(True)
            if not was_interrupted or not self.error_protocol_status:
                self.set_error("client_network_error", u"{}".format(error))
        self.task_manager._ws_onerror(wsapp, error)
        if wsapp:
            wsapp.close()

    def _on_close(self, wsapp, close_status_code=None, close_msg=None):
        logger.debug("MaicaAi::_on_close {}|{}".format(close_status_code, close_msg))
        with self._connection_state_lock:
            intentional_close = bool(
                wsapp in self._intentional_ws_closes
                or self._connection_close_in_progress
                or self._connection_cancel_requested
            )
        self._intentional_ws_closes.discard(wsapp)
        if not intentional_close and not self._is_login_rejection():
            was_interrupted = self._set_connection_interrupted(True)
            if not was_interrupted or not self.error_protocol_status:
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
            self._log_operation_skipped("chat", "service availability is not ready")
            return
        if not self.is_ready_to_input():
            self._log_operation_skipped(
                "chat",
                "the WebSocket is not ready to accept input",
            )
            return
        self._prepare_authenticated_operation()
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
            self._log_operation_skipped(
                "start_raw_context",
                "service availability is not ready",
            )
            return
        if not self.is_ready_to_input():
            self._log_operation_skipped(
                "start_raw_context",
                "the WebSocket is not ready to accept input",
            )
            return
        self._prepare_authenticated_operation()
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
        message = bot_interface.to_unicode(message)
        if len(message) == 0:
            return
        elif message[0] == " ":
            message = message[1:]
        message_step1 = key_replace(message, bot_interface.renpy_symbol_percentage, bot_interface.renpy_symbol_enter)
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
            logger.debug("upload_save:: savefile_access marker is missing")
            return {
                "success": False,
                "exception": "savefile_access marker is missing"
            }
        if not self.__accessable:
            return self._unavailable_result("upload_save")
        if self.ciphertext in ("", None):
            logger.error("upload_save:: token is null")
            return {"success": False, "exception": "Access token is null"}
        import requests, json
        content = {
                    "access_token": self.ciphertext,
                    "chat_session": self.chat_session,
                    "content": dict
                }
        try:
            res = requests.post(
                self.provider_manager.get_api_url() + "/savefile",
                json = content,
                headers = {"Content-Type": "application/json"},
                timeout=self.HTTP_TIMEOUT
            )
            result = res.json()
            if not result.get("success", False):
                logger.error("upload_save:: backend rejected request: {}".format(result))
            return result
        except Exception as e:
            logger.error("upload_save:: POST /savefile failed: {}".format(e))
            return {"success": False, "exception": str(e)}

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
            return self._unavailable_result("get_history", content=[])
        import requests, json
        try:
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
            return res.json()
        except Exception as e:
            logger.error("get_history:: {}".format(e))
            return {"success": False, "content": [], "exception": str(e)}

    def upload_history(self, history):
        """
        将历史记录上传到Maica服务器
        
        Args:
            history (dict): 
        
        Returns:
            dict: Maica服务器返回的JSON响应
        
        """

        if not self.__accessable:
            return self._unavailable_result("upload_history")
        if self.ciphertext in ("", None):
            logger.error("upload_history:: token is null")
            return {"success": False, "exception": "Access token is null"}
        import requests, json
        content = {
            "access_token": self.ciphertext,
            "chat_session": self.chat_session,
            "content": history
        }
        try:
            res = requests.put(
                self.provider_manager.get_api_url() + "/history",
                json = content,
                headers = {"Content-Type": "application/json"},
                timeout=self.HTTP_TIMEOUT
            )
            result = res.json()
            if not result.get("success", False):
                logger.error("upload_history:: backend rejected request: {}".format(result))
            return result
        except Exception as e:
            logger.error("upload_history:: PUT /history failed: {}".format(e))
            return {"success": False, "exception": str(e)}
        
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
            self._log_operation_skipped(
                "reset_chat_session",
                "service availability is not ready",
            )
            return False
        if self.is_connected() and self.Loginer.success:
            self._prepare_authenticated_operation()
        import json
        self.SessionReseter.start_event(chat_session = self.chat_session)
        self.message_list.clear()
        self.stat["received_token_by_session"][self.chat_session] = 0
        self.HistoryStatus.reset()
        return True

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
            self._workload_failure_state = None
            return None

        def log_workload_failure(state, message):
            if self._workload_failure_state == state:
                return
            self._workload_failure_state = state
            logger.warning(message)

        def task():
            try:
                res = requests.get(self.provider_manager.get_api_url() + "/workload", timeout=self.HTTP_TIMEOUT)
                data = res.json()
                if data["success"]:
                    self.workload_raw = data["content"]
                    self._workload_failure_state = None
                    #logger.debug("Workload updated successfully.")
                else:
                    log_workload_failure(
                        "backend_rejected",
                        "update_workload: backend rejected request: {}".format(data),
                    )
            except Exception as e:
                log_workload_failure(
                    "request_failed",
                    "update_workload: GET /workload failed: {}".format(e),
                )

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
        with self._connection_state_lock:
            self._connection_close_in_progress = True
            self._set_connection_interrupted(False)
            connection_thread = self.wss_thread
            self._connection_cancel_requested = bool(
                self._connection_in_progress
                or (connection_thread and connection_thread.is_alive())
                or self.task_manager.ws_client
            )
            ws_client = self.task_manager.ws_client
            # Provider migration may close before a transport exists; keep a
            # preceding availability failure visible in that case.
            connection_was_active = bool(
                self._connection_in_progress
                or connection_thread
                or ws_client
                or self.wss_session
            )
            if ws_client:
                self._intentional_ws_closes.add(ws_client)
        try:
            self.AutoReconnector.disable()
            self.task_manager.reset_all_task()
            if connection_was_active:
                self.clear_error(self.MaicaAiStatus.IDLE)
            if ws_client:
                try:
                    self.task_manager.close_ws()
                except Exception as error:
                    logger.error("Maica::close_wss_session failed: {}".format(error))
        finally:
            with self._connection_state_lock:
                self._connection_close_in_progress = False
    def del_mtrigger(self):
        import requests
        try:
            requests.delete(self.provider_manager.get_api_url()+"/trigger", json={"access_token": self.ciphertext, "chat_session": self.chat_session}, headers={'Content-Type': 'application/json'}, timeout=self.HTTP_TIMEOUT)
        except Exception as e:
            logger.error("del_mtrigger:: request failed: {}".format(e))

    def send_mtrigger(self):
        try:
            import time
            if not self.__accessable:
                self._log_operation_skipped(
                    "send_mtrigger",
                    "service availability is not ready",
                )
                return False
            if self.ciphertext in ("", None):
                logger.error("send_mtrigger:: token is null")
                return False
            
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
                    logger.debug("MaicaAi.send_mtrigger: trigger table accepted")
                    return True
                else:
                    logger.error("MaicaAi.send_mtrigger: backend rejected request: {}".format(response_data))
                    return False
            except Exception:
                logger.error(
                    "MaicaAi.send_mtrigger: POST /trigger returned non-JSON response: {}".format(
                        res.text
                    )
                )
                return False

        except Exception as e:
            import traceback
            logger.error(
                "MaicaAi.send_mtrigger POST /trigger failed: {}".format(
                    traceback.format_exc()
                )
            )
            return False



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

    def _set_accessibility_state_unlocked(self, accessible, status):
        sticky_status = getattr(self, "_sticky_disable_status", None)
        if sticky_status is not None:
            self.__accessable = False
            self.status = sticky_status
            return False
        self.__accessable = accessible
        self._clear_error_unlocked(status)
        return True

    def _set_accessibility_state(self, accessible, status):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            return self._set_accessibility_state_unlocked(accessible, status)
        with connection_lock:
            return self._set_accessibility_state_unlocked(accessible, status)

    def _set_availability_check_in_progress(self, in_progress):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            self._availability_check_in_progress = bool(in_progress)
            return
        with connection_lock:
            self._availability_check_in_progress = bool(in_progress)

    def is_checking_availability(self):
        return bool(getattr(self, "_availability_check_in_progress", False))

    def is_provider_refreshing(self):
        checker = getattr(self.provider_manager, "is_refreshing", None)
        return bool(checker and checker())

    def get_provider_refresh_error(self):
        getter = getattr(self.provider_manager, "get_last_refresh_error", None)
        return getter() if getter else None

    def refresh_provider_list(self):
        """Refresh provider metadata without invalidating an active connection."""
        if self.is_accessable() or self.is_connected() or self.is_connecting():
            return bool(self.provider_manager.get_provider())
        return bool(self.accessable())

    def accessable(self):
        """Run one serialized service-availability probe."""
        availability_lock = getattr(self, "_availability_check_lock", None)
        if availability_lock is None:
            return self._accessable_unlocked()

        availability_lock.acquire()
        self._set_availability_check_in_progress(True)
        try:
            return self._accessable_unlocked()
        finally:
            self._set_availability_check_in_progress(False)
            availability_lock.release()

    def _accessable_unlocked(self):
        """
        检查Maica服务是否可访问
        注意, 在开始使用前, 必须先使用该函数来检查MAICA服务器是否可用
        
        Args:
            无
        
        Returns:
            bool: 服务可用时返回True，否则返回False
        
        Raises:
            无
        """
        if not self._set_accessibility_state(
            False,
            self.MaicaAiStatus.WAIT_AVAILABILITY,
        ):
            return False
        self.version_info = {"success": False, "content": {}}

        # 检测证书是否是MAS版本/证书是否工作正常
        if self.in_mas:
            try:
                import certifi
                certifi.set_parent_dir
            except (ImportError, AttributeError):
                logger.error("accessable(): MAICA SSL integration is unavailable")
                self.set_error(
                    "client_certifi_broken",
                    "certifi is missing the MAS integration",
                    fallback=self.MaicaAiStatus.CERTIFI_BROKEN,
                )
                return False
            if not self.check_certifi():
                self.set_error(
                    "client_certifi_broken",
                    "SSL/TLS certificate validation is unavailable",
                    fallback=self.MaicaAiStatus.CERTIFI_BROKEN,
                )
                return False

        # 获取服务节点
        try:
            if not self.provider_manager.get_provider():
                if self.provider_id != 9999:
                    provider_error = self.get_provider_refresh_error() or {}
                    if self.can_access_internet():
                        self.set_error(
                            "client_provider_unavailable",
                            provider_error.get("exception") or "Failed to retrieve a service provider",
                            provider_error.get("code"),
                            fallback=self.MaicaAiStatus.FAILED_GET_NODE,
                        )
                    else:
                        self.set_error(
                            "client_no_internet",
                            "External network check failed",
                            fallback=self.MaicaAiStatus.NO_INTERNET,
                        )
                    return False
            vista_manager = getattr(self, "vista_manager", None)
            if vista_manager is not None:
                vista_manager.base_url = self.provider_manager.get_api_url()

        except Exception as e:
            logger.error("accessable(): service provider lookup failed: {}".format(e))
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
                return False

        #获取节点可用性
        import requests, json
        accessibility_url = self.provider_manager.get_api_url() + "/accessibility"
        logger.debug("accessable(): GET /accessibility from {}".format(accessibility_url))
        try:
            res = requests.get(accessibility_url, timeout=self.HTTP_TIMEOUT)
            d = res.json()
        except Exception as e:
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
            return False
        if not isinstance(d, dict):
            self.set_error(
                "client_response_invalid",
                "The accessibility endpoint returned an invalid response",
                fallback=self.MaicaAiStatus.RESPONSE_INVALID,
            )
            return False
        if d.get(u"success", False):
            if "content" not in d:
                self.set_error(
                    "client_response_invalid",
                    "The accessibility response did not contain a service status",
                    fallback=self.MaicaAiStatus.RESPONSE_INVALID,
                )
                return False
            self._serving_status = d["content"]
            if self._serving_status != "serving" and not self._ignore_accessable:
                self.set_error(
                    "client_server_unavailable",
                    u"{}".format(d["content"]),
                    fallback=self.MaicaAiStatus.SERVER_MAINTAIN,
                )
                logger.error(
                    "accessable(): backend reported unavailable service status {!r}".format(
                        d["content"]
                    )
                )
            else:
                if not self._set_accessibility_state(
                    True,
                    self.MaicaAiStatus.IDLE,
                ):
                    return False
        else:
            self.set_error(
                "client_availability_failed",
                d.get("exception") or "Accessibility request failed",
                fallback=self.MaicaAiStatus.CONNECT_PROBLEM,
            )
            logger.error("accessable(): /accessibility request was rejected: {}".format(d))
        
        # 版本信息获取
        if self.__accessable:
            self.version_info = self.get_version()
            try:
                res = requests.get(self.provider_manager.get_api_url() + "/defaults", timeout=self.HTTP_TIMEOUT).json()["content"]
                if type(res) == dict:
                    self.default_setting.update(res)
            except Exception as e:
                logger.warning("accessable(): GET /defaults failed; using local defaults: {}".format(e))
        return bool(self.__accessable)
        


    def _disable_unlocked(self, status=None, sticky=False):
        if sticky and status is not None:
            self._sticky_disable_status = status
        sticky_status = getattr(self, "_sticky_disable_status", None)
        if sticky_status is not None:
            self.error_protocol_status = None
            self.error_message = None
            self.error_protocol_code = None
            self.status = sticky_status
        elif status is not None:
            self.status = status
        self.__accessable = False

    def disable(self, status=None, sticky=False):
        connection_lock = getattr(self, "_connection_state_lock", None)
        if connection_lock is None:
            return self._disable_unlocked(status, sticky)
        with connection_lock:
            return self._disable_unlocked(status, sticky)



            

        
