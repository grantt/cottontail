import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(
    name='cottontail',
    version='0.1a',
    description='RabbitMQ PubSub Client and Message Broker.',
    long_description=(read('README.md')),
    url='http://github.com/grantt/cottontail/',
    license='MIT',
    author='Grant Toeppen',
    author_email='grant.toeppen@gmail.com',
    packages=find_packages(exclude=['*.examples', '*.examples.*']),
    install_requires=[
        'pika',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )