import requests

import config
import b_utils

from SlackException import SlackException


_LAST_NOTIFICATION = {}


def _send_message(text):
  url = config.slack_webhook
  data = {
    'text': text
  }
  try:
    resp = requests.post(url, json=data)
  except requests.exceptions.RequestException as e:
    raise SlackException(str(e))
  last_status = b_utils.get_http_status('slack')
  current_status = resp.status_code
  if last_status != current_status:
    b_utils.write_http_status('slack', current_status)
  if last_status != current_status >= 300:  # "неуспешные" коды
    raise SlackException(f'Slack unavailable, status code: {current_status}')
  return


def send_alert(**kwargs):
  global _LAST_NOTIFICATION
  if kwargs == _LAST_NOTIFICATION:  # TODO переделать механизм оповещений
    return  # Уже отправляли этот алерт
  _LAST_NOTIFICATION = kwargs.copy()
  text = ''
  for kwarg in kwargs:
    text += kwarg + ": " + str(kwargs[kwarg]) + '\n'
  _send_message(text)


if __name__ == '__main__':
  send_alert(message='Testing!')
