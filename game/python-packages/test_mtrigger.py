from maica_mtrigger import *

man = MTriggerManager()

def print_callback(param):
    print(f"{param} is triggered.")

class AffTrigger(MTriggerBase):
    def __init__(self, template, name, callback):
        super().__init__(template, name, "triggered aff", "triggered aff", callback=callback)
    
    def triggered(self, data):
        return self.callback(data.get("affection", 0.2))
    

aff_trigger = AffTrigger(MTriggerTemplate.common_affection_template, "aff", callback=print_callback)

man.add_trigger(aff_trigger)

man.triggered("aff", {"affection": "+1.5"})

man.run_trigger()

