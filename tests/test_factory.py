from app import create_app


def test_config():
    """Test create_app creates app with the right config"""
    assert not create_app().testing
    assert create_app({ 'TESTING': True }).testing
