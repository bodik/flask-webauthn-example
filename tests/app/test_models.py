"""models tests"""


def test_models(app, test_user):  # pylint: disable=unused-argument
    """test models methods"""

    assert repr(test_user)
