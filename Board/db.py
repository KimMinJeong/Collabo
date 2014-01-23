from config import *

engine = create_engine(app.config['DATABASE_URI'])

db_session =scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    email = Column(String(200))
    comment = Column(String(500))

    def __init__(self, email, comment):
        self.email = email
        self.comment = comment

class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)
    email = Column(String(200))
    contents = Column(String(1000))
    title = Column(String(100))
    status = Column(String(50))