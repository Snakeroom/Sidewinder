import random
import string

pool = string.ascii_letters + string.digits

def generate_state_token(length=24):
    return "".join(random.choices(pool, k=length))
