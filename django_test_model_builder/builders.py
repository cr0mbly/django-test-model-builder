import copy

from django.db import models

from .exceptions import CannotSetFieldOnModelException


def id_generator():
    """
    Helper generator for creating unique pks for models.
    """
    i = 1
    while True:
        yield i
        i += 1

model_id_generator = id_generator()

class ModelBuilder:
    dynamic_field_setter_prefix = 'with_'

    def __init__(self):
        self.cached_model_field_values = {}

    def __getattribute__(self, name):
        """
        Overridden handler to support field and custom field and method
        resolution for models. Implement using a chained
        dynamic_field_setter_prefix<fieldname> to set a custom field
        on the subclassed model e.g:

        Class FooBuilder(ModelBuilder):
            <dynamic_field_setter_prefix>username(self, name):
                self.cached_model_field_values['name'] = name or 'Billy'
        """

        # Ignore defined setter attribute prefix.
        if name == 'dynamic_field_setter_prefix':
            return super().__getattribute__(name)

        # Handle anything without prefix normally.
        if not name.startswith(self.dynamic_field_setter_prefix):
            return super().__getattribute__(name)

        # If prefixed function already exists, wrap it in a copy to allow
        # for side effect free chaining.
        try:
            attribute = super().__getattribute__(name)
            def f(*args, **kwargs):
                attribute(*args, **kwargs)
                return self._copy()

            return f

        # Otherwise dynamically create a default that adds the value to the
        # cached_model_field_values and returns a copy of the result.
        except AttributeError:
            if name.startswith(self.dynamic_field_setter_prefix):
                def default_field_call(value):
                    field_name = name[len(self.dynamic_field_setter_prefix):]
                    if hasattr(self.model, field_name):
                        self.cached_model_field_values[field_name] = value
                        return self._copy()

                    raise CannotSetFieldOnModelException(
                        'Cannot use method {} as field {} does not exist'
                        .format(name, field_name)
                    )

                return default_field_call

            raise AttributeError

    def _get_model_attributes(self):
        return [f.attname for f in self.model._meta.fields]

    def _copy(self):
        return copy.deepcopy(self)

    def get_default_fields(self):
        """
        Default values to be used when building the model.
        Returns a Dictionary containing matching fields names and their
        default values.
        """
        raise NotImplementedError(
            'Defaults method must be defined to set required fields on model.'
        )

    def get_model(self):
        if not hasattr(self, 'model'):
            raise NotImplementedError(
                'Model should be set on class or this method should be '
                'overridden'
            )

        return self.model

    def pre(self):
        """
        Pre process data before the instance is created.
        Extendable by Subclassed ModelBuilder.
        """

    def create(self):
        """
        Stub call for saving the as built in memory model, can be overridden to
        provide a more custom implementation on how the model should be saved.
        """
        self.instance.save()

    def post(self):
        """
        Complete any post processing after the instance is created.
        Extendable by Subclassed ModelBuilder.
        """

    def build(self, save_to_db=True):
        """
        Combine model defaults with any overridden values defined by the
        builder. save_to_db=False will render the model in memory for later
        propagation to the database defined by the user.
        """
        model_data = self.get_default_fields()

        # Generarate unique pk.
        model_data['id'] = (
            model_data['id']
            if model_data.get('id') else
            next(model_id_generator)
        )

        # Resolve any custom field implementations values and
        # temporarily set it for field addition on self.data.
        model_data.update({
            k: v
            for k, v in self.cached_model_field_values.items()
            if k in self._get_model_attributes()
        })

        # Merge defaults with cached_model_field_values provided using
        # dynamic_field_setter_prefix prefix methods.
        model_data.update({
            k: v
            for k, v in model_data.items()
            if k not in self.cached_model_field_values
        })

        # Change any models into there pks.
        for field, value in model_data.items():
            if isinstance(value, models.Model):
                del model_data[field]
                model_data[field + '_id'] = value.pk

        # Preform pre-db save actions.
        self.pre()

        # Attach fields to in memory model.
        self.instance = self.model(**model_data)

        if save_to_db:
            self.create()

        # Preform post-db save actions.
        self.post()

        return self.instance
