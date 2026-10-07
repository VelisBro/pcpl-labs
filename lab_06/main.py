"""Локальная демонстрация: сообщения выводятся в консоль."""
import sys
from notifications import EmailService, SmsService


if __name__ == "__main__":
    for service, recipient in ((EmailService(sys.stdout), "student@example.com"),
                               (SmsService(sys.stdout), "+70000000000")):
        service.notify(recipient, "Лабораторная работа готова")
