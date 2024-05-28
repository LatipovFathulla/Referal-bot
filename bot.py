from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand, CallbackQuery
from buttons import *
from database.otherservice import *
from database.userservice import *
from states import PaymentState

bot_router = Router()

async def check_channels(message):
    all_channels = get_channels()
    for i in all_channels:
        try:
            check = await message.bot.get_chat_member(f"{i}", user_id=message.from_user.id)
            print("Проверил")
            if check.status in ["left"]:
                await message.bot.send_message(chat_id=message.from_user.id,
                                               text="Для использования бота подпишитесь на наших спонсоров",
                                               reply_markup=await channels_in(all_channels))
                return False

        except:
            print("Не проверил")
            pass
    return True
async def banned(message):
    check = check_ban(message.from_user.id)
    if check:
        await message.bot.send_message(chat_id=message.from_user.id,
                                       text="Вы были заблокированы")
        return False
    return True



@bot_router.message(CommandStart())
async def start(message: Message, command: BotCommand = None):
    channels_checker = await check_channels(message)
    checker = check_user(message.from_user.id)
    checker_banned = await banned(message)
    if command.args and not checker and checker_banned:
        inv_id = int(decode_payload(command.args))
        inv_name = get_user_name(inv_id)
        if inv_name:
            add_user(user_name=message.from_user.first_name, tg_id=message.from_user.id,
                     invited=inv_name, invited_id=inv_id)
            plus_ref(inv_id)
            plus_money(inv_id)
            await message.bot.send_message(message.from_user.id, f"🎉Привет, {message.from_user.first_name}",
                                           reply_markup=await main_menu_bt())
        elif not inv_name:
            add_user(user_name=message.from_user.first_name, tg_id=message.from_user.id)
            await message.bot.send_message(message.from_user.id, f"🎉Привет, {message.from_user.first_name}",
                                           reply_markup=await main_menu_bt())
    elif not checker and checker_banned:
        add_user(user_name=message.from_user.first_name, tg_id=message.from_user.id)
        await message.bot.send_message(message.from_user.id, f"🎉Привет, {message.from_user.first_name}",
                                       reply_markup= await main_menu_bt())
    elif channels_checker and checker_banned and checker:
        await message.bot.send_message(message.from_user.id, f"🎉Привет, {message.from_user.first_name}",
                                       reply_markup= await main_menu_bt())



@bot_router.message(F.text=="💸Заработать")
async def gain(message: Message):
    channels_checker = await check_channels(message)
    checker_banned = await banned(message)
    if channels_checker and checker_banned:
        link = await create_start_link(message.bot, str(message.from_user.id), encode=True)
        price = get_actual_price()
        await message.bot.send_message(message.from_user.id,f"👥 Приглашай друзей и зарабатывай, за \nкаждого друга ты получишь {price}₽\n\n"
                             f"🔗 Ваша ссылка для приглашений:\n {link}")
@bot_router.message(F.text=="📱Профиль")
async def profile(message: Message):
    channels_checker = await check_channels(message)
    checker_banned = await banned(message)
    if channels_checker and checker_banned:
        info = get_user_info_db(message.from_user.id)
        if info:
            await message.bot.send_message(message.from_user.id, f"📝 Ваше имя: {info[0]}\n"
                                                                 f"🆔 Ваш ID: <code>{info[1]}</code>\n"
                                                                 f"==========================\n"
                                                                 f"💳 Баланс: {info[2]}\n"
                                                                 f"👥 Всего друзей: {info[3]}\n"
                                                                 f"👤 Вас привел {info[4]}\n"
                                                                 f"==========================\n",
                                           parse_mode="html", reply_markup= await payment_in())

@bot_router.message(F.text=="ℹ️Инфо")
async def info(message: Message):
    channels_checker = await check_channels(message)
    checker_banned = await banned(message)
    if channels_checker and checker_banned:
        all_info = count_info()
        # TODO изменить на юзернейм админа
        admin_user = "@refer_jabyum"
        await message.bot.send_message(message.from_user.id,
                                       f"👥 Всего пользователей: {all_info[0]}\n"
                                       f"📤 Выплачено всего: {all_info[1]}",
                                       reply_markup=await admin_in(admin_user))


@bot_router.callback_query(F.data.in_(["payment", "check_chan"]))
async def call_backs(query: CallbackQuery, state: FSMContext):
    await state.clear()
    if query.data == "payment":
        balance = get_user_info_db(query.from_user.id)[2]
        min_amount = get_actual_min_amount()
        check_wa = check_for_wa(query.from_user.id)
        if balance < min_amount:
            await query.message.bot.answer_callback_query(query.id, text=f"🚫Минимальная сумма вывода: {min_amount}",
                                                          show_alert=True)
        elif check_wa:
            await query.message.bot.answer_callback_query(query.id, text="⏳Вы уже оставили заявку. Ожидайте",
                                                          show_alert=True)
        elif balance >= min_amount:
            await query.bot.send_message(query.from_user.id, "💳Введите номер вашей карты", reply_markup= await cancel_bt())
            await state.set_state(PaymentState.get_card)
    elif query.data == "check_chan":
        checking = await check_channels(query)
        await query.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        if checking:
            await query.bot.send_message(query.from_user.id, f"🎉Привет, {query.from_user.first_name}",
                                         reply_markup= await main_menu_bt())

@bot_router.message(PaymentState.get_card)
async def get_card(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text:
        card = message.text
        await message.bot.send_message(message.from_user.id, "🏦Введите название банка")
        await state.set_data({"card": card})
        await state.set_state(PaymentState.get_bank)
    else:
        await message.bot.send_message(message.from_user.id, "❗️Ошибка", reply_markup= await main_menu_bt())
        await state.clear()

@bot_router.message(PaymentState.get_bank)
async def get_bank(message: Message, state: FSMContext):
    if message.text == "❌Отменить":
        await message.bot.send_message(message.from_user.id, "🚫Действие отменено", reply_markup=await main_menu_bt())
        await state.clear()
    elif message.text:
        bank = message.text
        card = await state.get_data()
        balance = get_user_info_db(message.from_user.id)[2]
        await message.bot.send_message(message.from_user.id, "✅Заявка на выплату принята. Ожидайте ответ",
                                       reply_markup= await main_menu_bt())
        reg_withdrawals(tg_id=message.from_user.id, amount=balance, card=card.get('card'), bank=bank)
        await state.clear()
    else:
        await message.bot.send_message(message.from_user.id, "️️❗Ошибка", reply_markup= await main_menu_bt())
        await state.clear()







