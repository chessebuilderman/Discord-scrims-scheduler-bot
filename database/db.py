from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from database.base import Base
from contextlib import contextmanager
import config as cfg


class Database(object):
    _instance = None
    dummy = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def __init__(self):
        if self.dummy is None:
            self.dummy = self
            self.initialize()
            print("Database pooling created successfully")

    def initialize(self):
        self.session = None
        self._conn_str = "{0}+{1}://{2}:{3}@{4}/{5}".format(
            "postgresql", "psycopg2", cfg.postgres["user"], cfg.postgres["password"], cfg.postgres["host"], cfg.postgres["database"]
        )
        print('Connecting to: "{0}"'.format(self._conn_str))
        self._engine = create_engine(
            self._conn_str, connect_args={"port": 5432}, echo=False
        )

        print("Initializing database schema")
        self.init_schema()

    def init_schema(self):
        Base.metadata.create_all(self._engine)

    def drop_schema(self):
        Base.metadata.drop_all(self._engine)

    @contextmanager
    def connect(self, autocommit=False):
        Session = scoped_session(
            sessionmaker(bind=self._engine, autocommit=autocommit, autoflush=False)
        )

        session = Session()

        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
