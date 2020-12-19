import time
import traceback
from collections import OrderedDict

import s_utils
import t_utils
import b_utils
import c_utils
import config
from ChatApiException import ChatApiException


def get_vendor_customer(order):
  vendor_id = order.get('vendor').get('profile_id')
  customer_id = order.get('orig_profile').get('profile_id')
  vendor = t_utils.request_profile(vendor_id)
  customer = t_utils.request_profile(customer_id)
  return vendor, customer


def get_name_and_phone_number(profile):
  address_books = profile.get('addresses')
  address_id = None
  for address_book in reversed(address_books):  # Обратный порядок чтобы искать сперва в последнем адресе
    if not address_book.get('is_shipping'):
      continue
    address_id = address_book.get('address_id')
    break
  if address_id is None:
    if len(address_books) == 1:
      address_id = address_books[0].get('address_id')
    else:
      raise ValueError("No address book")
  address = t_utils.request_address(address_id)
  address_fields = address.get('addressFields')
  ref_ids = config.params.get('address_field').get('id')
  result = OrderedDict()
  result['name'] = None
  result['phone'] = None
  result['company'] = None
  result['delivery_date'] = None
  result['city'] = None
  result['street'] = None
  for field in address_fields:
    address_field_value_id = field.get('id')
    address_field_value = t_utils.request_address_field(address_field_value_id)
    if not address_field_value.get('addressField'):
      continue
    address_field_id = address_field_value.get('addressField').get('id')
    for ref in ref_ids:
      if address_field_id == ref_ids[ref]:
        result[ref] = address_field_value.get('value')
    if all(v is not None for v in result.values()):
      break
  for key in result:
    if result[key] == '':
      result[key] = '-'
  raw_phone = result['phone']
  phone = ''.join([c for c in raw_phone if c.isdigit()])
  if phone.startswith('0'):  # TODO проверка получше
    phone = phone.replace('0', '971', 1)
  result['phone'] = phone
  return result.values()  # на том конце распакуются


def check_new_orders():
  last_order_number = b_utils.get_orders_count()
  orders_info = t_utils.request_latest_orders(last_order_number)
  for order_info in orders_info:
    order_id = order_info.get('order_id')
    order = t_utils.request_order(order_id)
    order_number = order.get('orderNumber')
    order_sum = order.get('total')
    customer_notes = order.get('notes')
    order_status = order.get('shippingStatus')
    if order_status:
      order_status = order_status.get('id')
    vendor, customer = get_vendor_customer(order)
    vendor_name = vendor_phone = customer_name = customer_phone = company = delivery_date = city = street = None
    vendor_id = vendor.get('profile_id')
    customer_id = customer.get('profile_id')
    # Вытаскиваем данные по поставщику
    try:
      vendor_name, vendor_phone, _, _, _, _ = get_name_and_phone_number(vendor)
    except ValueError as e:  # Не заполнен адрес бук в профиле поставщика
      # TODO всё равно записывать в базу + сделать обновление информации по незаполненным поставщикам
      s_utils.send_alert(message="Failed to get supplier's address book", order=order_number, error=e.args)
      continue
    try:
      customer_name, customer_phone, company, delivery_date, city, street = get_name_and_phone_number(customer)
    except ValueError as e:  # Не заполнен адрес бук в профиле клиента
      s_utils.send_alert(message="Failed to get restaurants's address book", order=order_number, error=e.args)
      continue
    # Сохраняем все данные в базу
    vendor_inner_id = b_utils.save_user(vendor_id, vendor_name, vendor_phone)
    customer_inner_id = b_utils.save_user(customer_id, customer_name, customer_phone)
    b_utils.save_order(order_id, order_number, order_sum, company, delivery_date, order_status,
               customer_notes, city, street, vendor_inner_id, customer_inner_id)


def send_notifications():
  unsent_notifications = b_utils.get_unsent_notifications()
  for unsent in unsent_notifications:
    direction, order_id, order_number, order_sum, company, \
      delivery_date, order_status_id, order_status, customer_notes, city, street, \
      vendor_inner_id, vendor_id, vendor_name, vendor_phone, \
      customer_inner_id, customer_id, customer_name, customer_phone = unsent
    wildcard = {  # Отсюда будут подставляться данные в шаблон
      'ORDER_NUMBER': order_number,
      'ORDER_SUM': order_sum,
      'COMPANY': company,
      'DELIVERY_DATE': delivery_date,
      'CUSTOMER_NOTES': customer_notes,
      'CITY': city,
      'STREET': street,
      'VENDOR_PHONE': vendor_phone,
      'VENDOR_NAME': vendor_name,
      'VENDOR_ID': vendor_id,
      'CUSTOMER_NAME': customer_name,
      'CUSTOMER_PHONE': customer_phone,
      'CUSTOMER_ID': customer_id,
    }
    # Отправляем оповещение поставщику
    if direction == 'supplier':
      if not (vendor_phone is None):
        try:
          c_utils.vendor_notification(vendor_phone, **wildcard)
        except (ValueError, ChatApiException) as e:  # вернулась ошибка, сообщение не отправлено
          s_utils.send_alert(message="Failed to send notification to supplier", params=wildcard, error=e.args)
        else:
          b_utils.save_notification(order_id, 1, order_status_id)
      else:
        s_utils.send_alert(message="Supplier does not have a address book", params=wildcard)
    # Отправляем оповещение клиенту
    if direction == 'restaurant':
      try:
        # TODO сделать обновление информации в таком случае
        c_utils.send_status_update(customer_phone, **wildcard)
      except ChatApiException as e:  # вернулась ошибка, сообщение не отправлено
        pass  # TODO доделать когда понадобится оповещение куда-нибудь
        b_utils.save_notification(order_id, 2, order_status_id)
      else:
        b_utils.save_notification(order_id, 2, order_status_id)


def main():
  while True:
    try:
      check_new_orders()
      send_notifications()
      time.sleep(config.interval)
    except Exception as e:
      s_utils.send_alert(message="Something go wrong, call @Сергей Спиридонов please via https://t.me/Sergeich0",
                         error=traceback.print_exc())


if __name__ == '__main__':
  main()
