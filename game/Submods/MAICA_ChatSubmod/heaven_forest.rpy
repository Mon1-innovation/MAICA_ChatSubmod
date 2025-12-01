
define use_amim_background = persistent.maica_setting_dict.get("use_anim_background", True) if persistent.maica_setting_dict else True
# 白天
image heaven_forest_day = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets\location\heaven_forest\\day.png"

# 晚上
image heaven_forest_night = Movie(play="mod_assets\location\heaven_forest\\night.mp4", side_mask=True) if use_amim_background else "mod_assets\location\heaven_forest\\night.png"



init -1 python:
    heaven_forest = MASFilterableBackground(
        # ID
        "heaven_forest",
        "heaven_forest",

        # mapping of filters to MASWeatherMaps
        MASFilterWeatherMap(
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_day_room",
                store.mas_weather.PRECIP_TYPE_RAIN: "monika_rain_room",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "monika_rain_room",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_day",
            }),
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_room",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_night",
            }),
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_ss_room",
                store.mas_weather.PRECIP_TYPE_RAIN: "monika_rain_room_ss",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "monika_rain_room_ss",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_ss",
            }),
        ),

        # filter manager
        MASBackgroundFilterManager(
            MASBackgroundFilterChunk(
                False,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            ),
            MASBackgroundFilterChunk(
                True,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_SUNSET,
                    60,
                    30*60,
                    10,
                ),
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_DAY,
                    60
                ),
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_SUNSET,
                    60,
                    30*60,
                    10,
                ),
            ),
            MASBackgroundFilterChunk(
                False,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            )
        ),
        
        disable_progressive=True,
        unlocked=False
    )

