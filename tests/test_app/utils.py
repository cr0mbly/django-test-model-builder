from django_test_model_builder import ModelBuilder, fake

from .models import Author, User


class AuthorBuilder(ModelBuilder):
    model = Author

    defaults = {
        'user': lambda: UserBuilder().build(),
        'publishing_name': fake.name(),
        'age': fake.number(),
    }


class UserBuilder(ModelBuilder):
    model = User

    defaults = {
        'email': fake.email(),
    }
