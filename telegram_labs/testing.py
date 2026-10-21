"""Изолированный Telegram transport для проверки настоящего диспетчера без сети."""
import json

from telegram import Update
from telegram.request import BaseRequest


class OfflineTelegram(BaseRequest):
    """Возвращает минимальные ответы Bot API, сохраняет исходящие сообщения."""
    def __init__(self):
        self.messages = []
        self.calls = []
        self.file_content = b""
        self.failure = None
        self.send_failures = []

    @property
    def read_timeout(self):
        return 5

    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def do_request(self, url, method, request_data=None, **kwargs):
        endpoint = url.rsplit("/", 1)[-1]
        if endpoint == "schedule.txt":
            return 200, self.file_content
        params = request_data.parameters if request_data else {}
        self.calls.append((endpoint, params))
        if endpoint == "getMe":
            result = {"id": 123456789, "is_bot": True, "first_name": "Study diary",
                      "username": "offline_study_bot"}
        elif endpoint == "getFile":
            result = {"file_id": "test_file", "file_unique_id": "unique_file",
                      "file_size": len(self.file_content), "file_path": "schedule.txt"}
        elif endpoint in ("sendMessage", "sendDocument"):
            if self.send_failures:
                raise self.send_failures.pop(0)
            if self.failure:
                code, description = self.failure
                return code, json.dumps({"ok": False, "error_code": code, "description": description}).encode()
            result = {"message_id": len(self.messages) + 1, "date": 1792573200,
                      "chat": {"id": int(params["chat_id"]), "type": "private"},
                      "text": params.get("text", params.get("caption", ""))}
            self.messages.append(result)
        elif endpoint == "setMyCommands":
            result = True
        else:
            raise AssertionError(f"Неожиданный метод Bot API: {endpoint}")
        return 200, json.dumps({"ok": True, "result": result}, ensure_ascii=False).encode()


def incoming(bot, text=None, chat_id=42, update_id=1, document=None, timestamp=1792573200):
    message = {"message_id": update_id, "date": timestamp,
               "chat": {"id": chat_id, "type": "private"},
               "from": {"id": chat_id, "is_bot": False, "first_name": "Студент"}}
    if text is not None:
        message["text"] = text
        if text.startswith("/"):
            message["entities"] = [{"type": "bot_command", "offset": 0,
                                    "length": len(text.split()[0])}]
    if document:
        message["document"] = {"file_id": "test_file", "file_unique_id": "unique_file", **document}
    return Update.de_json({"update_id": update_id, "message": message}, bot)
