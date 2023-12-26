import random
import threading
from datetime import datetime
from colorama import Fore, Style, init
from discord_webhook import *

Lock = threading.Lock()
init(convert=True)
init(autoreset=True)

proxies_list =[]
with open('proxy.txt') as f:
        for line in f:
                proxies_list.append(line.strip())
f.close()

def get_proxy():
        proxy_chosen = random.choice(proxies_list)
        proxy_ditails = proxy_chosen.split(":")
        proxy = proxy_ditails
        pelneproxy = proxy[2]+":"+proxy[3]+"@"+proxy[0]+":"+proxy[1]
        proxies = {
                'http': 'http://'+pelneproxy,
                'https': 'http://'+pelneproxy}
        return proxies

def log(content):
    with Lock:
        print(f'[{datetime.now()}] {Fore.LIGHTMAGENTA_EX}{content}{Style.RESET_ALL}')
def log_success(content):
    with Lock:
        print(f'[{datetime.now()}] {Fore.LIGHTGREEN_EX}{content}{Style.RESET_ALL}')

def log_error_p(content):
    with Lock:
        print(f'[{datetime.now()}] {Fore.LIGHTRED_EX}{content}{Style.RESET_ALL}')
def log_info(content):
    with Lock:
        print(f'[{datetime.now()}] {Fore.YELLOW}{content}{Style.RESET_ALL}')
