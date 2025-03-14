from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class KayzenConfig(BaseModel):
    """Kayzen API configuration"""
    user_name: str = os.getenv("KAYZEN_USERNAME", "")
    password: str = os.getenv("KAYZEN_PASSWORD", "")
    basic_auth_token: str = os.getenv("KAYZEN_BASIC_AUTH", "")
    base_url: str = "https://api.kayzen.io/v1"

config = KayzenConfig()

if not config.user_name or not config.password or not config.basic_auth_token:
    raise ValueError("KAYZEN_USERNAME, KAYZEN_PASSWORD, and KAYZEN_BASIC_AUTH must be set in environment variables")
