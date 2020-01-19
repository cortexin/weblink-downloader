from starlette.config import Config


config = Config('.env')

DATABASE_URL = config('DATABASE_URL', cast=str)
APP_SECRET = config('APP_SECRET', cast=str)
AUTH_COOKIE_TTL = config('AUTH_COOKIE_TTL', cast=int, default=3600)
