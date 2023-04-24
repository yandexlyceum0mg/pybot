import datetime
import sqlalchemy
from db_sess import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)  # идентификатор
    ratingchess = sqlalchemy.Column(sqlalchemy.Integer)
    ratingxo = sqlalchemy.Column(sqlalchemy.Integer)
