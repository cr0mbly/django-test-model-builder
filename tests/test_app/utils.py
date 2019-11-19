from django_test_model_builder import ModelBuilder, fake

from .models import Author, User


class AuthorBuilder(ModelBuilder):
    model = Author

    def get_default_fields(self):
        return {
            'user': UserBuilder().build(),
            'publishing_name': fake.name(),
            'age': fake.number(),
        }


class UserBuilder(ModelBuilder):
    model = User

    def get_default_fields(self):
        return {
            'email': fake.email(),
        }
