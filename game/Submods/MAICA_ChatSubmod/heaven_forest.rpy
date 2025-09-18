


















define use_amim_background = persistent.maica_setting_dict.get("use_anim_background", True) if persistent.maica_setting_dict else True

image heaven_forest_day = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"
image heaven_forest_rain = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"
image heaven_forest_overcast = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"
image heaven_forest_snow = Movie(play="mod_assets/location/heaven_forest/heaven_classroom.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom.jpg"


image heaven_forest_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"
image heaven_forest_rain_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"
image heaven_forest_overcast_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"
image heaven_forest_snow_night = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_n.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_n.jpg"


image heaven_forest_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"
image heaven_forest_rain_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"
image heaven_forest_overcast_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"
image heaven_forest_snow_ss = Movie(play="mod_assets/location/heaven_forest/heaven_classroom_ss.webm", side_mask=True) if use_amim_background else "mod_assets/location/heaven_forest/heaven_classroom_ss.jpg"




























init -1 python:
    heaven_forest = MASFilterableBackground(
        "heaven_forest",
        "天堂树林",
        MASFilterWeatherMap(
            
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_day",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_rain",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_overcast",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_snow",
            }),
            
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_night",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_rain_night",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_overcast_night",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_snow_night",
            }),
            
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_ss",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_rain_ss",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_overcast_ss",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_snow_ss",
            }),
        ),


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
        hide_masks=True,             
        hide_calendar=True,          
        unlocked=False,                
        ex_props={"skip_outro": None}           
    )
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
