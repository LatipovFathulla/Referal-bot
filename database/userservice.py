from database import get_db
from database.models import User, AdminInfo, Withdrawals
from datetime import datetime

def add_user(tg_id, user_name, invited="Никто", invited_id=None):
    with next(get_db()) as db:
        new_user = User(tg_id=tg_id, user_name=user_name, invited=invited, invited_id=invited_id,
                        reg_date=datetime.now())
        db.add(new_user)
        db.commit()

def check_user(tg_id):
    with next(get_db()) as db:
        checker = db.query(User).filter_by(tg_id=tg_id).first()
        if checker:
            return True
        return False

def check_ban(tg_id):
    with next(get_db()) as db:
        checker = db.query(User).filter_by(tg_id=tg_id).first()
        if checker:
            if checker.banned == True:
                return True
        return False
def get_user_info_db(tg_id):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        if user:
            return [user.user_name, user.tg_id, user.balance, user.refs, user.invited, user.paid]

def plus_ref(tg_id):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        if user:
            user.refs += 1
            db.commit()
def plus_money(tg_id):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        money = db.query(AdminInfo).first().price
        if user:
            user.balance += money
            db.commit()
def reg_withdrawals(tg_id, amount, card, bank):
    with next(get_db()) as db:
        new_wa = Withdrawals(tg_id=tg_id, amount=amount, card=card, bank=bank)
        db.add(new_wa)
        db.commit()

