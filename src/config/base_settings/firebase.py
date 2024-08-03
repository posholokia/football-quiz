from pydantic import Field
from pydantic_settings import BaseSettings


class FirebaseConf(BaseSettings):
    firebase_json_conf: str
    project_id: str
    base_url: str = Field(
        default="https://firebaseremoteconfig.googleapis.com"
    )
    scopes: list[str] = [
        "https://www.googleapis.com/auth/firebase.remoteconfig"
    ]

    @property
    def remote_config_endpoint(self):
        return f"v1/projects/{self.project_id}/remoteConfig"

    @property
    def remote_config_url(self):
        return f"{self.base_url}/{self.remote_config_endpoint}"
