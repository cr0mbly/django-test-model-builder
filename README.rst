=====================
Django Model Builders
=====================

.. image:: https://travis-ci.com/publons/django-test-model-builder.svg?token=WSHb2ssbuqzAyoqCvdCs&branch=master
    :target: https://travis-ci.com/publons/django-test-model-builder

A small python / django model designed to decouple creation of models for
testing from the creation of models in production to make updating tests
less painful.

Quickstart
----------

**Create generic models without defining fields**

.. code-block:: python

    class User(AbstractBaseUser):
        username = models.CharField()

    class UserBuilder(ModelBuilder):
        model = User

        def get_default_fields(self):
            return {'username': 'test_username'}

    user = UserBuilder().build()
    print(user.username)
    >>> test_username


**Override defaults when required**

.. code-block:: python

    user = UserBuilder().with_username('test').build()
    >>> user.username
    >>> test


**Create multiple models with the same values**

.. code-block:: python

    builder = UserBuilder().with_username('test')
    user_1 = builder.build()
    user_2 = builder.build()

    user_1.username == user_2.username
    >>> True

    user_1 == user_2
    >>> False

**Update models without updating tests**

.. code-block:: python

    class User(AbstractBaseUser):
        username = models.CharField()
        dob = models.DateField()

    class UserBuilder(ModelBuilder):
        model = User
        def get_default_fields(self):
            return {
                'username': random_string,
                'dob': date(1990, 1, 1),
            }

    user = UserBuilder().build()

    user.dob
    >>> date(1990, 1, 1)

    user = (
        UserBuilder()
        .with_dob(date(2000, 1, 1))
        .build()
    )

    user.dob
    >>> date(2000, 1, 1)

**Setting defaults**

The :code:`get_default_fields` returns a dictionary used to populate any unset
model fields when the model is created. These can be values or callables if you
need to delay the creation of models until it is needed or want to generate
random data for each instance to avoid breaking database constraints.

.. code-block:: python

    class UserBuilder(ModelBuilder):
        model = User

        def get_default_fields():
            return {
                # Callable, each user will have a random username.
                'username': random_string,

                # Value, each user will have the same date of birth.
                'dob': date(1990, 1, 1),

                # Called with uninitiated build() call so duplicate model isn't
                # generated until comparison with any custom `with_` setter
                # functions, this field will be thrown away
                # if custom setter is present. You can also use a
                # lambda to achieve the same thing.
                'user': UserBuilder().build
        }


**Providing custom values using the "with_" prefix**

:code:`with_` functions are dynamically generated, these are used to override
defaults.

.. code-block:: python

    class UserBuilder(ModelBuilder):
        model = User
        def get_default_fields():
            return {
                'username': random_string,
                'dob': date(1990, 1, 1),
            }

    user = UserBuilder().with_dob(date(2019, 10, 10)).build()
    user.dob
    >>> date(2019, 10, 10)

All these functions do is set the passed in value as the function name in an
internal dictionary. This pattern can be used to create more readable tests.

Any function prefixed with :code:`with_` is automatically wrapped with a function
that returns a copy of the builder for side-effect-free chaining.

You can also explicitly define these :code:`with_<>` on the ModelBuilder subclass
to add your own implementation.

.. code-block:: python

    from datetime import timedelta

    class UserBuilder(ModelBuilder):
        model = User
        def get_default_fields():
            return {
                'username': random_string,
                'dob': date(1990, 1, 1)
            }

        def with_under_18():
            self.data['dob'] = date.today() - timedelta(years=17)

    UserBuilder().under_18().build()

Finally the :code:`with_` prefix is adjustable in case you have a blocking field that
you want use. For example you can change this to use the prefix :code:`set_` by going

.. code-block:: python

        class CustomAuthorBuilder(AuthorBuilder):
            dynamic_field_setter_prefix = 'set_'

        author = (
            CustomAuthorBuilder()
            .set_publishing_name('Billy Fakeington')
            .build()
        )

        author.publishing_name
        >>> 'Billy Fakeington'

**Calling .build()**

Building the model is broken into four steps.

- Prepare the data dictionary.
- Perform pre processing.
- Create the instance.
- Perform post possessing.

There is also a :code:`save_to_db` kwarg that can be set to optionally persist the
built model to memory only for use in more complicated tests.

**Perform pre processing**

By default this method changes models to their their :code:`_id` suffix. This can be
extended to perform additional preprocessing of fields.

.. code-block:: python

    from datetime import timedelta

    class UserBuilder(ModelBuilder):
        model = User
        def get_default_fields():
            return {
                'username': random_string,
                'dob': date(1990, 1, 1),
            }

        def pre(self):
            self['dob'] += timedelta(days=1)

    UserBuilder().build().dob
    # date(1990, 1, 2)

If you wanting to add non field values for accession by the pre/post hooks
you can override the :code:`get_builder_context` call to load any extra fields
which will be made available to the self.data dict after the initial model
fields have been set, for instance:

.. code-block:: python

    class AuthorBuilder(ModelBuilder):

        def get_default_fields():
            return {
                'username': random_string,
                'dob': date(1990, 1, 1)
            }

        def get_builder_context(self):
            return {
                'email_address': fake_email
            }

        def post(self):
            print(self.dict)

    AuthorBuilder().build()
    >>> {
    >>>     'username': random_string,
    >>>     'dob': date(1990, 1, 1),
    >>>     'email_address': fake_email
    >>> }

**Create the instance**

By default instances are created by calling :code:`model.objects.create`
with the models fields from the data dictionary. This behavior can be changed
by overriding the builders `.create` method, this method must set the builders
instance attribute`self.instance = ...`.

.. code-block:: python

    class UserBuilder(ModelBuilder):
        model = User

        def get_default_fields():
            return {
                'username': random_string,
            }

        def create(self):
            model = self.get_model()
            try:
                instance = self.model.objects.get(
                    username=self.data['username']
                )
            except model.objects.DoesNotExist:
                super(UserBuilder, self).create()

    builder = UserBuilder().with_username('test')
    user_1 = builder.build()
    user_2 = builder.build()

    user_1 == user_2
    >>> True

**Preform post processing**

Post processing is carried out after the instance has been created. By default
it does nothing, but provides a useful place to do things like add related
models.

.. code-block:: python

    class UserBuilder(ModelBuilder):
        model = User

        def get_default_fields():
            return {
                'username': random_string,
            }

        def with_emails(*args):
            self.data['emails'] = args

        def post(self):
            for email in self.data.get('emails', []):
                (
                    EmailBuilder()
                    .with_address(email)
                    .with_user(self.instance)
                    .build()
                )

    user = (
        UserBuilder()
        .with_emails(random_email(), random_email())
        .build()
    )

    user.email_set.count()
    >>> 2
