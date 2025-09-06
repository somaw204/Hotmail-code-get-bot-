import requests
import re
import html as ihtml
from urllib.parse import unquote
import datetime
import time


def _grab(rx, text):
    m = re.search(rx, text, flags=re.IGNORECASE)
    return m.group(1) if m else None


def generate_account(identifier: str, password: str):
    """Create a Facebook account and return result info"""
    try:
        start_time = time.time()
        session = requests.session()

        headers_get = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'dpr': '1',
            'priority': 'u=0, i',
            'referer': 'https://m.facebook.com/?wtsid=rdr_0x8AtYsVuPUmHW3wo',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Google Chrome";v="139.0.7258.139", "Chromium";v="139.0.7258.139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
            'viewport-width': '1365',
        }

        response = session.get(
            'https://m.facebook.com/reg/?is_two_steps_login=0&cid=103&wtsid=rdr_0bhLQtxfQO047uW1A&refsrc=deprecated&_rdr',
            headers=headers_get,
            timeout=10,
        )

        html_text = ihtml.unescape(response.text)

        privacy_mutation_token = _grab(r'privacy_mutation_token=([^"&]+)', html_text)
        if privacy_mutation_token:
            privacy_mutation_token = unquote(privacy_mutation_token)

        reg_instance = _grab(r'name="reg_instance"\s+value="([^"]+)"', html_text)
        reg_impression_id = _grab(r'name="reg_impression_id"\s+value="([^"]+)"', html_text)
        logger_id = _grab(r'name="logger_id"\s+value="([^"]+)"', html_text)
        encrypted = _grab(r'"encrypted":\s*"([^"]+)"', html_text)

        headers_post = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://m.facebook.com',
            'priority': 'u=1, i',
            'referer': 'https://m.facebook.com/reg/?is_two_steps_login=0&cid=103&refsrc=deprecated&soft=hjk',
            'sec-ch-prefers-color-scheme': 'dark',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Google Chrome";v="139.0.7258.139", "Chromium";v="139.0.7258.139"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25',
            'x-asbd-id': '359341',
            'x-fb-lsd': 'AdEuEGQa_jw',
            'x-requested-with': 'XMLHttpRequest',
            'x-response-format': 'JSONStream',
        }

        params = {
            'privacy_mutation_token': privacy_mutation_token,
            'app_id': '103',
            'multi_step_form': '1',
            'skip_suma': '0',
            'shouldForceMTouch': '1',
        }

        data = {
            'ccp': '2',
            'reg_instance': reg_instance,
            'submission_request': 'true',
            'helper': '',
            'reg_impression_id': reg_impression_id,
            'ns': '1',
            'zero_header_af_client': '',
            'app_id': '103',
            'logger_id': logger_id,
            'field_names[0]': 'firstname',
            'firstname': 'Abdur',
            'lastname': 'Rahman',
            'field_names[1]': 'birthday_wrapper',
            'birthday_day': '4',
            'birthday_month': '6',
            'birthday_year': '2003',
            'age_step_input': '',
            'did_use_age': 'false',
            'field_names[2]': 'reg_email__',
            'reg_email__': identifier,
            'field_names[3]': 'sex',
            'sex': '2',
            'preferred_pronoun': '',
            'custom_gender': '',
            'field_names[4]': 'reg_passwd__',
            'name_suggest_elig': 'false',
            'was_shown_name_suggestions': 'false',
            'did_use_suggested_name': 'false',
            'use_custom_gender': 'false',
            'guid': '',
            'pre_form_step': '',
            'encpass': f'#PWD_BROWSER:0:{int(datetime.datetime.now().timestamp())}:{password}',
            'fb_dtsg': 'NAfs7Uk0neEOnoGm7aLRB2XQrKeZg8LZ7LbCkyG7brqrKxkdIhZ-5zQ:0:0',
            'jazoest': '24986',
            'lsd': 'AdEuEGQa_jw',
            '__dyn': '1Z3pawlEnwm8_Bg9ppoW5UdE4a2i5U4e0C86u7E39x60zU3ex608ewk9E4W0pKq0FE6S0x81vohw73wGwcq1GwqU2YwbK0oi0zE1jU1soG0hi0Lo6-0Co1kU1UU3jwea',
            '__csr': '',
            '__hsdp': '',
            '__hblp': '',
            '__sjsp': '',
            '__req': 'k',
            '__fmt': '1',
            '__a': encrypted,
            '__user': '0',
        }

        response = session.post(
            'https://m.facebook.com/reg/submit/',
            params=params,
            headers=headers_post,
            data=data,
            timeout=15,
        )

        c_user = session.cookies.get('c_user') or response.cookies.get('c_user')
        cookies = requests.utils.dict_from_cookiejar(session.cookies)

        try:
            ip = requests.get('https://api64.ipify.org?format=json', timeout=5).json().get('ip')
        except Exception:
            ip = 'Unknown'

        total_time = round(time.time() - start_time, 2)
        return {
            'success': bool(c_user),
            'identifier': identifier,
            'password': password,
            'c_user': c_user,
            'cookies': cookies,
            'ip': ip,
            'time': total_time,
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
