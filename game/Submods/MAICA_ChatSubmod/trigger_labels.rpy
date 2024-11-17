label mtrigger_change_clothes(outfit_name):
    call mas_transition_to_emptydesk

    python:
        renpy.pause(1.0, hard=True)

        outfit_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_CLOTHES,
            outfit_name
        )
        if outfit_to_wear is not None and store.mas_SELisUnlocked(outfit_to_wear):
            store.monika_chr.change_clothes(outfit_to_wear, by_user=True, outfit_mode=True)

        renpy.pause(4.0, hard=True)

    call mas_transition_from_emptydesk("monika 1eua")