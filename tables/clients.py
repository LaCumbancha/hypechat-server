from app import db


class ClientsTableEntry(db.Model):
    __tablename__ = 'clients'

    id = db.Column(name='id', type_=db.Integer, nullable=False, primary_key=True, autoincrement=True)
