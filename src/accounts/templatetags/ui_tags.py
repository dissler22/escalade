from django import template

register = template.Library()

_MESSAGE_LEVEL_FR = {
    "success": "Succès",
    "error": "Erreur",
    "warning": "Attention",
    "info": "Information",
    "debug": "Détail",
}


@register.filter
def message_level_fr(tag: str) -> str:
    key = (tag or "").strip().lower()
    if key in _MESSAGE_LEVEL_FR:
        return _MESSAGE_LEVEL_FR[key]
    if key:
        return key.replace("_", " ").capitalize()
    return "Message"
