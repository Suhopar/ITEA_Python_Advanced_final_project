from mongoengine import *
from mongoengine import IntField

from models.user_model import User


class Category(Document):
    title = StringField(max_length=64)
    sub_categories = ListField(ReferenceField('self'))
    language = StringField()

    def __str__(self):
        return f'title - {self.title}'

    @property
    def category_products(self):
        return Product.objects.filter(category=self)#,
                                      # is_available=True)

    @property
    def is_parent(self):
        if self.sub_categories:
            return True


class Product(Document):
    title = StringField(max_length=64)
    language = StringField()
    image = FileField(required=True)
    description = StringField(max_length=4096)
    price = IntField(min_value=0)
    quantity: IntField = IntField(min_value=0)
    is_available = BooleanField()
    is_discount = BooleanField(default=False)
    category = ReferenceField(Category)
    clothing_size = StringField(null=True)


    def __str__(self):
        return f'title - {self.title}, category - {self.category}, price - {self.price}'

    @property
    def get_product_info(self):
        return {"price": self.price/100,
                "clothing_size": self.clothing_size,
                "quantity": self.quantity}


class Texts(Document):
    title = StringField()
    text = StringField(max_length=4096)
    language = StringField()

    @classmethod
    def get_text(cls, title):
        return cls.objects.filter(title=title).first().text


class Cart(Document):
    user = ReferenceField(User, required=True)
    products = ListField(ReferenceField(Product))
    is_archived = BooleanField(default=False)

    @property
    def get_sum(self):
        cart_sum = 0
        for p in self.products:
            cart_sum += p.price

        return cart_sum/100

    @classmethod
    def create_or_append_to_cart(cls, product_id, user_id):
        user = User.objects.get(user_id=user_id)
        # for i in cls.objects:
        #     if i.user == user and not i.is_archived:
        user_cart = cls.objects.filter(user=user, is_archived=False).first()
        product = Product.objects.get(id=product_id)

        if user_cart and not user_cart.is_archived:
            user_cart.products.append(product)
            user_cart.save()
        else:
            cls(user=user, products=[product]).save()

    def clean_cart(self):
        self.products = []
        self.save()


class OrdersHistory(Document):
    user = ReferenceField(User)
    orders = ListField(ReferenceField(Cart))

    @classmethod
    def get_or_create(cls, user):
        history = cls.objects.filter(user=user).first()
        if history:
            return history
        else:
            return cls(user)

    @property
    def get_orders(self):
        return self.orders

    def __str__(self):
        return f'user - {self.user}, orders - {self.orders}'
