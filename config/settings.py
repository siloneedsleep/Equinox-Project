import os

LUMINOUS_TOKEN = os.environ.get("LUMINOUS_TOKEN")
TENEBRIS_TOKEN = os.environ.get("TENEBRIS_TOKEN")

LUMINOUS_CLIENT_ID = os.environ.get("LUMINOUS_CLIENT_ID")
LUMINOUS_CLIENT_SECRET = os.environ.get("LUMINOUS_CLIENT_SECRET")

TENEBRIS_CLIENT_ID = os.environ.get("TENEBRIS_CLIENT_ID")
TENEBRIS_CLIENT_SECRET = os.environ.get("TENEBRIS_CLIENT_SECRET")

OAUTH2_REDIRECT_URI = os.environ.get("OAUTH2_REDIRECT_URI")
REDIS_URI = os.environ.get("REDIS_URI")

OWNER_ID = int(os.environ.get("OWNER_ID", 0))
PORT = int(os.environ.get("PORT", 8000))
