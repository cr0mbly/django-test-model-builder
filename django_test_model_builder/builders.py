import copy

from django.db import models


class ModelBuilder:
    dynamic_field_setter_prefix = 'with_'

    def __init__(self):
        self.data = {}

    def __getattribute__(self, name):
        """
        Overridden handler to support field and custom field and method
        resolution for models. Implement using a chained
        dynamic_field_setter_prefix<fieldname> to set a custom field
        on the subclassed model e.g:

        Class FooBuilder(ModelBuilder):
            <dynamic_field_setter_prefix>username(self, name):
                self.data['name'] = name or 'Billy'
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
        # data and returns a copy of the result.
        except AttributeError:
            if name.startswith(self.dynamic_field_setter_prefix):
                def f(value):
                    field_name = name[len(self.dynamic_field_setter_prefix):]
                    self.data[field_name] = value
                    return self._copy()

                return f

            raise AttributeError

    def _get_model_attributes(self):
        return [f.name for f in self.model._meta.fields]

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

    def get_builder_context(self):
        """
        Override here with any extra context that you want to pass to the
        pre/post hooks to make on demand changes to the app.
        """
        return {}

    def get_model(self):
        if not hasattr(self, 'model'):
            raise NotImplementedError(
                'Model should be set on class or this method '
                'should be overridden'
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
        # Combine defaults and custom field setters generating a
        # dictionary of fields that correspond to the set model.
        self.model_fields = self.get_default_fields()
        self.model_fields.update({
            k: v
            for k, v in self.data.items()
            if k in self._get_model_attributes()
        })

        # Run any functions bound to defaults or returned
        # in the custom field setters
        self.model_fields = {
            k: v() if callable(v) else v for k, v in self.model_fields.items()
        }

        # Update internal data dictionary with any extra fields
        # the tester has defined. Only set fields that haven't been redefined
        # in any custom methods.
        self.data.update({
            k:v
            for k, v in self.get_builder_context().items()
            if k not in self.data
        })

        # Preform pre-db save actions.
        self.pre()

        # Attach fields to in memory model.
        self.instance = self.model(**self.model_fields)

        if save_to_db:
            self.create()

        # Preform post-db save actions.
        self.post()

        return self.instance
