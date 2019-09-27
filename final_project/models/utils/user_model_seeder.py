import random
import string
from models.cats_and_products import Category, Product, Texts
from models.user_model import User
from mongoengine import connect

random_bool = (True, False)


def random_string(str_len=20):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(str_len))


def seed_and_get_categories(list_cat, language):
    category_list = []
    for i in range(0, len(list_cat)):
        cat = Category(title=list_cat[i], language=language).save()
        category_list.append(cat)
    return category_list


def seed_and_get_categories_2():
    category_list = ["Outerwear", "T-shirts and shirts", "Pants", "Footwear", "Other clothes"]
    language = 'uk'
    l = []
    for i in range(0, len(category_list)):
        l.append(Category(title=str(category_list[i]), language=language).save())
    return l


def seed_and_cat_sub_cat():  # seed_sub_cat
    cats = seed_and_get_categories_2()
    language = 'uk'
    # category_list = ["Outerwear", "T-shirts and shirts", "Pants", "Footwear", "Other clothes"]
    outerwear = ["Jackets"]
    t_shirts_and_shirts = ["Blouse", "T-shirt", "Shirts"]
    pants = ["Sports Pants", "Casual Pants", "Shorts"]
    footwear = ["Sneakers", "Shoes"]
    other_clothes = ["Dress", "Pajamas", "Overalls", "Spacesuit"]

    for obj_cat in Category.objects:
        if obj_cat.title == 'Outerwear':
            cat_obj = Category.objects.get(title="Outerwear", language=language)
            cat_obj.sub_categories = seed_and_get_categories(outerwear, language)
            cat_obj.save()
        elif obj_cat.title == 'T-shirts and shirts':
            cat_obj = Category.objects.get(title="T-shirts and shirts", language=language)
            cat_obj.sub_categories = seed_and_get_categories(t_shirts_and_shirts, language)
            cat_obj.save()
        elif obj_cat.title == 'Pants':
            cat_obj = Category.objects.get(title="Pants", language=language)
            cat_obj.sub_categories = seed_and_get_categories(pants, language)
            cat_obj.save()
        elif obj_cat.title == 'Footwear':
            cat_obj = Category.objects.get(title="Footwear", language=language)
            cat_obj.sub_categories = seed_and_get_categories(footwear, language)
            cat_obj.save()
        elif obj_cat.title == 'Other clothes':
            cat_obj = Category.objects.get(title="Other clothes", language=language)
            cat_obj.sub_categories = seed_and_get_categories(other_clothes, language)
            cat_obj.save()


def seed_products():
    all_cat = ["Jackets", "Blouse", "T-shirt", "Shirts", "Sports Pants", "Casual Pants", "Shorts", "Sneakers",
               "Shoes", "Dress", "Pajamas", "Overalls", "Spacesuit"]
    clothing_size_list = ["XS", "S", "M", "L", "XL", "XXL"]
    for i in all_cat:
        for e in range(1, 4):
            cat_title = Category.objects.get(title=i)
            product = dict(
                title=i + ' ' + str(e),
                description='Very cool ' + i + str(e),
                price=random.randint(1000, 100 * 1000),
                quantity=random.randint(0, 100),
                is_available=random.choice(random_bool),
                is_discount=random.choice(random_bool),
                clothing_size=random.choice(clothing_size_list),
                category=Category.objects.get(title=i)

            )
            prod = Product(**product).save()
            url = i+'.jpg'
            with open(r'..\..\bot\images\%s' % (url), 'rb') as image:
                prod.image.put(image)
                prod.save()


def seed_products_with_image():
    products = Product.objects.all()
    all_cat = ["Jackets", "Blouse", "T-shirt", "Shirts", "Sports Pants", "Casual Pants", "Shorts", "Sneakers",
               "Shoes", "Dress", "Pajamas", "Overalls", "Spacesuit"]
    for i in products:
        title = i.title

        with open(r'images\test.png', 'rb') as image:
            i.image.put(image)
            i.save()


def seed_texts():
    title_list = ["Greetings", "Greetings", "Latest news", "Latest news", "Buyer Information", "Buyer Information"]
    text_list = ["Good day", "Доброго времени суток",
                 "A batch of T-shirts with a print of a cowboy-sloth riding a pig has been stolen",
                 "Была украдена партия футболок с принтом ленивца-ковбоя на свинье",
                 "There will be no discounts", "Не будет никаких скидок"]
    l = ''
    for i in range(6):
        if i == 0:
            l = 'uk'
        elif i % 2:
            l = 'ru'
        else:
            l = 'uk'
        text = dict(
            title=title_list[i],
            text=text_list[i],
            language=l
        )
        Texts(**text).save()


if __name__ == '__main__':

    # pass
    connect('bot_shop')
    # user_tst = dict(user_id=8888888,
    #            name='tst',
    #            surname='tst',
    #            nickname='tst',
    #            language='uk')
    # User(**user_tst).save()
    # seed_texts()
    # seed_and_cat_sub_cat()
    seed_products()


