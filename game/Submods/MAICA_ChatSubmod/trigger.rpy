
init 999 python in maica:
    from maica_mtrigger import *
    import store
    class AffTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super(AffTrigger, self).__init__(template, name, "triggered aff", "triggered aff", callback=callback, description = "好感调整trigger", exprop=MTriggerExprop(value_limits=[-1, 3]))
        
        def triggered(self, data):
            return self.callback(data.get("affection", 0.1))

    def aff_callback(affection):
        maica.send_to_outside_func("<mtrigger> aff_callback called")
        if affection < 0:
            store.mas_loseAffection(-affection)
        elif affection > 0:
            store.mas_gainAffection(affection)

    aff_trigger = AffTrigger(common_affection_template, "alter_affection", callback=aff_callback)
    maica.mtrigger_manager.add_trigger(aff_trigger)

#################################################################################

    class ClothesTrigger(MTriggerBase):
        def __init__(self, template, name):
            self.clothes_data = {key: store.mas_selspr.CLOTH_SEL_MAP[key].name for key in store.mas_selspr.CLOTH_SEL_MAP if self.outfit_has_and_unlocked(key)}
            super(ClothesTrigger, self).__init__(template, name, "衣服", "clothes", description="衣服调整trigger",callback=self.clothes_callback, 
                exprop=MTriggerExprop(
                    item_name_zh = "衣服",
                    item_name_en = "outfit",
                    item_list = self.clothes_data.keys(),
                    curr_value = store.monika_chr.clothes.name,
                ),
                action = MTriggerAction.post
            )
        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.CLOTH_SEL_MAP and store.mas_selspr.CLOTH_SEL_MAP[outfit_name].unlocked

        def triggered(self, data):
            clothes = data.get("selection", None)
            if clothes is not None:
                self.callback(self.clothes_data[clothes])

        def clothes_callback(self, clothes):
            maica.send_to_outside_func("<mtrigger> clothes_callback called")
            return store.renpy.call("mtrigger_change_clothes", clothes)
            outfit_name = self.clothes_data[clothes]
            outfit_to_wear = store.mas_sprites.get_sprite(
                store.mas_sprites.SP_CLOTHES,
                outfit_name
            )
            if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
                pass
                #store.monika_chr.change_clothes(outfit_to_wear, by_user=True, outfit_mode=True)

    clothes_trigger = ClothesTrigger(common_switch_template, "clothes")
    maica.mtrigger_manager.add_trigger(clothes_trigger)

#################################################################################

    unlocked_games_dict = {
        ev.prompt: ev.eventlabel
        for ev in store.mas_games.game_db.values()
        if store.mas_isGameUnlocked(ev.prompt)
    }

    def minigame_callback(item):
        maica.send_to_outside_func("<mtrigger> minigame_callback called")
        game_label = unlocked_games_dict[item]
        store.renpy.call(game_label)
    
    minigame_trigger = MTriggerBase(common_switch_template, "minigame", "玩小游戏", "play minigame", callback=minigame_callback,
        exprop=MTriggerExprop(
            item_name_zh="小游戏",
            item_name_en="minigame",
            item_list=unlocked_games_dict.keys(),
        ))
    maica.mtrigger_manager.add_trigger(minigame_trigger)
    

#################################################################################






