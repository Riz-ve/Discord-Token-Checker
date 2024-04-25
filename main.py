import os, threading, requests, random, time, ctypes, json
from pystyle import Colors, Colorate

use_proxies = True
proxy_type  = "socks5" # or "socks4"
timeout     = 15
check_loop  = False # runs a while loop which might give better results
retries     = 3 # maximum retries

# change these names to whatever you like
required_files = ["input", # folder
                  "input/proxies.txt", # proxies
                  "input/tokens.txt", # tokens
                  "valid.txt" # valid tokens
                  ]

needs_to_fill = []
def check(file:str) -> None:
    if "." in file:
        if file == required_files[3] or (not use_proxies and file == required_files[1]):
            return
        with open(file) as f:
            text = f.read()
            if text == "" or text == " " or text == "\n":
                needs_to_fill.append(file)

for file in required_files:
    if not os.path.exists(file):
        if "." in file:
            open(file, "x").close()
            check(file)
        else:
            os.makedirs(file)
    else:
        check(file)

if len(needs_to_fill) >= 1:
    input(f"{Colors.orange} Please fill these files: {needs_to_fill}")
    exit(0)

class newFile:
    def __init__(self, fileAddress):
        self.file = open(fileAddress, "r+")
        self.file.seek(0, 2)

    def read(self) -> str:
        return self.file.read()
    
    def write(self, text:str) -> None:
        self.file.seek(0, 2)
        self.file.write(text)
        self.file.flush()

    def convert_to_list(self) -> list:
        self.file.seek(0)
        return [line.strip() for line in self.file.readlines()]
    
    def remove(self, text:str) -> None:
        self.file.remove()

    def remove_text_line(self, text) -> None:
        self.file.seek(0)
        lines = self.file.readlines()
        self.file.seek(0)
        self.file.truncate()
        for line in lines:
            if text not in line:
                self.file.write(line)
                self.file.flush()
        self.file.seek(0)

def get_token_info(headers:list, proxies:list) -> list:
    try:
        response = requests.get("https://canary.discordapp.com/api/v6/users/@me", headers=headers, proxies=proxies, timeout=timeout)
    except:
        pass
    if response.status_code == 200:
        return json.loads(response.content)

def check_token(token:str, tries=None) -> None:
    proxy = random.choice(proxies_list)
    if tries:
        if tries > retries:
            print(f"{Colors.orange}{token} reached the max retries of {retries}")
            return
        tries+=1
    try:
        proxies = {
            "http" : f"{proxy_type}://{proxy}",
            "https" : f"{proxy_type}://{proxy}"
        }
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        response = requests.get("https://discord.com/api/v6/users/@me", headers=headers, proxies=proxies, timeout=timeout)
    except requests.RequestException as e:
        if isinstance(e, requests.ConnectTimeout) and retries >= 1:
            print(f"{Colors.cyan}{token}")
            return check_token(token, tries or 1)
        return
    if response.status_code == 401 or response.status_code == 403:
        print(f"{Colors.dark_gray}{token} Is invalid")
    else:
        print(Colorate.Horizontal(Colors.cyan_to_green, f"{token} Is valid"))
        token_info = get_token_info(headers, proxies)
        if token_info:
            valid.write(f"\n---------------------------------------\nToken: {token}\nUsername: {token_info["username"]}\nDisplay Name: {token_info["global_name"]}\nEmail: {token_info["email"]}\nPhone: {token_info["phone"]}\nBio: {token_info["bio"]}\nID: {token_info["id"]}\nLocale: {token_info["locale"]}\nMfa: {token_info["mfa_enabled"]}\n---------------------------------------\n")
        else:
            valid.write(f"\n---------------------------------------\nToken: {token}\nFailed to get details.\n---------------------------------------\n")
valid = newFile(required_files[3])
tokens = newFile(required_files[2]).convert_to_list()

total_tokens = len(tokens)
total_valid = 0
total_checked = 0

proxies = newFile(required_files[1])
proxies_list = proxies.convert_to_list()

start_time = time.time()

def window_title() -> None:
    global total_checked
    while total_checked < total_tokens:
        elapsed = time.time() - start_time
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        total_checked = total_tokens - threading.active_count()
        ctypes.windll.kernel32.SetConsoleTitleW(f"Checking: {total_checked}/{total_tokens} | Valid: {total_valid} | Elapsed: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        time.sleep(1)
threading.Thread(target=window_title).start()

while check_loop:
    for token in tokens:
        threading.Thread(target=check_token, args=[token]).start()

for token in tokens:
    threading.Thread(target=check_token, args=[token]).start()
