from flask.ext.restful import reqparse, abort, Api, Resource
from flask import url_for
from schema.answer import Answer
from schema.question import Question
from schema.worker import Worker
import json
from collections import Counter

answer_agg_parser = reqparse.RequestParser()
answer_agg_parser.add_argument('question_id', type=str, required=True)
answer_agg_parser.add_argument('strategy', type=str, required=True)

class AnswerAggregationApi(Resource):
    def get(self):
        """
        Get list of all answers.
        """
        args = answer_agg_parser.parse_args()
        question_id = args['question_id']
        strategy = args['strategy']
        
        question = Question.objects.get_or_404(id=question_id)

        # call
        aggregated_answer = self.aggregated_answer(question, strategy)
        return {'question_id': str(question.id),
                'aggregated_answer': str(aggregated_answer)}

    def aggregated_answer(self, question, strategy):
        if strategy == 'majority_vote':
            return self.majority_vote(question)
        else:
            return None

    def majority_vote(self, question):
        """
        Returns the most common answer to the given question.
        """
        answers = Answer.objects(question=question)
        values = []
        for answer in answers:
            values.append(answer.value)

        counts = Counter(values)
        return counts.most_common(1)[0][0]
