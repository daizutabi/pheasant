import os

import pytest


@pytest.fixture(scope='module')
def root():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(root, '../resources/office'))
    return root
