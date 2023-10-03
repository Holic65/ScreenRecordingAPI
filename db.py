from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class VideoDatabase(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.String(255), unique=True, nullable=False)
    createdAt = db.Column(db.String(255), nullable=False)

    def __init__(self, sessionID, createdAt):
        self.sessionID = sessionID
        self.createdAt = createdAt

    @classmethod
    def find_by_sessionID(cls, sessionID):
        return cls.query.filter_by(sessionID=sessionID).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
