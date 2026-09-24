import os
from http.cookies import SimpleCookie

from dotenv import load_dotenv
from utils.Logger import logger

load_dotenv()

def is_true(value):
    if isinstance(value, bool): return value
    if isinstance(value, str): return value.lower() in ('true','1','t','y','yes')
    if isinstance(value, int): return value == 1
    return False

api_prefix = os.getenv('API_PREFIX', '').strip('/')
authorization = os.getenv('AUTHORIZATION', '').replace(' ', '')
chatgpt_base_url = os.getenv('CHATGPT_BASE_URL', 'https://chatgpt.com').strip()
auth_key = os.getenv('AUTH_KEY')
proxy_url = os.getenv('PROXY_URL', '').strip()
history_disabled = is_true(os.getenv('HISTORY_DISABLED', 'true'))
upload_by_url = is_true(os.getenv('UPLOAD_BY_URL', 'false'))
oai_language = os.getenv('OAI_LANGUAGE', 'en-US')
retry_times = int(os.getenv('RETRY_TIMES', '3'))
enable_gateway = is_true(os.getenv('ENABLE_GATEWAY', 'false'))
chatgpt_cookies = os.getenv('CHATGPT_COOKIES', '').strip()

def parse_cookie_header(value):
    if not value: return {}
    c = SimpleCookie()
    try:
        c.load(value)
        return {k:m.value for k,m in c.items()}
    except Exception:
        out = {}
        for p in value.split(';'):
            if '=' in p:
                k,v = p.strip().split('=',1)
                out[k] = v
        return out

chatgpt_cookie_dict = parse_cookie_header(chatgpt_cookies)
authorization_list = [x for x in authorization.split(',') if x]
chatgpt_base_url_list = [x.strip() for x in chatgpt_base_url.split(',') if x.strip()]
proxy_url_list = [x.strip() for x in proxy_url.split(',') if x.strip()]

# curl_cffi 0.7.3 supports chrome124, but chrome131 was added only in 0.8.0.
# Keep the pinned dependency compatible with the impersonation target.
impersonate_list = ['chrome124']

try:
    with open('version.txt', encoding='utf-8') as f: version = f.read().strip()
except Exception:
    version = 'unknown'

logger.info('Chat2API Vercel configuration loaded')
logger.info(f'CHATGPT_COOKIES configured: {bool(chatgpt_cookie_dict)}')
