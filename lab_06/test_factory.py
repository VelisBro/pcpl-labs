from io import StringIO
from unittest.mock import Mock
import pytest
from notifications import EmailService, SmsService, EmailNotification, SmsNotification


@pytest.mark.parametrize("service, product", [
    (EmailService, EmailNotification), (SmsService, SmsNotification)])
def test_factory_returns_correct_product(service, product):
    assert isinstance(service(StringIO()).create_notification(), product)


def test_email_format():
    output = StringIO()
    result = EmailService(output).notify("student@example.com", "Готово")
    assert result == "EMAIL | Кому: student@example.com | Готово"
    assert output.getvalue() == result + "\n"


def test_mock_output_called_once():
    output = Mock()
    result = SmsService(output).notify("+70000000000", "Готово")
    output.write.assert_called_once_with(result + "\n")


def test_empty_message_does_not_write():
    output = Mock()
    with pytest.raises(ValueError):
        SmsService(output).notify("+70000000000", " ")
    output.write.assert_not_called()


def test_output_failure_propagates():
    output = Mock()
    output.write.side_effect = OSError("disk full")
    with pytest.raises(OSError, match="disk full"):
        EmailService(output).notify("student@example.com", "Готово")
