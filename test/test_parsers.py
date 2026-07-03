import unittest
from io import StringIO

from bs4 import BeautifulSoup
from rich.console import Console

from my_xxt.answer_type import AnswerType
from my_xxt.question_type import QuestionType


class ParserSafetyTests(unittest.TestCase):
    def test_answer_parser_returns_empty_dict_when_required_nodes_are_missing(self):
        item = BeautifulSoup('<div class="questionLi" data="1"></div>', "lxml").div

        result = AnswerType.multipleChoice(item, Console(file=StringIO(), record=True))

        self.assertEqual({}, result)

    def test_question_parser_returns_empty_dict_when_required_nodes_are_missing(self):
        item = BeautifulSoup('<div class="questionLi" data="1"></div>', "lxml").div

        result = QuestionType.multipleChoice(item)

        self.assertEqual({}, result)


if __name__ == "__main__":
    unittest.main()
