from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from gamification.models.user_score import UserScore, Base
from configuration import sql_file_path  # Assuming there's a configuration file with DB path
from slack.client import get_bot_user_id


class ScoreManager:
    def __init__(self):
        self.engine = create_engine('sqlite:///' + sql_file_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.bot_user_id = get_bot_user_id()

    def add_or_update_score(self, slack_user_id, category, points=1):
        """
        Adds or updates the score for a user in a given category. If the user does not exist, creates a new record.
        """
        # Check if the user ID is the bot's user ID
        if slack_user_id == self.bot_user_id:
            print("Skipping score update for bot user.")
            return
        session = self.Session()
        try:
            user_score = session.query(UserScore).filter_by(slack_user_id=slack_user_id).first()
            if not user_score:
                # If the user score does not exist, create a new one with default scores initialized to 0
                user_score = UserScore(slack_user_id=slack_user_id, seeker_score=0, revealer_score=0, luminary_score=0)
                session.add(user_score)
                session.flush()  # Flush here to ensure user_score is persisted before we try to update it

            # Increment the score based on the category
            if category == 'seeker':
                user_score.seeker_score += points
            elif category == 'revealer':
                user_score.revealer_score += points
            elif category == 'luminary':
                user_score.luminary_score += points
            else:
                raise ValueError("Invalid category provided.")

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_top_users(self, category, top_n=10):
        """
        Retrieves the top N users for a given category.
        """
        session = self.Session()
        try:
            if category == 'seeker':
                return session.query(UserScore).order_by(UserScore.seeker_score.desc()).limit(top_n).all()
            elif category == 'revealer':
                return session.query(UserScore).order_by(UserScore.revealer_score.desc()).limit(top_n).all()
            elif category == 'luminary':
                return session.query(UserScore).order_by(UserScore.luminary_score.desc()).limit(top_n).all()
            else:
                raise ValueError("Invalid category provided.")
        finally:
            session.close()
