import atexit

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from ..config import config

db_filename = config['PATHS']['Database']
db_path = 'sqlite:///' + db_filename
engine = create_engine(db_path, convert_unicode=True)
atexit.register(lambda engine: engine.dispose(), engine)
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    engine.dispose()
