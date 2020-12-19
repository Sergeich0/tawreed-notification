import sqlite3
import config
import time


def get_orders_count():
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'SELECT COUNT(*) from orders'
  cursor.execute(query)
  orders_number = cursor.fetchone()[0]
  conn.close()
  return orders_number


def save_order(order_id, number, order_sum, company, delivery_date, order_status,
               customer_notes, city, street, vendor_id, customer_id):
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = '''INSERT INTO orders (
                                  id, number, sum, company, delivery_date, status, 
                                  customer_notes, city, street, vendor_id, customer_id) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
  cursor.execute(query, (order_id, number, order_sum, company, delivery_date, order_status,
                 customer_notes, city, street, vendor_id, customer_id))
  conn.commit()
  conn.close()
  return


def save_user(user_id, first_name, phone):
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'INSERT OR REPLACE INTO profiles (xcart_id, first_name, phone) VALUES (?, ?, ?)'
  cursor.execute(query, (user_id, first_name, phone))
  conn.commit()
  inner_id = cursor.lastrowid
  conn.close()
  return inner_id


def write_http_status(api, status):
  c_time = int(time.time())
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'INSERT OR REPLACE INTO http_statuses (api, status, time) VALUES (?, ?, ?)'
  cursor.execute(query, (api, status, c_time))
  conn.commit()
  inner_id = cursor.lastrowid
  conn.close()
  return inner_id


def get_http_status(api):
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'SELECT status FROM http_statuses WHERE api = ? ORDER BY id DESC LIMIT 1'
  cursor.execute(query, (api, ))
  conn.commit()
  status = cursor.fetchone()
  if status is not None:
    status = status[0]
  conn.close()
  return status


def get_unsent_notifications():
  # TODO переделать запрос для поставщиков, чтобы не отправлялись оповещения о старых заказах при изменении статуса
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = '''
    SELECT directions.name, o.id, o.number, o.sum, o.company, o.delivery_date, statuses.id, statuses.status, 
           o.customer_notes, o.city, o.street, 
           sp.id, sp.xcart_id, sp.first_name, sp.phone,
           cs.id, cs.xcart_id, cs.first_name, cs.phone
    FROM orders AS o
      INNER JOIN directions
      INNER JOIN statuses
      INNER JOIN profiles as sp
      INNER JOIN profiles as cs
      LEFT JOIN notifications
    ON notifications.order_id == o.id
      AND notifications.status == statuses.id
      AND directions.id == notifications.direction
    WHERE notifications.notification_id is NULL
      AND o.status == statuses.id
      AND o.vendor_id == sp.id
      AND o.customer_id == cs.id
  '''
  cursor.execute(query)
  result = cursor.fetchall()
  return result


def get_group_id_by_phone(phone):
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'SELECT group_id FROM phone_group WHERE phone = ? ORDER BY id DESC LIMIT 1'
  cursor.execute(query, (phone, ))
  group_id = cursor.fetchone()
  if group_id is not None:
    group_id = group_id[0]
  conn.close()
  return group_id


def save_phone_group_id(phone, group):
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'INSERT OR REPLACE INTO phone_group (phone, group_id) VALUES (?, ?)'
  cursor.execute(query, (phone, group))
  conn.commit()
  inner_id = cursor.lastrowid
  conn.close()
  return inner_id


def save_notification(order_id, direction, order_status):
  c_time = int(time.time())
  conn = sqlite3.connect(config.db)
  cursor = conn.cursor()
  query = 'INSERT OR REPLACE INTO notifications (order_id, direction, status, time) VALUES (?, ?, ?, ?)'
  cursor.execute(query, (order_id, direction, order_status, c_time))
  conn.commit()
  inner_id = cursor.lastrowid
  conn.close()
  return inner_id


if __name__ == '__main__':
  print(get_group_id_by_phone('79872650520'))
