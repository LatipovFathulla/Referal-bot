from database import get_db
from database.models import User, Channels, AdminInfo, Withdrawals
from datetime import datetime

def get_channels():
    with next(get_db()) as db:
        all_channels = db.query(Channels).all()
        if all_channels:
            return [i.channel_url for i in all_channels]
        return []
def add_chanel(channel_url):
    with next(get_db()) as db:
        new_channel = Channels(channel_url=channel_url)
        db.add(new_channel)
        db.commit()

def get_actual_price():
    with next(get_db()) as db:
        money = db.query(AdminInfo).first().price
        return money
def get_actual_min_amount():
    with next(get_db()) as db:
        amount = db.query(AdminInfo).first().min_amount
        return amount
def get_user_name(tg_id):
    with next(get_db()) as db:
        user = db.query(User).filter_by(tg_id=tg_id).first()
        if user:
            return user.user_name
def get_admin_info_chanels():
    with next(get_db()) as db:
        info = db.query(AdminInfo).first()
        return [info.admin_channel, info.payments_channel]

def add_admin_info():
    with next(get_db()) as db:
        info = AdminInfo(id=1, payments_channel="t.me/refer_jabyum", admin_channel="t.me/refer_jabyum")
        db.add(info)
        db.commit()
def count_info():
    with next(get_db()) as db:
        users = db.query(User).count()
        wa = db.query(Withdrawals).filter_by(status="выведено").all()
        amount = 0
        try:
            for i in wa:
                amount += i.amount
        except:
            pass
        return [users, amount]