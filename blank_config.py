# tawreed
db                  = 'blank_tawreedbase.sqlite'  # Путь до базы
x_cart_key          = 'AaAAaAAaaaAA000AAAaAAaaaa0AaA0aA'  # only-read https://market.address/admin.php?target=module&moduleId=XC-RESTAPI
x_cart_url          = 'https://market.address/admin.php'  # Адрес админки
orders_per_request  = 1
chatapi_token       = '0aaa0aa0a0aa0aaa'  # Токен их ЛК чатапи
chatapi_instance    = '000000'  # Номер инстанса чатапи
slack_webhook       = 'https://hooks.slack.com/services/A0AAA0AAA/AAAA0000A/aAaa0AaAa0aAaAaAaaAAAaaa'  # Вебхук слака
vendor_notification = 'vendor.template'  # Шаблон для отправки сообщения поставищику
goo_su_token        = 'AAAaaAaAa0aaAAA0a0AaAAaA0aAAAa0aA00aAA0AAaAaaAAAa00aAa0aAaa0'  # Токен goo.su
goo_su_api_endpoint = 'https://goo.su/api/convert'
short_link_alias    = 'twrd'  # Что пишем перед номером заказа
interval            = 60  # с какой периодичностью обновляется информация о заказах и рассылаются уведомления
log_level           = 'debug'
params = {  # Часть полей кастомные, могут отличаться в разных настроенных МП
  'address_field': {  # https://market.address/admin.php?target=RESTAPI&_key=AaAAaAAaaaAA000AAAaAAaaaa0AaA0aA&_path=addressfield
    'id': {
      'name': 2,
      'phone': 10,
      'company': 18,
      'delivery_date': 13,
      'city': 5,
      'street': 4,
    }
  }
}
