from rest_framework.permissions import AllowAny
from rest_framework.settings import APISettings

USER_SETTINGS = None
DEFAULTS = {
    "REGISTER_SERIALIZER": "accounts.serializers.SignUpSerializer",
    "REGISTER_PERMISSION_CLASSES": [AllowAny],
    "USE_JWT": False,
    "JWT_SERIALIZER": None,
    "TOKEN_SERIALIZER": "rest_framework.authtoken.serializers.TokenSerializer",
    "TOKEN_CREATOR": None,
}
IMPORT_STRINGS = [
    "REGISTER_SERIALIZER",
    "JWT_SERIALIZER",
    "TOKEN_SERIALIZER",
]

api_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
