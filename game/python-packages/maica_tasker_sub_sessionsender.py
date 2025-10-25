from maica_tasker import *
from bot_interface import PY2
import threading
class ChatLock:
    def __init__(self):
        self._lock = threading.Lock()
        self.running_info = ""

    def acquire(self, blocking=True, timeout=-1):
        """
        获取锁
        Args:
            blocking (bool): 是否阻塞等待
            timeout (float): 超时时间(秒)，-1表示永久等待
        Returns:
            bool: 是否成功获取锁
        """
        return self._lock.acquire(blocking, timeout)

    def release(self):
        """
        释放锁
        """
        self._lock.release()
        self.running_info = ""

    def __enter__(self):
        """
        上下文管理器入口
        Returns:
            ChatLock: 返回自身实例
        """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪信息
        """
        self.release()

    def locked(self):
        """
        检查锁是否被占用
        Returns:
            bool: 如果锁被占用返回True，否则返回False
        """
        return self._lock.locked()

class SessionSenderAndReceiver(MaicaWSTask):
    multi_lock = ChatLock()
    strict_cookie = None
    def __init__(self, task_type, name, except_ws_types=[
            'maica_core_streaming_continue',
            #'maica_core_nostream_reply',
            'maica_chat_loop_finished'
        ],
        logger = None):
        super().__init__(task_type, name, except_ws_types)
        self.logger = logger
        self.processing = False

    def start_request(self, *args, **kwargs):
        if SessionSenderAndReceiver.multi_lock.locked():
            raise RuntimeError("SessionSenderAndReceiver is already processing a request.")
        with SessionSenderAndReceiver.multi_lock:
            self.processing = True
            SessionSenderAndReceiver.multi_lock.running_info = self.__str__()
            try:
                self.process_request(*args, **kwargs)
            except Exception as e:
                if self.logger:
                    self.logger.error("[SessionSenderAndReceiver] start_request error: " + str(e))
            finally:
                self.processing = False
    def on_received(self, event):
        wspack = event.data
        raise NotImplementedError

    def process_request(self, request):
        raise NotImplementedError


    def reset(self):
        self.processing = False

class MAICAGeneralChatProcessor(SessionSenderAndReceiver):
    def process_request(self, query, session, trigger, taskowner):
        data = {
            'type': 'query',
            'chat_session': session,
            'query': query,
            'trigger': trigger
        }
        if SessionSenderAndReceiver.strict_cookie:
            data['cookie'] = SessionSenderAndReceiver.strict_cookie
        taskowner.ws_client.send(data)
    
    def on_received(self, event):
        raise NotImplementedError("该方法在外部实现")

class MAICAMSpireProcessor(SessionSenderAndReceiver):
    mspire_type = "in_fuzzy_all"
    use_cache = False
    def process_request(self, category, session, taskowner):
        import random
        data = {
            "type": "query",
            "chat_session":session, 
            "inspire":{
                    "type":MAICAMSpireProcessor.mspire_type,
                    "sample":250,
                    "title": random.choice(category),
                } if len(category) else True,
            "use_cache":MAICAMSpireProcessor.use_cache,
            }
        if SessionSenderAndReceiver.strict_cookie:
            data['cookie'] = SessionSenderAndReceiver.strict_cookie
        taskowner.ws_client.send(data)
    
    def on_received(self, event):
        raise NotImplementedError("该方法在外部实现")
    
class MAICAMPostalProcessor(SessionSenderAndReceiver):
    use_session = 0
    def __init__(self, task_type, name, except_ws_types=[]):
        super().__init__(task_type, name, except_ws_types)
        self.except_ws_types.remove('maica_core_streaming_continue')
        self.except_ws_types.append('maica_core_nostream_reply')
    def process_request(self, query, taskowner):
        data = {
            'type': 'query',
            'chat_session': MAICAMPostalProcessor.use_session,
            'query': query,
        }
        if SessionSenderAndReceiver.strict_cookie:
            data['cookie'] = SessionSenderAndReceiver.strict_cookie
        taskowner.ws_client.send(data)
    
    def on_received(self, event):
        raise NotImplementedError("该方法在外部实现")