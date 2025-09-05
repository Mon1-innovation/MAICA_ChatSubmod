from maica_mtrigger import *

man = MTriggerManager()
def _(str):
    return str
def print_callback(param):
    print(f"{param} is triggered.")
    return "stop"

class AffTrigger(MTriggerBase):
    def __init__(self, template, name, callback):
        super().__init__(template, name, "triggered aff", "triggered aff", callback=callback, action=MTriggerAction.post)
    
    def triggered(self, data):
        return self.callback(0)
    

#aff_trigger = AffTrigger(common_affection_template, "aff", callback=print_callback)
leave_trigger = MTriggerBase(customize_template, "leave", callback=print_callback, description=_("内置 | 关闭游戏"),method=MTriggerMethod.table,
    exprop=MTriggerExprop(item_name_zh="帮助玩家离开游戏", item_name_en="help player quit game"))
#man.add_trigger(aff_trigger)
man.add_trigger(leave_trigger)

man.triggered("aff", {"affection": "+1.5"})
man.triggered("leave")

print(man.triggered_list)
print(leave_trigger.build())

res = man.run_trigger(action=MTriggerAction.post)
print(res)

