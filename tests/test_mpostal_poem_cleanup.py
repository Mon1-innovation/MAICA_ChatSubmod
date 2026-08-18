from pathlib import Path


def test_mpostal_response_poem_is_removed_after_display():
    main_source = (
        Path(__file__).resolve().parents[1]
        / "game"
        / "Submods"
        / "MAICA_ChatSubmod"
        / "main.rpy"
    ).read_text(encoding="utf-8")
    show_label = main_source[
        main_source.index('label maica_mpostal_show(content = "no content"):'):
        main_source.index("label maica_mpostal_show_backtoscreen")
    ]

    display_call = 'call mas_showpoem(store._MP, "mod_assets/poem_assets/mail_maica_bg.png")'
    poem_map_removal = "store.mas_poems.poem_map.pop(store._MP.poem_id, None)"
    seen_removal = "persistent._mas_poems_seen.pop(store._MP.poem_id, None)"

    assert display_call in show_label
    assert poem_map_removal in show_label
    assert seen_removal in show_label
    assert show_label.index(display_call) < show_label.index(poem_map_removal)
    assert show_label.index(poem_map_removal) < show_label.index(seen_removal)


def test_mpostal_reread_uses_the_game_scene_and_restores_the_history_menu():
    root = Path(__file__).resolve().parents[1]
    main_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "main.rpy"
    ).read_text(encoding="utf-8")
    screen_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs.rpy"
    ).read_text(encoding="utf-8")

    back_to_screen = main_source[
        main_source.index("label maica_mpostal_show_backtoscreen"):
        main_source.index("label _maica_return_game_menu")
    ]
    for screen_name in (
        "maica_mpostals",
        "maica_setting",
        "maica_setting_tooltip",
        "submods",
    ):
        assert "hide screen {}".format(screen_name) in back_to_screen
    assert "with None" in back_to_screen
    assert "call maica_mpostal_show(content)" in back_to_screen

    reread_menu = screen_source[
        screen_source.index("screen maica_mpostals():"):
        screen_source.index("screen maica_support():")
    ]
    assert reread_menu.count("_maica_call_in_new_context_preserve_layers") == 2
    reread_actions = reread_menu[
        reread_menu.index('textbutton _("Read [player]'):
        reread_menu.index('if postal["responsed_status"]')
    ]
    assert "Hide(\"maica_mpostals\")" not in reread_actions

    # The old event-queue callback reopened the settings context after a poem.
    assert "label maica_mpostal_show_mpscreen" not in main_source
    assert 'functionplugin("maica_mpostal_show_backtoscreen")' not in main_source


def test_mpostal_attachment_moves_to_private_cache_only_after_successful_read():
    root = Path(__file__).resolve().parents[1]
    api_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"
    ).read_text(encoding="utf-8")
    main_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "main.rpy"
    ).read_text(encoding="utf-8")

    assert "mpostal_cache" in api_source
    assert "def cache_mpostal_image(postal):" in api_source
    assert "def delete_mpostal_image(postal):" in api_source
    assert "shutil.move" in api_source
    assert "os.path.relpath" in api_source
    assert "cache_mpostal_image(cur_postal)" in main_source
    assert main_source.index('cur_postal["responsed_status"] = "received"') < main_source.index(
        "cache_mpostal_image(cur_postal)"
    )
    assert main_source.index("if ai.response_timed_out():") < main_source.index(
        "cache_mpostal_image(cur_postal)"
    )


def test_mpostal_delete_action_cleans_only_the_private_attachment_cache():
    root = Path(__file__).resolve().parents[1]
    api_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "api.rpy"
    ).read_text(encoding="utf-8")
    screen_source = (
        root / "game" / "Submods" / "MAICA_ChatSubmod" / "screen_subs.rpy"
    ).read_text(encoding="utf-8")

    assert "delete_mpostal_image(item)" in screen_source
    assert "os.remove(image_path)" in api_source
    assert "relative_path != os.pardir" in api_source
    assert "relative_path.startswith(os.pardir + os.sep)" in api_source
