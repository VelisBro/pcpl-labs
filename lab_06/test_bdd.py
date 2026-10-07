from io import StringIO
import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from notifications import EmailService, SmsService

scenarios("features/notifications.feature")


@given(parsers.parse("an {channel} service"), target_fixture="service")
def service(channel):
    return {"email": EmailService, "sms": SmsService}[channel](StringIO())


@when("I notify the student", target_fixture="message")
def notify(service):
    return service.notify("student", "Готово")


@then(parsers.parse("the notification starts with {prefix}"))
def check_prefix(message, prefix):
    assert message.startswith(prefix + " |")


@when("I submit an empty message")
def invalid_message(service):
    with pytest.raises(ValueError):
        service.notify("student", "")


@then("no notification is written")
def no_output(service):
    assert service.output.getvalue() == ""
