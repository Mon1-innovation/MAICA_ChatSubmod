
init 999 python in maica:
    from maica_mtrigger import *
    import store
    import time
    ai = store.maica.maica_instance

    def log_invalid_mtrigger(kind, value, source="callback", key=None, index=None, reason=None):
        """Log a rejected MTrigger value with bounded, actionable context."""
        if reason is None:
            reason = "callback selection is not present"
        try:
            message = (
                "[MTrigger] invalid data: trigger={} source={} key={} index={} "
                "type={} value={} reason={}".format(
                    safe_value_repr(kind, 96),
                    safe_value_repr(source, 160),
                    safe_value_repr(key, 96),
                    safe_value_repr(index, 32),
                    safe_value_repr(type(value).__name__, 64),
                    safe_value_repr(value),
                    safe_value_repr(reason, 256),
                )
            )
        except Exception:
            message = "[MTrigger] invalid data; diagnostic formatting failed"
        try:
            ai.logger_both_wrapper.warning(message)
        except Exception:
            # Logging must not turn a recoverable bad runtime entry into a crash.
            try:
                logger.warning(message)
            except Exception:
                pass

    def _add_mtrigger_item(target, trigger_name, source, display_name, mapped_value,
                           source_key=None, index=None):
        reason = add_valid_mtrigger_item(target, display_name, mapped_value)
        if reason is not None:
            log_invalid_mtrigger(
                trigger_name,
                display_name,
                source=source,
                key=source_key,
                index=index,
                reason=reason,
            )
            return False
        return True

    def _valid_mtrigger_selection(collection, trigger_name, value):
        try:
            if value in collection:
                return True
            reason = "callback selection is not present"
        except Exception as error:
            reason = "failed to check callback selection: {}".format(
                safe_value_repr(error, 160)
            )
        log_invalid_mtrigger(trigger_name, value, reason=reason)
        return False

    class AffTrigger(MTriggerBase):
        def __init__(self, template, name, callback):
            super(AffTrigger, self).__init__(template, name, callback=callback, description = _("Integrated | Adjust affection, 0~3 per time * 10 minutes cooldown"),method=MTriggerMethod.request)
            self.last_triggered = time.time()

        def triggered(self, data):
            if data is None:
                data = {}
            if not is_builtin_dict(data):
                log_invalid_mtrigger(
                    "alter_affection",
                    data,
                    source="callback payload",
                    reason="payload must be a dict",
                )
                return
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
            self.clothes_data = {}
            self.refresh_clothes()
            super(ClothesTrigger, self).__init__(template, name, description=_("Integrated | Changing clothes"),callback=self.clothes_callback,
                exprop=MTriggerExprop(
                    item_name_zh = "更换游戏内服装",
                    item_name_en = "change in-game outfit",
                    item_list = list(self.clothes_data.keys()),
                    curr_value = self.current_item(),
                ),
                action = MTriggerAction.post,
                method = MTriggerMethod.table
            )

        def refresh_clothes(self):
            self.clothes_data = {}
            _add_mtrigger_item(
                self.clothes_data,
                "clothes",
                "built-in fallback",
                "玩家挑选",
                "mas_pick_a_clothes",
            )
            _add_mtrigger_item(
                self.clothes_data,
                "clothes",
                "built-in fallback",
                "__none__",
                "mas_pick_a_clothes",
            )
            source = "store.mas_selspr.CLOTH_SEL_MAP"
            try:
                clothes_map = store.mas_selspr.CLOTH_SEL_MAP
                for index, key in enumerate(clothes_map):
                    try:
                        if not self.outfit_has_and_unlocked(key):
                            continue
                        display_name = clothes_map[key].display_name
                    except Exception as error:
                        log_invalid_mtrigger(
                            "clothes",
                            None,
                            source=source,
                            key=key,
                            index=index,
                            reason="failed to read display name: {}".format(
                                safe_value_repr(error, 160)
                            ),
                        )
                        continue
                    _add_mtrigger_item(
                        self.clothes_data,
                        "clothes",
                        source,
                        display_name,
                        key,
                        source_key=key,
                        index=index,
                    )
            except Exception as error:
                log_invalid_mtrigger(
                    "clothes",
                    clothes_map if "clothes_map" in locals() else None,
                    source=source,
                    reason="failed to enumerate source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )

        def current_item(self):
            try:
                clothes = store.monika_chr.clothes
                current = store.mas_selspr.CLOTH_SEL_MAP.get(clothes.name)
                display_name = getattr(current, "display_name", None)
                reason = mtrigger_item_error(display_name)
                if reason is not None and display_name is not None:
                    log_invalid_mtrigger(
                        "clothes",
                        display_name,
                        source="store.mas_selspr.CLOTH_SEL_MAP",
                        key=safe_getattr(clothes, "name"),
                        reason=reason,
                    )
                    return None
                if display_name in self.clothes_data:
                    return display_name
            except Exception as error:
                log_invalid_mtrigger(
                    "clothes",
                    None,
                    source="store.monika_chr.clothes",
                    reason="failed to resolve current item: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
            return None

        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.CLOTH_SEL_MAP and store.mas_selspr.CLOTH_SEL_MAP[outfit_name].unlocked

        def on_build_pre(self):
            self.refresh_clothes()
            self.exprop.item_list = list(self.clothes_data.keys())
            self.exprop.curr_value = self.current_item()

        def triggered(self, data):
            if data is None:
                return
            if not is_builtin_dict(data):
                log_invalid_mtrigger(
                    "clothes",
                    data,
                    source="callback payload",
                    reason="payload must be a dict",
                )
                return
            clothes = data.get("choice", None)
            if clothes is not None:
                self.callback(clothes)

        def clothes_callback(self, clothes):
            if not _valid_mtrigger_selection(self.clothes_data, "clothes", clothes):
                return
            return store.renpy.call("mtrigger_change_clothes", self.clothes_data[clothes])

    clothes_trigger = ClothesTrigger(common_switch_template, "clothes")
    ai.mtrigger_manager.add_trigger(clothes_trigger)

#################################################################################

    def get_unlocked_games():
        games = {}
        _add_mtrigger_item(games, "minigame", "built-in fallback", "玩家自行选择", "mas_pick_a_game")
        _add_mtrigger_item(games, "minigame", "built-in fallback", "__none__", "mas_pick_a_game")
        _add_mtrigger_item(games, "minigame", "built-in fallback", "Pong", "game_pong")
        try:
            hangman_unlocked = (
                store.mas_isGameUnlocked("Hangman")
                or store.mas_isGameUnlocked("上吊小人")
            )
        except Exception as error:
            hangman_unlocked = False
            log_invalid_mtrigger(
                "minigame",
                None,
                source="store.mas_isGameUnlocked",
                key="Hangman",
                reason="failed to check optional game: {}".format(
                    safe_value_repr(error, 160)
                ),
            )
        if hangman_unlocked:
            _add_mtrigger_item(
                games,
                "minigame",
                "built-in fallback",
                "Hangman",
                "game_hangman",
            )

        source = "store.mas_games.game_db"
        try:
            game_values = store.mas_games.game_db.values()
            for index, ev in enumerate(game_values):
                try:
                    prompt = ev.prompt
                    eventlabel = ev.eventlabel
                except Exception as error:
                    log_invalid_mtrigger(
                        "minigame",
                        None,
                        source=source,
                        key=safe_getattr(ev, "eventlabel"),
                        index=index,
                        reason="failed to read game metadata: {}".format(
                            safe_value_repr(error, 160)
                        ),
                    )
                    continue
                prompt_reason = mtrigger_item_error(prompt)
                if prompt_reason is not None:
                    log_invalid_mtrigger(
                        "minigame",
                        prompt,
                        source=source,
                        key=safe_getattr(ev, "eventlabel"),
                        index=index,
                        reason=prompt_reason,
                    )
                    continue
                label_reason = mtrigger_item_error(eventlabel)
                if label_reason is not None:
                    log_invalid_mtrigger(
                        "minigame",
                        eventlabel,
                        source=source,
                        key=safe_getattr(ev, "eventlabel"),
                        index=index,
                        reason="invalid event label: {}".format(label_reason),
                    )
                    continue
                try:
                    unlocked = store.mas_isGameUnlocked(prompt)
                except Exception as error:
                    log_invalid_mtrigger(
                        "minigame",
                        prompt,
                        source="store.mas_isGameUnlocked",
                        key=safe_getattr(ev, "eventlabel"),
                        index=index,
                        reason="failed to check unlock state: {}".format(
                            safe_value_repr(error, 160)
                        ),
                    )
                    continue
                if not unlocked:
                    continue
                _add_mtrigger_item(
                    games,
                    "minigame",
                    source,
                    prompt,
                    eventlabel,
                    source_key=safe_getattr(ev, "eventlabel"),
                    index=index,
                )
        except Exception as error:
            log_invalid_mtrigger(
                "minigame",
                None,
                source=source,
                reason="failed to enumerate source: {}".format(
                    safe_value_repr(error, 160)
                ),
            )

        if "NOU" in games:
            _add_mtrigger_item(games, "minigame", "built-in alias", "UNO", games["NOU"])
        return games

    unlocked_games_dict = get_unlocked_games()
    def minigame_callback(item):

        if item is None:
            return
        if not _valid_mtrigger_selection(unlocked_games_dict, "minigame", item):
            return
        game_label = unlocked_games_dict[item]
        store.renpy.call("mtrigger_minigame", game_label)

    class MinigameTrigger(MTriggerBase):
        def __init__(self):
            super(MinigameTrigger, self).__init__(
                common_switch_template,
                "minigame",
                callback=minigame_callback,
                exprop=MTriggerExprop(
                    item_name_zh="玩小游戏",
                    item_name_en="play minigame",
                    item_list=list(unlocked_games_dict.keys()),
                    curr_value=None,
                ),
                description = _("Integrated | Starting minigames"),
                method=MTriggerMethod.table
            )

        def on_build_pre(self):
            global unlocked_games_dict
            unlocked_games_dict = get_unlocked_games()
            self.exprop.item_list = list(unlocked_games_dict.keys())

    minigame_trigger = MinigameTrigger()
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
                    curr_value=self.current_item()
                ),
                callback = self.callback,
                description = _("Integrated | Change weather * Not effective in Heaven Forest"),
                condition = self.condition
            )

        def condition(self):
            return store.mas_isMoniAff(higher=True) and self.can_change

        def on_build_pre(self):
            self.weathers = self.get_weather_dict()
            self.weathers_list = self.get_weather_list()
            self.exprop.item_list = self.weathers_list
            self.exprop.curr_value = self.current_item()

        def current_item(self):
            try:
                current = getattr(store.mas_current_weather, "prompt", None)
            except Exception as error:
                log_invalid_mtrigger(
                    "weather",
                    None,
                    source="store.mas_current_weather",
                    reason="failed to resolve current item: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
                return None
            reason = mtrigger_item_error(current)
            if reason is not None and current is not None:
                log_invalid_mtrigger(
                    "weather",
                    current,
                    source="store.mas_current_weather.prompt",
                    reason=reason,
                )
                return None
            return current if current in self.weathers_list else None

        def get_weather_list(self):
            return list(self.weathers.keys())

        def get_weather_dict(self):
            source = "store.mas_weather.WEATHER_MAP"
            weathers = {}
            _add_mtrigger_item(
                weathers,
                "weather",
                "built-in fallback",
                "__none__",
                None,
            )
            try:
                import store.mas_weather as mas_weather
            except Exception as error:
                log_invalid_mtrigger(
                    "weather",
                    None,
                    source="store.mas_weather",
                    reason="failed to import weather source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
                return weathers

            try:
                default_weather = store.mas_weather_def
                _add_mtrigger_item(
                    weathers,
                    "weather",
                    "store.mas_weather_def",
                    default_weather.prompt,
                    default_weather,
                    source_key="def",
                    index=0,
                )
            except Exception as error:
                log_invalid_mtrigger(
                    "weather",
                    None,
                    source="store.mas_weather_def",
                    key="def",
                    index=0,
                    reason="failed to read default weather: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )

            weather_items = []
            try:
                for index, (mw_id, mw_obj) in enumerate(mas_weather.WEATHER_MAP.items()):
                    if mw_id == "def":
                        continue
                    try:
                        if not mw_obj.unlocked:
                            continue
                        prompt = mw_obj.prompt
                    except Exception as error:
                        log_invalid_mtrigger(
                            "weather",
                            None,
                            source=source,
                            key=mw_id,
                            index=index,
                            reason="failed to read weather metadata: {}".format(
                                safe_value_repr(error, 160)
                            ),
                        )
                        continue
                    reason = mtrigger_item_error(prompt)
                    if reason is not None:
                        log_invalid_mtrigger(
                            "weather",
                            prompt,
                            source=source,
                            key=mw_id,
                            index=index,
                            reason=reason,
                        )
                        continue
                    weather_items.append((prompt, mw_id, mw_obj, index))
            except Exception as error:
                log_invalid_mtrigger(
                    "weather",
                    None,
                    source=source,
                    reason="failed to enumerate source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )

            try:
                sorted_weather_items = sorted(
                    weather_items,
                    key=lambda item: item[0],
                )
            except Exception as error:
                sorted_weather_items = weather_items
                log_invalid_mtrigger(
                    "weather",
                    [item[0] for item in weather_items],
                    source=source,
                    reason="failed to sort valid entries; using source order: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )

            for prompt, mw_id, mw_obj, index in sorted_weather_items:
                _add_mtrigger_item(
                    weathers,
                    "weather",
                    source,
                    prompt,
                    mw_obj,
                    source_key=mw_id,
                    index=index,
                )

            return weathers

        def callback(self, selection):
            if selection is None:
                return
            if selection == "__none__":
                return
            selection = u"\u6674\u5929" if selection == "Clear" and u"\u6674\u5929" in self.weathers else selection
            if not _valid_mtrigger_selection(self.weathers, "weather", selection):
                return
            weather = self.weathers[selection]
            store.renpy.call("mtrigger_weather", weather)
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
        description = _("Integrated | Backup persistent * Extra Plus Submod required"), method=MTriggerMethod.table,
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
                    suggestion=self.web_musicplayer_installed

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
            try:
                current = store.songs.getPlayingMusicName()
            except Exception as error:
                log_invalid_mtrigger(
                    "music",
                    None,
                    source="store.songs.getPlayingMusicName()",
                    reason="failed to resolve current item: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
                return None
            reason = mtrigger_item_error(current)
            if reason is not None and current is not None:
                log_invalid_mtrigger(
                    "music",
                    current,
                    source="store.songs.getPlayingMusicName()",
                    reason=reason,
                )
                return None
            return current if current in self.musics else None

        def song_list(self):
            m = ["__none__"]
            seen = {"__none__": True}
            reserved = {
                "__none__": True,
                self.PLAYER_CHOICE: True,
                "停止/静音": True,
            }
            source = "store.songs.music_choices"
            try:
                music_choices = store.songs.music_choices
                for index, song in enumerate(music_choices):
                    try:
                        title = song[0]
                    except Exception as error:
                        log_invalid_mtrigger(
                            "music",
                            song,
                            source=source,
                            key=index,
                            index=index,
                            reason="entry has no usable title: {}".format(
                                safe_value_repr(error, 160)
                            ),
                        )
                        continue
                    reason = mtrigger_item_error(title)
                    if reason is not None:
                        log_invalid_mtrigger(
                            "music",
                            title,
                            source=source,
                            key=index,
                            index=index,
                            reason=reason,
                        )
                        continue
                    if title in reserved:
                        log_invalid_mtrigger(
                            "music",
                            title,
                            source=source,
                            key=index,
                            index=index,
                            reason="reserved built-in item name",
                        )
                        continue
                    if title in seen:
                        log_invalid_mtrigger(
                            "music",
                            title,
                            source=source,
                            key=index,
                            index=index,
                            reason="duplicate item name",
                        )
                        continue
                    seen[title] = True
                    m.append(title)
            except Exception as error:
                log_invalid_mtrigger(
                    "music",
                    None,
                    source=source,
                    reason="failed to enumerate source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
            for index, title in enumerate((self.PLAYER_CHOICE, "停止/静音")):
                if title in seen:
                    log_invalid_mtrigger(
                        "music",
                        title,
                        source="built-in fallback",
                        key=index,
                        index=index,
                        reason="duplicate item name",
                    )
                    continue
                reason = mtrigger_item_error(title)
                if reason is not None:
                    log_invalid_mtrigger(
                        "music",
                        title,
                        source="built-in fallback",
                        key=index,
                        index=index,
                        reason=reason,
                    )
                    continue
                seen[title] = True
                m.append(title)
            return m

        @staticmethod
        def find(selection):
            try:
                music_choices = store.songs.music_choices
            except Exception as error:
                log_invalid_mtrigger(
                    "music",
                    None,
                    source="store.songs.music_choices",
                    reason="failed to enumerate source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
                return None
            for index, song in enumerate(music_choices):
                try:
                    title = song[0]
                    path = song[1]
                    if selection != title:
                        continue
                    if not isinstance(path, basestring) or not path:
                        log_invalid_mtrigger(
                            "music",
                            path,
                            source="store.songs.music_choices",
                            key=index,
                            index=index,
                            reason="entry path must be a non-empty string",
                        )
                        return None
                    return path
                except Exception as error:
                    log_invalid_mtrigger(
                        "music",
                        song,
                        source="store.songs.music_choices",
                        key=index,
                        index=index,
                        reason="failed to resolve selected song: {}".format(
                            safe_value_repr(error, 160)
                        ),
                    )
            return None

        def callback(self, selection):
            if selection is None:
                return
            if selection == "__none__":
                return
            if selection == self.PLAYER_CHOICE:
                store.renpy.call("mtrigger_music_menu")
                return
            if not selection in self.musics:
                if isinstance(selection, basestring) and selection and selection.lower() != "false":
                    if store.mas_submod_utils.isSubmodInstalled("Netease Music"):
                        store.renpy.call("mtrigger_neteasemusic_search", selection)
                        return
                    elif store.mas_submod_utils.isSubmodInstalled("Youtube Music"):
                        store.renpy.call("mtrigger_youtubemusic_search", selection)
                        return
                log_invalid_mtrigger("music", selection)
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
            self.clothes_data = {}
            self.refresh_hair()
            super(HairTrigger, self).__init__(template, name, description=_("Integrated | Change hairstyle"),callback=self.clothes_callback,
                exprop=MTriggerExprop(
                    item_name_zh = "更换游戏内发型",
                    item_name_en = "change in-game hair",
                    item_list = list(self.clothes_data.keys()),
                    curr_value = self.current_item(),
                ),
                action = MTriggerAction.post,
                method = MTriggerMethod.table
            )

        def refresh_hair(self):
            self.clothes_data = {}
            _add_mtrigger_item(
                self.clothes_data,
                "hair",
                "built-in fallback",
                "玩家挑选",
                "mas_pick_a_clothes",
            )
            _add_mtrigger_item(
                self.clothes_data,
                "hair",
                "built-in fallback",
                "__none__",
                "mas_pick_a_clothes",
            )
            source = "store.mas_selspr.HAIR_SEL_MAP"
            try:
                hair_map = store.mas_selspr.HAIR_SEL_MAP
                for index, key in enumerate(hair_map):
                    try:
                        if self.outfit_has_and_unlocked(key):
                            display_name = hair_map[key].display_name
                        else:
                            continue
                    except Exception as error:
                        log_invalid_mtrigger(
                            "hair",
                            None,
                            source=source,
                            key=key,
                            index=index,
                            reason="failed to read display name: {}".format(
                                safe_value_repr(error, 160)
                            ),
                        )
                        continue
                    _add_mtrigger_item(
                        self.clothes_data,
                        "hair",
                        source,
                        display_name,
                        key,
                        source_key=key,
                        index=index,
                    )
            except Exception as error:
                log_invalid_mtrigger(
                    "hair",
                    hair_map if "hair_map" in locals() else None,
                    source=source,
                    reason="failed to enumerate source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
        def current_item(self):
            try:
                current = store.mas_selspr.HAIR_SEL_MAP.get(store.monika_chr.hair.name)
                display_name = getattr(current, "display_name", None)
                reason = mtrigger_item_error(display_name)
                if reason is not None and display_name is not None:
                    log_invalid_mtrigger(
                        "hair",
                        display_name,
                        source="store.mas_selspr.HAIR_SEL_MAP",
                        key=safe_getattr(
                            safe_getattr(safe_getattr(store, "monika_chr"), "hair"),
                            "name",
                        ),
                        reason=reason,
                    )
                    return None
                if current is not None and display_name in self.clothes_data:
                    return display_name
            except Exception as error:
                log_invalid_mtrigger(
                    "hair",
                    None,
                    source="store.monika_chr.hair",
                    reason="failed to resolve current item: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )
            return None

        def on_build_pre(self):
            self.refresh_hair()
            self.exprop.item_list = list(self.clothes_data.keys())
            self.exprop.curr_value = self.current_item()

        def outfit_has_and_unlocked(self, outfit_name):
            """
            Returns True if we have the outfit and it's unlocked
            """
            return outfit_name in store.mas_selspr.HAIR_SEL_MAP and store.mas_selspr.HAIR_SEL_MAP[outfit_name].unlocked

        def triggered(self, data):
            if data is None:
                return
            if not is_builtin_dict(data):
                log_invalid_mtrigger(
                    "hair",
                    data,
                    source="callback payload",
                    reason="payload must be a dict",
                )
                return
            clothes = data.get("choice", None)
            if clothes is not None:
                self.callback(clothes)

        def clothes_callback(self, clothes):
            if not _valid_mtrigger_selection(self.clothes_data, "hair", clothes):
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
                    curr_value = None,
                ),
                action=MTriggerAction.post,
                method=MTriggerMethod.table
            )

        def outfit_has_and_unlocked(self, outfit_name):
            return outfit_name in store.mas_selspr.ACS_SEL_MAP and store.mas_selspr.ACS_SEL_MAP[outfit_name].unlocked

        def refresh_accessories(self):
            self.accessory_data = {
                "__none__": (None, None),
                "wear|玩家挑选": ("wear", "mas_pick_a_clothes"),
            }
            source = "store.mas_selspr.ACS_SEL_MAP"
            try:
                accessory_map = store.mas_selspr.ACS_SEL_MAP
                for index, key in enumerate(accessory_map):
                    try:
                        if not self.outfit_has_and_unlocked(key):
                            continue
                        display_name = accessory_map[key].display_name
                        reason = mtrigger_item_error(display_name)
                        if reason is not None:
                            log_invalid_mtrigger(
                                "accessory",
                                display_name,
                                source=source,
                                key=key,
                                index=index,
                                reason=reason,
                            )
                            continue
                        item_name = "wear|{}".format(display_name)
                    except Exception as error:
                        log_invalid_mtrigger(
                            "accessory",
                            None,
                            source=source,
                            key=key,
                            index=index,
                            reason="failed to read wear metadata: {}".format(
                                safe_value_repr(error, 160)
                            ),
                        )
                        continue
                    _add_mtrigger_item(
                        self.accessory_data,
                        "accessory",
                        source,
                        item_name,
                        ("wear", key),
                        source_key=key,
                        index=index,
                    )
            except Exception as error:
                log_invalid_mtrigger(
                    "accessory",
                    None,
                    source=source,
                    reason="failed to enumerate wear source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )

            try:
                worn_accessories = store.monika_chr.get_acs()
                for index, accessory in enumerate(worn_accessories):
                    try:
                        key = accessory.name
                        if key not in store.mas_selspr.ACS_SEL_MAP:
                            continue
                        display_name = store.mas_selspr.ACS_SEL_MAP[key].display_name
                        reason = mtrigger_item_error(display_name)
                        if reason is not None:
                            log_invalid_mtrigger(
                                "accessory",
                                display_name,
                                source="store.mas_selspr.ACS_SEL_MAP",
                                key=key,
                                index=index,
                                reason=reason,
                            )
                            continue
                        item_name = "unwear|{}".format(display_name)
                    except Exception as error:
                        log_invalid_mtrigger(
                            "accessory",
                            accessory,
                            source="store.monika_chr.get_acs()",
                            key=safe_getattr(accessory, "name"),
                            index=index,
                            reason="failed to read unwear metadata: {}".format(
                                safe_value_repr(error, 160)
                            ),
                        )
                        continue
                    _add_mtrigger_item(
                        self.accessory_data,
                        "accessory",
                        "store.monika_chr.get_acs()",
                        item_name,
                        ("unwear", accessory),
                        source_key=key,
                        index=index,
                    )
            except Exception as error:
                log_invalid_mtrigger(
                    "accessory",
                    None,
                    source="store.monika_chr.get_acs()",
                    reason="failed to enumerate unwear source: {}".format(
                        safe_value_repr(error, 160)
                    ),
                )

        def on_build_pre(self):
            self.refresh_accessories()
            self.exprop.item_list = list(self.accessory_data.keys())

        def accessory_callback(self, choice):
            if choice is None:
                return
            if not _valid_mtrigger_selection(self.accessory_data, "accessory", choice):
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
