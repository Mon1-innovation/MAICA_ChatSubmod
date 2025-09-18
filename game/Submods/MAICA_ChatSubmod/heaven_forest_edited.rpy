




















image heaven_forest_d_day = "mod_assets/location/heaven_forest_2/disruption_classroom.jpg"
image heaven_forest_d_rain = "mod_assets/location/heaven_forest_2/disruption_classroom.jpg"
image heaven_forest_d_overcast = "mod_assets/location/heaven_forest_2/disruption_classroom.jpg"
image heaven_forest_d_snow = "mod_assets/location/heaven_forest_2/disruption_classroom.jpg"


image heaven_forest_d_night = "mod_assets/location/heaven_forest_2/disruption_classroom_n.jpg"
image heaven_forest_d_rain_night = "mod_assets/location/heaven_forest_2/disruption_classroom_n.jpg"
image heaven_forest_d_overcast_night = "mod_assets/location/heaven_forest_2/disruption_classroom_n.jpg"
image heaven_forest_d_snow_night = "mod_assets/location/heaven_forest_2/disruption_classroom_n.jpg"


image heaven_forest_d_ss = "mod_assets/location/heaven_forest_2/disruption_classroom_ss.jpg"
image heaven_forest_d_rain_ss = "mod_assets/location/heaven_forest_2/disruption_classroom_ss.jpg"
image heaven_forest_d_overcast_ss = "mod_assets/location/heaven_forest_2/disruption_classroom_ss.jpg"
image heaven_forest_d_snow_ss = "mod_assets/location/heaven_forest_2/disruption_classroom_ss.jpg"




























init -1 python:
    heaven_forest_d = MASFilterableBackground(
        "heaven_forest_d",
        "破碎树林",
        MASFilterWeatherMap(
            
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_d_day",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_d_rain",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_d_overcast",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_d_snow",
            }),
            
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_d_night",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_d_rain_night",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_d_overcast_night",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_d_snow_night",
            }),
            
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "heaven_forest_d_ss",
                store.mas_weather.PRECIP_TYPE_RAIN: "heaven_forest_d_rain_ss",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "heaven_forest_d_overcast_ss",
                store.mas_weather.PRECIP_TYPE_SNOW: "heaven_forest_d_2_snow_ss",
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
