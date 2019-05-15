# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='django-admin-easy',
    version='0.5.1',
    url='http://github.com/ebertti/django-admin-easy/',
    author='Ezequiel Bertti',
    author_email='ebertti@gmail.com',
    install_requires=['django',],
    packages=find_packages(exclude=('test_app', 'test_project')),
    include_package_data=True,
    license='MIT License',
    platforms=['OS Independent'],
    description="Collection of admin fields and decorators to help to create computed or custom fields more friendly and easy way",
    long_description=(open('README.rst').read()),
    keywords='admin field fields django easy simple',
    test_suite="runtests.runtests",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
