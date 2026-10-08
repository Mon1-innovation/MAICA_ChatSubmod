from __future__ import unicode_literals

import json


PLAYER_ADDITIONS_KEY = "mas_player_additions"
PLAYER_ADDITIONS_MAX_ITEMS = 512
PLAYER_ADDITION_MAX_BYTES = 1536

PERSISTENT_UPLOAD_KEYS = (
    "mas_playername",
    "mas_monikaname",
    "mas_player_bday",
    "mas_affection",
    "mas_geolocation",
    "mas_player_additions",
    "target_lang",
    "_mas_pm_added_custom_bgm",
    "_mas_pm_religious",
    "_mas_pm_cares_about_dokis",
    "_mas_pm_love_yourself",
    "_mas_pm_like_mint_ice_cream",
    "_mas_pm_likes_horror",
    "_mas_pm_likes_spoops",
    "_mas_pm_like_rap",
    "_mas_pm_like_rock_n_roll",
    "_mas_pm_like_jazz",
    "_mas_pm_like_vocaloids",
    "_mas_pm_like_orchestral_music",
    "_mas_pm_like_other_music",
    "_mas_pm_like_other_music_history",
    "_mas_pm_plays_instrument",
    "_mas_pm_play_jazz",
    "_mas_pm_likes_rain",
    "_mas_pm_a_hater",
    "_mas_pm_has_contributed_to_mas",
    "_mas_pm_wants_to_contribute_to_mas",
    "_mas_pm_drawn_art",
    "_mas_pm_lang_other",
    "_mas_pm_lang_jpn",
    "_mas_pm_eye_color",
    "_mas_pm_hair_color",
    "_mas_pm_hair_length",
    "_mas_pm_shaved_hair",
    "_mas_pm_no_hair_no_talk",
    "_mas_pm_skin_tone",
    "_mas_pm_height",
    "_mas_pm_units_height_metric",
    "_mas_pm_shared_appearance",
    "_mas_pm_would_like_mt_peak",
    "_mas_pm_live_in_city",
    "_mas_pm_live_near_beach",
    "_mas_pm_live_south_hemisphere",
    "_mas_pm_gets_snow",
    "_mas_pm_social_personality",
    "_mas_pm_likes_panties",
    "_mas_pm_no_talk_panties",
    "_mas_pm_drinks_soda",
    "_mas_pm_eat_fast_food",
    "_mas_pm_wearsRing",
    "_mas_pm_like_playing_sports",
    "_mas_pm_like_playing_tennis",
    "_mas_pm_meditates",
    "_mas_pm_see_therapist",
    "_mas_pm_watch_mangime",
    "_mas_pm_do_smoke",
    "_mas_pm_do_smoke_quit",
    "_mas_pm_do_smoke_quit_succeeded_before",
    "_mas_pm_driving_can_drive",
    "_mas_pm_driving_learning",
    "_mas_pm_driving_been_in_accident",
    "_mas_pm_driving_post_accident",
    "_mas_pm_donate_charity",
    "_mas_pm_volunteer_charity",
    "_mas_pm_have_fam",
    "_mas_pm_no_fam_bother",
    "_mas_pm_have_fam_mess",
    "_mas_pm_have_fam_mess_better",
    "_mas_pm_have_fam_sibs",
    "_mas_pm_no_talk_fam",
    "_mas_pm_fam_like_monika",
    "_mas_pm_gone_to_prom",
    "_mas_pm_no_prom",
    "_mas_pm_prom_good",
    "_mas_pm_had_prom_date",
    "_mas_pm_prom_monika",
    "_mas_pm_prom_not_interested",
    "_mas_pm_prom_shy",
    "_mas_pm_has_been_to_amusement_park",
    "_mas_pm_likes_travelling",
    "_mas_pm_had_relationships_many",
    "_mas_pm_had_relationships_just_one",
    "_mas_pm_read_yellow_wp",
    "_mas_pm_monika_evil",
    "_mas_pm_monika_evil_but_ok",
    "_mas_pm_is_bullying_victim",
    "_mas_pm_has_bullied_people",
    "_mas_pm_currently_bullied",
    "_mas_pm_has_friends",
    "_mas_pm_few_friends",
    "_mas_pm_feels_lonely_sometimes",
    "_mas_pm_listened_to_grad_speech",
    "_mas_grad_speech_timed_out",
    "_mas_pm_liked_grad_speech",
    "_mas_pm_given_false_justice",
    "_mas_pm_monika_deletion_justice",
    "_mas_monika_deletion_justice_kidding",
    "_mas_pm_would_come_to_spaceroom",
    "_mas_pm_owns_car",
    "_mas_pm_owns_car_type",
    "_mas_pm_has_code_experience",
    "_mas_pm_likes_poetry",
    "_mas_pm_likes_board_games",
    "_mas_pm_works_out",
    "_mas_pm_likes_nature",
    "_mas_pm_swear_frequency",
    "_mas_gender",
    "_mas_bday_said_happybday",
    "_mas_f14_spent_f14",
    "_mas_nye_spent_nye",
    "_mas_nye_spent_nyd",
    "_mas_player_bday_spent_time",
    "_mas_d25_spent_d25",
    "_mas_o31_tt_count",
    "sessions",
)

try:
    TEXT_TYPES = (basestring,)
except NameError:
    TEXT_TYPES = (str,)


def select_monika_nickname(persistent_value, runtime_value=None):
    """Prefer MAS's persistent nickname and reject its temporary hidden-name value."""
    for value in (persistent_value, runtime_value):
        if not isinstance(value, TEXT_TYPES):
            continue
        if not value.strip() or value == "???":
            continue
        return value
    return None


class PlayerAdditionsValidationError(ValueError):
    def __init__(self, code, reason, index=None):
        self.code = code
        self.reason = reason
        self.index = index
        if index is None:
            message = reason
        else:
            message = "item {}: {}".format(index, reason)
        ValueError.__init__(self, message)


def utf8_byte_length(value):
    if isinstance(value, bytes):
        return len(value)
    if isinstance(value, TEXT_TYPES):
        return len(value.encode("utf-8"))
    return len(str(value).encode("utf-8"))


def validate_player_addition_item(value, bytes_limit=PLAYER_ADDITION_MAX_BYTES, index=None):
    if not isinstance(value, TEXT_TYPES):
        raise PlayerAdditionsValidationError("invalid_type", "must be text", index)
    try:
        value_bytes = utf8_byte_length(value)
    except UnicodeError:
        raise PlayerAdditionsValidationError(
            "invalid_encoding",
            "cannot be encoded as UTF-8",
            index,
        )
    if value_bytes > bytes_limit:
        raise PlayerAdditionsValidationError(
            "too_long",
            "uses {} UTF-8 bytes; maximum is {}".format(value_bytes, bytes_limit),
            index,
        )
    return value


def validate_player_additions(values):
    if not isinstance(values, list):
        raise PlayerAdditionsValidationError(
            "invalid_container",
            "container must be a list",
        )
    if len(values) > PLAYER_ADDITIONS_MAX_ITEMS:
        raise PlayerAdditionsValidationError(
            "too_many",
            "contains {} items; maximum is {}".format(
                len(values),
                PLAYER_ADDITIONS_MAX_ITEMS,
            )
        )
    for index, value in enumerate(values):
        validate_player_addition_item(value, index=index)
    return values


def _sanitize_value(value, allowed_keys, depth=0):
    if depth > 3:
        return "REMOVED|TOO_DEEP"
    if value is None:
        return None
    if isinstance(value, dict):
        return {
            key: _sanitize_value(item, allowed_keys, depth + 1)
            for key, item in value.items()
            if key in allowed_keys
        }
    if isinstance(value, (list, tuple)):
        return [_sanitize_value(item, allowed_keys, depth + 1) for item in value]
    try:
        json.dumps(value)
        return value
    except Exception:
        return "REMOVED|UNSERIALIZABLE"


def sanitize_persistent_dict(values, allowed_keys=PERSISTENT_UPLOAD_KEYS):
    if not isinstance(values, dict):
        raise TypeError("persistent upload source must be a dictionary")

    allowed_keys = frozenset(allowed_keys)
    sanitized = {}
    for key, value in values.items():
        if key not in allowed_keys:
            continue
        if key == PLAYER_ADDITIONS_KEY:
            validate_player_additions(value)
            sanitized[key] = list(value)
        else:
            sanitized[key] = _sanitize_value(value, allowed_keys)
    return sanitized
