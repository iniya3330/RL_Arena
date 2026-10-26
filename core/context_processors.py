from .i18n import SPEECH_LANGUAGE, get_language, strings_for
from .level_bank import TOTAL_LEVELS


def interface(request):
    """Translated interface strings, available to every template as {{ i18n }}."""
    lang = get_language(request)
    return {"i18n": {
        "lang": lang,
        "speech": SPEECH_LANGUAGE[lang],
        "total": TOTAL_LEVELS,
        "strings": strings_for(lang),
    }}
