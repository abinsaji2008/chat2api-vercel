import random
import uuid
from utils import configs
import utils.globals as globals

def get_fp(req_token):
    user_agent = configs.user_agents_list[0] if configs.user_agents_list else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36"
    return {
        "user-agent": user_agent,
        "impersonate": random.choice(globals.impersonate_list),
        "proxy_url": random.choice(configs.proxy_url_list) if configs.proxy_url_list else None,
        "oai-device-id": str(uuid.uuid4()),
    }
