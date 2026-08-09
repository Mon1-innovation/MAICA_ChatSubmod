
init 999 python in maica:
    from maica_mtrigger import *
    import store
    import time
    ai = store.maica.maica_instance
    class AffTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super(AffTrigger, self).__init__(template, name, callback=callback, description = _("Intergrated | Adjust affection, 0~3 per time * 10 minutes cooldown"),method=MTriggerMethod.request)
            self.last_triggered = time.time()

        def triggered(self, data):
            self.last_triggered = time.time()
            return self.callback(data.get("alter_value", data.get("affection", 0.1)))

        def can_triggered(self):
            return (time.time() - self.last_triggered) >= 600.0

    def aff_callback(alter_value):
        #from math import ceil
        alter_value = float(alter_value)
        ai.console_logger.debug("<mtrigger> aff_callback called")
        if alter_value < 0:
            pass#store.mas_loseAffection(1, -alter_value)
        elif alter_value > 0:
            store.mas_gainAffection(1, alter_value)

    aff_trigger = AffTrigger(common_affection_template, "alter_affection", callback=aff_callback)
    aff_trigger.condition = aff_trigger.can_triggered
    ai.mtrigger_manager.add_trigger(aff_trigger)

#################################################################################

    class ClothesTrigger(MTriggerBase):
        def __init__(self, template, name):
            self.clothes_data = {store.mas_selspr.CLOTH_SEL_MAP[key].display_name:key for key in store.mas_selspr.CLOTH_SEL_MAP if self.outfit_has_and_unlocked(key)}
            self.clothes_data["玩家挑选"] = "mas_pick_a_clothes"
            self.clothes_data["__none__"] = "mas_pick_a_clothes"
            super(ClothesTrigger, self).__init__(template, name, description=_("Integrated | Changing clothes"),callback=self.clothes_callback,
                exprop=MTriggerExprop(
                    item_name_zh = "更换游戏内服装",
                    item_name_en = "change in-game outfit",
                    item_list = list(self.clothes_data.keys()),
                    curr_value = store.mas_selspr.CLOTH_SEL_MAP[store.monika_chr.clothes.name].display_name,
                ),
                action = MTriggerAction.post,
                method = MTriggerMethod.table
            )
        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.CLOTH_SEL_MAP and store.mas_selspr.CLOTH_SEL_MAP[outfit_name].unlocked

        def triggered(self, data):
            clothes = data.get("choice", None)
            if clothes is not None:
                self.callback(clothes)

        def clothes_callback(self, clothes):
            if not clothes in self.clothes_data:
                ai.console_logger.warning("<mtrigger> {} is not a vaild outfit".format(clothes))
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid outfit".format(clothes))
                return
            return store.renpy.call("mtrigger_change_clothes", self.clothes_data[clothes])

    clothes_trigger = ClothesTrigger(common_switch_template, "clothes")
    ai.mtrigger_manager.add_trigger(clothes_trigger)

#################################################################################

    unlocked_games_dict = {
        ev.prompt: ev.eventlabel
        for ev in store.mas_games.game_db.values()
        if store.mas_isGameUnlocked(ev.prompt)
    }

    unlocked_games_dict["玩家自行选择"] = "mas_pick_a_game"
    unlocked_games_dict["__none__"] = "mas_pick_a_game"
    unlocked_games_dict["Pong"] = "game_pong"
    if "NOU" in unlocked_games_dict:
        unlocked_games_dict["UNO"] = unlocked_games_dict["NOU"]
    if store.mas_isGameUnlocked("Hangman") or store.mas_isGameUnlocked("上吊小人"):
        unlocked_games_dict["Hangman"] = "game_hangman"
    def minigame_callback(item):

        if not item in unlocked_games_dict:
            ai.console_logger.warning("<mtrigger> {} is not a vaild minigame".format(item))
            store.mas_submod_utils.submod_log.error("maica: {} is not a valid minigame".format(item))
            return
        game_label = unlocked_games_dict[item]
        store.renpy.call("mttrigger_minigame", game_label)

    minigame_trigger = MTriggerBase(common_switch_template, "minigame", callback=minigame_callback,
        exprop=MTriggerExprop(
            item_name_zh="玩小游戏",
            item_name_en="play minigame",
            item_list=list(unlocked_games_dict.keys()),
            curr_value="__none__",
        ),
        description = _("Integrated | Starting minigames"),method=MTriggerMethod.table
    )
    ai.mtrigger_manager.add_trigger(minigame_trigger)


#################################################################################

    def mtrigger_kiss_condition():
        import datetime
        return store.mas_shouldKiss(1, datetime.timedelta(0))

    def mtrigger_kiss_callback(arg):
        store.renpy.call("mtrigger_kiss")

    kiss_trigger = MTriggerBase(customize_template, "kiss", condition=mtrigger_kiss_condition, callback=mtrigger_kiss_callback,
        description = _("Integrated | Call a kiss"),
        exprop = MTriggerExprop(item_name_zh = "亲吻玩家", item_name_en = "kiss player")
        )
    ai.mtrigger_manager.add_trigger(kiss_trigger)

#################################################################################

    def mtrigger_leave_callback(arg):
        ai.console_logger.debug("<mtrigger> mtrigger_leave_callback called")
        store.renpy.call("mtrigger_leave")
    leave_trigger = MTriggerBase(customize_template, "leave", callback=mtrigger_leave_callback, description=_("Integrated | Shutdown game"),method=MTriggerMethod.table,
        exprop=MTriggerExprop(item_name_zh="帮助玩家离开游戏", item_name_en="help player quit game"))
    ai.mtrigger_manager.add_trigger(leave_trigger)

#################################################################################

    def mtrigger_takeout_callback(arg):
        ai.console_logger.debug("<mtrigger> mtrigger_takeout_callback called")
        store.renpy.call("mtrigger_takeout")
    takeout_trigger = MTriggerBase(customize_template, "go_outside", callback=mtrigger_takeout_callback, description=_("Integrated | Take [m_name] out"),method=MTriggerMethod.table,
        exprop=MTriggerExprop(item_name_zh="和玩家一起出门", item_name_en="go outside with player"))
    ai.mtrigger_manager.add_trigger(takeout_trigger)

#################################################################################

    def mtrigger_idle_callback(arg):
        ai.console_logger.debug("<mtrigger> mtrigger_idle_callback called")
        store.MASEventList.push("mtrigger_brb")
        return "stop"
    idle_trigger = MTriggerBase(customize_template, "idle", callback=mtrigger_idle_callback, description=_("Integrated | Be right back"), method=MTriggerMethod.table,
        exprop=MTriggerExprop(item_name_zh="当玩家表示想要短暂离开(<1小时)时调用", item_name_en="Call when the player indicates they want to take a temporary leave (<1 hour)."))
    ai.mtrigger_manager.add_trigger(idle_trigger)

#################################################################################

    class WeatherTrigger(MTriggerBase):
        def __init__(self):
            self.weathers = self.get_weather_dict()
            self.weathers_list = self.get_weather_list()
            self.can_change = True
            super(WeatherTrigger, self).__init__(
                common_switch_template,
                "weather",
                exprop=MTriggerExprop(
                    item_name_zh="更改游戏内天气",
                    item_name_en="Change the in-game weather.r",
                    item_list=self.weathers_list,
                    curr_value=store.mas_current_weather.prompt
                ),
                callback = self.callback,
                description = _("Intergrated | Change weather * Not effective in Heaven Forest"),
                condition = self.condition
            )

        def condition(self):
            return store.mas_isMoniAff(higher=True) and self.can_change

        def build(self):
            self.weathers = self.get_weather_dict()
            self.weathers_list = self.get_weather_list()
            return super(WeatherTrigger, self).build()

        def get_weather_list(self):
            return list(self.weathers.keys())

        def get_weather_dict(self):
            import store.mas_weather as mas_weather

            # Default weather at the top
            weathers = {store.mas_weather_def.prompt: store.mas_weather_def}

            # Build and sort other weather list
            other_weathers = {
                mw_obj.prompt: mw_obj
                for mw_id, mw_obj in mas_weather.WEATHER_MAP.items()
                if mw_id != "def" and mw_obj.unlocked
            }

            # Sort by prompt and merge with default weather
            sorted_weathers = dict(sorted(other_weathers.items()))
            weathers.update(sorted_weathers)

            return weathers

        def callback(self, selection):
            selection = u"\u6674\u5929" if selection == "Clear" and u"\u6674\u5929" in self.weathers else selection
            if not selection in self.weathers:
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid weather!".format(selection))
                ai.console_logger.warning("<mtrigger> {} is not a valid weather!".format(selection))
                return
            weather = self.weathers[selection]
            store.renpy.call("mas_change_weather", weather, by_user=True, set_persistent=True)
    weather_trigger = WeatherTrigger()
    ai.mtrigger_manager.add_trigger(weather_trigger)

#################################################################################

    def mtrigger_location_condition():
        return store.mas_isMoniEnamored(True)

    def mtrigger_location_callback(arg):
        store.renpy.call("mtrigger_location")

    location_trigger = MTriggerBase(customize_template, "location", condition=mtrigger_location_condition, callback=mtrigger_location_callback,
        description = _("Integrated | Change room"), method=MTriggerMethod.table,
        exprop = MTriggerExprop(item_name_zh="切换游戏内场景/房间", item_name_en="change in-game location/room"))
    ai.mtrigger_manager.add_trigger(location_trigger)

#################################################################################

    def mtrigger_backup_condition():
        return store.mas_submod_utils.isSubmodInstalled("Extra Plus")

    def mtrigger_backup_callback(arg):
        store.renpy.call("mtrigger_backup")

    backup_trigger = MTriggerBase(customize_template, "backup", condition=mtrigger_backup_condition, callback=mtrigger_backup_callback,
        description = _("Intergrated | Backup persistent * Extra Plus Submod required"), method=MTriggerMethod.table,
        exprop=MTriggerExprop(item_name_zh="备份存档", item_name_en="backup savefile"))
    ai.mtrigger_manager.add_trigger(backup_trigger)

#################################################################################

    def mtrigger_hold_condition():
        return store.renpy.seen_label("monika_holdme_prep")

    def mtrigger_hold_callback(arg):
        store.renpy.call("mtrigger_hold")

    hold_trigger = MTriggerBase(customize_template, "hold", condition=mtrigger_hold_condition, callback=mtrigger_hold_callback,
        description = _("Integrated | Hug"), method=MTriggerMethod.table,
        exprop = MTriggerExprop(item_name_zh="拥抱玩家", item_name_en="hold player"))
    ai.mtrigger_manager.add_trigger(hold_trigger)

#################################################################################

    class MusicTrigger(MTriggerBase):
        web_musicplayer_installed = store.mas_submod_utils.isSubmodInstalled("Netease Music") or store.mas_submod_utils.isSubmodInstalled("Youtube Music")
        PLAYER_CHOICE = "玩家自行选择" if not web_musicplayer_installed else "玩家自行选择(仅在玩家明确想要自行选择时使用)"
        def __init__(self):
            self.musics = self.song_list()
            super(MusicTrigger, self).__init__(
                common_switch_template,
                "music",
                exprop=MTriggerExprop(
                    item_name_zh="播放音乐",
                    item_name_en="play music",
                    item_list=self.musics,
                    curr_value=self.current_item(),
                    suggestion=store.mas_submod_utils.isSubmodInstalled("Netease Music") or store.mas_submod_utils.isSubmodInstalled("Youtube Music")

                ),
                callback = self.callback,
                description = _("Integrated | Change BGM"),
                perf_suggestion=True,
                method = MTriggerMethod.table
            )

        def on_build_pre(self):
            self.musics = self.song_list()
            self.exprop.item_list = self.musics
            self.exprop.curr_value = self.current_item()

        def current_item(self):
            current = store.songs.current_track
            return current if isinstance(current, basestring) and current in self.musics else "__none__"

        def song_list(self):
            m = ["__none__"]
            for s in store.songs.music_choices:
                m.append(s[0])
            if (store.mas_submod_utils.isSubmodInstalled("Netease Music") or store.mas_submod_utils.isSubmodInstalled("Youtube Music")):
                pass
            m.append(self.PLAYER_CHOICE)
            m.append("停止/静音")
            return m

        def build(self):
            self.musics = self.song_list()
            return super(MusicTrigger, self).build()

        @staticmethod
        def find(selection):
            return [x for x in store.songs.music_choices if selection in x][0]

        def callback(self, selection):
            if selection == "__none__":
                return
            if selection == self.PLAYER_CHOICE:
                store.renpy.call("mtrigger_music_menu")
                return
            if not selection in self.musics:
                if selection and selection.lower() != "false":
                    if store.mas_submod_utils.isSubmodInstalled("Netease Music"):
                        store.renpy.call("mtrigger_neteasemusic_search", selection)
                        return
                    elif store.mas_submod_utils.isSubmodInstalled("Youtube Music"):
                        store.renpy.call("mtrigger_youtubemusic_search")
                        return
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid music!".format(selection))
                ai.console_logger.warning("<mtrigger> {} is not a valid music!".format(selection))
                return
            if selection == "停止/静音":
                store.mas_play_song(None)
                return

            store.renpy.call("mtrigger_music_auto", self.__class__, selection)

    music_trigger = MusicTrigger()
    ai.mtrigger_manager.add_trigger(music_trigger)

#################################################################################

    class HairTrigger(MTriggerBase):
        def __init__(self, template, name):
            self.clothes_data = {store.mas_selspr.HAIR_SEL_MAP[key].display_name:key for key in store.mas_selspr.HAIR_SEL_MAP if self.outfit_has_and_unlocked(key)}
            self.clothes_data["玩家挑选"] = "mas_pick_a_clothes"
            self.clothes_data["__none__"] = "mas_pick_a_clothes"
            super(HairTrigger, self).__init__(template, name, description=_("Integrated | Change hairstyle"),callback=self.clothes_callback,
                exprop=MTriggerExprop(
                    item_name_zh = "更换游戏内发型",
                    item_name_en = "change in-game hair",
                    item_list = list(self.clothes_data.keys()),
                    curr_value = store.mas_selspr.HAIR_SEL_MAP[store.monika_chr.hair.name].display_name,
                ),
                action = MTriggerAction.post,
                method = MTriggerMethod.table
            )

        def on_build_pre(self):
            self.exprop.curr_value = store.mas_selspr.HAIR_SEL_MAP[store.monika_chr.hair.name].display_name

        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.HAIR_SEL_MAP and store.mas_selspr.HAIR_SEL_MAP[outfit_name].unlocked

        def triggered(self, data):
            clothes = data.get("choice", None)
            if clothes is not None:
                self.callback(clothes)

        def clothes_callback(self, clothes):
            if not clothes in self.clothes_data:
                ai.console_logger.warning("<mtrigger> {} is not a vaild hair".format(clothes))
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid hair".format(clothes))
                return
            return store.renpy.call("mtrigger_change_hair", self.clothes_data[clothes])

    hair_trigger = HairTrigger(common_switch_template, "hair")
    ai.mtrigger_manager.add_trigger(hair_trigger)

#################################################################################

    class AccessoryTrigger(MTriggerBase):
        def __init__(self):
            self.accessory_data = {}
            self.refresh_accessories()
            super(AccessoryTrigger, self).__init__(common_switch_template, "accessory", description=_("Integrated | Wear or remove accessories"), callback=self.accessory_callback,
                exprop=MTriggerExprop(
                    item_name_zh = "佩戴或取下游戏内饰品",
                    item_name_en = "wear or remove an in-game accessory",
                    item_list = list(self.accessory_data.keys()),
                    curr_value = "__none__",
                ),
                action=MTriggerAction.post,
                method=MTriggerMethod.table
            )

        def outfit_has_and_unlocked(self, outfit_name):
            return outfit_name in store.mas_selspr.ACS_SEL_MAP and store.mas_selspr.ACS_SEL_MAP[outfit_name].unlocked

        def refresh_accessories(self):
            wear = {
                "wear|{}".format(store.mas_selspr.ACS_SEL_MAP[key].display_name): ("wear", key)
                for key in store.mas_selspr.ACS_SEL_MAP
                if self.outfit_has_and_unlocked(key)
            }
            unwear = {
                "unwear|{}".format(store.mas_selspr.ACS_SEL_MAP[key.name].display_name): ("unwear", key)
                for key in store.monika_chr.get_acs()
                if key.name in store.mas_selspr.ACS_SEL_MAP
            }
            self.accessory_data = {
                "__none__": (None, None),
                "wear|玩家挑选": ("wear", "mas_pick_a_clothes"),
            }
            self.accessory_data.update(wear)
            self.accessory_data.update(unwear)

        def on_build_pre(self):
            self.refresh_accessories()
            self.exprop.item_list = list(self.accessory_data.keys())

        def accessory_callback(self, choice):
            if choice not in self.accessory_data:
                ai.console_logger.warning("<mtrigger> {} is not a valid accessory".format(choice))
                store.mas_submod_utils.submod_log.error("maica: {} is not a valid accessory".format(choice))
                return
            action, accessory = self.accessory_data[choice]
            if choice == "__none__":
                return
            if action == "unwear":
                return store.renpy.call("mtrigger_unwear_acs", accessory)
            return store.renpy.call("mtrigger_change_acs", accessory)

    accessory_trigger = AccessoryTrigger()
    ai.mtrigger_manager.add_trigger(accessory_trigger)

#################################################################################

    def mtrigger_write_memory_callback(memory_item):
        addition = store.maica_validate_player_addition(
            memory_item,
            store.persistent.mas_player_additions,
            prefix_player=False
        )
        if addition is not None:
            store.persistent.mas_player_additions.append(addition)
            store._upload_persistent_dict()

    memory_trigger = MTriggerBase(
        memory_writeback_template,
        "write_memory",
        callback=mtrigger_write_memory_callback,
        method=MTriggerMethod.request,
        description = _("Integrated | Memory writing")
    )
    ai.mtrigger_manager.add_trigger(memory_trigger)
