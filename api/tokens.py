import math
import tiktoken
async def calculate_image_tokens(width,height,detail):
    if detail=="low": return 85
    return math.ceil(width/512)*math.ceil(height/512)*170+85
async def num_tokens_from_messages(messages,model=""):
    try: enc=tiktoken.encoding_for_model(model)
    except KeyError: enc=tiktoken.get_encoding("cl100k_base")
    total=3
    for msg in messages:
        for value in msg.values():
            if isinstance(value,str): total += len(enc.encode(value))
    return total
async def num_tokens_from_content(content,model=None):
    return len(tiktoken.get_encoding("cl100k_base").encode(content))
async def split_tokens_from_content(content,max_tokens,model=None):
    enc=tiktoken.get_encoding("cl100k_base"); tokens=enc.encode(content)
    if len(tokens)>=max_tokens: return enc.decode(tokens[:max_tokens]),max_tokens,"length"
    return content,len(tokens),"stop"
