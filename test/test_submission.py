import unittest

from my_xxt.submission import build_submission_data


class SubmissionDataTests(unittest.TestCase):
    def test_build_submission_data_maps_supported_question_types(self):
        commit_from = {
            "courseid": "course-1",
            "_classId": "class-1",
            "knowledgeId": "knowledge-1",
            "cpi": "cpi-1",
            "workRelationId": "work-rel-1",
            "workAnswerId": "work-answer-1",
            "jobid": "job-1",
            "standardEnc": "standard-enc",
            "token": "token-1",
            "totalQuestionNum": "3",
            "pyFlag": "0",
            "mooc2": "1",
            "randomOptions": "false",
        }
        answers = [
            {"id": "1", "title": "1. (单选题)", "answer": "A"},
            {"id": "2", "title": "2. (判断题)", "answer": "错"},
            {"id": "3", "title": "3. (编程题)", "answer": ["(1)<script>alert(1)</script>"]},
        ]

        data = build_submission_data(commit_from, answers)

        self.assertEqual("1,2,3,", data["answerwqbid"])
        self.assertEqual(0, data["answertype1"])
        self.assertEqual("A", data["answer1"])
        self.assertEqual(3, data["answertype2"])
        self.assertEqual("false", data["answer2"])
        self.assertEqual(9, data["answertype3"])
        self.assertEqual("<p>&lt;script&gt;alert(1)&lt;/script&gt;<br/></p>", data["answerEditor31"])


if __name__ == "__main__":
    unittest.main()
