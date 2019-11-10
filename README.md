# Django Model Builders
A small python / django model designed to decouple creation of models for
testing from the creation of models in production to make updating tests
less painful.

## Quickstart

### Create generic models without defining fields
```python
class User(AbstractBaseUser):
    username = models.CharField()

class UserBuilder(object):
    model = User
    defaults = {'username': random_string}

user = UserBuilder().build()

user.username
# ans92013u9021jdlands2
```

### Override defaults when required

```python
user = (
    UserBuilder()
    .with_username('test')
    .build()
)

user.username
# test

```
### Create multiple models with the same values

```python
builder = UserBuilder().with_username('test')
user_1 = builder.build()
user_2 = builder.build()

user_1.username == user_2.username
# True

user_1 == user_2
# False
```
### Update models without updating tests
```python
class User(AbstractBaseUser):
    username = models.CharField()
    dob = models.DateField()

class UserBuilder(ModelBuilder):
    model = User
    defaults = {
        'username': random_string,
        'dob': date(1990, 1, 1),
    }

user = UserBuilder().build()

user.dob
# date(1990, 1, 1)

user = (
    UserBuilder()
    .with_dob(date(2000, 1, 1))
    .build()
)

user.dob
# date(2000, 1, 1)
```

## Setting defaults

The defaults dictionary is used to populate any unset model fields when the
model is created. These can be values or callables if you need to delay the
creation of models until it is needed or want to generate random data for each
instance to avoid breaking database constraints.

```python
class UserBuilder(object):
    model = User
    defaults = {
        # Callable, each user will have a random username.
        'username': random_string,

        # Value, each user will have the same date of birth.
        'dob': date(1990, 1, 1),

        # Lambda, avoid creating models before they are loaded.
        'profile': lambda: ProfileBuilder().build()}
```

## Providing custom values using the `with_` prefix

`with_` functions are dynamically generated, these are used to override
defaults.

```python
class UserBuilder(object):
    model = User
    defaults = {
        'username': random_string,
        'dob': date(1990, 1, 1)}

 UserBuilder().with_dob(date.today()).build()
```
All these functions do it set the passed value as the function name in an
internal dictionary. This pattern can be used to create more readable tests.

```python
from datetime import timedelta


class UserBuilder(object):
    model = User
    defaults = {
        'username': random_string,
        'dob': date(1990, 1, 1)}

    def with_under_18():
        self.data['dob'] = date.today() - timedelta(years=17)

UserBuilder().under_18().build()
```

Any function prefixed with `with_` is automatically wrapped with a function
that returns a copy of the builder for side-effect-free chaining.

## Calling `.build()`
Building the model is broken broken into four steps.
* Prepare the data dictionary.
* Perform pre processing.
* Create the instance.
* Perform post possessing.

### Prepare the data dictionary

Populate the data dictionary of any unset fields with their defaults.

### Perform pre processing.

By default this method changes models to their their _id suffix. This can be
extended to perform additional preprocessing of fields.

```python
from datetime import timedelta


class UserBuilder(object):
    model = User
    defaults = {
        'username': random_string,
        'dob': date(1990, 1, 1),
    }

    def pre(self):
        self['dob'] += timedelta(days=1)

UserBuilder().build().dob
# date(1990, 1, 2)
```

### Create the instance

By default instances are created by calling `model.objects.create` with the
models fields from the data dictionary. This behavior can be changed by
overriding the builders `.create` method, this method must set the builders
instance attribute`self.instance = ...`.

```python
class UserBuilder(object):
    model = User
    defaults = {'username': random_string}

    def create(self):
        model = self.get_model()
        try:
            self.instance = self.model.objects.get(
                username=self.data['username']
            )
        except model.objects.DoesNotExist:
            super(UserBuilder, self).create()

builder = UserBuilder().with_username('test')
user_1 = builder.build()
user_2 = builder.build()

user_1 == user_2
# True
```

### Preform post processing

Post processing is carried out after the instance has been created. By default
it does nothing, but provides a useful place to do things like add related
models.

```python
class UserBuilder(object):
    model = User
    defaults = {'username': random_string}

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
# 2
```
