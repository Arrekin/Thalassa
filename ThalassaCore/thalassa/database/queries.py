""" Containes specialized queries to database. """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from thalassa.database.models import Base, User

class DatabaseSessionManager:
    """ Keeps session to database. """

    engine = None
    session_class = None

    def CreateNewSession(self):
        """ Creates new session to the database. """
        if DatabaseSessionManager.engine is None:
            self.__initialize_engine()

        return DatabaseSessionManager.session_class()


    def __initialize_engine(self):
        """ Initialize SQLAlchemy engine. """
        DatabaseSessionManager.engine = create_engine('sqlite:////var/lib/thalassa/thalassa_database.db')
        
        Base.metadata.bind = DatabaseSessionManager.engine

        DatabaseSessionManager.session_class = sessionmaker(bind=DatabaseSessionManager.engine)
