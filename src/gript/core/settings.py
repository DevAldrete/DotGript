from os import getenv
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv("./.env")


class Settings(BaseSettings):
    openrouter_api_key: str | None  = getenv("OPENROUTER_API_KEY")
    groq_api_key: str | None = getenv("GROQ_API_KEY")
    openai_api_key: str | None = getenv("OPENAI_API_KEY")
    anthropic_api_key: str | None = getenv("ANTHROPIC_API_KEY")
    grok_api_key: str | None = getenv("GROK_API_KEY")
    groq_api_key: str | None = getenv("GROQ_API_KEY")
    custom_base_url: str | None = getenv("CUSTOM_BASE_URL")



settings = Settings()


def main():
    print("GROQ:\n")
    print(settings.groq_api_key)
    print("OPENROUTER:\n")
    print(settings.openrouter_api_key)
    print("OPENAI:\n")
    print(settings.openai_api_key)


if __name__ == "__main__":
    main()
