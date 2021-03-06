from put_tasks import put_tasks
from delete_task import delete_task

import requests
import json
import pickle
import unittest

class TestTabooWorkflow(unittest.TestCase):

    def setUp(self):
        # Load configuration file
        with open('config.json') as json_config_file:
            config = json.load(json_config_file)

        self.crowdjs_url = config['crowdjs_url']
        self.email = config['test_requester_email']
        self.password = config['test_requester_password']

        # Get requester's ID and API token
        r = requests.get(self.crowdjs_url + '/token', auth=(self.email, self.password))
        data = r.json()
        self.requester_id = data['requester_id']
        self.API_KEY = data['auth_token']

        self.threshold = 2
        self.answers_per_question = 3
        
    def test_workflow(self):

        crowdjs_url = self.crowdjs_url
        email = self.email
        API_KEY = self.API_KEY
        requester_id = self.requester_id
        
        #First delete all existing tasks
        print "DELETING ALL EXISTING TASKS"
        response = delete_task(crowdjs_url, email, API_KEY, requester_id)
        self.assertIn('success', response)
        
        #Now put in a new task
        print "INSERTING TASK"
        question_file = open('data/turkTrainingRandom1.csv', 'r')
        (response, questions) = put_tasks(crowdjs_url, email,
                                          API_KEY, requester_id, 1,
                                          self.threshold, question_file)
        self.assertIn('task_id', response)
        task_id = response['task_id']

        #Now preview a question
        print "PREVIEWING A QUESTION"
        assign_url = '/assign_next_question?worker_id=worker1&worker_source=mturk&task_id=%s&requester_id=%s&preview=True' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('question_name', r.json())
        question_name = r.json()['question_name']

        #There should not be any answers in the answers table
        answer_get_url = '/answers?requester_id=%s&task_id=%s' % (
            requester_id, task_id)
        answer_get_url = crowdjs_url + answer_get_url
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(answer_get_url, headers=headers)
        answers = r.json()
        self.assertEqual(len(answers), 0)
        
        #Now assign a question
        print "ASSIGNING A QUESTION"
        assign_url = '/assign_next_question?worker_id=worker1&worker_source=mturk&task_id=%s&requester_id=%s&preview=False' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('question_name', r.json())
        question_name = r.json()['question_name']


        #There should now be an answer awaiting a value in the databse
        answer_get_url = '/answers?requester_id=%s&task_id=%s' % (
            requester_id, task_id)
        answer_get_url = crowdjs_url + answer_get_url
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(answer_get_url, headers=headers)

        answers = r.json()
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0]['is_alive'], True)
        
        #Now do a question
        print "SUBMITTING AN ANSWER"
        answer_url = crowdjs_url + '/answers'
        answer_data = {"requester_id" : requester_id,
                       "task_id" : task_id,
                       "question_name" : question_name,
                       "worker_id" : "worker1",
                       "worker_source" : "mturk", 
                       "value" : question_name.split('\t')[0] + ' head honcho'}

        r = requests.put(answer_url, json=answer_data)
        print "Here is the response"
        print r.text

        #Now try to assign another question. This should not work
        #because the worker already answered the question
        print "ASSIGNING A QUESTION"
        assign_url = '/assign_next_question?worker_id=worker1&worker_source=mturk&task_id=%s&requester_id=%s' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('error', r.json())
        
        #Now assign another question. This should also not work because
        #the budget for the question has been surpassed.
        print "ASSIGNING ANOTHER QUESTION"
        assign_url = '/assign_next_question?worker_id=worker2&worker_source=mturk&task_id=%s&requester_id=%s' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('error', r.json())


        #Set the answers per question to be higher
        set_budget_url = crowdjs_url + '/tasks/set_budget'
        budget_data = {'task_id': task_id,
                       'requester_id': requester_id,
                       'answers_per_question': 3} 
        headers = {'Authentication-Token': API_KEY}
        r = requests.post(set_budget_url, headers=headers,
                          json=budget_data)
        self.assertNotIn('error', r.json())
        

        print "ASSIGNING ANOTHER QUESTION"
        assign_url = '/assign_next_question?worker_id=worker2&worker_source=mturk&task_id=%s&requester_id=%s' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('question_name', r.json())
        question_name = r.json()['question_name']
        
        taboo_words = question_name.split('\t')[5]
        taboo_words = taboo_words.split(';')
        
        self.assertEqual(len(taboo_words), 2)
        self.assertNotIn('head', taboo_words)
        self.assertNotIn('honcho', taboo_words)
        self.assertIn('not', taboo_words)

        #There should now be another answer awaiting a value in the databse
        answer_get_url = '/answers?requester_id=%s&task_id=%s' % (
            requester_id, task_id)
        answer_get_url = crowdjs_url + answer_get_url
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(answer_get_url, headers=headers)

        answers = r.json()
        self.assertEqual(len(answers), 2)
        
        #Now do a question
        print "SUBMITTING ANOTHER ANSWER"        
        answer_url = crowdjs_url + '/answers'
        answer_data = {"requester_id" : requester_id,
                       "task_id" : task_id,
                       "question_name" : question_name,
                       "worker_id" : "worker1",
                       "worker_source" : "mturk", 
                       "value" : question_name.split('\t')[0] + ' head honcho'}

        r = requests.put(answer_url, json=answer_data)
        print "Here is the response"
        print r.text


    def test_concurrency(self):

        print "TESTING CONCURRENCY"
        
        crowdjs_url = self.crowdjs_url
        email = self.email
        API_KEY = self.API_KEY
        requester_id = self.requester_id
        
        
        #First delete all existing tasks
        print "DELETING ALL EXISTING TASKS"
        response = delete_task(crowdjs_url, email, API_KEY, requester_id)
        self.assertIn('success', response)
        
        #Now put in a new task
        print "INSERTING TASK"
        question_file = open('data/turkTrainingRandom1.csv', 'r')
        (response, questions) = put_tasks(crowdjs_url, email,
                                          API_KEY, requester_id, 3,
                                          self.threshold, question_file)
        self.assertIn('task_id', response)
        task_id = response['task_id']
        
        
        #Now assign a question
        print "ASSIGNING FIRST QUESTION"
        assign_url = '/assign_next_question?worker_id=worker1&worker_source=mturk&task_id=%s&requester_id=%s' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('question_name', r.json())
        question_name = r.json()['question_name']
        print question_name

        #There should now be an answer awaiting a value in the databse
        answer_get_url = '/answers?requester_id=%s&task_id=%s' % (
            requester_id, task_id)
        answer_get_url = crowdjs_url + answer_get_url
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(answer_get_url, headers=headers)

        answers = r.json()
        self.assertEqual(len(answers), 1)
        for answer in answers:
            self.assertEqual(answer['is_alive'], True)


        #Now assign another question
        print "ASSIGNING ANOTHER QUESTION"
        assign_url = '/assign_next_question?worker_id=worker2&worker_source=mturk&task_id=%s&requester_id=%s' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('question_name', r.json())
        question_name = r.json()['question_name']


        #There should now be two answers awaiting a value in the databse
        answer_get_url = '/answers?requester_id=%s&task_id=%s' % (
            requester_id, task_id)
        answer_get_url = crowdjs_url + answer_get_url
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(answer_get_url, headers=headers)

        answers = r.json()
        self.assertEqual(len(answers), 2)
        for answer in answers:
            self.assertEqual(answer['is_alive'], True)

            
        #Now do a question
        print "SUBMITTING AN ANSWER"
        answer_url = crowdjs_url + '/answers'
        answer_data = {"requester_id" : requester_id,
                       "task_id" : task_id,
                       "question_name" : question_name,
                       "worker_id" : "worker1",
                       "worker_source" : "mturk", 
                       "value" : question_name.split('\t')[0] + ' head honcho'}

        r = requests.put(answer_url, json=answer_data)
        print "Here is the response"
        print r.text

        #Now check that there is one question in total, and it still has
        # a budget of 3
        question_url = '/questions?requester_id=%s' % requester_id
        question_url = crowdjs_url + question_url
        
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(question_url, headers=headers)
        all_questions = r.json()
        print all_questions
        self.assertEqual(len(all_questions), 1)
        self.assertEqual(all_questions[0]['answers_per_question'] , 3)
        
        print "ASSIGNING A THIRD QUESTION "
        assign_url = '/assign_next_question?worker_id=worker3&worker_source=mturk&task_id=%s&requester_id=%s' % (task_id, requester_id)
        assign_url = crowdjs_url + assign_url
        r = requests.get(assign_url)
        self.assertIn('question_name', r.json())
        question_name = r.json()['question_name']
        
        taboo_words = question_name.split('\t')[5]
        taboo_words = taboo_words.split(';')
        
        self.assertEqual(len(taboo_words), 2)
        self.assertNotIn('head', taboo_words)
        self.assertNotIn('honcho', taboo_words)
        self.assertIn('not', taboo_words)
        
        #Now do a question
        print "SUBMITTING THE SECOND ANSWER"        
        answer_url = crowdjs_url + '/answers'
        answer_data = {"requester_id" : requester_id,
                       "task_id" : task_id,
                       "question_name" : question_name,
                       "worker_id" : "worker2",
                       "worker_source" : "mturk", 
                       "value" : question_name.split('\t')[0] + ' head honcho'}

        r = requests.put(answer_url, json=answer_data)
        print "Here is the response"
        print r.text

        

        question_url = '/questions?requester_id=%s' % requester_id
        question_url = crowdjs_url + question_url
        
        headers = {'Authentication-Token': API_KEY}
        r = requests.get(question_url, headers=headers)
        all_questions = r.json()
        print all_questions
        self.assertEqual(len(all_questions), 1)
        questions_with_zero_budget = 0
        questions_with_gtzero_budget = 0
        for question in all_questions:
            print question['answers_per_question']
            if int(question['answers_per_question']) > 0:
                questions_with_gtzero_budget += 1
            else:
                questions_with_zero_budget += 1
        self.assertEqual(questions_with_zero_budget, 0)
        self.assertEqual(questions_with_gtzero_budget, 1)


        
if __name__ == '__main__':
    unittest.main()
