import requests
import config

# cs = {'target': 'RESTAPI', '_key': x_cart_key, '_path': 'order', '_cnd[limit][0]': 51, '_cnd[limit][1]': 1}


def _get_request(**kwargs):
  url = config.x_cart_url
  cs = {
    'target': 'RESTAPI',
    '_key': config.x_cart_key,
    **kwargs  # Объединяем с условиями из вызывающей функции
  }
  response = requests.get(url, cs)
  return response.json()


def request_latest_orders(from_order, amount=1):
  cs = {
    '_path': 'order',
    '_cnd[limit][0]': from_order,
    '_cnd[limit][1]': amount
  }
  return _get_request(**cs)


def request_order(order_id):
  cs = {
    '_path': 'order/{}'.format(order_id)
  }
  return _get_request(**cs)


def request_profile(profile_id):
  cs = {
    '_path': 'profile/{}'.format(profile_id)
  }
  return _get_request(**cs)


def request_address(address_id):
  cs = {
    '_path': 'address/{}'.format(address_id)
  }
  return _get_request(**cs)


def request_address_field(adv_id):
  cs = {
    '_path': 'addressFieldValue/{}'.format(adv_id)
  }
  return _get_request(**cs)
