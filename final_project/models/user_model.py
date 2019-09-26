from mongoengine import *


class User(Document):
    user_id = IntField()
    name = StringField()
    surname = StringField()
    nickname = StringField()
    user_state = IntField()
    language = StringField()

    @property
    def get_user_language(self):
        return self.language

    def new_language(self, lang):
        self.language = lang
        return

    @classmethod
    def get_or_create_user(cls, message, language):
        user = cls.objects.filter(user_id=message.from_user.id).first()
        if user:
            return user
        else:
            return cls(user_id=message.from_user.id,
                       name=message.from_user.first_name,
                       surname=message.from_user.last_name,
                       nickname=message.from_user.username,
                       language=language).save()
