import logging
import copy

maica_default_dict = {
    "auto_reconnect": False,
    "maica_model": None,
    "use_custom_model_config": False,
    "sf_extraction": True,
    "chat_session": 1,
    "console": True,
    "console_font": "maica_confont",
    "target_lang": None,
    "_event_pushed": False,
    "mspire_enable": True,
    "mspire_category": [],
    "mspire_interval": 60,
    "mspire_session": 0,
    "log_level": logging.DEBUG,
}

maica_advanced_setting = {
    "top_p": 0.7,
    "temperature": 0.4,
    "max_tokens": 1024,
    "frequency_penalty": 0.3,
    "presence_penalty": 0.0,
    "seed": 0.0,
    "mf_aggressive": False,
    "sfe_aggressive": False,
    "tnd_aggressive": 1,
    "esc_aggressive": True,
}

class AdvancedSettings:
    def __init__(self, default_settings):
        self._defaults = default_settings
        self._settings = {}

    def __getattr__(self, name):
        if name in self._settings:
            return self._settings[name]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        if name in ("_defaults", "_settings"):
            super().__setattr__(name, value)
        else:
            self._settings[name] = value

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def reset(self):
        self._settings.clear()

    def import_settings(self, settings_dict):
        self._settings.update(settings_dict)

    def export_settings(self):
        return copy.deepcopy(self._settings)

class Settings:
    def __init__(self, default_settings, advanced_settings):
        self._defaults = default_settings
        self._settings = {}
        self.advanced = AdvancedSettings(advanced_settings)

    def __getattr__(self, name):
        if name in self._settings:
            return self._settings[name]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        if name in ("_defaults", "_settings", "advanced"):
            super().__setattr__(name, value)
        else:
            self._settings[name] = value

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def reset(self):
        self._settings.clear()

    def import_settings(self, settings_dict):
        self._settings.update(settings_dict)

    def export_settings(self):
        return copy.deepcopy(self._settings)

# Example of usage:
settings = Settings(maica_default_dict, maica_advanced_setting)
print(settings.auto_reconnect)  # False by default
settings.auto_reconnect = True
print(settings.auto_reconnect)  # True

print(settings.advanced.top_p)  # 0.7 by default
settings.advanced.top_p = 0.9
print(settings.advanced.top_p)  # 0.9

settings.import_settings({"auto_reconnect": False, "chat_session": 2})
print(settings.auto_reconnect)  # False
print(settings.chat_session)    # 2

print(settings.export_settings())  # Current settings excluding defaults

settings.reset()
print(settings.auto_reconnect)  # False, back to default