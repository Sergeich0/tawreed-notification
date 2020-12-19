import requests

from ChatApiException import ChatApiException
from string import Template

import config
import b_utils
import l_utils
import s_utils


def _send_request(method, body, _type='GET'):
  url = f'https://api.chat-api.com/instance{config.chatapi_instance}/{method}?token={config.chatapi_token}'
  request_types = {
    'GET': requests.get,
    'POST': requests.post
  }
  if _type not in request_types:
    raise ValueError(f'Unknown method: {_type}')
  request_type = request_types[_type]
  try:
    resp = request_type(url, body)
  except requests.exceptions.RequestException as e:
    raise ChatApiException(str(e))
  last_status = b_utils.get_http_status('chat-api')
  current_status = resp.status_code
  if last_status != current_status:
    b_utils.write_http_status('chat-api', current_status)
    if last_status == 200:
      s_utils.send_alert(chatapi="Available now")
  if last_status != current_status >= 300:  # "неуспешные" коды
    raise ChatApiException(f'ChatApi server is not available, response code: {current_status}')
  result = resp.json()
  if 'error' in result:
    raise ChatApiException(f'ChatApi server returned an error: {result.get("error")}. Method {method}, body {str(body)}')
  return result


def _check_phone(func):
  def wrapper(phone=None, *args, **kwargs):
    if phone is None:
      return func(phone, *args, **kwargs)
    req_body = {
      'phone': phone
    }
    result = _send_request('checkPhone', req_body, 'GET')
    if result['result'] == 'exists':
      return func(phone, *args, **kwargs)
    else:
      raise ChatApiException(f'Phone "{phone}" is not in WhatsApp')
  return wrapper


def _send_message(phone=None, chat_id=None, message=""):
  req_body = {
    'body': message
  }
  if phone is None and chat_id is None:
    raise ValueError("No phone, no chat ID too")
  if phone is not None and chat_id is not None:
    raise ValueError(f"There are both chat ID and phone number: {chat_id} and {phone}")
  if phone is not None:
    req_body['phone'] = phone
  if chat_id is not None:
    req_body['chatId'] = chat_id
  result = _send_request('sendMessage', req_body, 'POST')
  if result['sent']:
    return
  raise ChatApiException(result['message'])


def _get_dialogs():
  result = _send_request('dialogs', {})
  if 'dialogs' in result:
    return result.get('dialogs')
  raise ChatApiException("Failed to get list of WhatsApp dialogs")


def _get_group_id(phone=None):
  group_id = b_utils.get_group_id_by_phone(phone)
  if group_id is not None:
    return group_id
  dialogs = _get_dialogs()
  for dialog in dialogs:
    if 'metadata' in dialog and not dialog.get('metadata').get('isGroup'):
      continue
    participants = dialog.get('metadata').get('participants')
    if participants is None:
      continue
    for participant in participants:
      number = participant.split('@')[0]
      if not b_utils.get_group_id_by_phone(number):
        b_utils.save_phone_group_id(phone, dialog.get('id'))
      if number == phone:
        return dialog.get('id')


@_check_phone
def vendor_notification(phone=None, **kwargs):
  subst = kwargs.copy()
  order_number = subst.get("ORDER_NUMBER")
  long_url = f'{config.x_cart_url}?target=order&order_number={order_number}'
  alias = f'{config.short_link_alias}{order_number}'
  short_link = l_utils.make_short_url(long_url, alias)
  subst['LINK'] = short_link
  chat_id = _get_group_id(phone)
  if chat_id is not None:
    phone = None  # Сообщение отправится в чат
  with open(config.vendor_notification, 'r') as template_src:
    template = Template(template_src.read())
    try:
      text = template.substitute(subst)
    except KeyError as e:
      print(e.args)
      raise ChatApiException(f'Template Error {config.vendor_notification}: unknown field "{e.args[0]}"')
  _send_message(phone, chat_id, text)
  s_utils.send_alert(message='Successfully sent notification',
                     order_number=order_number,
                     link=short_link)


@_check_phone
def send_status_update(phone=None, chat_id=None, **kwargs):
  return  # для ресторанов TODO сделать, когда понадобится по аналогии с вендором


if __name__ == '__main__':
  vendor_notification('79872650520',
                      chat_id=None,
                      NAME='Sergey',
                      ORDER_NUMBER='001',
                      ORDER_SUM=45.5,
                      CUSTOMER_NAME='Olegik',
                      CUSTOMER_PHONE='+78005553535',
                      THERE_IS_NO_SPOON=True
                      )
  # print(_get_group_id('79872650520'))
