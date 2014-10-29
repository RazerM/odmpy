def test():
    """Run tests from tests directory."""
    import os.path
    import pytest
    pytest.main(os.path.dirname(os.path.abspath(__file__)))
