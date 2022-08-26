import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
# function for handling pagination
def paginate(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    items = [item.format() for item in selection]
    paginated = items[start:end]
    return paginated


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization, true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, DELETE, PATCH, OPTIONS"
        )
        return response

    # just for fun, please disregard
    @app.route("/")
    def hello():
        return "Hello World!"

    @app.route("/categories")
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        current_categories = {
            category.id: category.type for category in categories
        }

        return jsonify({"categories": current_categories})

    @app.route("/questions")
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.all()
        current_questions = paginate(request, questions)
        # check if range exceeded
        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "questions": current_questions,
                "total_questions": len(questions),
                "categories": {
                    category.id: category.type for category in categories
                },
                "current_category": categories[0].type,
            }
        )

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            abort(404)
        try:
            question.delete()
            return jsonify({"success": True})
        except:
            abort(422)

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        if body is None:
            abort(400)

        question = body.get("question")
        answer = body.get("answer")
        category = body.get("category")
        difficulty = body.get("difficulty")
        search = body.get("searchTerm")

        if search:
            # if body contains a search term, proceed as a search
            questions = Question.query.filter(
                Question.question.ilike("%{}%".format(search))
            ).all()
            if len(questions) == 0:
                return jsonify(
                    {
                        "questions": [],
                        "total_questions": 0,
                        "current_category": None,
                    }
                )
            current_questions = paginate(request, questions)
            search_category = Category.query.get(questions[0].category)
            return jsonify(
                {
                    "questions": current_questions,
                    "total_questions": len(questions),
                    "current_category": search_category.type,
                }
            )

        else:
            try:
                new_question = Question(question, answer, category, difficulty)
                new_question.insert()
                return jsonify({"success": True})
            except:
                abort(500)

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        questions = Question.query.filter(
            Question.category == category_id
        ).all()
        current_questions = paginate(request, questions)
        category = Category.query.get(category_id)
        # check if range exceeded
        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "questions": current_questions,
                "total_questions": len(questions),
                "current_category": category.type,
            }
        )

    @app.route("/quizzes", methods=["POST"])
    def get_next_question_for_game():
        def random_choice(choices, previous_questions):
            # function for selecting a random unique question
            for choice in choices:
                question = random.choice(choices)
                if question in previous_questions:
                    pass
                elif question not in previous_questions:
                    return question

        body = request.get_json()
        category = body.get("quiz_category")
        previous_questions = body.get("previous_questions")

        if category["id"]:
            # get questions by category if category is included in body
            category_id = int(category["id"])
            get_category = Category.query.get(category_id)
            get_questions = Question.query.filter(
                Question.category == get_category.id
            ).all()

            if len(previous_questions) == len(get_questions):
                return jsonify({"question": None})
            else:
                category_choices = [question.id for question in get_questions]
                category_question = random_choice(
                    category_choices, previous_questions
                )
                category_next_question = Question.query.get(category_question)
                if not category_question:
                    print("nothing")
                return jsonify({"question": category_next_question.format()})
        else:
            # if category not in body, get all questions
            get_questions = Question.query.all()

            if len(previous_questions) == len(get_questions):
                return jsonify({"question": None})
            else:
                choices = [question.id for question in get_questions]
                question = random_choice(choices, previous_questions)
                next_question = Question.query.get(question)
                return jsonify({"question": next_question.format()})

    # Error handlers______________________
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 400,
                    "message": "request body not specified",
                }
            ),
            400,
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 404,
                    "message": "resource not found",
                }
            ),
            404,
        )

    @app.errorhandler(422)
    def unprocessible(error):
        return (
            jsonify(
                {"success": False, "error": 422, "message": "unprocessible"}
            ),
            422,
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify(
                {
                    "success": False,
                    "error": 500,
                    "message": "something went wrong, try again",
                }
            ),
            500,
        )

    return app
