import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-desarrollo-cocomo-ii")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
