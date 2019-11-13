secret_key = 'super_secret_key_shhhhh'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'tests.test_app.apps.TestAppConfig',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}
