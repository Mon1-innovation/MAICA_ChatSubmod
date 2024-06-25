EMOTE_DICT = {}

def set_emotedata(dict):
    global EMOTE_DICT
    EMOTE_DICT = dict

def add_emotedata(dict):
    global EMOTE_DICT
    EMOTE_DICT |= dict

class MoodStatus(object):
    MOOD_STATUS = {}