from os import getenv
from dotenv import load_dotenv

load_dotenv("./.env")


class Settings:
    @property
    def openrouter_api_key(self):
        return getenv("OPENROUTER_API_KEY", "")

    @property
    def groq_api_key(self):
        return getenv("OPENROUTER_API_KEY", "")

    @property
    def openai_api_key(self):
        return getenv("OPENAI_API_KEY", "")


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
