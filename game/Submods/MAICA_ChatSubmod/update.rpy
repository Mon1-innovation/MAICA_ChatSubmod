label maica_update_v0_2_7(version="v0_2_6"):
    return


label maica_update_v0_2_8(version="v0_2_7"):
    python:
        mas_setEVLPropValues('maica_chr', conditional="renpy.seen_label('maica_end_1')")
        mas_setEVLPropValues('maica_wants_preferences', conditional="renpy.seen_label('maica_end_1')")
    return