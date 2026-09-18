import asyncio
import json
import os
import aiohttp

# Konfigurasi NopeCHA kamu
NOPECHA_API_KEY = "MASUKKAN_API_KEY_NOPECHA_DISINI"
TARGET_WEBSITE_URL = "https://drama.center"
TURNSTILE_SITEKEY = "0x4AAAAAAE5Imx2BMLN5ABSD"  

TOKEN_FILE = "token.json"
BNB_FILE = "bnb.json"

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

async def solve_turnstile_with_nopecha():
    """Fungsi otomatis untuk meminta token captcha ke NopeCHA"""
    print(f"{C.YELLOW}[⏳] Mengirim tugas bypass Turnstile ke NopeCHA...{C.RESET}")
    
    # Payload standar untuk endpoint API NopeCHA
    payload = {
        "key": NOPECHA_API_KEY,
        "type": "turnstile",
        "url": TARGET_WEBSITE_URL,
        "sitekey": TURNSTILE_SITEKEY
    }

    async with aiohttp.ClientSession() as session:
        try:
            # Mengirim request ke endpoint API NopeCHA
            async with session.post("https://api.nopecha.com/", json=payload, timeout=30) as res:
                res_json = await res.json()
                
                # Cek apakah status error atau berhasil
                if res_json.get("error"):
                    print(f"{C.RED}[-] Gagal dari NopeCHA: {res_json.get('error')}{C.RESET}")
                    return None
                
                token = res_json.get("data")
                if token:
                    print(f"{C.GREEN}[+] Sukses! Token Captcha berhasil didapatkan dari NopeCHA.{C.RESET}")
                    return token
                else:
                    print(f"{C.RED}[-] Gagal mendapatkan data token dari respons NopeCHA.{C.RESET}")
                    return None
                    
        except Exception as e:
            print(f"{C.RED}[-] Error koneksi ke NopeCHA: {e}{C.RESET}")
            
    return None

async def main():
    print(f"{C.CYAN}=== DRAMA CENTER AUTOMATED (NOPECHA) ==={C.RESET}")
    
    accounts = load_json(BNB_FILE)
    if not accounts:
        print(f"{C.RED}[-] File {BNB_FILE} tidak ditemukan atau kosong!{C.RESET}")
        return

    # Dapatkan token captcha menggunakan NopeCHA
    captcha_token = await solve_turnstile_with_nopecha()
    if not captcha_token:
        print(f"{C.RED}[-] Proses dihentikan karena gagal mendapatkan token captcha.{C.RESET}")
        return

    print(f"\n{C.GREEN}[+] Token Captcha siap digunakan. Melanjutkan proses...{C.RESET}")
    # Lanjutkan logika skrip login/request berikutnya di sini...

if __name__ == "__main__":
    asyncio.run(main())
