import re

from bs4 import BeautifulSoup


def escape_tags(html_str: str):
    if bool(BeautifulSoup(html_str, "html.parser").find()):
        pattern = re.compile(r'<.+?>')
        return pattern.sub(lambda m: m.group(0).replace("<", "&lt;").replace(">", "&gt;"), html_str)
    return html_str


def all_question_ids(answer: list) -> str:
    return "".join(item["id"] + "," for item in answer)


def build_submission_data(commit_from: dict, answer: list) -> dict:
    data = {
        "courseId": commit_from["courseid"],
        "classId": commit_from["_classId"],
        "knowledgeId": commit_from["knowledgeId"],
        "cpi": commit_from["cpi"],
        "workRelationId": commit_from["workRelationId"],
        "workAnswerId": commit_from["workAnswerId"],
        "jobid": commit_from["jobid"],
        "standardEnc": commit_from["standardEnc"],
        "enc_work": commit_from["token"],
        "totalQuestionNum": commit_from["totalQuestionNum"],
        "pyFlag": commit_from["pyFlag"],
        "answerwqbid": all_question_ids(answer),
        "mooc2": commit_from["mooc2"],
        "randomOptions": commit_from["randomOptions"],
    }
    question_fields = {}
    for item in answer:
        question_fields.update(build_answer_fields(item))
    return dict(question_fields, **data)


def build_answer_fields(item: dict) -> dict:
    title = item["title"]
    question_id = item["id"]
    if "单选题" in title:
        return {
            "answertype" + question_id: 0,
            "answer" + question_id: item["answer"],
        }
    if "多选题" in title:
        return {
            "answertype" + question_id: 1,
            "answer" + question_id: item["answer"],
        }
    if "填空题" in title:
        return build_editor_fields(question_id, item["answer"], answer_type=2)
    if "判断题" in title:
        return {
            "answertype" + question_id: 3,
            "answer" + question_id: "false" if item["answer"] == "错" else "true",
        }
    if "简答题" in title:
        return {
            "answertype" + question_id: 4,
            "answer" + question_id: item["answer"],
        }
    if "论述题" in title:
        return {
            "answertype" + question_id: 6,
            "answer" + question_id: item["answer"],
        }
    if "其他" in title:
        return {
            "answertype" + question_id: 8,
            "answer" + question_id: item["answer"],
        }
    if "编程题" in title:
        return build_editor_fields(question_id, item["answer"], answer_type=9, escape_html=True)
    return {}


def build_editor_fields(question_id: str, answers: list, answer_type: int, escape_html: bool = False) -> dict:
    fields = {
        "answertype" + question_id: answer_type,
        "tiankongsize" + question_id: len(answers),
    }
    for index, answer in enumerate(answers, 1):
        value = answer[3:]
        if escape_html:
            value = escape_tags(value)
        fields["answerEditor" + question_id + str(index)] = "<p>" + value + "<br/></p>"
    return fields
