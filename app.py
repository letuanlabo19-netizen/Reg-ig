import os
import sys
import json
import uuid
import time
import threading
import subprocess
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ta_tool_secret_2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(SESSIONS_DIR, exist_ok=True)

TEMP_TOOLS_DIR = os.path.join(tempfile.gettempdir(), "ta_tool_embedded")
os.makedirs(TEMP_TOOLS_DIR, exist_ok=True)


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
from datetime import datetime

import requests
try:
    from curl_cffi import requests as cf_requests
    CF_AVAILABLE = True
except ImportError:
    cf_requests = None
    CF_AVAILABLE = False

red = "\033[1;31m"; green = "\033[1;32m"; yellow = "\033[1;33m"
cyan = "\033[1;36m"; blue = "\033[1;34m"; white = "\033[0;37m"; reset = "\033[0m"

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    sys.stdout.flush()

FINGERPRINT_FILE = "fingerprints.json"
RESULTS_FILE = "reg_results.txt"


# ================= MÁY ẢO =================
DEVICES_ANDROID = [
    {"brand": "Xiaomi", "model": "Redmi Note 7", "device": "lavender", "android": "9", "sdk": 28, "dpi": 480, "w": 1080, "h": 1920, "build": "PKQ1.180904.001"},
    {"brand": "Samsung", "model": "SM-G991B", "device": "o1s", "android": "11", "sdk": 30, "dpi": 420, "w": 1080, "h": 2340, "build": "RP1A.200720.012"},
    {"brand": "Samsung", "model": "SM-A525F", "device": "a52q", "android": "11", "sdk": 30, "dpi": 405, "w": 1080, "h": 2400, "build": "RP1A.200720.012"},
    {"brand": "Xiaomi", "model": "POCO X3 NFC", "device": "surya", "android": "10", "sdk": 29, "dpi": 440, "w": 1080, "h": 2400, "build": "QKQ1.200512.002"},
    {"brand": "OPPO", "model": "CPH2091", "device": "OP4A7A", "android": "10", "sdk": 29, "dpi": 400, "w": 1080, "h": 2400, "build": "QP1A.190711.020"},
    {"brand": "Google", "model": "Pixel 5", "device": "redfin", "android": "11", "sdk": 30, "dpi": 440, "w": 1080, "h": 2340, "build": "RQ1A.201105.002"},
    {"brand": "Huawei", "model": "MAR-LX1A", "device": "HWMAR", "android": "10", "sdk": 29, "dpi": 480, "w": 1080, "h": 2312, "build": "HUAWEIMAR-L21A"},
    {"brand": "Realme", "model": "RMX2061", "device": "RMX2061L1", "android": "10", "sdk": 29, "dpi": 405, "w": 1080, "h": 2400, "build": "QP1A.190711.020"},
    {"brand": "Vivo", "model": "vivo 1909", "device": "PD1948", "android": "9", "sdk": 28, "dpi": 480, "w": 1080, "h": 2340, "build": "PPR1.180610.011"},
    {"brand": "OnePlus", "model": "AC2001", "device": "OnePlusNORD", "android": "10", "sdk": 29, "dpi": 420, "w": 1080, "h": 2400, "build": "QKQ1.200412.002"},
]

DEVICES_IOS = [
    {"device": "iPhone15,2", "ios": "17_2", "build": "21C62", "webkit": "605.1.15"},
    {"device": "iPhone15,3", "ios": "17_1", "build": "21B74", "webkit": "605.1.15"},
    {"device": "iPhone14,7", "ios": "16_6", "build": "20G75", "webkit": "605.1.15"},
    {"device": "iPhone14,2", "ios": "16_5", "build": "20F66", "webkit": "605.1.15"},
    {"device": "iPhone13,2", "ios": "15_7", "build": "19H12", "webkit": "605.1.15"},
    {"device": "iPhone13,4", "ios": "16_0", "build": "20A362", "webkit": "605.1.15"},
    {"device": "iPhone12,1", "ios": "15_5", "build": "19F77", "webkit": "605.1.15"},
]


class DeviceFingerprint:
    """Máy ảo - có thể sinh mới hoặc load từ dict"""

    def __init__(self, data=None):
        if data:
            # Load từ file
            self.platform = data["platform"]
            self.device = data["device"]
            self.uuid = data["uuid"]
            self.phone_id = data["phone_id"]
            self.adid = data["adid"]
            self.guid = data["guid"]
            self.android_id = data["android_id"]
            self.machine_id = data["machine_id"]
            self.device_id = data["device_id"]
            self.waterfall_id = data["waterfall_id"]
            self.session_id = data["session_id"]
        else:
            # Sinh mới
            self.platform = random.choice(["android", "ios"])
            self.device = random.choice(DEVICES_ANDROID if self.platform == "android" else DEVICES_IOS)
            self.uuid = str(uuid.uuid4())
            self.phone_id = str(uuid.uuid4())
            self.adid = str(uuid.uuid4())
            self.guid = str(uuid.uuid4())
            self.android_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
            self.machine_id = self.android_id + hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:8]
            self.device_id = "android-" + self.android_id
            self.waterfall_id = str(uuid.uuid4())
            self.session_id = str(uuid.uuid4())

    def to_dict(self):
        return {
            "platform": self.platform, "device": self.device, "uuid": self.uuid,
            "phone_id": self.phone_id, "adid": self.adid, "guid": self.guid,
            "android_id": self.android_id, "machine_id": self.machine_id,
            "device_id": self.device_id, "waterfall_id": self.waterfall_id,
            "session_id": self.session_id,
        }

    def get_user_agent(self):
        if self.platform == "android":
            d = self.device
            return f'Mozilla/5.0 (Linux; Android {d["android"]}; {d["model"]} Build/{d["build"]}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        else:
            d = self.device
            return f'Mozilla/5.0 ({d["device"]}; CPU iPhone OS {d["ios"]} like Mac OS X) AppleWebKit/{d["webkit"]} (KHTML, like Gecko) Version/{d["ios"].split("_")[0]}.0 Mobile/{d["build"]} Safari/{d["webkit"]}'

    def get_headers_extra(self):
        if self.platform == "android":
            return {'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
                    'sec-ch-ua': '"Chromium";v="120", "Not_A Brand";v="8"'}
        else:
            return {'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"iOS"',
                    'sec-ch-ua': '"Safari";v="17", "Not_A Brand";v="8"'}


def load_fingerprints():
    if os.path.exists(FINGERPRINT_FILE):
        try:
            with open(FINGERPRINT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception: pass
    return {}

def save_fingerprints(data):
    try:
        with open(FINGERPRINT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception: pass


class TempEmailGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        self.generated_usernames = set()
        self.email_tokens = {}

    def generate_vietnamese_username(self):
        ho = ['nguyen', 'tran', 'le', 'pham', 'hoang', 'huynh', 'phan', 'vu', 'vo', 'dang', 'bui', 'do', 'ho', 'ngo', 'duong', 'ly']
        ten_dem = ['thi', 'van', 'duc', 'minh', 'quoc', 'thanh', 'ngoc', 'bao', 'gia', 'khanh']
        ten = ['an', 'binh', 'chi', 'duong', 'giang', 'han', 'khang', 'lam', 'long', 'my', 'nhi', 'phong', 'quan', 'son', 'trang', 'uyen', 'vy', 'yen', 'anh', 'bao']
        fmt = random.choice([1, 2, 3])
        if fmt == 1: u = f"{random.choice(ho)}{random.choice(ten_dem)}{random.choice(ten)}"
        elif fmt == 2: u = f"{random.choice(ho)}{random.choice(ten)}{random.choice(ten)}"
        else: u = f"{random.choice(ten)}{random.choice(ten_dem)}{random.choice(ho)}"
        u = u + str(random.randint(10, 999))
        if u in self.generated_usernames: u = u + str(random.randint(1000, 9999))
        self.generated_usernames.add(u)
        return u

    def get_available_domains(self):
        for _ in range(3):
            try:
                r = self.session.get('https://api.mail.tm/domains', timeout=8)
                if r.status_code == 200:
                    data = r.json()
                    domains = []
                    if 'hydra:member' in data: domains = [d['domain'] for d in data['hydra:member'] if d.get('isActive')]
                    elif isinstance(data, list): domains = [d['domain'] for d in data if d.get('isActive')]
                    if domains: return domains
                time.sleep(2)
            except Exception: time.sleep(2)
        return ['agristur.com', 'febbox.com', 'main.truf.biz', 'laste.ml', 'failing.com']

    def create_mailtm_account(self, username, domain):
        for _ in range(3):
            try:
                password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
                r = self.session.post('https://api.mail.tm/accounts',
                                      json={'address': f'{username}@{domain}', 'password': password}, timeout=12)
                if r.status_code == 201:
                    token = self.get_mailtm_token(f'{username}@{domain}', password)
                    info = {'email': f'{username}@{domain}', 'password': password, 'service': 'mailtm', 'domain': domain, 'token': token}
                    if token: self.email_tokens[f'{username}@{domain}'] = token
                    return info
                elif r.status_code == 422: return None
            except Exception: pass
            time.sleep(2)
        return None

    def get_mailtm_token(self, email, password):
        if email in self.email_tokens: return self.email_tokens[email]
        try:
            r = self.session.post('https://api.mail.tm/token', json={'address': email, 'password': password}, timeout=10)
            if r.status_code == 200:
                token = r.json().get('token')
                self.email_tokens[email] = token
                return token
        except Exception: pass
        return None

    def get_message_content(self, token, message_id):
        try:
            r = self.session.get(f'https://api.mail.tm/messages/{message_id}', headers={'Authorization': f'Bearer {token}'}, timeout=8)
            if r.status_code == 200:
                data = r.json()
                return data.get('text', '') or data.get('html', '')
        except Exception: pass
        return ''

    def get_all_messages(self, email_info):
        try:
            token = email_info.get('token') or self.get_mailtm_token(email_info['email'], email_info['password'])
            if not token: return []
            r = self.session.get('https://api.mail.tm/messages', headers={'Authorization': f'Bearer {token}'}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                msgs = data.get('hydra:member', []) if 'hydra:member' in data else (data if isinstance(data, list) else [])
                try: msgs.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
                except Exception: pass
                for msg in msgs[:3]:
                    mid = msg.get('id')
                    if mid: msg['full_content'] = self.get_message_content(token, mid)
                return msgs
        except Exception: pass
        return []

    def create_random_email(self):
        for _ in range(3):
            try:
                domains = self.get_available_domains()
                if not domains: return None
                username = self.generate_vietnamese_username()
                domain = random.choice(domains)
                info = self.create_mailtm_account(username, domain)
                if info:
                    log(f"{green}[+] Mail: {info['email']}{reset}")
                    return info
                time.sleep(1)
            except Exception: time.sleep(2)
        return None

class InstagramAutoRegister:
    def __init__(self, config):
        self.config = config
        self.email_generator = TempEmailGenerator()
        self.emails_pool = []
        self.current_email_index = 0
        self.displayed_message_ids = set()
        self.account_counter = 0
        self.avatar_urls = config.get("avatar_urls", [])
        self.proxies = config.get("proxies", [])
        self.sms_man_token = config.get("sms_man_token", "").strip()
        self.sms_country_id = str(config.get("country_id", "0"))
        self.sms_app_id = str(config.get("app_id", "12"))
        self.current_proxy = None
        self.current_proxy_str = ""
        self.current_device_data = None
        self.fingerprints = load_fingerprints()

    # ============== FINGERPRINT CỐ ĐỊNH ==============
    def get_fingerprint_for_index(self, idx):
        """Lấy máy ảo cố định theo index — lưu file để dùng lại"""
        key = f"nick_{idx}"
        if key in self.fingerprints:
            data = self.fingerprints[key]
            log(f"{cyan}[*] Load máy ảo cũ: {data['device'].get('model', data['device'].get('device'))}{reset}")
            return DeviceFingerprint(data)
        # Sinh mới
        dev = DeviceFingerprint()
        self.fingerprints[key] = dev.to_dict()
        save_fingerprints(self.fingerprints)
        log(f"{cyan}[*] Máy ảo mới: {dev.platform.upper()} - {dev.device.get('model', dev.device.get('device'))}{reset}")
        return dev

    # ============== PROXY CỐ ĐỊNH ==============
    def get_proxy_for_index(self, idx):
        """Mỗi nick 1 proxy cố định"""
        if not self.proxies:
            return None, ""
        # Round-robin: nick 1 → proxy 1, nick 2 → proxy 2...
        proxy_str = self.proxies[idx % len(self.proxies)].strip().strip('.')
        parts = [p.strip() for p in proxy_str.split(':')]
        if len(parts) == 4:
            if '.' in parts[0]:
                formatted = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            else:
                formatted = f"http://{parts[0]}:{parts[1]}@{parts[2]}:{parts[3]}"
        elif "@" in proxy_str:
            formatted = f"http://{proxy_str}"
        else:
            formatted = f"http://{proxy_str}"
        return {"http": formatted, "https": formatted}, proxy_str

    # ============== SESSION VỚI CURL_CFFI ==============
    def create_new_session(self, idx=0):
        """Session với curl_cffi + proxy cố định + máy ảo cố định"""
        # Máy ảo cố định theo index
        self.current_device_data = self.get_fingerprint_for_index(idx)

        if CF_AVAILABLE:
            try:
                self.session = cf_requests.Session(impersonate="chrome120")
                log(f"{cyan}[*] Session: curl_cffi (Chrome){reset}")
            except Exception as e:
                log(f"{yellow}[!] curl_cffi lỗi: {e}{reset}")
                self.session = requests.Session()
        else:
            self.session = requests.Session()
            log(f"{yellow}[*] Session: requests{reset}")

        ua = self.current_device_data.get_user_agent()
        extra = self.current_device_data.get_headers_extra()

        self.base_headers = {
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.instagram.com',
            'referer': 'https://www.instagram.com/accounts/emailsignup/',
            'user-agent': ua,
        }
        self.base_headers.update(extra)
        self.session.headers.update(self.base_headers)

        # Proxy cố định
        self.current_proxy, self.current_proxy_str = self.get_proxy_for_index(idx)
        if self.current_proxy:
            self.session.proxies.update(self.current_proxy)
            log(f"{cyan}[*] Proxy: {self.current_proxy_str[:40]}...{reset}")

    def wait_human(self, min_sec, max_sec):
        time.sleep(random.uniform(min_sec, max_sec))

    def generate_vietnamese_name(self):
        ho = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Ngô', 'Dương', 'Lý']
        ten_dem = ['Thị', 'Văn', 'Đức', 'Minh', 'Quốc', 'Thanh', 'Ngọc', 'Bảo', 'Gia', 'Khánh']
        ten = ['An', 'Bình', 'Chi', 'Dương', 'Giang', 'Hân', 'Khang', 'Lam', 'Long', 'My', 'Nhi', 'Phong', 'Quân', 'Sơn', 'Trang', 'Uyên', 'Vy', 'Yến', 'Ánh', 'Bảo']
        fmt = random.choice([1, 2, 3])
        if fmt == 1: return f"{random.choice(ho)} {random.choice(ten_dem)} {random.choice(ten)}"
        elif fmt == 2: return f"{random.choice(ho)} {random.choice(ten)} {random.choice(ten)}"
        else: return f"{random.choice(ten_dem)} {random.choice(ten)} {random.choice(ho)}"

    def remove_accents(self, text):
        patterns = {'[àáảãạăắằẵặẳâầấậẫẩ]': 'a', '[đ]': 'd', '[èéẻẽẹêềếểễệ]': 'e',
                    '[ìíỉĩị]': 'i', '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
                    '[ùúủũụưừứửữự]': 'u', '[ỳýỷỹỵ]': 'y'}
        for p, r in patterns.items():
            text = re.sub(p, r, text)
            text = re.sub(p.upper(), r.upper(), text)
        return text

    def generate_username(self, first_name):
        u = self.remove_accents(first_name).lower().replace(' ', '')
        m = random.choice([1, 2, 3, 4, 5])
        if m == 1: u = u + '_' + str(random.randint(100, 999))
        elif m == 2: u = u + '.' + str(random.randint(100, 999))
        elif m == 3: u = u + str(random.randint(1000, 9999))
        elif m == 4:
            if len(u) > 4:
                pos = random.randint(2, len(u) - 2)
                u = u[:pos] + '_' + u[pos:] + str(random.randint(10, 99))
        else: u = u + random.choice(['', '_', '.']) + str(random.randint(1000, 9999))
        return u

    def generate_random_date(self):
        return random.randint(1, 28), random.randint(1, 12), random.randint(1990, 2000)

    def generate_device_id(self):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(20))

    def generate_jazoest(self):
        return ''.join(random.choice(string.digits) for _ in range(5))

    def generate_web_session_id(self):
        c = string.ascii_lowercase + string.digits
        return ':'.join(''.join(random.choice(c) for _ in range(6)) for _ in range(3))

    def generate_random_csrf_token(self):
        patterns = [
            lambda: ''.join(random.choice(string.ascii_letters + string.digits + '_-') for _ in range(32)),
            lambda: ''.join(random.choice('0123456789abcdef') for _ in range(32)),
            lambda: ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(28)) + '==',
        ]
        return random.choice(patterns)()

    # ============== SMS-MAN API ==============
    def sms_man_request(self):
        if not self.sms_man_token:
            log(f"{red}[!] Không có SMS-Man token{reset}")
            return None
        try:
            r = requests.get("https://api.sms-man.com/control/get-number",
                             params={"token": self.sms_man_token, "country_id": self.sms_country_id,
                                     "application_id": self.sms_app_id}, timeout=20)
            data = r.json()
            if "request_id" in data and "number" in data:
                log(f"{green}[+] SMS-Man số: {data['number']} (id={data['request_id']}){reset}")
                return data
            log(f"{red}[!] SMS-Man lỗi: {str(data)[:200]}{reset}")
            return None
        except Exception as e:
            log(f"{red}[!] SMS-Man lỗi: {e}{reset}")
            return None

    def sms_man_get_code(self, request_id, timeout=180):
        if not self.sms_man_token: return None
        start = time.time()
        while time.time() - start < timeout:
            try:
                r = requests.get("https://api.sms-man.com/control/get-sms",
                                 params={"token": self.sms_man_token, "request_id": request_id}, timeout=15)
                data = r.json()
                code = data.get("sms_code", "") or data.get("code", "")
                if code:
                    code = re.sub(r'\D', '', str(code))[:6]
                    if len(code) >= 4:
                        log(f"{green}[+] SMS OTP: {code}{reset}")
                        return code
            except Exception: pass
            time.sleep(5)
        return None

    def sms_man_set_status(self, request_id, status="used"):
        if not self.sms_man_token: return
        try:
            requests.get("https://api.sms-man.com/control/set-status",
                         params={"token": self.sms_man_token, "request_id": request_id, "status": status}, timeout=10)
        except Exception: pass

    def get_initial_cookies_and_csrf(self):
        try:
            log(f"{yellow}[*] Khởi tạo session hữu cơ...{reset}")
            main_headers = {
                'authority': 'www.instagram.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'accept-language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
                'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none', 'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': self.base_headers['user-agent'],
            }
            self.session.get('https://www.instagram.com/', headers=main_headers, timeout=30)
            self.wait_human(3, 7)
            signup_headers = main_headers.copy()
            signup_headers['referer'] = 'https://www.instagram.com/'
            r = self.session.get('https://www.instagram.com/accounts/emailsignup/', headers=signup_headers, timeout=30)
            if r.status_code == 200:
                self.session.headers.update(self.base_headers)
                csrf_token = self.session.cookies.get('csrftoken')
                if not csrf_token:
                    m = re.search(r'"csrf_token":"([^"]+)"', r.text)
                    if m: csrf_token = m.group(1)
                if not csrf_token: csrf_token = self.generate_random_csrf_token()
                self.base_headers['x-csrftoken'] = csrf_token
                self.web_session_id = self.generate_web_session_id()
                if 'ig_nrcb' not in self.session.cookies:
                    self.session.cookies.set('ig_nrcb', '1')
                self.client_id = self.generate_device_id()
                self.jazoest = self.generate_jazoest()
                log(f"{green}[+] Session OK!{reset}")
                return True
            return False
        except Exception as e:
            log(f"{red}[!] Session init lỗi: {e}{reset}")
            return False

    def generate_enc_password(self, password):
        timestamp = int(datetime.now().timestamp())
        return f"#PWD_INSTAGRAM_BROWSER:0:{timestamp}:{password}"

    def attempt_signup(self, email, first_name, username, password):
        enc_password = self.generate_enc_password(password)
        data = {
            'enc_password': enc_password, 'email': email, 'username': username,
            'first_name': first_name, 'client_id': self.client_id,
            'seamless_login_enabled': '1', 'opt_into_one_tap': 'false',
            'jazoest': self.jazoest,
        }
        time.sleep(random.uniform(2, 3))
        log(f"{cyan}[*] Gửi form đăng ký...{reset}")
        self.wait_human(3, 6)

        for attempt in range(3):
            try:
                r = self.session.post(
                    'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/attempt/',
                    headers=self.base_headers, data=data, timeout=45
                )
                log(f"{cyan}    HTTP {r.status_code}{reset}")
                if r.status_code == 200:
                    try:
                        result = r.json()
                        if 'errors' in result:
                            err = str(result['errors']).lower()
                            if 'username' in err:
                                log(f"{red}    Username trùng{reset}")
                                return None
                            elif 'email' in err:
                                log(f"{red}    Email đã dùng{reset}")
                            elif 'spam' in err:
                                log(f"{red}    Spam detect{reset}")
                            else:
                                log(f"{yellow}    Errors: {str(result['errors'])[:150]}{reset}")
                    except Exception: pass
                return r
            except Exception as e:
                log(f"{yellow}    Attempt {attempt+1}/3 lỗi: {type(e).__name__}: {str(e)[:100]}{reset}")
                if attempt < 2: time.sleep(3); continue
                log(f"{red}[!] Thử 3 lần fail, bỏ nick này{reset}")
                return None
        return None

    def check_age_eligibility(self):
        day, month, year = self.generate_random_date()
        data = {'day': str(day), 'month': str(month), 'year': str(year), 'jazoest': self.jazoest}
        time.sleep(random.uniform(2, 4))
        try:
            return self.session.post(
                'https://www.instagram.com/api/v1/web/consent/check_age_eligibility/',
                headers=self.base_headers, data=data, timeout=30
            )
        except Exception:
            return None

    def send_verification_email(self, email):
        log(f"{yellow}[*] Gửi mã email đến {email}...{reset}")
        data = {'device_id': self.client_id, 'email': email, 'jazoest': self.jazoest}
        try:
            r = self.session.post(
                'https://www.instagram.com/api/v1/accounts/send_verify_email/',
                headers=self.base_headers, data=data, timeout=30
            )
            if r.status_code == 200:
                try:
                    result = r.json()
                    if result.get('email_sent') == True or result.get('status') == 'ok':
                        log(f"{green}[+] Email sent OK{reset}")
                        return True
                except Exception: return True
            log(f"{red}[!] Send email fail: {r.status_code}{reset}")
            return False
        except Exception as e:
            log(f"{red}[!] Lỗi gửi email: {e}{reset}")
            return False

    def wait_for_verification_code(self, email, timeout=180):
        log(f"{yellow}[*] Chờ OTP từ {email}...{reset}")
        email_info = None
        for info in self.emails_pool:
            if info['email'] == email:
                email_info = info; break
        if not email_info:
            log(f"{red}[!] Không có info email{reset}")
            return None
        start = time.time()
        while time.time() - start < timeout:
            try:
                messages = self.email_generator.get_all_messages(email_info)
                for message in messages:
                    msg_id = message.get('id', '')
                    key = f"{email}_{msg_id}"
                    if key in self.displayed_message_ids: continue
                    self.displayed_message_ids.add(key)
                    sender = message.get('from', {}).get('address', '')
                    subject = message.get('subject', '')
                    if self.is_instagram_message(sender, subject):
                        content = message.get('full_content', '')
                        if content:
                            code = self.extract_verification_code(content)
                            if code:
                                log(f"{green}[+] OTP: {code}{reset}")
                                return code
                time.sleep(3)
            except Exception as e:
                log(f"{red}[!] Lỗi check mail: {e}{reset}")
                time.sleep(3)
        log(f"{red}[!] Timeout chờ OTP{reset}")
        return None

    def extract_verification_code(self, content):
        if not content: return None
        patterns = [r'\b(\d{6})\b', r'\b(\d{8})\b', r'code[:\s]*[#]?(\d{6})',
                    r'mã[:\s]*[#]?(\d{6})', r'is[:\s]*(\d{6})\b',
                    r'【(\d{6})】', r'\[(\d{6})\]']
        for p in patterns:
            m = re.findall(p, content, re.IGNORECASE)
            if m: return m[0]
        all_nums = re.findall(r'\b\d{4,8}\b', content)
        for n in all_nums:
            if len(n) == 6: return n
        return None

    def is_instagram_message(self, sender, subject):
        indicators = ['instagram', 'no-reply@mail.instagram.com', 'confirmation', 'verify', 'verification', 'code', 'mã']
        s = (sender + ' ' + subject).lower()
        return any(k in s for k in indicators)

    def check_confirmation_code(self, email, code):
        data = {'code': code, 'device_id': self.client_id, 'email': email, 'jazoest': self.jazoest}
        headers = self.base_headers.copy()
        headers['x-csrftoken'] = self.session.cookies.get('csrftoken', '')
        time.sleep(random.uniform(2, 3))
        try:
            return self.session.post(
                'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
                headers=headers, data=data, timeout=30
            )
        except Exception:
            return None

    def complete_signup(self, email, first_name, username, password, code):
        log(f"{yellow}[4/4] Hoàn tất đăng ký...{reset}")
        enc_password = self.generate_enc_password(password)
        day, month, year = self.generate_random_date()
        data = {
            'enc_password': enc_password, 'day': str(day), 'email': email,
            'failed_birthday_year_count': '{}', 'first_name': first_name,
            'month': str(month), 'username': username, 'year': str(year),
            'client_id': self.client_id, 'seamless_login_enabled': '1',
            'tos_version': 'row', 'force_sign_up_code': code,
            'extra_session_id': self.web_session_id, 'jazoest': self.jazoest,
        }
        headers = self.base_headers.copy()
        headers['x-csrftoken'] = self.session.cookies.get('csrftoken', '')
        self.wait_human(3, 6)
        try:
            r = self.session.post(
                'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
                headers=headers, data=data, timeout=30
            )
            if r.status_code == 200:
                try:
                    result = r.json()
                    if result.get('account_created') == True or result.get('user_id') is not None:
                        log(f"{green}[+] REG THÀNH CÔNG!{reset}")
                        return True, result
                    if 'errors' in result:
                        log(f"{red}[!] Lỗi: {str(result['errors'])[:200]}{reset}")
                    return False, result
                except Exception as e:
                    log(f"{red}[!] Parse JSON lỗi: {e}{reset}")
                    return False, {}
            log(f"{red}[!] HTTP {r.status_code}{reset}")
            return False, {}
        except Exception as e:
            log(f"{red}[!] Lỗi complete: {e}{reset}")
            return False, {}

    def check_and_complete_signup(self, email, first_name, username, password, code):
        log(f"{yellow}[*] Check code...{reset}")
        r_check = self.check_confirmation_code(email, code)
        if not r_check:
            return False
        if r_check.status_code == 200:
            try:
                result = r_check.json()
                if (result.get('status') == 'ok' or result.get('signup_code_valid') == True or
                        result.get('confirmed') == True or 'signup_code' in result):
                    log(f"{green}[+] Code hợp lệ!{reset}")
                    signup_code = result.get('signup_code', code)
                    success, final = self.complete_signup(email, first_name, username, password, signup_code)
                    if success:
                        post_ok = self.perform_post_registration_actions(username)
                        if post_ok:
                            self.account_counter += 1
                            cookie_str = self.get_cookie_string()
                            twofa_secret = self.get_2fa_secret()
                            self.save_result(username, password, twofa_secret, cookie_str,
                                             first_name, email, self.current_proxy_str)
                            return True
                        else:
                            log(f"{red}[!] Nick bị khoá sau reg{reset}")
                            return False
                    return False
                else:
                    log(f"{red}[!] Code sai: {result}{reset}")
                    return False
            except Exception as e:
                log(f"{red}[!] Lỗi check: {e}{reset}")
                return False
        log(f"{red}[!] Check code fail: {r_check.status_code}{reset}")
        return False

    def get_cookie_string(self):
        try:
            cookies_dict = self.session.cookies.get_dict()
            important = ['csrftoken', 'sessionid', 'ds_user_id', 'ig_did', 'mid', 'datr']
            parts = [f"{k}={cookies_dict[k]}" for k in important if k in cookies_dict]
            return '; '.join(parts)
        except Exception:
            return ""

    def get_2fa_secret(self):
        try:
            log(f"{yellow}[*] Lấy 2FA secret...{reset}")
            headers = self.base_headers.copy()
            headers['x-csrftoken'] = self.session.cookies.get('csrftoken', '')
            headers['x-ig-app-id'] = '936619743392459'
            r = self.session.get('https://www.instagram.com/api/v1/accounts/two_factor/seed/', headers=headers, timeout=20)
            if r.status_code == 200:
                data = r.json()
                secret = data.get('totp_seed') or data.get('secret') or ""
                if secret:
                    log(f"{green}[+] 2FA: {secret}{reset}")
                    return secret
            return ""
        except Exception:
            return ""

    def save_result(self, username, password, twofa_secret, cookie_str, first_name, email, proxy_str):
        """Lưu kết quả vào file reg_results.txt — format: username|password|2fa|cookie"""
        try:
            line = f"{username}|{password}|{twofa_secret}|{cookie_str}"
            with open(RESULTS_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
            # Lưu thêm info phụ vào file riêng
            with open("reg_details.txt", "a", encoding="utf-8") as f:
                f.write(f"=== {username} ===\n")
                f.write(f"Password: {password}\n")
                f.write(f"2FA Secret: {twofa_secret}\n")
                f.write(f"Cookie: {cookie_str}\n")
                f.write(f"Name: {first_name}\n")
                f.write(f"Email: {email}\n")
                f.write(f"Proxy: {proxy_str}\n")
                f.write(f"Device: {self.current_device_data.platform.upper()} - {self.current_device_data.device.get('model', self.current_device_data.device.get('device'))}\n")
                f.write(f"Created: {datetime.now().isoformat()}\n")
                f.write("=" * 50 + "\n\n")
            log(f"{green}[+] Đã lưu: {username} → reg_results.txt{reset}")
        except Exception as e:
            log(f"{red}[!] Lỗi lưu file: {e}{reset}")

    def change_profile_picture(self, image_url=None):
        """Đổi avatar từ URL"""
        try:
            if not image_url:
                if not self.avatar_urls: return False
                image_url = random.choice(self.avatar_urls)
            log(f"{yellow}[*] Đổi avatar...{reset}")

            img_resp = requests.get(image_url, timeout=20)
            if img_resp.status_code != 200:
                log(f"{red}[!] Không tải được ảnh{reset}")
                return False
            image_data = img_resp.content
            ct = img_resp.headers.get('Content-Type', 'image/jpeg')
            ext = '.jpg'
            if 'png' in ct: ext = '.png'
            elif 'webp' in ct: ext = '.webp'

            boundary = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            form_data = (
                f'--{boundary}\r\n'
                f'Content-Disposition: form-data; name="profile_pic"; filename="profile_pic{ext}"\r\n'
                f'Content-Type: {ct}\r\n\r\n'
            ).encode() + image_data + f'\r\n--{boundary}--\r\n'.encode()

            headers = {
                'accept': '*/*',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/edit/',
                'user-agent': self.base_headers['user-agent'],
                'x-csrftoken': self.session.cookies.get('csrftoken', ''),
                'x-ig-app-id': '936619743392459',
                'content-type': f'multipart/form-data; boundary={boundary}',
                'content-length': str(len(form_data)),
            }
            r = self.session.post(
                'https://www.instagram.com/api/v1/web/accounts/web_change_profile_picture/',
                data=form_data, headers=headers, timeout=30
            )
            if r.status_code == 200:
                try:
                    if r.json().get('status') == 'ok':
                        log(f"{green}[+] Avatar OK{reset}")
                        return True
                except Exception:
                    if 'ok' in r.text.lower():
                        log(f"{green}[+] Avatar OK{reset}")
                        return True
            log(f"{red}[!] Avatar fail: {r.status_code}{reset}")
            return False
        except Exception as e:
            log(f"{red}[!] Lỗi avatar: {e}{reset}")
            return False

    def update_bio(self, bio):
        try:
            headers = {
                'accept': '*/*',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/edit/',
                'user-agent': self.base_headers['user-agent'],
                'x-csrftoken': self.session.cookies.get('csrftoken', ''),
                'x-ig-app-id': '936619743392459',
                'content-type': 'application/x-www-form-urlencoded',
            }
            r = self.session.post(
                'https://www.instagram.com/api/v1/web/accounts/edit_profile/',
                data={'biography': bio, 'external_url': '', 'chaining_enabled': 'on'},
                headers=headers, timeout=30
            )
            return r.status_code == 200
        except Exception:
            return False

    def generate_random_bio(self):
        bios = [
            "Sống để học hỏi và sẻ chia.",
            "Photography is my passion 📸",
            "Loving life in Vietnam 🇻🇳",
            "Đơn giản là tôi.",
            "Keep it real 💯",
            "Traveler | Foodie | Dreamer",
            "Work hard, play hard.",
            "Always be yourself.",
            "Khám phá thế giới qua ống kính.",
            "Vietnamese developer 👨‍💻"
        ]
        return random.choice(bios)

    def follow_user(self, target_username="instagram"):
        try:
            log(f"{yellow}[*] Follow @{target_username}...{reset}")
            headers = {
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.instagram.com',
                'referer': f'https://www.instagram.com/{target_username}/',
                'user-agent': self.base_headers['user-agent'],
                'x-csrftoken': self.session.cookies.get('csrftoken', ''),
                'x-ig-app-id': '936619743392459',
            }
            profile_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target_username}"
            pr = self.session.get(profile_url, headers=headers, timeout=30)
            user_id = None
            if pr.status_code == 200:
                try:
                    user_id = pr.json().get('data', {}).get('user', {}).get('id')
                except Exception: pass
            if not user_id:
                known = {"instagram": "25025320", "cristiano": "173560420", "leomessi": "427553890",
                         "natgeo": "787132", "therock": "232192182", "kyliejenner": "12281817"}
                user_id = known.get(target_username)
                if not user_id: return False
            data = {'container_module': 'profile', 'user_id': user_id, 'radio_type': 'wifi-none'}
            r = self.session.post(f'https://www.instagram.com/api/v1/friendships/create/{user_id}/',
                                  data=data, headers=headers, timeout=30)
            if r.status_code == 200:
                try:
                    result = r.json()
                    if 'checkpoint_required' in str(result) and 'suspended' in str(result):
                        log(f"{red}[!] Nick bị checkpoint{reset}")
                        return False
                    if result.get('status') == 'ok' or result.get('friendship_status', {}).get('following') == True:
                        log(f"{green}[+] Follow OK{reset}")
                        return True
                    return True
                except Exception: return True
            return True
        except Exception as e:
            log(f"{red}[!] Follow lỗi: {e}{reset}")
            return True

    def view_popular_profiles(self):
        popular = ["instagram", "cristiano", "leomessi", "selenagomez", "kyliejenner", "natgeo"]
        targets = random.sample(popular, random.randint(2, 3))
        for target in targets:
            try:
                self.session.get(f'https://www.instagram.com/{target}/', timeout=30)
                self.wait_human(3, 7)
            except Exception: pass

    def is_account_suspended(self, username=None):
        try:
            url = f'https://www.instagram.com/{username}/' if username else 'https://www.instagram.com/'
            r = self.session.get(url, timeout=30)
            if 'suspended' in r.url.lower() or 'challenge' in r.url.lower() or 'checkpoint' in r.url.lower():
                return True
            lower = r.text.lower()
            if any(kw in lower for kw in ['suspended', 'tài khoản của bạn đã bị khoá', 'checkpoint']):
                return True
            return False
        except Exception:
            return False

    def warmup_account(self, username):
        """Warm-up nhẹ nhàng — giống tool gốc"""
        log(f"{yellow}[+] Warm-up nick {username}...{reset}")
        time.sleep(5)
        if self.is_account_suspended(): return False

        # Xem feed
        try:
            self.session.get('https://www.instagram.com/', timeout=30)
            self.wait_human(4, 8)
            self.view_popular_profiles()
        except Exception: pass

        # Random hoá actions
        actions = []
        if random.random() < 0.7:
            actions.append(('bio', self.generate_random_bio()))
        if random.random() < 0.5:
            actions.append(('follow', random.choice(["instagram", "cristiano", "natgeo"])))
        if self.avatar_urls:
            actions.append(('avatar', None))

        random.shuffle(actions)
        for act_type, act_val in actions:
            if act_type == 'bio':
                self.update_bio(act_val)
                self.wait_human(5, 12)
            elif act_type == 'follow':
                self.follow_user(act_val)
                self.wait_human(8, 15)
            elif act_type == 'avatar':
                self.change_profile_picture()
                self.wait_human(8, 18)
            if self.is_account_suspended(): return False

        log(f"{green}[+] Warm-up OK{reset}")
        return True

    def perform_post_registration_actions(self, username):
        return self.warmup_account(username)

    def create_single_account(self, num, total, password, nickname_idx):
        log(f"\n{cyan}===== TÀI KHOẢN {num}/{total} ====={reset}")
        self.create_new_session(idx=nickname_idx)
        if not self.get_initial_cookies_and_csrf():
            log(f"{red}[!] Session init fail{reset}")
            return False

        # Lấy email
        if self.current_email_index >= len(self.emails_pool) * 2:
            email_info = self.email_generator.create_random_email()
            if not email_info:
                log(f"{red}[!] Không tạo được email{reset}")
                return False
            self.emails_pool.append(email_info)
        else:
            idx = self.current_email_index // 2
            email_info = self.emails_pool[idx]
        self.current_email_index += 1
        email = email_info['email']

        first_name = self.generate_vietnamese_name()
        username = self.generate_username(first_name)
        log(f"{cyan}    Mail: {email}{reset}")
        log(f"{cyan}    Username: {username}{reset}")
        log(f"{cyan}    Name: {first_name}{reset}")

        # 1. Attempt signup
        log(f"{yellow}[1/4] Gửi thông tin TK...{reset}")
        r1 = self.attempt_signup(email, first_name, username, password)
        if not r1:
            log(f"{red}[!] Không kết nối{reset}")
            return False
        log(f"{cyan}    Status: {r1.status_code}{reset}")
        if r1.status_code == 429:
            log(f"{red}[!] Spam detect, chờ 30s{reset}")
            time.sleep(30)
            return False
        if r1.status_code != 200:
            return False

        # Retry username if trùng
        try:
            result = r1.json()
            if 'errors' in result and 'username' in str(result['errors']).lower():
                log(f"{yellow}    Username trùng, thử lại{reset}")
                username = self.generate_username(first_name)
                r1 = self.attempt_signup(email, first_name, username, password)
                if not r1 or r1.status_code != 200: return False
        except Exception: pass

        # 2. Check age
        log(f"{yellow}[2/4] Check tuổi...{reset}")
        r2 = self.check_age_eligibility()
        if r2 and r2.status_code == 200:
            log(f"{green}    OK{reset}")

        # 3. Gửi email verify
        if not self.send_verification_email(email):
            log(f"{red}[!] Không gửi được email{reset}")
            return False

        # 4. Chờ OTP
        log(f"{yellow}[3/4] Chờ OTP...{reset}")
        code = self.wait_for_verification_code(email)
        if not code:
            log(f"{red}[!] Không nhận OTP, thử SMS-Man...{reset}")
            if self.sms_man_token:
                sms_data = self.sms_man_request()
                if sms_data:
                    req_id = sms_data["request_id"]
                    log(f"{green}[+] Đã mua số, chờ OTP qua SMS...{reset}")
                    sms_code = self.sms_man_get_code(req_id, timeout=180)
                    if sms_code:
                        code = sms_code
                        self.sms_man_set_status(req_id, "used")
                    else:
                        self.sms_man_set_status(req_id, "reject")
            if not code:
                log(f"{red}[!] Không lấy được code{reset}")
                return False

        # 5. Complete
        log(f"{yellow}[4/4] Hoàn tất đăng ký...{reset}")
        success = self.check_and_complete_signup(email, first_name, username, password, code)
        if success:
            return True
        return False

    def run(self):
        num_instagram = int(self.config.get("count", 1))
        password = self.config.get("password_pattern", "Pass{rand}!").replace(
            "{rand}", ''.join(random.choices(string.ascii_letters + string.digits, k=6)))

        log(f"{cyan}[*] Sẽ reg {num_instagram} nick | Password: {password}{reset}")

        num_emails = (num_instagram + 1) // 2
        log(f"{yellow}[*] Cần tạo {num_emails} email...{reset}")

        for i in range(num_emails):
            info = self.email_generator.create_random_email()
            if info:
                self.emails_pool.append(info)
            time.sleep(3)

        if not self.emails_pool:
            log(f"{red}[!] Không tạo được email, dừng{reset}")
            return

        log(f"{green}[+] Đã tạo {len(self.emails_pool)} email{reset}")

        successful = 0
        max_acc = min(num_instagram, len(self.emails_pool) * 2)

        for i in range(max_acc):
            try:
                if self.create_single_account(i + 1, max_acc, password, nickname_idx=i):
                    successful += 1
                    log(f"{green}[# {i+1}] ✅ THÀNH CÔNG ({successful}/{max_acc}){reset}")
                else:
                    log(f"{red}[# {i+1}] ❌ THẤT BẠI{reset}")
            except Exception as e:
                log(f"{red}[# {i+1}] LỖI: {e}{reset}")
            if i < max_acc - 1:
                time.sleep(random.uniform(3, 8))

        log(f"\n{cyan}===== KẾT QUẢ: {successful}/{max_acc} nick thành công ====={reset}")
        log(f"{yellow}[*] File kết quả: reg_results.txt (username|password|2fa|cookie){reset}")
        log(f"{yellow}[*] File chi tiết: reg_details.txt{reset}")


def main():
    log(f"{cyan}===== IG REG TOOL START ====={reset}")

    config = {}
    try:
        log("Nhận config từ web...")
        config_raw = input().strip()
        config = json.loads(config_raw) if config_raw else {}
    except Exception as e:
        log(f"{red}[!] Không nhận được config: {e}{reset}")
        config = {
            "avatar_urls": [], "proxies": [], "count": 1,
            "password_pattern": "Pass{rand}!", "sms_man_token": "",
            "country_id": "0", "app_id": "12",
        }

    log(f"{green}[+] Config:{reset}")
    log(f"    - Số nick: {config.get('count', 1)}")
    log(f"    - Số avatar: {len(config.get('avatar_urls', []))}")
    log(f"    - Số proxy: {len(config.get('proxies', []))}")
    log(f"    - SMS-Man: {'Có' if config.get('sms_man_token') else 'Không'}")

    try:
        tool = InstagramAutoRegister(config)
        tool.run()
    except KeyboardInterrupt:
        log(f"{red}[!] Đã dừng bởi user{reset}")
    except Exception as e:
        log(f"{red}[!] Lỗi không xác định: {e}{reset}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''

# ============================================================================
# ================== EMBEDDED TOOLS + FLASK ROUTES ===========================
# ============================================================================
EMBEDDED_TOOLS = {
    "igreg": {
        "name": "IG Reg Tool",
        "desc": "Reg Instagram hàng loạt — Web API + máy ảo + proxy cố định + SMS-Man",
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


@app.route('/api/download-results')
def download_results():
    path = os.path.join(TEMP_TOOLS_DIR, "reg_results.txt")
    if not os.path.exists(path):
        return "Chưa có file kết quả", 404
    return send_file(path, as_attachment=True, download_name="reg_results.txt")


@app.route('/api/download-details')
def download_details():
    path = os.path.join(TEMP_TOOLS_DIR, "reg_details.txt")
    if not os.path.exists(path):
        return "Chưa có file chi tiết", 404
    return send_file(path, as_attachment=True, download_name="reg_details.txt")


@app.route('/api/view-results')
def view_results():
    path = os.path.join(TEMP_TOOLS_DIR, "reg_results.txt")
    if not os.path.exists(path):
        return "Chưa có file kết quả"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"<pre style='color:#0f0;background:#000;padding:20px;font-size:13px'>{content}</pre>"
    except Exception as e:
        return f"Lỗi: {e}"


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
