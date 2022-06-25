from nis import cat
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, all_questions):
    """Separate questions into pages of 10 question per page"""
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    formatted_questions = [question.format() for question in all_questions]
    current_questions = formatted_questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"api/*": {"origin": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization"
        )
        response.headers.add(
            "Access-Control-Headers", "GET, POST, PATCH, DELETE, OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def get_all_categories():
        try:
            categories = Category.query.all()
            formatted_categories = [category.format() for category in categories]

            # convert categories to dictionary
            categories_dictionary = {
                formatted_category["id"]: formatted_category["type"]
                for formatted_category in formatted_categories
            }

            if len(categories) is None:
                abort(404, "No category found")

            return jsonify({"success": True, "categories": categories_dictionary})
        except Exception as err:
            abort(err.code)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def get_paginated_questions():
    
        # get categories in json format from the above defined get_categories
        categories = get_all_categories().get_json()["categories"]
        
        all_questions = Question.query.order_by(Question.id).all()


        current_questions = paginate_questions(request, all_questions)

        # raise error if there is no question on the current page
        if len(current_questions) == 0:
            abort(404, "No questions on requested page")

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "len_question":len(current_questions),
                "current_category": None,
                "categories": categories,
                "total_questions": len(all_questions),
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_specific_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if not question:
            abort(404, f"Question with id: {question_id} does not exist")
        else:
            try:
                question.delete()

                current_questions = get_paginated_questions().get_json()["questions"]

                return jsonify(
                    {
                        "success": True,
                        "deleted": question_id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )
            except Exception as err:
                abort(err.code)



    return app