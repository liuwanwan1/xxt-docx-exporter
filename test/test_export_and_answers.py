import json
import os
import tempfile
import unittest

from my_xxt.export_docx import export_course_assignments_to_docx, generate_docx_from_json
from my_xxt.answer_files import answer_file_exists, load_answer_file_infos


def write_answer_file(directory, filename, course_name="数据结构与算法", work_name="第7章 图-作业"):
    path = os.path.join(directory, filename)
    payload = {
        "27835863": [
            {
                "id": "163657918",
                "title": "1. (单选题)在一个无向图G中，所有顶点的度数之和等于所有边数之和的（ ）倍。",
                "type": "单选题",
                "answer": "C",
                "option": ["A.l/2", "B.1", "C.2", "D.4"],
            }
        ],
        "info": {
            "id": "27835863",
            "work_name": work_name,
            "course_name": course_name,
        },
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False)
    return path


class ExportAndAnswerFileTests(unittest.TestCase):
    def test_generate_docx_from_json_creates_document(self):
        with tempfile.TemporaryDirectory() as directory:
            json_path = write_answer_file(directory, "27835863.json")
            output_path = os.path.join(directory, "out.docx")

            generated_path = generate_docx_from_json(json_path, output_path)

            self.assertEqual(output_path, generated_path)
            self.assertTrue(os.path.exists(generated_path))
            self.assertGreater(os.path.getsize(generated_path), 0)

    def test_load_answer_file_infos_ignores_non_json_and_invalid_json(self):
        with tempfile.TemporaryDirectory() as directory:
            write_answer_file(directory, "27835863.json")
            with open(os.path.join(directory, "27835863.docx"), "wb") as file:
                file.write(b"not json")
            with open(os.path.join(directory, "broken.json"), "w", encoding="utf-8") as file:
                file.write("{")

            infos = load_answer_file_infos(directory)

            self.assertEqual(1, len(infos))
            self.assertEqual("27835863.json", infos[0]["file_name"])
            self.assertEqual("数据结构与算法", infos[0]["course_name"])

    def test_is_exist_answer_file_handles_missing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            missing_directory = os.path.join(directory, "missing")

            self.assertFalse(answer_file_exists("27835863.json", missing_directory))

    def test_export_course_assignments_matches_course_keyword(self):
        with tempfile.TemporaryDirectory() as directory:
            write_answer_file(directory, "27835863.json", course_name="数据结构与算法")
            output_path = os.path.join(directory, "course.docx")

            generated_path = export_course_assignments_to_docx("结构", directory, output_path)

            self.assertEqual(output_path, generated_path)
            self.assertTrue(os.path.exists(generated_path))


if __name__ == "__main__":
    unittest.main()
