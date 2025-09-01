import json

from src.config import PATH_TO_RESOURCES


def get_image_path(name: str) -> str:
    return str(PATH_TO_RESOURCES / "images" / f"{name}.jpg")


def load_message(name: str) -> str:
    path = PATH_TO_RESOURCES / "messages" / f"{name}.txt"
    with open(path, encoding="utf-8", errors="replace") as file:
        return file.read()

def load_prompt(name: str) -> str:
    path = PATH_TO_RESOURCES / "prompts" / f"{name}.txt"
    with open(path, encoding="utf-8") as file:
        return file.read()

def load_image(name: str) -> bytes:
    path = PATH_TO_RESOURCES / "images" / f"{name}.jpg"
    with open(path, mode="rb") as file:
        return file.read()

def load_personalities(name: str) -> dict:
    path = PATH_TO_RESOURCES / "talk" / f"{name}.json"
    with open(path, encoding="utf-8") as file:
        content = file.read()
        return json.loads(content)


def load_topics(name: str) -> dict:
    path = PATH_TO_RESOURCES / "quiz" / f"{name}.json"
    with open(path, encoding="utf-8") as file:
        content = file.read()
        return json.loads(content)

def load_translate_lang(name: str) -> dict:
    path = PATH_TO_RESOURCES / "translate" / f"{name}.json"
    with open(path, encoding="utf-8") as file:
        content = file.read()
        return json.loads(content)