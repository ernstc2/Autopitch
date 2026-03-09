import pytest


def test_collect_all_errors():
    """INPT-02: Validation returns ALL errors in one pass, not just the first."""
    pytest.fail("Not implemented — complete in plan 02")


def test_error_message_format():
    """INPT-02: Error messages include sheet name, row label, and expected value."""
    pytest.fail("Not implemented — complete in plan 02")


def test_warnings_do_not_halt():
    """INPT-02: Optional missing rows produce warnings but processing continues."""
    pytest.fail("Not implemented — complete in plan 02")


def test_fatal_errors_raise():
    """INPT-02: Fatal errors (missing required row) raise ValidationError."""
    pytest.fail("Not implemented — complete in plan 02")
