#!/bin/zsh
cd -- "$(dirname -- "$0")" || exit 1
if [[ ! -x .venv/bin/python ]]; then
  python3 -m venv .venv || exit 1
fi
.venv/bin/python telegram_labs/launch.py "$@"
result=$?
if [[ $result -ne 0 ]]; then
  echo "Не удалось запустить бота. Прочитай сообщение выше."
fi
read -r "reply?Нажми Enter, чтобы закрыть окно."
exit $result
