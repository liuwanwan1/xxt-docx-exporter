import json
import os
from json import JSONDecodeError


def project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def default_answers_path() -> str:
    return os.path.join(project_root(), "answers")


def answer_json_files(answers_path: str | None = None) -> list[str]:
    path = answers_path or default_answers_path()
    if not os.path.isdir(path):
        return []
    return sorted(file for file in os.listdir(path) if file.lower().endswith(".json"))


def read_answer_json(file_path: str) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return dict(json.loads(file.read()))


def write_answer_json(answer: list, info: dict, answers_path: str | None = None) -> str:
    path = answers_path or default_answers_path()
    os.makedirs(path, exist_ok=True)
    data = {
        info["id"]: answer,
        "info": info,
    }
    file_path = os.path.join(path, f"{info['id']}.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
    return file_path


def load_answer_file_infos(answers_path: str | None = None) -> list[dict]:
    path = answers_path or default_answers_path()
    infos = []
    for file_name in answer_json_files(path):
        file_path = os.path.join(path, file_name)
        try:
            info = read_answer_json(file_path).get("info")
        except (OSError, JSONDecodeError, TypeError, ValueError):
            continue
        if not isinstance(info, dict):
            continue
        infos.append({**info, "file_name": file_name, "file_path": file_path})
    return infos


def answer_file_exists(work_file_name: str, answers_path: str | None = None) -> bool:
    return work_file_name in answer_json_files(answers_path)
