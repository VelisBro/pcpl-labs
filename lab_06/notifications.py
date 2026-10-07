"""Порождающий паттерн Factory Method в сервисе уведомлений."""
from abc import ABC, abstractmethod
from typing import TextIO


class Notification(ABC):
    @abstractmethod
    def render(self, recipient: str, message: str) -> str:
        raise NotImplementedError


class EmailNotification(Notification):
    def render(self, recipient, message):
        return f"EMAIL | Кому: {recipient} | {message}"


class SmsNotification(Notification):
    def render(self, recipient, message):
        return f"SMS | Кому: {recipient} | {message}"


class NotificationService(ABC):
    def __init__(self, output: TextIO):
        self.output = output

    @abstractmethod
    def create_notification(self) -> Notification:
        raise NotImplementedError

    def notify(self, recipient: str, message: str) -> str:
        if not recipient.strip() or not message.strip():
            raise ValueError("Получатель и сообщение должны быть непустыми")
        rendered = self.create_notification().render(recipient, message)
        self.output.write(rendered + "\n")
        return rendered


class EmailService(NotificationService):
    def create_notification(self):
        return EmailNotification()


class SmsService(NotificationService):
    def create_notification(self):
        return SmsNotification()
