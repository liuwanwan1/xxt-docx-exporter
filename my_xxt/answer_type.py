# -*- coding = utf-8 -*-
# @Time :2023/5/17 14:31
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  answer_type.py
import bs4
from rich.console import Console


ANSWER_TITLE_SELECTOR = {"class": "mark_name colorDeep"}
FILL_ANSWER_SELECTOR = {"class": "mark_fill colorGreen"}
CORRECT_ANSWER_SELECTOR = {"class": "colorGreen marginRight40 fl"}
MY_ANSWER_SELECTOR = {"class": "colorDeep marginRight40 fl"}


class AnswerType:
    @staticmethod
    def multipleChoice(item: bs4.element.Tag, console: Console) -> dict:
        return build_choice_answer(item, console, "单选题")

    @staticmethod
    def multipleChoices(item: bs4.element.Tag, console: Console) -> dict:
        return build_choice_answer(item, console, "多选题")

    @staticmethod
    def judgeChoice(item: bs4.element.Tag, console: Console) -> dict:
        return build_simple_answer(item, console, "判断题", options=[])

    @staticmethod
    def comprehensive(item: bs4.element.Tag, console: Console) -> dict:
        return build_fill_answer(item, console, "填空题")

    @staticmethod
    def shortAnswer(item: bs4.element.Tag, console: Console) -> dict:
        return build_dd_answer(item, console, "简答题")

    @staticmethod
    def essayQuestion(item: bs4.element.Tag, console: Console):
        return build_dd_answer(item, console, "论述题")

    @staticmethod
    def programme(item: bs4.element.Tag, console: Console):
        return build_fill_answer(item, console, "编程题")

    @staticmethod
    def other(item: bs4.element.Tag, console: Console):
        return build_dd_answer(item, console, "其他")

    @staticmethod
    def error(item: bs4.element.Tag, console: Console):
        try:
            title_type = item.find_next("span").string.split(",")[0].replace("(", "").replace(")", "")
            console.log(f"[bold red]该题目类型[bold green]{title_type}[/bold green]还没有支持，请到本项目提交issue[/bold red]")
        except Exception as e:
            console.log(f"[bold red]题目解析错误[/bold red]")
            console.log(f"[bold red]错误信息:{e}[/bold red]")
        return {}


def build_choice_answer(item: bs4.element.Tag, console: Console, question_type: str) -> dict:
    try:
        return build_simple_answer(item, console, question_type, options=extract_options(item))
    except (KeyError, ValueError, TypeError) as e:
        log_parse_error(console, question_type, e)
        return {}


def build_simple_answer(item: bs4.element.Tag, console: Console, question_type: str, options: list | None = None) -> dict:
    try:
        return {
            "id": item.attrs["data"],
            "title": required_text(item.find("h3", attrs=ANSWER_TITLE_SELECTOR), "题目标题"),
            "type": question_type,
            "answer": extract_choice_answer(item),
            "option": options or [],
        }
    except (KeyError, ValueError, TypeError) as e:
        log_parse_error(console, question_type, e)
        return {}


def build_fill_answer(item: bs4.element.Tag, console: Console, question_type: str) -> dict:
    try:
        answer_list = first_existing(item.find("dl", attrs=FILL_ANSWER_SELECTOR), item.find_next("dl", attrs=FILL_ANSWER_SELECTOR))
        answers = [my_replace(answer.text) for answer in answer_list.find_all("dd")]
        return {
            "id": item.attrs["data"],
            "title": required_text(item.find("h3", attrs=ANSWER_TITLE_SELECTOR), "题目标题"),
            "type": question_type,
            "answer": answers,
            "option": [],
        }
    except (KeyError, ValueError, TypeError, AttributeError) as e:
        log_parse_error(console, question_type, e)
        return {}


def build_dd_answer(item: bs4.element.Tag, console: Console, question_type: str) -> dict:
    try:
        answer_node = item.find("dd")
        return {
            "id": item.attrs["data"],
            "title": required_text(item.find("h3", attrs=ANSWER_TITLE_SELECTOR), "题目标题"),
            "type": question_type,
            "answer": required_text(answer_node, "答案"),
            "option": [],
        }
    except (KeyError, ValueError, TypeError) as e:
        log_parse_error(console, question_type, e)
        return {}


def extract_options(item: bs4.element.Tag) -> list:
    option_list = first_existing(item.find("ul"), item.find_next("ul"))
    options = []
    for option in option_list:
        if option == "\n":
            continue
        options.append(my_replace(option.text))
    return options


def extract_choice_answer(item: bs4.element.Tag) -> str:
    correct_answer = item.find("span", attrs=CORRECT_ANSWER_SELECTOR) or item.find_next("span", attrs=CORRECT_ANSWER_SELECTOR)
    if correct_answer:
        return my_replace(correct_answer.text.replace("正确答案: ", ""))
    my_answer = item.find("span", attrs=MY_ANSWER_SELECTOR) or item.find_next("span", attrs=MY_ANSWER_SELECTOR)
    if my_answer:
        return my_replace(my_answer.text.replace("我的答案: ", ""))
    raise ValueError("缺少答案")


def required_text(node, label: str) -> str:
    if node is None or node.text is None:
        raise ValueError(f"缺少{label}")
    return node.text


def first_existing(*nodes):
    for node in nodes:
        if node is not None:
            return node
    raise ValueError("缺少必要节点")


def log_parse_error(console: Console, question_type: str, error: Exception):
    console.print(f"[bold red]{question_type}题目解析错误[/bold red]")
    console.print(f"[bold red]错误信息:{error}[/bold red]")


def my_replace(_string: str):
    if _string is None:
        return Exception
    return _string.replace("\xa0", ' ').replace("\n", "").replace(" ", "").replace("\t", "").replace(" ", "").replace(
        "\r", "")
