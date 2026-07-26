import requests, json, math, re

try:
    basestring  # 套路检查
except NameError:
    basestring = str  # Python 3 统一用 str

try:
    integer_types = (int, long)
except NameError:
    integer_types = (int,)
number_types = integer_types + (float,)

try:
    fullmatch = re.fullmatch
except AttributeError:
    def fullmatch(pattern, value):
        return re.match("(?:{})\\Z".format(pattern), value)

_math_isfinite = getattr(math, "isfinite", None)

def isfinite(value):
    if isinstance(value, integer_types):
        return True
    if _math_isfinite is not None:
        return _math_isfinite(value)
    return not math.isinf(value) and not math.isnan(value)


class NothingLogger(object):
    def debug(self, *args):
        return

logger = NothingLogger()

def check_and_search(sub, target):
    if isinstance(target, basestring):
        return sub in target
    else:
        return False

class MTriggerAction(object):
    instant = 0     #收到以后立刻触发
    post = 1        #当前轮对话结束后触发

class MTriggerExprop(object):
    """
    注意: 所有的值都有默认值, 如有需要请务必修改
    """
    def __init__(self, item_name_zh="", item_name_en="", item_list=[],value_limits=[0, 1], curr_value=None, suggestion=False):
        """
        初始化函数。
        
        Args:
            item_name_zh (str): 中文选择类目的性质。
            item_name_en (str): 英文选择类目的性质。
            item_list (list): 所有可选条目的list。
            value_limits (list): 数值可取的上下限。
            curr_value (Any, optional): 当前值，默认为None。
        """
        self.item_name_zh = item_name_zh
        self.item_name_en = item_name_en
        self.item_list = item_list
        self.value_limits = value_limits
        self.curr_value = curr_value
        self.suggestion = suggestion

class MTriggerMethod(object):
    all = -1
    request = 0
    table = 1

class MTriggerTemplate(object):
    def __init__(self, name, datakey=None, exprop=MTriggerExprop(True,True,True,True,True,True)):
        self.name = name
        self.datakey = datakey
        self.exprop = exprop


common_affection_template = MTriggerTemplate("common_affection_template", "alter_value", exprop=MTriggerExprop(False, False, False, False, False, False))
common_switch_template = MTriggerTemplate("common_switch_template", "choice", exprop=MTriggerExprop(True, True, True, False, True, True))
common_meter_template = MTriggerTemplate("common_meter_template", "value", exprop=MTriggerExprop(True, True, False, True, True, False))
customize_template = MTriggerTemplate("customized", None, exprop=MTriggerExprop(True, True, False, False, False, False))

TEMPLATE_EXPROP_FIELDS = (
    "item_name_zh",
    "item_name_en",
    "item_list",
    "value_limits",
    "curr_value",
    "suggestion",
)

def template_spec(template):
    return (
        template.datakey,
        tuple(getattr(template.exprop, field) for field in TEMPLATE_EXPROP_FIELDS),
    )

CANONICAL_TEMPLATE_SPECS = {
    template.name: template_spec(template)
    for template in (
        common_affection_template,
        common_switch_template,
        common_meter_template,
        customize_template,
    )
}

class MTriggerManager(object):
    TEMPLATE_LIMITS = {
        common_affection_template.name: 1,
        common_switch_template.name: 6,
        common_meter_template.name: 6,
        customize_template.name: 20,
    }
    SIZE_LIMIT = {
        MTriggerMethod.all : 100000,
        MTriggerMethod.request : 3870,
        MTriggerMethod.table : 100000
    }
    MAX_LENGTH_REQUEST = SIZE_LIMIT[MTriggerMethod.request]
    MAX_LENGTH_TABLE = SIZE_LIMIT[MTriggerMethod.table]


    def __init__(self):
        self.triggers = []
        self.triggered_list = []
        self.enable_map = {}
        self._running = False
    
    def add_trigger(self, trigger):
        self.triggers.append(trigger)
        self.enable_map[trigger.name] = True
    
    def enable_trigger(self, name, enable=True):
        self.enable_map[name] = enable
    
    def disable_trigger(self, name):
        self.enable_trigger(name, False)
    
    def output_settings(self):
        return self.enable_map
    
    def import_settings(self, settings):
        for k, v in settings.items():
            self.enable_map[k] = v
    
    def remove_trigger(self, name):
        for i in self.triggers:
            if i.name == name:
                self.triggers.remove(i)


    def trigger_status(self, name):
        return self.enable_map[name] if name in self.enable_map else False

    def validate_batch(self):
        template_counts = {}
        for trigger in self.triggers:
            trigger.validate_template()
            template_name = trigger.template.name
            template_counts[template_name] = template_counts.get(template_name, 0) + 1
        for template_name, count in template_counts.items():
            limit = self.TEMPLATE_LIMITS.get(template_name)
            if limit is not None and count > limit:
                raise ValueError("Too many {} triggers: maximum is {}.".format(template_name, limit))

        return True


    def build_data(self, method=MTriggerMethod.all, full = False):
        self.validate_batch()
        self.triggered_list = []
        self._running = False
        res = []
        current_length = len(json.dumps(res, ensure_ascii=False))

        for i in self.triggers:
            if i.condition() and self.trigger_status(i.name) and (i.method == method or method == MTriggerMethod.all):
                i.validate()
                item_length = len(i)
                if current_length + item_length > self.SIZE_LIMIT[method] and not full:
                    self.disable_trigger(i.name)
                    continue
                res.append(i.build())
                current_length += item_length

        return res

    def get_length(self, method=MTriggerMethod.all):
        return len(json.dumps(self.build_data(method=method, full=True), ensure_ascii=False))

    def triggered(self, name = "", param=None):
        for t in self.triggers:
            if param:
                # 如果不是dict就丢弃
                if not isinstance(param, dict):
                    logger.error("triggered param is not dict! ({}:{})".format(name, param))
                    return
            if t.name == name:
                logger.debug("triggered {} <- {}".format(name, param))
                self.triggered_list.append((t, param))

    def run_trigger(self, action=MTriggerAction.post, remove=True):
        doact = {
            "stop":False,
        }
        self._running = True
        # Create a copy of the list to safely iterate
        triggers_to_process = [t for t in self.triggered_list if t[0].action == action]

        # Sort by priority (highest first)
        triggers_to_process.sort(key=lambda t: t[0].priority, reverse=True)

        for t in triggers_to_process:
            if remove:
                self.triggered_list.remove(t)
            res = t[0].triggered(t[1])
            if check_and_search("stop", res):
                doact["stop"] = True
                break

        self._running = False
        return doact
                

def null_callback(*args,**kwargs):
    pass

def null_condition():
    return True

class MTriggerBase(object):

    def __init__(self, template, name, description = "", callback=null_callback, action=MTriggerAction.post, exprop=MTriggerExprop(), condition=null_condition, method=MTriggerMethod.request, perf_suggestion = False, priority=0):
        self.name = name
        self.template = template
        self.callback = callback
        self.action = action
        self.exprop = exprop
        self.description = description if description != "" else self.name
        self.condition = condition
        self.method = method
        self.perf_suggestion = perf_suggestion
        self.priority = priority

        if self.template.name != common_affection_template.name and exprop.item_name_zh == "":
            raise ValueError("Non affection template must have exprop.item_name_zh.")
    def on_build_pre(self):
        pass

    @staticmethod
    def _validate_display_string(value, field, allow_empty=True):
        if not isinstance(value, basestring):
            raise ValueError("{} must be a string.".format(field))
        if not allow_empty and not value:
            raise ValueError("{} must not be empty.".format(field))
        if len(value) > 256:
            raise ValueError("{} must be at most 256 characters.".format(field))

    def validate_template(self):
        canonical_spec = CANONICAL_TEMPLATE_SPECS.get(self.template.name)
        if canonical_spec is None:
            raise ValueError("Unknown MTrigger template: {}.".format(self.template.name))
        actual_datakey, actual_flags = template_spec(self.template)
        canonical_datakey, canonical_flags = canonical_spec
        if actual_datakey != canonical_datakey or any(
            actual is not canonical
            for actual, canonical in zip(actual_flags, canonical_flags)
        ):
            raise ValueError("MTrigger template {} does not match its canonical schema.".format(self.template.name))

        return True

    def validate(self):
        self.validate_template()
        if not isinstance(self.name, basestring) or fullmatch(r"[A-Za-z0-9_-]{1,64}", self.name) is None:
            raise ValueError("Trigger name must match [A-Za-z0-9_-]{1,64}.")
        self._validate_display_string(self.description, "description")

        if self.template.exprop.item_name_zh:
            self._validate_display_string(self.exprop.item_name_zh, "item_name_zh")
            self._validate_display_string(self.exprop.item_name_en, "item_name_en")

        if self.template.name == common_switch_template.name:
            if not isinstance(self.exprop.item_list, list) or not self.exprop.item_list:
                raise ValueError("Switch item_list must be a non-empty list.")
            for item in self.exprop.item_list:
                self._validate_display_string(item, "item_list entry", allow_empty=False)
            if not isinstance(self.exprop.curr_value, basestring):
                raise ValueError("Switch curr_item must be a string.")
            if self.exprop.curr_value not in self.exprop.item_list:
                raise ValueError("Switch curr_item must belong to item_list.")

        if self.template.name == common_meter_template.name:
            limits = self.exprop.value_limits
            if not isinstance(limits, (list, tuple)) or len(limits) != 2:
                raise ValueError("Meter value_limits must contain exactly two numbers.")
            if any(isinstance(value, bool) or not isinstance(value, number_types) for value in limits):
                raise ValueError("Meter value_limits must contain only numbers.")
            if any(not isfinite(value) for value in limits):
                raise ValueError("Meter value_limits must contain only finite numbers.")
            if limits[0] > limits[1]:
                raise ValueError("Meter value_limits must be in non-descending order.")
            value = self.exprop.curr_value
            if value is not None:
                if isinstance(value, bool) or not isinstance(value, number_types):
                    raise ValueError("Meter curr_value must be a number.")
                if not isfinite(value):
                    raise ValueError("Meter curr_value must be finite.")
                if value < limits[0] or value > limits[1]:
                    raise ValueError("Meter curr_value must be within value_limits.")

        return True

    def build(self):
        self.on_build_pre()
        self.validate()
        data = {
            "template": self.template.name,
            "name": self.name,
            "exprop":{
            }
        }

        if self.template.exprop.suggestion:
            data["exprop"]["suggestion"] = self.exprop.suggestion
        if self.template.exprop.item_name_zh:
            data["exprop"]["item_name"] = {"zh": self.exprop.item_name_zh, "en": self.exprop.item_name_en} 
        if self.template.exprop.item_list:
            data["exprop"]["item_list"] = self.exprop.item_list
        if self.template.exprop.value_limits:
            data["exprop"]["value_limits"] = self.exprop.value_limits
        if self.template.exprop.curr_value and self.exprop.curr_value is not None:
            if self.template.name == common_switch_template.name:
                data["exprop"]["curr_item"] = self.exprop.curr_value
            else:
                data["exprop"]["curr_value"] = self.exprop.curr_value
        if data["exprop"] == {}:
            del data["exprop"]
        return data

    
    def triggered(self, data={}):
        value = data.get(self.template.datakey) if self.template.datakey else None
        if value is None and self.template.name == common_affection_template.name:
            value = data.get("affection")
        if self.perf_suggestion and "suggestion" in data:
            return self.callback(data.get("suggestion"))
        if value is None and self.template.exprop.suggestion and "suggestion" in data:
            value = data.get("suggestion")
        return self.callback(value)

    def __repr__(self):
        return (
            u"Trigger(name='{}', "
            u"perf_suggestion={})".format(
                self.name, 
                self.perf_suggestion
            )
        )

    def __str__(self):
        return self.__repr__()
    def __len__(self):
        return len(json.dumps(self.build(), ensure_ascii=False))
