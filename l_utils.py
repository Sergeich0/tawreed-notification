import requests
import config
import s_utils


def make_short_url(long_url, short_name):
  return long_url  # TODO убрать это перед публикацией
  data_req = {
    'token': config.goo_su_token,
    'url': long_url,
    'alias': short_name,
    'is_public': 0
  }
  resp = requests.get(config.goo_su_api_endpoint, data_req)
  if resp.status_code != 200:
    s_utils.send_alert(action='shorting links',
                       message='Can\'t convert link to short, long URI returned.',
                       long_url=long_url, short_name=short_name, status_code=resp.status_code)
    return long_url
  result = resp.json()
  if result and result.get('short_url'):
    return result.get('short_url')
  return long_url


if __name__ == '__main__':
  make_short_url('https://dxbx.ru/', 'dxbx')
