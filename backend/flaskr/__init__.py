import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  cors = CORS(app, resources={r'/': {'origins': '*'}})

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()

    if len(categories) == 0:
      abort(404)

    try:
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      return jsonify({
        'success': True,
        'categories': categories_dict
      }), 200

    except:
      abort(422)

  @app.route('/questions')
  def get_questions():
    categories = Category.query.order_by(Category.id).all()
    questions = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)
    
    try:
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      return jsonify({
        'success': True,
        'questions': current_questions,
        'totalQuestions': len(questions),
        'categories': categories_dict
      }), 200

    except:
      abort(422)

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(
    Question.id == question_id).one_or_none()

    if question is None:
      abort(404)

    try:
      question.delete()

      return jsonify({
        'success': True,
        'id': question_id
      }), 200

    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    searchTerm = body.get('searchTerm', None)

    try:
      if searchTerm:
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
        formatted_questions = [ question.format() for question in questions ]

        return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(formatted_questions)
          }), 200

      else:
        for param in [new_question, new_answer, new_category, new_difficulty]:
          if param is None:
            abort(422)
            
        question = Question(question=new_question, answer=new_question, category=new_category, difficulty=new_difficulty)
        question.insert()

      return jsonify({
        'success': True
        }), 200

    except:
      abort(422)
    
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = Question.query.filter(Question.category == category_id).all()

    if len(questions) == 0:
      abort(404)

    try:
      formatted_questions = [ question.format() for question in questions ]

      return jsonify({
          'success': True,
          'questions': formatted_questions
        }), 200
    
    except:
      abort(422)

  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)

    questions = Question.query.order_by(Question.id).all()

    previous_question_ids = [question_id for question_id in previous_questions]
    possible_questions = [ question for question in questions if question.id not in previous_question_ids ]

    if len(possible_questions) == 0:
      abort(404)

    try:
    
      formatted_random_question = random.choice(possible_questions).format()

      return jsonify({
          'success': True,
          'question': formatted_random_question
        }), 200
      
    except:
      abort(422)

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422
  
  return app
