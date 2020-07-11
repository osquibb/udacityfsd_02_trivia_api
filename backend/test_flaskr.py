import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

def create_test_question():
    question = Question(
        question='test question',
        answer='test answer',
        difficulty=1,
        category=1)

    question.insert()

    return { 'id': question.id, 'formatted': question.format() }
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['totalQuestions'])
        self.assertTrue(data['categories'])

    def test_delete_question(self):
        test_question_id = create_test_question()['id']

        res = self.client().delete('/questions/' + str(test_question_id))
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == test_question_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_create_new_question(self):
        new_question = create_test_question()

        res = self.client().post('/questions', json=new_question['formatted'])
        data = json.loads(res.data)
    
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'royal'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_get_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 5)

    def test_get_next_question(self):
        res = self.client().post('/quizzes', json={ 'previous_questions': '', 'quiz_category': 2 })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    # TODO: Add negative test cases
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()