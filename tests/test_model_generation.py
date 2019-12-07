from django.test import TestCase

from .test_app.utils import AuthorBuilder, UserBuilder
from .test_app.models import Author, User


class TestAuthorModelCreation(TestCase):

    def setUp(self):
        self.publishing_name = 'Billy Fakington'

    def test_model_is_generated_with_defaults(self):
        author = AuthorBuilder().build()
        self.assertIsNotNone(author.user)
        self.assertIsNotNone(author.publishing_name)
        self.assertIsNotNone(author.age)

    def test_model_is_generated_with_overridden_config(self):
        author = (
            AuthorBuilder()
            .with_publishing_name(self.publishing_name)
            .build()
        )
        self.assertEqual(self.publishing_name, author.publishing_name)
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

        author = (
            CustomAuthorBuilder()
            .set_publishing_name(self.publishing_name)
            .build()
        )
        self.assertEqual(self.publishing_name, author.publishing_name)
        self.assertEqual(1, Author.objects.count())

    def test_default_is_set_on_build(self):
        new_publishing_name = self.publishing_name
        class CustomAuthorBuilder(AuthorBuilder):
            def get_default_fields(self):
                defaults = super().get_default_fields()
                defaults['publishing_name'] = new_publishing_name
                return defaults

        author = CustomAuthorBuilder().build()
        self.assertEqual(self.publishing_name, author.publishing_name)
        self.assertEqual(1, Author.objects.count())

    def test_builder_can_chain_fields(self):
        new_age = 3
        author = (
            AuthorBuilder()
            .with_publishing_name(self.publishing_name)
            .with_age(new_age)
            .build()
        )
        self.assertEqual(self.publishing_name, author.publishing_name)
        self.assertEqual(new_age, author.age)
        self.assertEqual(1, Author.objects.count())

    def test_builder_can_override_user(self):
        new_user = UserBuilder().build()
        author = (
            AuthorBuilder()
            .with_user(new_user)
            .build()
        )
        self.assertEqual(new_user, author.user)
        self.assertEqual(1, User.objects.count())

    def test_builder_can_save_model_in_memory(self):
        author = (
            AuthorBuilder()
            .with_publishing_name(self.publishing_name)
            .build(save_to_db=False)
        )
        self.assertEqual(self.publishing_name, author.publishing_name)
        self.assertEqual(0, Author.objects.count())

    def test_builder_can_use_post_builder_calls(self):
        fake_email = 'test@test.com'

        class CustomAuthorBuilder(AuthorBuilder):

            def with_user_email(self, user_email=None):
                self.data['user_email'] = user_email

            def post(self):
                self.instance.user = (
                    UserBuilder().with_email(self.data['user_email']).build()
                )

        author = CustomAuthorBuilder().with_user_email(fake_email).build()

        self.assertEqual(fake_email, author.user.email)

    def test_builder_can_use_post_builder_call_with_exta_non_field_data(self):
        fake_email = 'test@test.com'

        class CustomAuthorBuilder(AuthorBuilder):

            def get_extra_model_config(self):
                return {
                    'email_address': fake_email
                }

            def post(self):
                self.instance.user = (
                    UserBuilder()
                    .with_email(self.data['email_address'])
                    .build()
                )

        author = CustomAuthorBuilder().build()

        self.assertEqual(fake_email, author.user.email)

    def test_builder_extra_non_field_data_is_overridden_on_redefinition(self):
        fake_email = 'test@test.com'

        class CustomAuthorBuilder(AuthorBuilder):

            def get_extra_model_config(self):
                return {
                    'email_address': 'test_email@gmail.com'
                }

            def with_alternaitve_email(self, email):
                self.data['email_address'] = email

            def post(self):
                self.instance.user = (
                    UserBuilder()
                    .with_email(self.data['email_address'])
                    .build()
                )

        author = (
            CustomAuthorBuilder()
            .with_alternaitve_email(fake_email)
            .build()
        )

        self.assertEqual(fake_email, author.user.email)


    def test_builder_field_is_redefined_on_pre_configuration(self):
        fake_email = 'test@test.com'

        class CustomAuthorBuilder(AuthorBuilder):

            def pre(self):
                self.model_fields['user'].email = fake_email
                self.model_fields['user'].save()

        author = CustomAuthorBuilder().build()

        self.assertEqual(fake_email, author.user.email)
