from django.test import TestCase
from django_test_model_builder import fake
from django_test_model_builder.exceptions import CannotSetFieldOnModelException

from .test_app.utils import AuthorBuilder
from .test_app.models import Author


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
        self.assertEqual(1, Author.objects.count())

    def test_multiple_models_are_generated_with_distinct_pks(self):
        number_of_models_to_generate = 50

        for _ in range(number_of_models_to_generate):
            author_id = AuthorBuilder().build().pk
            self.assertIsInstance(author_id, int)

        self.assertEqual(
            number_of_models_to_generate, Author.objects.all().count()
        )

    def test_dynamic_field_setter_changes(self):
        class CustomAuthorBuilder(AuthorBuilder):
            dynamic_field_setter_prefix = 'set_'

        new_publishing_name = fake.gibberish()
        author = (
            CustomAuthorBuilder()
            .set_publishing_name(new_publishing_name)
            .build()
        )
        self.assertEqual(new_publishing_name, author.publishing_name)
        self.assertEqual(1, Author.objects.count())

    def test_default_is_set_on_build(self):
        new_publishing_name = fake.name()

        class CustomAuthorBuilder(AuthorBuilder):
            def get_default_fields(self):
                defaults = super().get_default_fields()
                defaults['publishing_name'] = new_publishing_name
                return defaults

        author = CustomAuthorBuilder().build()
        self.assertEqual(new_publishing_name, author.publishing_name)
        self.assertEqual(1, Author.objects.count())

    def test_setting_non_existant_field_raises_an_exception(self):
        self.assertRaises(
            CannotSetFieldOnModelException,
            lambda: (
                AuthorBuilder()
                .with_non_existant_field(fake.gibberish())
                .build()
            )
        )

    def test_builder_can_chain_fields(self):
        new_publishing_name = fake.gibberish()
        new_age = fake.number()
        author = (
            AuthorBuilder()
            .with_publishing_name(new_publishing_name)
            .with_age(new_age)
            .build()
        )
        self.assertEqual(new_publishing_name, author.publishing_name)
        self.assertEqual(new_age, author.age)
        self.assertEqual(1, Author.objects.count())
