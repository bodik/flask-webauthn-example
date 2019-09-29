"""models tests"""


def test_models(app, test_user, test_wncred):  # pylint: disable=unused-argument
    """test models methods"""

    assert repr(test_user)
    assert repr(test_wncred)
