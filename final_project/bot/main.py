import telebot
from bot.config import TOKEN, START_KEYBOARD
from models.cats_and_products import Texts, Category, Cart, Product, OrdersHistory
from mongoengine import connect
from models.user_model import User
from bson import ObjectId
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

connect('bot_shop')
bot = telebot.TeleBot(TOKEN)


class Storage:
    language = ''
    user_id = ''


@bot.message_handler(commands=['start'])
def language_or_greetings(message):
    if User.objects(user_id=message.from_user.id):
        language = User.objects.get(user_id=message.from_user.id).get_user_language
        start_keyboard = START_KEYBOARD[language]
        s = u'\U0000270C'
        hello = s + Texts.objects.get(title='Greetings', language=language).text + f', {message.chat.first_name}'
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(*start_keyboard.values())
        bot.send_message(message.chat.id, hello, reply_markup=kb)

    else:
        kb = ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add(START_KEYBOARD['uk'].values())


@bot.message_handler(func=lambda m: m.text == 'Category' or m.text == 'Категории')
def show_category(message):
    print("Category")
    if User.objects.get(user_id=message.from_user.id):
        language = User.objects.get(user_id=message.from_user.id).get_user_language
    else:
        language = 'uk'
    inline_kb = telebot.types.InlineKeyboardMarkup()
    buttons_list = []
    for i in Category.objects:
        callback_data = 'category_' + str(i.id)
        if i.is_parent:
            callback_data = 'subcategory_' + str(i.id)
            buttons_list.append(
                telebot.types.InlineKeyboardButton(text=i.title + " >>", callback_data=callback_data))
        else:
            buttons_list.append(
                telebot.types.InlineKeyboardButton(text=i.title, callback_data=callback_data))
    inline_kb.add(*buttons_list)
    bot.send_message(chat_id=message.chat.id,
                     text=START_KEYBOARD[language]['category'],
                     reply_markup=inline_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'subcategory')
def sub_cat(call):
    print(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    subcats_kb = telebot.types.InlineKeyboardMarkup()
    subcats_buttons = []
    subcats = Category.objects.get(id=call.data.split('_')[1])
    for i in subcats.sub_categories:
        callback_data = 'category_' + str(i.id)

        if i.is_parent:
            callback_data = 'subcategory_' + str(i.id)

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


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'category')
def show_product(call):
    cat = Category.objects.filter(id=call.data.split('_')[1]).first()
    print(call)
    products = cat.category_products

    language = User.objects.get(user_id=call.from_user.id).get_user_language
    cart_lang = ""
    info_lang = ""
    # START_KEYBOARD[language]['category']
    if language == 'uk':
        cart_lang = "Basket"
        info_lang = "Details"
    elif language == 'ru':
        cart_lang = "Корзина"
        info_lang = "Подробно"

    if not products:
        bot.send_message(call.message.chat.id, 'В данной категории пока нет продуктов.')

    for p in products:
        products_kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        products_kb.add(telebot.types.InlineKeyboardButton(text=cart_lang,
                                                           callback_data='addtocart_' + str(p.id)),
                        telebot.types.InlineKeyboardButton(text=info_lang,
                                                           callback_data='product_' + str(p.id)))

        bot.send_photo(call.message.chat.id, p.image.get(),
                       caption=p.title + p.description, reply_markup=products_kb)
        # bot.send_message(call.message.chat.id, text=p.title + p.description, reply_markup=products_kb)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'addtocart')
def add_to_cart(call):
    Cart.create_or_append_to_cart(product_id=call.data.split('_')[1],
                                  user_id=call.message.chat.id)
    cart = Cart.objects.all().first()
    print("add_to_cart - ", cart.products)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'product')
def show_info_product(call):
    product_info = Product.objects.get(id=call.data.split('_')[1]).get_product_info
    bot.send_message(call.message.chat.id, f"price - {product_info['price']}"
                                           f"\nweight - {product_info['weight']}"
                                           f"\nwidth - {product_info['width']}"
                                           f"\nheight - {product_info['height']}"
                                           f"\nquantity - {product_info['quantity']}")


@bot.message_handler(func=lambda message: message.text == 'Basket') # Cart
def show_cart(message):
    current_user = User.objects.get(user_id=message.chat.id)
    cart = Cart.objects.filter(user=current_user, is_archived=False).first()

    if not cart:
        bot.send_message(message.chat.id, 'Корзина пустая')
        return

    if not cart.products:
        bot.send_message(message.chat.id, 'Корзина пустая')
        return

    for product in cart.products:
        remove_kb = InlineKeyboardMarkup()
        remove_button = InlineKeyboardButton(text='Удалить продукт с корзины',
                                             callback_data='rmproduct_' + str(product.id))
        remove_kb.add(remove_button)
        bot.send_message(message.chat.id, product.title,
                         reply_markup=remove_kb)

    submit_kb = InlineKeyboardMarkup()
    submit_button = InlineKeyboardButton(
        text='Оформить заказ',
        callback_data='submit'
    )
    submit_kb.add(submit_button)
    bot.send_message(message.chat.id, 'Подтвердите Ваш заказ', reply_markup=submit_kb)


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
    bot.send_message(call.message.chat.id, 'Спасибо за заказ!')
    cart.save()
    order_history.save()


@bot.message_handler(func=lambda m: m.text == 'Past purchases' or m.text == 'Прошлые покупки')
def show_arh(message):
    list_product = (OrdersHistory.objects.filter(user=User.objects.get(user_id=message.chat.id)).first()).get_orders
    for i in range(0, len(list_product)):
        p = list_product[i].products
        for i in range(0, len(p)):
            bot.send_message(message.chat.id, p[i].title)



@bot.message_handler(func=lambda m: m.text == 'Latest news' or m.text == 'Последние новости')
def latest_news(message):
    print("Latest news")
    bot.send_message(message.chat.id, Texts.objects.get(title=START_KEYBOARD['uk']['latest_news'],
                                                        language=User.objects.get(
                                                            user_id=message.from_user.id).get_user_language).text)


@bot.message_handler(func=lambda m: m.text == 'Buyer Information' or m.text == 'Информация для покупателя')
def buyer_information(message):
    print("Buyer Information")
    bot.send_message(message.chat.id, Texts.objects.get(title=START_KEYBOARD['uk']['buyer_information'],
                                                        language=User.objects.get(
                                                            user_id=message.from_user.id).get_user_language).text)


if __name__ == '__main__':
    print("Bot started")
    bot.polling()
