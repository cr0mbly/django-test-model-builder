import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='django-test-model-builder',
    version='0.0.2',
    packages=find_packages(
        include=['django_test_model_builder'], exclude=('tests')
    ),
    include_package_data=True,
    license='MIT License',
    long_description=README,
    description=(
        'A small python / django model designed to decouple creation of '
        'models for testing from the creation of models in production to make '
        'updating tests less painful.'
    ),
    install_requires=[
        'Django',
    ],
    url='https://github.com/publons/django-test-model-builder',
    author='Matthew Betts, Aidan Houlihan',
    author_email='aidan@publons.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ]
)
