from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    redis_url: str = "redis://localhost:6379/0"
    database_url: str
    tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    demo_mode: bool = True

    class Config:
        env_file = ".env"

settings = Settings()