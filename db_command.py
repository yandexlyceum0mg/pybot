import db_sess
from users import User


def createdb_and_globinit_if_db_not_exists_else_globinit():
    db_sess.global_init("users.db")


def add_user(id):
    user = User()
    user.id = id
    user.ratingchess = 0
    user.ratingxo = 0
    db_s = db_sess.create_session()
    db_s.add(user)
    db_s.commit()


# def del_user(id):
#     db_s = db_sess.create_session()
#     db_s.delete(db_s.query(User).filter_by(id=id).first())
#     db_s.commit()

def user_is_exists(id):
    db_s = db_sess.create_session()
    if db_s.query(User).filter_by(id=id).first() is not None:
        return True
    return False


def get_chess_rating(id):
    if not user_is_exists(id):
        add_user(id)
    return db_sess.create_session().query(User).filter_by(id=id).first().ratingchess


def get_xo_rating(id):
    if not user_is_exists(id):
        add_user(id)
    return db_sess.create_session().query(User).filter_by(id=id).first().ratingxo


def inc_chess_rating(id):
    if not user_is_exists(id):
        add_user(id)
    db_s = db_sess.create_session()
    user = db_s.query(User).filter_by(id=id).first()
    user.ratingchess += 1
    db_s.add(user)
    db_s.commit()


def dec_chess_rating(id):
    if not user_is_exists(id):
        add_user(id)
    db_s = db_sess.create_session()
    user = db_s.query(User).filter_by(id=id).first()
    user.ratingchess -= 1
    db_s.add(user)
    db_s.commit()


def inc_xo_rating(id):
    if not user_is_exists(id):
        add_user(id)
    db_s = db_sess.create_session()
    user = db_s.query(User).filter_by(id=id).first()
    user.ratingxo += 1
    db_s.add(user)
    db_s.commit()


def dec_xo_rating(id):
    if not user_is_exists(id):
        add_user(id)
    db_s = db_sess.create_session()
    user = db_s.query(User).filter_by(id=id).first()
    user.ratingxo -= 1
    db_s.add(user)
    db_s.commit()


if __name__ == '__main__':
    createdb_and_globinit_if_db_not_exists_else_globinit()
    add_user(5)
    inc_xo_rating(5)
    add_user(6)
    inc_chess_rating(6)
    add_user(0)
    dec_xo_rating(0)
    add_user(1)
    dec_chess_rating(1)
    add_user(8)
    # del_user(8)
