# ./interactions/quiz_question_dto.py
class QuizQuestionDTO:
    def __init__(self, id, question_text, thread_id=None,
                 summary=None, posted_on_slack=None, posted_on_confluence=None
                 ):
        self.id = id
        self.question_text = question_text
        self.thread_id = thread_id
        self.summary = summary
        self.posted_on_slack = posted_on_slack
        self.posted_on_confluence = posted_on_confluence
