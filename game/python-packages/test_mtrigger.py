from maica_mtrigger import *

man = MTriggerManager()

def print_callback(param):
    print(f"{param} is triggered.")
    return "stop"

class AffTrigger(MTriggerBase):
    def __init__(self, template, name, callback):
        super().__init__(template, name, "triggered aff", "triggered aff", callback=callback, action=MTriggerAction.post)
    
    def triggered(self, data):
        return self.callback(0)
    

aff_trigger = AffTrigger(common_affection_template, "aff", callback=print_callback)

man.add_trigger(aff_trigger)

man.triggered("aff", {"affection": "+1.5"})

print(man.triggered_list)

res = man.run_trigger(action=MTriggerAction.post)
print(res)

