import copy

from django.db import models

from . import fake


class ModelBuilder:
    def __init__(self):
        self.data = {}

    def copy(self):
        return copy.deepcopy(self)

    def get_defaults(self):
        """
        Default values to be used when building the model.
        """
        try:
            defaults = self.defaults
        except AttributeError:
            raise ValueError(
                'Defaults should be set class or this method should be '
                'overridden.'
            )
        else:
            if callable(defaults):
                return defaults()
            else:
                return defaults

    def get_model(self):
        try:
            return self.model
        except AttributeError:
            raise ValueError(
                'Model should be set on class or this method should be '
                'overridden'
            )

    def get_model_attributes(self):
        return [f.attname for f in self.model._meta.fields]

    def with_id(self, id=None):
        self.data['id'] = id if id else fake.id(945632)

    def __getattribute__(self, name):

        # Handle anything without prefix normally
        if not name.startswith('with_'):
            return super().__getattribute__(name)

        # If prefixed function already exists, wrap it in a copy to allow
        # for side effect free chaining.
        try:
            attribute = super().__getattribute__(name)

            def f(*args, **kwargs):
                attribute(*args, **kwargs)
                return self.copy()

            return f

        # Otherwise dynamically create a default that adds the value to the
        # data dict and returns a copy of the result.
        except AttributeError:

            if name.startswith('with_'):

                def f(value):
                    self.data[name[len('with_') :]] = value
                    return self.copy()

                return f

            raise

    def pre(self):
        """
        Pre process data before the instance is created.
        """
        # Change any models into there pks
        model_data = [
            k
            for k in self.data.keys()
            if isinstance(self.data[k], models.Model)
        ]
        self.data.update({k + '_id': self.data[k].id for k in model_data})

    def create(self):
        """
        Create the instance from the data.
        """
        model_data = {
            k: v
            for k, v in self.data.items()
            if k in self.get_model_attributes()
        }
        instance = self.model(**model_data)
        instance = self.save_instance_to_db(instance)
        return instance

    def save_instance_to_db(self, instance):
        """
        Save the built instance to the database.
        """
        instance.save()
        return instance

    def post(self):
        """
        Complete any post processing after the instance is created.
        """

    def build(self):

        # Merge defaults with data provided using with_ prefix methods.
        defaults = self.get_defaults()
        defaults = {k: v for k, v in defaults.items() if k not in self.data}
        defaults = {k: v() if callable(v) else v for k, v in defaults.items()}

        self.data.update(defaults)

        # Process data and create instance
        self.pre()
        self.instance = self.create()
        self.post()

        return self.instance
