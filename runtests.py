# coding: utf-8
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import os
import sys
import django

from django.conf import settings
from django.test.utils import get_runner


def runtests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'test_project.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))

if __name__ == '__main__':
    runtests()