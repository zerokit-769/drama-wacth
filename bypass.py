import asyncio
import json
import os
import random
import sys
import time
import hashlib
import aiohttp

# Konfigurasi CapSolver kamu
CAPSOLVER_API_KEY = "CAP-3B72E23C185A98B0AE56F5A4A489BF4C7CBBB562DE30ED7CF34495098B5D650E"
TARGET_WEBSITE_URL = "https://drama.center"
# Sitekey Turnstile drama.center (pastikan diisi jika berubah, ambil dari halaman web target)
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

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

async def solve_turnstile_with_capsolver():
    """Fungsi otomatis untuk meminta token captcha ke CapSolver"""
    print(f"{C.YELLOW}[⏳] Mengirim tugas bypass Turnstile ke CapSolver...{C.RESET}")
    
    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteURL": TARGET_WEBSITE_URL,
            "websiteKey": TURNSTILE_SITEKEY
        }
    }

    async with aiohttp.ClientSession() as session:
        try:
            # 1. Buat task ke capsolver
            async with session.post("https://api.capsolver.com/createTask", json=payload, timeout=30) as res:
                res_json = await res.json()
                if res_json.get("errorId") != 0:
                    print(f"{C.RED}[-] Gagal membuat task CapSolver: {res_json.get('errorDescription')}{C.RESET}")
                    return None
                
                task_id = res_json.get("taskId")

            # 2. Ambil hasilnya (polling)
            get_result_payload = {
                "clientKey": CAPSOLVER_API_KEY,
                "taskId": task_id
            }

            for _ in range(15): # Coba tunggu hingga 45 detik
                await asyncio.sleep(3)
                async with session.post("https://api.capsolver.com/getTaskResult", json=get_result_payload, timeout=30) as r_res:
                    r_json = await r_res.json()
                    status = r_json.get("status")
                    
                    if status == "ready":
                        token = r_json.get("solution", {}).get("token")
                        print(f"{C.GREEN}[+] Sukses! Token Captcha berhasil didapatkan.{C.RESET}")
                        return token
                    elif status == "failed":
                        print(f"{C.RED}[-] Gagal solve captcha oleh CapSolver.{C.RESET}")
                        return None
        except Exception as e:
            print(f"{C.RED}[-] Error koneksi ke CapSolver: {e}{C.RESET}")
            
    return None

async def main():
    print(f"{C.CYAN}=== DRAMA CENTER AUTOMATED TOKEN GENERATOR (CAPSOLVER) ==={C.RESET}")
    
    accounts = load_json(BNB_FILE)
    if not accounts:
        print(f"{C.RED}[-] File {BNB_FILE} tidak ditemukan atau kosong! Generate wallet EVM-mu dulu.{C.RESET}")
        return

    # Dapatkan token captcha valid menggunakan CapSolver sebelum login
    captcha_token = await solve_turnstile_with_capsolver()
    if not captcha_token:
        print(f"{C.RED}[-] Proses dihentikan karena gagal mendapatkan token captcha.{C.RESET}")
        return

    print(f"\n{C.GREEN}[+] Token Captcha siap digunakan. Melanjutkan proses login akun...{C.RESET}")
    
    # Contoh implementasi token disisipkan ke header / payload Supabase auth
    existing_tokens = load_json(TOKEN_FILE)
    token_map = {item.get("user_id"): item for item in existing_tokens if item.get("user_id")}

    TARGET_URL = "https://tagxhipylkobyguviedc.supabase.co/auth/v1/token?grant_type=web3"

    for i, acc in enumerate(accounts):
        private_key = acc.get("privateKey")
        if not private_key:
            continue

        # Proses sign message EVM wallet kamu bisa disisipkan di sini
        # (Menggunakan logika web3/ethers seperti skrip sebelumnya)
        print(f"{C.YELLOW}⏳ Memproses akun ke-{i+1} dengan captcha_token valid...{C.RESET}")
        
        # Simulasi payload login yang menyertakan captcha_token agar lolos
        # payload = { "chain": "ethereum", "message": ..., "signature": ..., "captchaToken": captcha_token }

    print(f"\n{C.GREEN}[✔] Selesai! Silakan sesuaikan eksekusi payload login menggunakan token di atas.{C.RESET}")

if __name__ == "__main__":
    asyncio.run(main())
