import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            "postgres", "kaosi", "localhost:5432", self.database_name
        )
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question": "Heres a new question string",
            "answer": "Heres a new answer string",
            "difficulty": 1,
            "category": 3,
        }
        self.quiz_question = {
            "previous_questions": [13, 14, 15],
            "quiz_category": {"id": 3},
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_getting_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])
        self.assertIsInstance(data["categories"], dict)

    def test_getting_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertTrue(data["current_category"])
        self.assertTrue(data["total_questions"])
        self.assertIsInstance(data["questions"], list)
        self.assertIsInstance(data["categories"], dict)

    def test_failed_getting_paginated_questions(self):
        res = self.client().get("/questions?page=1000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_delete_question(self):
        question_id = 47
        res = self.client().delete("/questions/{}".format(question_id))
        question = Question.query.get(question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)

    def test_invalid_delete(self):
        res = self.client().delete("/questions/100000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_successful_question_post(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_unsuccessful_question_post(self):
        res = self.client().post("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_search_questions_with_result(self):
        res = self.client().post("/questions", json={"searchTerm": "Heres"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertIsInstance(data["questions"], list)
        self.assertIsNotNone(data["current_category"])
        self.assertNotEqual(data["total_questions"], 0)

    def test_search_questions_without_result(self):
        res = self.client().post("/questions", json={"searchTerm": "qwertyuiop"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data["questions"], list)
        self.assertIsNone(data["current_category"])
        self.assertEqual(data["total_questions"], 0)

    def test_get_questions_by_categoty(self):
        res = self.client().get("/categories/3/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertIsInstance(data["questions"], list)
        self.assertIsNotNone(data["current_category"])
        self.assertTrue(data["total_questions"])

    def test_get_questions_by_category_exceding_range(self):
        res = self.client().get("/categories/6/questions?page=10000000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertTrue(data["message"])

    def test_getting_next_question_for_game(self):
        res = self.client().post("/quizzes", json=self.quiz_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        question_id = [data["question"]["id"]]

        check = list(
            set(question_id).intersection(self.quiz_question["previous_questions"])
        )
        try:
            self.assertTrue(len(check) == 0)
        except AssertionError as e:
            e.args += data["questions"]["id"] + "is present in previous_question"
            raise


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
