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
