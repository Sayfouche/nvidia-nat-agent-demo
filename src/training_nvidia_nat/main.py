import os
from pathlib import Path

from dotenv import load_dotenv

NVIDIA_API_KEY_ENV = "NVIDIA_API_KEY"


def load_nvidia_api_key(dotenv_path: str | Path = ".env") -> str | None:
    load_dotenv(dotenv_path=dotenv_path)
    return os.getenv(NVIDIA_API_KEY_ENV)


def main() -> None:
    api_key = load_nvidia_api_key()
    print("API key loaded:", "Yes" if api_key else "No")


if __name__ == "__main__":
    main()
