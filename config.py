import os

class Config:
    SECRET_KEY = "super_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 🔑 Only OpenAI key
    OPENAI_API_KEY = "your_openai_api_key_here"
