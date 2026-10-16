import os
import sys
import json
import uuid
import time
import threading
import subprocess
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ta_tool_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

TEMP_TOOLS_DIR = os.path.join(tempfile.gettempdir(), "ta_tool_embedded")
os.makedirs(TEMP_TOOLS_DIR, exist_ok=True)


# ============================================================================
# ==================== TOOL: IG REG ==========================================
# ============================================================================
TOOL_CODE_IG_REG = r'''# -*- coding: utf-8 -*-
import os
import sys
import time
import json
import random
import string
import re
import uuid
import hashlib
import base64
import urllib.parse
from datetime import datetime

import requests
from curl_cffi import requests as c_requests

red = "\033[1;31m"; pink = "\033[1;35m"; green = "\033[1;32m"
yellow = "\033[1;33m"; white = "\033[0;37m"; cyan = "\033[1;36m"
blue = "\033[1;34m"; cam = "\033[38;5;208m"; reset = "\033[0m"

IG_APP_ID = "936619743392459"
IG_APP_VERSION = "269.0.0.18.75"
IG_API_URL = "https://i.instagram.com/api/v1"

DEVICES = [
    {"brand": "Xiaomi", "model": "Redmi Note 7", "device": "lavender", "android": "9", "sdk": 28, "dpi": 480, "width": 1080, "height": 1920},
    {"brand": "Samsung", "model": "Galaxy S21", "device": "exynos2100", "android": "11", "sdk": 30, "dpi": 420, "width": 1080, "height": 2340},
    {"brand": "Samsung", "model": "Galaxy A52", "device": "a52q", "android": "11", "sdk": 30, "dpi": 405, "width": 1080, "height": 2400},
    {"brand": "Xiaomi", "model": "POCO X3", "device": "surya", "android": "10", "sdk": 29, "dpi": 440, "width": 1080, "height": 2400},
    {"brand": "OPPO", "model": "Reno4", "device": "CPH2091", "android": "10", "sdk": 29, "dpi": 400, "width": 1080, "height": 2400},
    {"brand": "Google", "model": "Pixel 5", "device": "redfin", "android": "11", "sdk": 30, "dpi": 440, "width": 1080, "height": 2340},
    {"brand": "Huawei", "model": "P30 Lite", "device": "HWANE", "android": "10", "sdk": 29, "dpi": 480, "width": 1080, "height": 2312},
    {"brand": "Realme", "model": "6 Pro", "device": "RMX2061", "android": "10", "sdk": 29, "dpi": 405, "width": 1080, "height": 2400},
    {"brand": "Vivo", "model": "Y19", "device": "vivo_1909", "android": "9", "sdk": 28, "dpi": 480, "width": 1080, "height": 2340},
    {"brand": "OnePlus", "model": "Nord", "device": "avicii", "android": "10", "sdk": 29, "dpi": 420, "width": 1080, "height": 2400},
]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    sys.stdout.flush()

def rand_str(n=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(n))

def rand_username():
    prefixes = ["user", "ig", "acc", "id", "pro", "real", "vip"]
    return random.choice(prefixes) + rand_str(random.randint(6, 10), string.ascii_lowercase + string.digits)

def rand_password():
    return random.choice(["Pass", "Ig", "Acc"]) + rand_str(6, string.ascii_letters + string.digits) + random.choice(["!", "@", "#"]) + str(random.randint(10, 99))

def rand_name():
    first = random.choice(["Minh", "An", "Linh", "Trang", "Hoa", "Nam", "Long", "Khang", "Phuong", "Nhi", "My", "Quang", "Hung", "Duy"])
    last = random.choice(["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Phan", "Vu", "Vo", "Dang", "Bui", "Do"])
    return f"{last} {first}"

def rand_device():
    return random.choice(DEVICES)

def gen_android_id():
    return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]

def gen_uuid():
    return str(uuid.uuid4())

def gen_device_id():
    return "android-" + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]

def gen_machine_id():
    return gen_android_id() + gen_android_id()[:8]

def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    p = proxy_str.strip()
    if not p:
        return None
    scheme = "http"
    if "://" in p:
        scheme, p = p.split("://", 1)
    parts = p.split(":")
    if len(parts) == 4:
        ip, port, user, pwd = parts
        f = f"{scheme}://{user}:{pwd}@{ip}:{port}"
    elif "@" in p:
        f = f"{scheme}://{p}"
    elif len(parts) == 2:
        f = f"{scheme}://{p}"
    else:
        f = f"{scheme}://{p}"
    return {"http": f, "https": f}

def test_proxy(proxy_str):
    proxies = parse_proxy(proxy_str)
    if not proxies:
        return None
    try:
        r = requests.get("https://api.ipify.org?format=json", proxies=proxies, timeout=15)
        if r.status_code == 200:
            return r.json().get("ip")
    except Exception:
        pass
    return None

# ================= EMAIL =================
def get_email_1secmail():
    try:
        r = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", timeout=15)
        email = r.json()[0]
        return {"provider": "1secmail", "email": email, "login": email.split("@")[0], "domain": email.split("@")[1]}
    except Exception as e:
        log(f"[!] 1secmail loi: {e}")
        return None

def get_email_mailtm():
    try:
        r = requests.get("https://api.mail.tm/domains", timeout=15)
        domains = r.json().get("hydra:member", [])
        if not domains:
            return None
        domain = domains[0]["domain"]
        login = rand_str(10)
        email = f"{login}@{domain}"
        pw = rand_str(12)
        r = requests.post("https://api.mail.tm/accounts", json={"address": email, "password": pw}, timeout=15)
        if r.status_code not in [200, 201]:
            return None
        r = requests.post("https://api.mail.tm/token", json={"address": email, "password": pw}, timeout=15)
        token = r.json().get("token", "")
        return {"provider": "mailtm", "email": email, "password": pw, "token": token}
    except Exception as e:
        log(f"[!] mail.tm loi: {e}")
        return None

def check_email_1secmail(login, domain):
    try:
        r = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}", timeout=15)
        return r.json()
    except Exception:
        return []

def read_email_1secmail(login, domain, msg_id):
    try:
        r = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}", timeout=15)
        return r.json()
    except Exception:
        return {}

def check_email_mailtm(token):
    try:
        r = requests.get("https://api.mail.tm/messages", headers={"Authorization": f"Bearer {token}"}, timeout=15)
        return r.json().get("hydra:member", [])
    except Exception:
        return []

def extract_otp(text):
    if not text:
        return None
    m = re.search(r'\b(\d{6})\b', text)
    if m:
        return m.group(1)
    m = re.search(r'\b(\d{5})\b', text)
    if m:
        return m.group(1)
    return None

def wait_for_email_otp(provider_info, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        if provider_info["provider"] == "1secmail":
            msgs = check_email_1secmail(provider_info["login"], provider_info["domain"])
            if msgs:
                for msg in msgs:
                    body = read_email_1secmail(provider_info["login"], provider_info["domain"], msg["id"])
                    text = body.get("textBody", "") + body.get("htmlBody", "") + body.get("subject", "")
                    otp = extract_otp(text)
                    if otp:
                        return otp
        elif provider_info["provider"] == "mailtm":
            msgs = check_email_mailtm(provider_info["token"])
            if msgs:
                for msg in msgs:
                    text = (msg.get("subject", "") + " " + str(msg.get("intro", ""))).lower()
                    otp = extract_otp(text)
                    if otp:
                        return otp
        time.sleep(5)
    return None

# ================= SMS =================
SMS_MAN_BASE = "https://api.sms-man.com/control"

def sms_man_get_limits(token, country_id, application_id):
    try:
        r = requests.get(f"{SMS_MAN_BASE}/limits", params={"token": token, "country_id": country_id, "application_id": application_id}, timeout=15)
        return r.json()
    except Exception:
        return {}

def sms_man_request_number(token, country_id, application_id):
    try:
        r = requests.get(f"{SMS_MAN_BASE}/get-number", params={"token": token, "country_id": country_id, "application_id": application_id}, timeout=20)
        return r.json()
    except Exception as e:
        log(f"[!] SMS-Man get-number loi: {e}")
        return {}

def sms_man_get_sms(token, request_id):
    try:
        r = requests.get(f"{SMS_MAN_BASE}/get-sms", params={"token": token, "request_id": request_id}, timeout=15)
        return r.json()
    except Exception:
        return {}

def sms_man_set_status(token, request_id, status):
    try:
        r = requests.get(f"{SMS_MAN_BASE}/set-status", params={"token": token, "request_id": request_id, "status": status}, timeout=15)
        return r.json()
    except Exception:
        return {}

# ================= DEVICE FINGERPRINT =================
def build_device_headers(device, cookie="", csrf=""):
    dpi = device["dpi"]
    w = device["width"]
    h = device["height"]
    return {
        "User-Agent": f"Instagram {IG_APP_VERSION} Android ({device['android']}/{device['sdk']}; {dpi}dpi; {w}x{h}; {device['brand']}; {device['model']}; {device['device']}; qcom; en_US; 317822529)",
        "Accept-Language": "en-US",
        "X-IG-Capabilities": "3brTvx0=",
        "X-IG-Connection-Type": "WIFI",
        "X-IG-App-ID": IG_APP_ID,
        "X-CSRFToken": csrf,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "i.instagram.com",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate",
        "Cookie": cookie,
    }

def build_common_params(device):
    return {
        "_uuid": gen_uuid(),
        "_uid": "0",
        "_csrftoken": "missing",
        "device_id": gen_device_id(),
        "guid": gen_uuid(),
        "phone_id": gen_uuid(),
        "adid": gen_uuid(),
        "android_id": gen_android_id(),
        "machine_id": gen_machine_id(),
        "waterfall_id": gen_uuid(),
        "device_model": device["model"],
        "device_manufacturer": device["brand"],
        "os_version": device["android"],
        "os_api_level": str(device["sdk"]),
        "dpi": str(device["dpi"]),
        "resolution": f"{device['width']}x{device['height']}",
        "app_version": IG_APP_VERSION,
        "locale": "en_US",
        "timezone_offset": "25200",
    }

# ================= IG NATIVE API =================
def ig_reg_email(email, fullname, username, password, device, proxy=None, session=None):
    if session is None:
        session = c_requests.Session(impersonate="chrome120")
        proxies = parse_proxy(proxy) if proxy else None
        if proxies:
            session.proxies = proxies
    params = build_common_params(device)
    params["email"] = email
    params["username"] = username
    params["first_name"] = fullname
    params["password"] = password
    headers = build_device_headers(device)
    try:
        r = session.post(f"{IG_API_URL}/accounts/create/", data=params, headers=headers, timeout=30)
        return r.json() if r.text else {"status": "fail", "message": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ig_send_email_verify(email, device, proxy=None, session=None):
    if session is None:
        session = c_requests.Session(impersonate="chrome120")
        proxies = parse_proxy(proxy) if proxy else None
        if proxies:
            session.proxies = proxies
    params = build_common_params(device)
    params["email"] = email
    headers = build_device_headers(device)
    try:
        r = session.post(f"{IG_API_URL}/accounts/send_verify_email/", data=params, headers=headers, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ig_verify_email(email, code, device, proxy=None, session=None):
    if session is None:
        session = c_requests.Session(impersonate="chrome120")
        proxies = parse_proxy(proxy) if proxy else None
        if proxies:
            session.proxies = proxies
    params = build_common_params(device)
    params["email"] = email
    params["code"] = code
    headers = build_device_headers(device)
    try:
        r = session.post(f"{IG_API_URL}/accounts/verify_email_code/", data=params, headers=headers, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ig_verify_sms(phone, code, device, proxy=None, session=None):
    if session is None:
        session = c_requests.Session(impersonate="chrome120")
        proxies = parse_proxy(proxy) if proxy else None
        if proxies:
            session.proxies = proxies
    params = build_common_params(device)
    params["phone_number"] = phone
    params["verification_code"] = code
    headers = build_device_headers(device)
    try:
        r = session.post(f"{IG_API_URL}/accounts/verify_sms_code/", data=params, headers=headers, timeout=20)
        return r.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ig_set_profile_pic(session, device, image_url, cookie="", csrf=""):
    try:
        img = session.get(image_url, timeout=20)
        if img.status_code != 200:
            return {"status": "fail", "message": "Khong tai duoc anh"}
        params = build_common_params(device)
        headers = build_device_headers(device, cookie, csrf)
        headers.pop("Content-Type", None)
        files = {"profile_pic": ("pic.jpg", img.content, "image/jpeg")}
        r = session.post(f"{IG_API_URL}/accounts/edit_profile/", data=params, headers=headers, files=files, timeout=30)
        return r.json() if r.text else {"status": "fail"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ig_upload_photo(session, device, image_url, caption, cookie="", csrf=""):
    try:
        img = session.get(image_url, timeout=20)
        if img.status_code != 200:
            return {"status": "fail", "message": "Khong tai duoc anh"}
        params = build_common_params(device)
        headers = build_device_headers(device, cookie, csrf)
        headers.pop("Content-Type", None)
        files = {"photo": ("photo.jpg", img.content, "image/jpeg")}
        r = session.post(f"{IG_API_URL}/media/upload/", data=params, headers=headers, files=files, timeout=60)
        res = r.json() if r.text else {}
        upload_id = res.get("upload_id", "")
        if not upload_id:
            return {"status": "fail", "message": "Upload ID fail", "raw": str(res)[:200]}
        params2 = build_common_params(device)
        params2["upload_id"] = upload_id
        params2["caption"] = caption
        params2["source_type"] = "4"
        headers2 = build_device_headers(device, cookie, csrf)
        r2 = session.post(f"{IG_API_URL}/media/configure/", data=params2, headers=headers2, timeout=60)
        return r2.json() if r2.text else {"status": "fail"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def ig_enable_2fa(session, device, cookie="", csrf=""):
    try:
        params = build_common_params(device)
        headers = build_device_headers(device, cookie, csrf)
        r = session.get(f"{IG_API_URL}/accounts/2fa/secret/", headers=headers, timeout=20)
        data2 = r.json() if r.text else {}
        secret = data2.get("secret", "") or data2.get("totp_seed", "")
        return {"secret": secret, "raw": data2}
    except Exception as e:
        return {"secret": "", "error": str(e)}

# ================= REG FLOW =================
def reg_one_account(config):
    result = {
        "success": False,
        "username": "", "password": "", "email": "", "phone": "",
        "cookie": "", "token": "", "2fa_secret": "",
        "proxy": config.get("proxy", ""), "error": "",
        "created_at": datetime.now().isoformat(),
    }

    email_info = None
    if config.get("email_provider") in ["1secmail", "both"]:
        email_info = get_email_1secmail()
        if email_info:
            log(f"{cyan}[*] Email (1secmail): {email_info['email']}{reset}")
    if not email_info and config.get("email_provider") in ["mailtm", "both"]:
        email_info = get_email_mailtm()
        if email_info:
            log(f"{cyan}[*] Email (mail.tm): {email_info['email']}{reset}")
    if not email_info:
        result["error"] = "Khong lay duoc email"
        return result

    result["email"] = email_info["email"]

    username = config.get("username_pattern", "user{rand}").replace("{rand}", rand_str(8))
    password = config.get("password_pattern", "Pass{rand}!").replace("{rand}", rand_str(6))
    fullname = rand_name()
    device = rand_device()

    log(f"{yellow}[*] Username: {username}{reset}")
    log(f"{yellow}[*] Password: {password}{reset}")
    log(f"{yellow}[*] Fullname: {fullname}{reset}")
    log(f"{yellow}[*] Device: {device['brand']} {device['model']} (Android {device['android']}){reset}")

    proxy = config.get("proxy", "")
    if proxy:
        proxy_ip = test_proxy(proxy)
        if not proxy_ip:
            result["error"] = "Proxy die"
            return result
        log(f"{green}[+] Proxy OK - IP: {proxy_ip}{reset}")

    session = c_requests.Session(impersonate="chrome120")
    proxies = parse_proxy(proxy) if proxy else None
    if proxies:
        session.proxies = proxies

    log(f"{yellow}[*] Dang goi API reg IG...{reset}")
    reg_res = ig_reg_email(email_info["email"], fullname, username, password, device, proxy, session)
    log(f"{cyan}[*] Reg response: {json.dumps(reg_res)[:300]}{reset}")

    if reg_res.get("status") == "ok" or reg_res.get("account_created") is True:
        log(f"{green}[+] REG THANH CONG ngay!{reset}")
        result["success"] = True
        result["username"] = username
        result["password"] = password
    else:
        msg = json.dumps(reg_res).lower()
        if "email" in msg or "verify" in msg:
            log(f"{yellow}[*] IG yeu cau verify email - cho OTP...{reset}")
            otp = wait_for_email_otp(email_info, timeout=180)
            if otp:
                log(f"{green}[+] Email OTP: {otp}{reset}")
                ver = ig_verify_email(email_info["email"], otp, device, proxy, session)
                log(f"{cyan}[*] Verify response: {json.dumps(ver)[:200]}{reset}")
                if ver.get("status") == "ok" or ver.get("verified"):
                    result["success"] = True
                    result["username"] = username
                    result["password"] = password
        if not result["success"] and config.get("sms_man_token"):
            log(f"{yellow}[*] Thu SMS verify qua SMS-Man...{reset}")
            sms_num = sms_man_request_number(config["sms_man_token"], config.get("country_id", "0"), config.get("app_id", "12"))
            if sms_num.get("request_id"):
                req_id = sms_num["request_id"]
                phone = sms_num.get("number", "")
                log(f"{green}[+] So SMS: {phone}{reset}")
                time.sleep(60)
                sms = sms_man_get_sms(config["sms_man_token"], req_id)
                otp_sms = sms.get("sms_code", "")
                if otp_sms:
                    ver = ig_verify_sms(phone, otp_sms, device, proxy, session)
                    if ver.get("status") == "ok":
                        result["success"] = True
                        result["username"] = username
                        result["password"] = password
                        result["phone"] = phone
                sms_man_set_status(config["sms_man_token"], req_id, "used" if result["success"] else "reject")

    if result["success"]:
        cookies = session.cookies.get_dict()
        cookie_parts = []
        for k in ["csrftoken", "sessionid", "ds_user_id", "mid", "ig_did"]:
            if k in cookies:
                cookie_parts.append(f"{k}={cookies[k]}")
        result["cookie"] = "; ".join(cookie_parts)
        result["token"] = ""
        csrf = cookies.get("csrftoken", "")

        avatar_urls = config.get("avatar_urls", [])
        if avatar_urls:
            avatar = random.choice(avatar_urls)
            log(f"{yellow}[*] Update avatar: {avatar[:60]}...{reset}")
            pic_res = ig_set_profile_pic(session, device, avatar, result["cookie"], csrf)
            log(f"{cyan}[*] Avatar response: {json.dumps(pic_res)[:150]}{reset}")

        captions = config.get("captions", [])
        if captions and avatar_urls:
            for i in range(3):
                pic_url = random.choice(avatar_urls)
                cap = random.choice(captions)
                log(f"{yellow}[*] Dang dang bai {i+1}/3...{reset}")
                post_res = ig_upload_photo(session, device, pic_url, cap, result["cookie"], csrf)
                log(f"{cyan}[*] Post {i+1}: {json.dumps(post_res)[:150]}{reset}")
                time.sleep(random.randint(30, 60))

        log(f"{yellow}[*] Lay 2FA secret...{reset}")
        twofa = ig_enable_2fa(session, device, result["cookie"], csrf)
        result["2fa_secret"] = twofa.get("secret", "")
        log(f"{cyan}[*] 2FA secret: {result['2fa_secret']}{reset}")

        log(f"{green}[+] HOAN THANH nick {username}!{reset}")
    else:
        log(f"{red}[-] REG THAT BAI!{reset}")

    return result

def save_result(result, output_file="reg_results.txt"):
    try:
        line = f"{result.get('username','')}|{result.get('password','')}|{result.get('email','')}|{result.get('phone','')}|{result.get('2fa_secret','')}|{result.get('cookie','')}|{result.get('token','')}|{result.get('proxy','')}|{result.get('created_at','')}"
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        log(f"[!] Loi luu file: {e}")

# ================= MAIN =================
def main():
    log(f"{cyan}===== IG REG TOOL START ====={reset}")
    config = {}
    try:
        log("Nhan config tu web...")
        config_raw = input().strip()
        config = json.loads(config_raw) if config_raw else {}
    except Exception as e:
        log(f"[!] Khong nhan duoc config: {e}")
        config = {
            "email_provider": "1secmail",
            "sms_man_token": "",
            "country_id": "0",
            "app_id": "12",
            "proxy": "",
            "avatar_urls": [],
            "captions": ["Hello IG!"],
            "username_pattern": "user{rand}",
            "password_pattern": "Pass{rand}!",
            "count": 1,
            "threads": 1,
            "delay": 15,
        }

    log(f"{green}[+] Config: {json.dumps(config)[:300]}{reset}")

    count = int(config.get("count", 1))
    threads = int(config.get("threads", 1))
    delay = int(config.get("delay", 15))

    log(f"{cyan}[*] Se reg {count} nick | {threads} luong | delay {delay}s{reset}")

    if threads > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for i in range(count):
                futures.append(executor.submit(_reg_task, config, i + 1))
            for f in futures:
                try:
                    result = f.result()
                    if result:
                        save_result(result)
                except Exception as e:
                    log(f"[!] Task loi: {e}")
    else:
        for i in range(count):
            result = _reg_task(config, i + 1)
            if result:
                save_result(result)
            if i < count - 1:
                log(f"{yellow}[*] Nghi {delay}s truoc nick tiep theo...{reset}")
                time.sleep(delay)

    log(f"{cyan}===== IG REG TOOL DONE ====={reset}")

def _reg_task(config, index):
    log(f"\n{cyan}===== NICK #{index} ====={reset}")
    result = reg_one_account(config)
    if result["success"]:
        log(f"{green}[# {index}] THANH CONG: {result['username']}{reset}")
    else:
        log(f"{red}[# {index}] THAT BAI: {result.get('error', '')[:200]}{reset}")
    return result

if __name__ == "__main__":
    main()
'''

# ============================================================================
# ================== EMBEDDED TOOLS + FLASK ROUTES ===========================
# ============================================================================
EMBEDDED_TOOLS = {
    "igreg": {
        "name": "IG Reg Tool",
        "desc": "Tool đăng ký tài khoản Instagram hàng loạt qua API native (Android)",
        "color": "#ec4899",
        "filename": "igreg.py",
        "code": TOOL_CODE_IG_REG,
    },
}

sessions = {}
sessions_lock = threading.Lock()

TOOL_INFO = {k: {"name": v["name"], "desc": v["desc"], "color": v["color"]}
             for k, v in EMBEDDED_TOOLS.items()}


def ensure_tool_file(tool_key):
    if tool_key not in EMBEDDED_TOOLS:
        return None, f"Tool không hợp lệ: {tool_key}"
    info = EMBEDDED_TOOLS[tool_key]
    filepath = os.path.join(TEMP_TOOLS_DIR, info["filename"])
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(info["code"])
        return filepath, None
    except Exception as e:
        return None, f"Không thể tạo file tool: {e}"


def read_process_output(session_id, process):
    try:
        for line in iter(process.stdout.readline, ''):
            if line == '' and process.poll() is not None:
                break
            if line:
                line = line.rstrip('\n').rstrip('\r')
                with sessions_lock:
                    if session_id in sessions:
                        sessions[session_id]["output_lines"].append(line)
                        if len(sessions[session_id]["output_lines"]) > 5000:
                            sessions[session_id]["output_lines"] = sessions[session_id]["output_lines"][-5000:]
                socketio.emit('output', {
                    'session_id': session_id,
                    'line': line,
                    'ts': datetime.now().strftime('%H:%M:%S')
                }, room=session_id)
    except Exception:
        pass
    finally:
        try:
            process.wait()
            rc = process.returncode
        except Exception:
            rc = -1
        with sessions_lock:
            if session_id in sessions:
                sessions[session_id]["status"] = "stopped" if rc == 0 else f"exited({rc})"
        socketio.emit('status', {
            'session_id': session_id,
            'status': 'stopped',
            'return_code': rc,
            'message': f'Tool đã kết thúc (code {rc})'
        }, room=session_id)


def start_tool_process(session_id, tool_key):
    filepath, err = ensure_tool_file(tool_key)
    if err:
        return None, err
    if not filepath or not os.path.exists(filepath):
        return None, f"Không tìm thấy file tool: {filepath}"
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    env['TERM'] = 'xterm-256color'
    env['LC_ALL'] = 'C.UTF-8'
    env['LANG'] = 'C.UTF-8'
    process = subprocess.Popen(
        [sys.executable, '-u', filepath],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=TEMP_TOOLS_DIR,
        env=env,
        bufsize=1,
        universal_newlines=True,
        encoding='utf-8',
        errors='replace',
    )
    return process, None


@app.route('/')
def index():
    return render_template('index.html', tools=TOOL_INFO)


@app.route('/health')
def health():
    return jsonify({"ok": True, "time": datetime.now().isoformat()})


@app.route('/api/tools')
def api_tools():
    return jsonify(TOOL_INFO)


@app.route('/api/sessions')
def api_sessions():
    with sessions_lock:
        result = []
        for sid, s in sessions.items():
            result.append({
                "session_id": sid,
                "tool": s["tool"],
                "status": s["status"],
                "started_at": s["started_at"],
                "output_count": len(s["output_lines"]),
            })
        return jsonify(result)


@app.route('/api/start/<tool_key>', methods=['POST'])
def api_start(tool_key):
    if tool_key not in EMBEDDED_TOOLS:
        return jsonify({"ok": False, "error": "Tool không hợp lệ"}), 400
    session_id = str(uuid.uuid4())[:8]
    process, err = start_tool_process(session_id, tool_key)
    if err:
        return jsonify({"ok": False, "error": err}), 500
    with sessions_lock:
        sessions[session_id] = {
            "tool": tool_key,
            "process": process,
            "output_lines": [],
            "status": "running",
            "started_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    t = threading.Thread(target=read_process_output, args=(session_id, process), daemon=True)
    t.start()
    return jsonify({"ok": True, "session_id": session_id})


@app.route('/api/stop/<session_id>', methods=['POST'])
def api_stop(session_id):
    with sessions_lock:
        s = sessions.get(session_id)
    if not s:
        return jsonify({"ok": False, "error": "Session không tồn tại"}), 404
    try:
        proc = s["process"]
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        with sessions_lock:
            sessions[session_id]["status"] = "stopped"
        socketio.emit('status', {
            'session_id': session_id,
            'status': 'stopped',
            'message': 'Đã dừng theo yêu cầu'
        }, room=session_id)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/input/<session_id>', methods=['POST'])
def api_input(session_id):
    data = request.get_json() or {}
    text = data.get("text", "")
    with sessions_lock:
        s = sessions.get(session_id)
    if not s:
        return jsonify({"ok": False, "error": "Session không tồn tại"}), 404
    try:
        proc = s["process"]
        if proc.poll() is not None:
            return jsonify({"ok": False, "error": "Process đã kết thúc"}), 400
        proc.stdin.write(text + "\n")
        proc.stdin.flush()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/clear/<session_id>', methods=['POST'])
def api_clear(session_id):
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id]["output_lines"] = []
    socketio.emit('cleared', {'session_id': session_id}, room=session_id)
    return jsonify({"ok": True})


@app.route('/api/save/<session_id>', methods=['POST'])
def api_save(session_id):
    with sessions_lock:
        s = sessions.get(session_id)
    if not s:
        return jsonify({"ok": False, "error": "Session không tồn tại"}), 404
    filename = f"{s['tool']}_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    filepath = os.path.join(SESSIONS_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Tool: {s['tool']}\n")
            f.write(f"# Started: {s['started_at']}\n")
            f.write(f"# Session: {session_id}\n")
            f.write("=" * 60 + "\n")
            f.write("\n".join(s["output_lines"]))
        return jsonify({"ok": True, "filename": filename})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route('/api/test-proxy', methods=['POST'])
def api_test_proxy():
    data = request.get_json() or {}
    proxy_str = data.get("proxy", "").strip()
    if not proxy_str:
        return jsonify({"ok": False, "error": "Proxy trống"})
    p = proxy_str
    if "://" not in p:
        p = "http://" + p
    try:
        r = requests.get("https://api.ipify.org?format=json",
                         proxies={"http": p, "https": p}, timeout=15)
        if r.status_code == 200:
            return jsonify({"ok": True, "ip": r.json().get("ip", "")})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
    return jsonify({"ok": False, "error": "Proxy die hoặc timeout"})


@app.route('/download/reg_results')
def download_reg_results():
    from flask import send_file
    path = os.path.join(TEMP_TOOLS_DIR, "reg_results.txt")
    if not os.path.exists(path):
        return "Chưa có file kết quả", 404
    return send_file(path, as_attachment=True)


@socketio.on('join')
def on_join(data):
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        emit('joined', {'session_id': session_id})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print(" 🚀 TA TOOL WEB — IG REG MANAGER")
    print(f" 📁 Temp tools: {TEMP_TOOLS_DIR}")
    print(f" 🌐 Port: {port}")
    print(f" 📦 Tools: {list(EMBEDDED_TOOLS.keys())}")
    print("=" * 60)
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
