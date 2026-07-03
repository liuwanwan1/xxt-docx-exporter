# -*- coding = utf-8 -*-
# @Time :2023/5/23 20:34
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  question_type.py
import bs4


QUESTION_TITLE_SELECTOR = {"class": "mark_name colorDeep fontLabel"}
OPTION_SELECTOR = {"class": "clearfix answerBg"}


class QuestionType:
    @staticmethod
    def multipleChoice(item: bs4.element.Tag) -> dict:
        return build_question(item, "单选题", include_options=True)

    @staticmethod
    def multipleChoices(item: bs4.element.Tag) -> dict:
        return build_question(item, "多选题", include_options=True)

    @staticmethod
    def judgeChoice(item: bs4.element.Tag) -> dict:
        return build_question(item, "判断题")

    @staticmethod
    def comprehensive(item: bs4.element.Tag) -> dict:
        return build_question(item, "填空题")

    @staticmethod
    def shortAnswer(item: bs4.element.Tag) -> dict:
        return build_question(item, "简答题")

    @staticmethod
    def essayQuestion(item: bs4.element.Tag):
        return build_question(item, "论述题")

    @staticmethod
    def programme(item: bs4.element.Tag):
        return build_question(item, "编程题")

    @staticmethod
    def other(item: bs4.element.Tag):
        return build_question(item, "其他")

    @staticmethod
    def error(item: bs4.element.Tag):
        print("该题型暂不支持")
        return {}


def build_question(item: bs4.element.Tag, question_type: str, include_options: bool = False) -> dict:
    try:
        title = required_text(item.find("h3", attrs=QUESTION_TITLE_SELECTOR), "题目标题")
        question = {
            "id": item.attrs["data"],
            "title": my_replace(title),
            "type": question_type,
            "answer": None,
            "option": extract_options(item) if include_options else None,
        }
        return question
    except (KeyError, ValueError, TypeError):
        return {}


def extract_options(item: bs4.element.Tag) -> list:
    options = []
    for option in item.find_all("div", attrs=OPTION_SELECTOR):
        aria_label = option.get("aria-label")
        if aria_label:
            options.append(aria_label.replace("选择", ""))
    return options


def required_text(node, label: str) -> str:
    if node is None or node.text is None:
        raise ValueError(f"缺少{label}")
    return node.text


def my_replace(_string: str):
    if _string is None:
        return Exception
    return _string.replace("\xa0", ' ').replace("\n", "").replace(" ", "").replace("\t", "").replace(" ", "").replace(
        "\r", "")
