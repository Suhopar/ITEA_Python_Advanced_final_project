import random
import string
from models.cats_and_products import Category, Product, Texts
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


def seed_and_cat_sub_cat(): # seed_sub_cat
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
            cat_obj.sub_categories = seed_and_get_categories(outerwear,language)
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
    connect('bot_shop')
    seed_and_cat_sub_cat()
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
