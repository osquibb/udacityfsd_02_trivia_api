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
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response

  '''
  @DONE?: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    try:
      categories = Category.query.all()

      if len(categories) == 0:
        abort(404)
      
      categories_dict = {}
      for category in categories:
        categories_dict[category.id] = category.type

      return jsonify({
        'success': True,
        'categories': categories_dict
      }), 200
    except:
      abort(422)

  '''
  @DONE w/o Test: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''

  @app.route('/questions')
  def get_questions():
    try:
      categories = Category.query.order_by(Category.id).all()
      questions = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, questions)

      if len(current_questions) == 0:
        abort(404)

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

  '''
  @DONE w/o Test: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success': True
      }), 200
    
    except:
      abort(422)


  '''
  @DONE w/o Test: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

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
        questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm)))
        
        if len(questions) == 0:
          abort(404)

        formatted_questions = [ question.format() for question in questions ]

        return jsonify({
          'success': True,
          'questions': formatted_questions
        }), 200

      else:
        question = Question(question=new_question, answer=new_question, category=new_category, difficulty=new_difficulty)
        question.insert()

        return jsonify({
          'success': True
        }), 200
    
    except:
      abort(422)

  '''
  @DONE w/o Test: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''


  '''
  @DONE w/o test: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == category_id).all()

      if len(questions) == 0:
        abort(404)

      formatted_questions = [ question.format() for question in questions ]

      return jsonify({
          'success': True,
          'questions': formatted_questions
        }), 200

    except:
      abort(422)

  '''
  @DONE w/o test: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    quiz_category = body.get('quiz_category', None)

    questions = Question.query.order_by(Question.id).all()

    try:
      previous_question_ids = [question['id'] for question in previous_questions]
      possible_questions = [ question for question in questions if question.id not in previous_question_ids ]

      if len(possible_questions) == 0:
        abort(404)
      
      formatted_random_question = random.choice(possible_questions).format()

      return jsonify({
          'success': True,
          'question': formatted_random_question
        }), 200
    
    except:
      abort(422)

  '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

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

    