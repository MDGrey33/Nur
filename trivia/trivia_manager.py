
class TriviaQuizz:
    # Below is just a filler class to be written from scratch
    def __init__(self, TriviaRequestEvent):
        self.domain = TriviaRequestEvent.domain
        self.thread_ts = TriviaRequestEvent.thread_ts
        self.channel = TriviaRequestEvent.channel
        self.user = TriviaRequestEvent.user

        self.questions = []
        self.current_question = 0

    def get_questions_from_db(self, domain):
        """Based on the domain make a call to ChromaDB collection and get the nearest neighbors
        using the domain and the statement couldn't find answer in context
        send to gpt to generate questions and add them to the trivia quizz
        the relevant interactions will be sent in context
        the model will be instructed to return the questions in a json list
        the question list will be sent as return
        """
        pass

    def post_questions(self, questions, channel, thread_ts, user):
        """Post the question to the channel tagging the user
        the message ts for each question will be associated to collect the summary at the end
        """
        pass

    def add_question(self, question):
        self.questions.append(question)

    def get_next_question(self):
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.current_question += 1
            return question
        else:
            return None

    def reset(self):
        self.current_question = 0
