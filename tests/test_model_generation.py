from django.test import TestCase
from django_test_model_builder import fake

from .test_app.utils import AuthorBuilder

class TestAuthorModelCreation(TestCase):

    def test_model_is_generated_with_defaults(self):
        author = AuthorBuilder().build()
        self.assertIsNotNone(author.user)
        self.assertIsNotNone(author.publishing_name)
        self.assertIsNotNone(author.age)

    def test_model_is_generated_with_overridden_config(self):
        new_publishing_name = fake.gibberish()
        author = (
            AuthorBuilder()
            .with_publishing_name(new_publishing_name)
            .build()
        )
        self.assertEqual(new_publishing_name, author.publishing_name)
