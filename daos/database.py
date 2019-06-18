from app import db


class DatabaseClient:

    @classmethod
    def commit(cls):
        db.session.commit()

    @classmethod
    def rollback(cls):
        db.session.rollback()

    @classmethod
    def add(cls, entry):
        db.session.add(entry)
        db.session.flush()
