from django_test_model_builder import ModelBuilder

from .models import Author, User


class AuthorBuilder(ModelBuilder):
    model = Author

    def get_default_fields(self):
        return {
            'user': UserBuilder().build,
            'publishing_name': 'Jack Jackson',
            'age': 23,
        }


class UserBuilder(ModelBuilder):
    model = User

    def get_default_fields(self):
        return {
            'email': 'fakeFakeson@gmail.com',
        }
