import random
import string
from models.cats_and_products import Category, Product, Texts
from mongoengine import connect

random_bool = (True, False)


def random_string(str_len=20):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(str_len))


def seed_and_get_categories(num_of_cats):
    category_list = []
    for i in range(num_of_cats):
        cat = Category(title=random_string()).save()
        category_list.append(cat)
    return category_list


def seed_and_get_categories_2():
    category_list = ["pants", "blouse", "T-shirt", "shorts", "dress",
                     "jackets", "pajamas", "overalls", "sneakers", "shoes"]
    l = []
    for i in range(0, len(category_list)):
        l.append(Category(title=str(category_list[i])).save())
    return l


def seed_products(nam_of_products, list_of_cats):
    for i in range(nam_of_products):
        product = dict(
            title=random_string(),
            description=random_string(),
            price=random.randint(1000, 100 * 1000),
            quantity=random.randint(0, 100),
            is_available=random.choice(random_bool),
            is_discount=random.choice(random_bool),
            weight=random.uniform(0, 100),
            width=random.uniform(0, 100),
            height=random.uniform(0, 100),
            category=random.choice(list_of_cats)
        )
        Product(**product).save()

def seed_products_with_image():
    products = Product.objects.all()
    image = open(r'C:\python_base\ITEA_Python_Advanced\lesson_adv_13_classwork\bot\images\tst.jpg', 'rb')
    for i in products:
        with open(r'C:\python_base\ITEA_Python_Advanced\lesson_adv_13_classwork\bot\images\tst.jpg', 'rb') as image:
            i.image.replace(image)
            i.save()



if __name__ == '__main__':
    pass
    # connect('bot_shop')
    # # #
    # seed_products_with_image()
    # cats = seed_and_get_categories_2()
    # seed_products(20, cats)
    # text = dict(
    #     title='Greetings',
    #     text='Доброго времени суток',
    #     language='ru'
    # )
    # Texts(**text).save()
    # cats = seed_and_get_categories_2()
    # cat_obj = Category.objects.get(title="sneakers")
    # cat_obj.sub_categories = cats
    # print(cat_obj.save())
