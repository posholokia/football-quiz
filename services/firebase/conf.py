import os

from dotenv import load_dotenv


load_dotenv()


PROJECT_ID = os.getenv("PROJECT_ID")
JSON_CONF = os.getenv("FIREBASE_JSON_CONF")

BASE_URL = "https://firebaseremoteconfig.googleapis.com"
REMOTE_CONFIG_ENDPOINT = f"v1/projects/{PROJECT_ID}/remoteConfig"
REMOTE_CONFIG_URL = f"{BASE_URL}/{REMOTE_CONFIG_ENDPOINT}"
SCOPES = ["https://www.googleapis.com/auth/firebase.remoteconfig"]
