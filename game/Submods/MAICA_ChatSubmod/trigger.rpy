
init 999 python in maica:
    from maica_mtrigger import *
    import store

    class AffTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super().__init__(template, name, "triggered aff", "triggered aff", callback)
        
        def triggered(self, data):
            return self.callback(data.get("affection", 0.1))

    def aff_callback(affection):
        if affection < 0:
            store.mas_loseAffection(-affection)
        elif affection > 0:
            store.mas_gainAffection(affection)

    aff_trigger = AffTrigger(MTriggerTemplate.common_affection_template, "aff", callback=aff_callback)
    maica.mtrigger_manager.add_trigger(aff_trigger)


    class ClothesTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super().__init__(template, name, "衣服", "outfit", callback)
            self.clothes_data =  {key: store.mas_selspr.CLOTH_SEL_MAP[key].display_name for key in store.mas_selspr.CLOTH_SEL_MAP}
        
        def triggered(self, data):
            clothes = data.get("selection", None)
            if clothes is not None:
                self.callback(self.clothes_data[clothes])

    def clothes_callback(clothes):
        outfit_name = self.clothes_data[clothes]
        outfit_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_CLOTHES,
            outfit_name
        )
        if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
            _moni_chr.change_clothes(outfit_to_wear, by_user=by_user, outfit_mode=outfit_mode)

    clothes_trigger = ClothesTrigger(MTriggerTemplate.common_clothes_template, "clothes", callback=clothes_callback)
    maica.mtrigger_manager.add_trigger(clothes_trigger)




