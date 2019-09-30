import telebot
from bot.config import TOKEN, START_KEYBOARD, MESSAGE_NOTIFICATION
from models.cats_and_products import Texts, Category, Cart, Product, OrdersHistory
from mongoengine import connect, register_connection
from models.user_model import User
from bson import ObjectId
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)
#---
#sudo apt-get install openssl
#openssl genrsa -out webhook_pkey.pem 2048
#openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
import time
from flask import Flask, request, abort
# from mongoengine import register_connection
#
# register_connection(alias=None, db='bot_shop', host='35.224.157.246', port='27017')

connect('bot_shop')
bot = telebot.TeleBot(TOKEN)

API_TOKEN = TOKEN

WEBHOOK_HOST = '35.224.157.246'
WEBHOOK_PORT = 80  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)


app = Flask(__name__)

# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if  request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)


class Storage:
    language = 'uk'


@bot.message_handler(commands=['start'])
def language_or_greetings(message):
    if User.objects(user_id=message.from_user.id):
        language = User.objects.get(user_id=message.from_user.id).get_user_language
        Storage.language = language
        start_keyboard = START_KEYBOARD[language]
        s = u'\U0000270C'
        hello = s + Texts.objects.get(title='Greetings', language=language).text + f', {message.chat.first_name}'
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(*start_keyboard.values())
        bot.send_message(message.chat.id, hello, reply_markup=kb)
    else:
        Storage.language = 'uk'
        User.get_or_create_user(message, 'uk')
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(*START_KEYBOARD['uk'].values())


@bot.message_handler(func=lambda m: m.text == START_KEYBOARD[Storage.language]['category'])
def show_category(message):
    print("Category")
    if User.objects.get(user_id=message.from_user.id):
        language = User.objects.get(user_id=message.from_user.id).get_user_language
    else:
        language = 'uk'
    inline_kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons_list = []
    for i in Category.objects:
        callback_data = 'category_' + str(i.id)
        if i.is_parent:
            callback_data = 'subcategory_' + str(i.id)
            buttons_list.append(
                telebot.types.InlineKeyboardButton(text=i.title + " >>", callback_data=callback_data))
        # else:
        #     buttons_list.append(
        #         telebot.types.InlineKeyboardButton(text=i.title, callback_data=callback_data))
    inline_kb.add(*buttons_list)
    bot.send_message(chat_id=message.chat.id,
                     text=START_KEYBOARD[language]['category'],
                     reply_markup=inline_kb, )


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'subcategory')
def sub_cat(call):
    print(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    subcats_kb = telebot.types.InlineKeyboardMarkup()
    subcats_buttons = []
    subcats = Category.objects.get(id=call.data.split('_')[1])
    for i in subcats.sub_categories:
        # if i.is_parent:
        #     callback_data = 'subcategory_' + str(i.id)
        # else:
        callback_data = 'category_' + str(i.id)

        subcats_buttons.append(
            telebot.types.InlineKeyboardButton(text=i.title,
                                               callback_data=callback_data)
        )
    subcats_buttons.append(
        telebot.types.InlineKeyboardButton(text="<<",
                                           callback_data="<<")
    )
    subcats_kb.add(*subcats_buttons)
    bot.send_message(call.from_user.id,
                     text='sub category',
                     reply_markup=subcats_kb)


@bot.callback_query_handler(func=lambda call: call.data == '<<')
def beck_to_cat(call):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    if User.objects.get(user_id=call.message.chat.id):
        language = User.objects.get(user_id=call.message.chat.id).get_user_language
    else:
        language = 'uk'
    inline_kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons_list = []
    for i in Category.objects:
        callback_data = 'category_' + str(i.id)
        if i.is_parent:
            callback_data = 'subcategory_' + str(i.id)
            buttons_list.append(
                telebot.types.InlineKeyboardButton(text=i.title + " >>", callback_data=callback_data))
        # else:
        #     buttons_list.append(
        #         telebot.types.InlineKeyboardButton(text=i.title, callback_data=callback_data))
    inline_kb.add(*buttons_list)
    bot.send_message(chat_id=call.message.chat.id,
                     text=START_KEYBOARD[language]['category'],
                     reply_markup=inline_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'category')
def show_product(call):
    print(call.data.split('_')[1])
    cat = Category.objects.filter(id=call.data.split('_')[1]).first()
    print(call)
    products = cat.category_products
    print(products)
    language = User.objects.get(user_id=call.from_user.id).get_user_language
    cart_lang = MESSAGE_NOTIFICATION[language]['in_cart']
    info_lang = MESSAGE_NOTIFICATION[language]['details']

    if not products:
        bot.send_message(call.message.chat.id, MESSAGE_NOTIFICATION[language]['no_products_in_category'])

    for p in products:
        products_kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        products_kb.add(telebot.types.InlineKeyboardButton(text=cart_lang,
                                                           callback_data='addtocart_' + str(p.id)),
                        telebot.types.InlineKeyboardButton(text=info_lang,
                                                           callback_data='product_' + str(p.id)))

        bot.send_photo(call.message.chat.id, p.image.get(),
                       caption=p.title +'\n'+ p.description, reply_markup=products_kb)
        # bot.send_message(call.message.chat.id, text=p.title, reply_markup=products_kb)  # +'\n'+ p.description


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'addtocart')
def add_to_cart(call):
    Cart.create_or_append_to_cart(product_id=call.data.split('_')[1],
                                  user_id=call.message.chat.id)
    cart = Cart.objects.all().first()
    print("add_to_cart - ", cart.products)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'product')
def show_info_product(call):
    product_info = Product.objects.get(id=call.data.split('_')[1]).get_product_info
    bot.send_message(call.message.chat.id, f"{MESSAGE_NOTIFICATION[Storage.language]['price']} - {product_info['price']}"
    f"\n{MESSAGE_NOTIFICATION[Storage.language]['clothing_size']}"
    f" - {product_info['clothing_size']}"
    f"\n{MESSAGE_NOTIFICATION[Storage.language]['quantity']}"
    f" - {product_info['quantity']}")


@bot.message_handler(func=lambda m: m.text == START_KEYBOARD[Storage.language]['cart'])
def show_cart(message):
    current_user = User.objects.get(user_id=message.chat.id)
    cart = Cart.objects.filter(user=current_user, is_archived=False).first()
    language = User.objects.get(user_id=message.from_user.id).get_user_language
    if not cart:
        bot.send_message(message.chat.id, MESSAGE_NOTIFICATION[language]['cart_empty'])
        return

    if not cart.products:
        bot.send_message(message.chat.id, MESSAGE_NOTIFICATION[language]['cart_empty'])
        return

    for product in cart.products:
        remove_kb = InlineKeyboardMarkup()
        remove_button = InlineKeyboardButton(text=MESSAGE_NOTIFICATION[language]['remove_product_from_cart'],
                                             callback_data='rmproduct_' + str(product.id))
        remove_kb.add(remove_button)
        bot.send_message(message.chat.id, product.title,
                         reply_markup=remove_kb)

    submit_kb = InlineKeyboardMarkup()
    submit_button = InlineKeyboardButton(
        text=MESSAGE_NOTIFICATION[language]['сheckout_order'],
        callback_data='submit'
    )
    submit_kb.add(submit_button)
    bot.send_message(message.chat.id,
                     MESSAGE_NOTIFICATION[Storage.language]['confirm_your_order'], reply_markup=submit_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'rmproduct')
def rm_product_from_cart(call):
    current_user = User.objects.get(user_id=call.message.chat.id)
    cart = Cart.objects.get(user=current_user)
    cart.update(pull__products=ObjectId(call.data.split('_')[1]))
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'submit')
def submit_cart(call):
    current_user = User.objects.get(user_id=call.message.chat.id)
    cart = Cart.objects.filter(user=current_user, is_archived=False).first()
    cart.is_archived = True

    order_history = OrdersHistory.get_or_create(current_user)
    order_history.orders.append(cart)
    bot.send_message(call.message.chat.id, MESSAGE_NOTIFICATION[current_user.get_user_language]['thank_for_order'])
    cart.save()
    order_history.save()


@bot.message_handler(func=lambda m: m.text == START_KEYBOARD[Storage.language]['cart_archive'])
def show_arh(message):
    list_product = (OrdersHistory.objects.filter(user=User.objects.get(user_id=message.chat.id)).first()).get_orders
    for i in range(0, len(list_product)):
        p = list_product[i].products
        for i in range(0, len(p)):
            bot.send_message(message.chat.id, p[i].title)


@bot.message_handler(func=lambda m: m.text == START_KEYBOARD[Storage.language]['language'])
def language(message):
    products_kb = telebot.types.InlineKeyboardMarkup(row_width=2)
    products_kb.add(telebot.types.InlineKeyboardButton(text='uk',
                                                       callback_data='language_' + 'uk'),
                    telebot.types.InlineKeyboardButton(text='ru',
                                                       callback_data='language_' + 'ru'))
    bot.send_message(message.chat.id, text='language', reply_markup=products_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'language')
def language_upd(call):
    lang = call.data.split('_')[1]
    User.objects(user_id=call.message.chat.id).update(language=lang)
    Storage.language = lang
    bot.send_message(call.message.chat.id, MESSAGE_NOTIFICATION[lang]['enter_start'])


@bot.message_handler(func=lambda m: m.text == START_KEYBOARD[Storage.language]['latest_news'])
def latest_news(message):
    print("Latest news")
    bot.send_message(message.chat.id, Texts.objects.get(title=START_KEYBOARD['uk']['latest_news'],
                                                        language=User.objects.get(
                                                            user_id=message.from_user.id).get_user_language).text)


@bot.message_handler(func=lambda m: m.text == START_KEYBOARD[Storage.language]['buyer_information'])
def buyer_information(message):
    print("Buyer Information")
    bot.send_message(message.chat.id, Texts.objects.get(title=START_KEYBOARD['uk']['buyer_information'],
                                                        language=User.objects.get(
                                                            user_id=message.from_user.id).get_user_language).text)



bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)