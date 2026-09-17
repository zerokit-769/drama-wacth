import asyncio
import json
import os
import random
import sys
import time
import uuid
import hashlib
import aiohttp

PROGRESS_FILE = "selesai.json"
TOKEN_FILE = "token.json"
BATCH_SIZE = 10
COOLDOWN_SECONDS = 90 

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

def clear_screen():
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()

def print_main_banner():
    clear_screen()
    print(f"{C.MAGENTA}╭─────────────────────────────────────────────────────────╮{C.RESET}")
    print(f"{C.MAGENTA}│{C.BOLD}{C.CYAN}{'🎬 PURE AUTO WATCH & CLAIM v3.0':^57}{C.MAGENTA}│{C.RESET}")
    print(f"{C.MAGENTA}│{C.WHITE}{'⚡ ZeinthHub project - Algorithm Alchemist':^57}{C.MAGENTA}│{C.RESET}")
    print(f"{C.MAGENTA}╰─────────────────────────────────────────────────────────╯{C.RESET}\n")

def generate_random_ip():
    return f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return []
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(progress_data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress_data, f, indent=2)

def get_headers(cookie_token):
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-A217F Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36",
        "sec-ch-ua-platform": '"Android"',
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
        "sec-ch-ua-mobile": "?1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "X-Forwarded-For": generate_random_ip(),
        "Origin": "https://drama.center",
        "Referer": "https://drama.center/",
        "Cookie": cookie_token,
    }

async def process_account_tick(batch_id, session, account_data, all_progress, progress_lock, global_pause):
    token = account_data.get("token")
    if not token:
        return

    await global_pause.wait()
    headers = get_headers(token)

    # 1. CEK AUTENTIKASI (Apakah Cookie Valid?)
    auth_url = "https://drama.center/api/auth/me"
    try:
        async with session.get(auth_url, headers=headers, timeout=10) as auth_res:
            if auth_res.status != 200:
                print(f"{C.RED}❌ [Gagal Auth] HTTP {auth_res.status} - Cookie mungkin kedaluwarsa.{C.RESET}")
                return
            
            auth_json = await auth_res.json()
            if not auth_json.get("success"):
                print(f"{C.RED}❌ [Gagal Auth] Cookie tidak valid atau expired!{C.RESET}")
                return

            user_info = auth_json.get("user", {})
            account_id = user_info.get("id")
            email = user_info.get("email")
            wallet = user_info.get("wallet_address")
            acc_label = wallet or email or account_id
            
            device_id = str(uuid.UUID(hashlib.md5(account_id.encode()).hexdigest()))
    except Exception as e:
        print(f"{C.RED}❌ [Network Error] Gagal terhubung ke auth server: {e}{C.RESET}")
        return

    async with progress_lock:
        if account_id not in all_progress:
            all_progress[account_id] = {}
        account_progress = all_progress[account_id]

    await global_pause.wait()

    # 2. AMBIL DAFTAR DRAMA
    try:
        dramas_api_url = "https://drama.center/api/dramas?sort=popular&limit=50&language=en"
        async with session.get(dramas_api_url, headers=headers, timeout=10) as res:
            res_json = await res.json()
            dramas_data = res_json.get("data", [])
    except Exception as e:
        print(f"{C.RED}❌ Gagal mengambil daftar drama: {e}{C.RESET}")
        return

    for drama in dramas_data:
        await global_pause.wait()
        drama_id = drama["id"]
        drama_title = drama.get("title", "Unknown Title")

        if account_progress.get(drama_id, {}).get("completed"):
            continue

        # 3. AMBIL EPISODE DRAMA
        episodes_url = f"https://drama.center/api/dramas/{drama_id}"
        try:
            async with session.get(episodes_url, headers=headers, timeout=10) as ep_res:
                ep_json = await ep_res.json()
                episodes = ep_json.get("data", {}).get("episodes", [])
        except Exception:
            continue

        if not episodes:
            continue

        total_episodes = len(episodes)
        last_saved_ep = account_progress.get(drama_id, {}).get("last_episode", 0)

        if last_saved_ep >= total_episodes:
            async with progress_lock:
                account_progress[drama_id]["completed"] = True
                save_progress(all_progress)
            continue

        ep_idx = last_saved_ep
        ep = episodes[ep_idx]
        ep_id = ep["id"]
        ep_number = ep_idx + 1

        # 4. TICK (NONTON) & CLAIM REWARD
        tick_url = f"https://drama.center/api/dramas/{drama_id}/episodes/watch-tick"
        payload = {"episodeId": ep_id, "deviceId": device_id}

        try:
            # Jeda sebentar sebelum tick layaknya orang nonton
            await asyncio.sleep(random.uniform(1.5, 3.5))

            async with session.post(tick_url, headers=headers, json=payload, timeout=15) as tick_res:
                if tick_res.status != 200:
                    raw_err = await tick_res.text()
                    print(f"{C.YELLOW}⚠️ [Batch {batch_id}] HTTP {tick_res.status} | Respon Server: {raw_err.strip()[:60]}{C.RESET}")
                    return # Stop sementara biar nggak spam error

                tick_json = await tick_res.json()
                tick_data = tick_json.get("data", {})
                
                # Tambahkan print debug kalau JSON formatnya aneh
                if not tick_data and not tick_json.get("success"):
                    print(f"{C.YELLOW}⚠️ Respon Server Aneh: {tick_json}{C.RESET}")

                credited = tick_data.get("credited", 0)
                reject_reason = tick_data.get("rejectReason")

                if credited > 0:
                    collect_url = "https://drama.center/api/watch-reward/collect"
                    async with session.post(collect_url, headers=headers, json={}, timeout=10) as collect_res:
                        collect_json = await collect_res.json()
                        collect_data = collect_json.get("data", {})

                        print(f"{C.CYAN}[{acc_label[:8]}..] {C.GREEN}✅ Nonton '{drama_title[:10]}..' Ep {ep_number}/{total_episodes} | Koin Masuk: +{credited} | Total: {collect_data.get('totalToday', '?')}{C.RESET}")

                    async with progress_lock:
                        account_progress[drama_id] = {
                            "title": drama_title,
                            "last_episode": ep_number,
                            "total_episodes": total_episodes,
                            "completed": (ep_number == total_episodes),
                        }
                        all_progress[account_id] = account_progress
                        save_progress(all_progress)

                elif reject_reason == "episode_maxed":
                    print(f"{C.BLUE}⏩ Skip '{drama_title[:10]}..' Ep {ep_number} (Maxed/Sudah Ditonton){C.RESET}")
                    async with progress_lock:
                        account_progress[drama_id] = {
                            "title": drama_title, "last_episode": ep_number,
                            "total_episodes": total_episodes, "completed": (ep_number == total_episodes),
                        }
                        all_progress[account_id] = account_progress
                        save_progress(all_progress)

                elif reject_reason == "ip_daily_cap":
                    print(f"{C.RED}⛔ IP Limit Detected! Harap Ganti IP (Mode Pesawat){C.RESET}")
                    return

                else:
                    # Ini untuk menangkap kalau dia ditolak tapi bukan karena maxed/ip
                    print(f"{C.YELLOW}⚠️ '{drama_title[:10]}..' Ep {ep_number} Ditolak server. Alasan: {reject_reason or 'Terlalu Cepat/Tanpa Alasan'}{C.RESET}")
                    return

        except Exception as e:
            print(f"{C.RED}❌ Error saat proses tick: {e}{C.RESET}")
            return

async def batch_worker(batch_id, batch_accounts, session, all_progress, progress_lock, global_pause):
    while True:
        await global_pause.wait()
        start_time = time.time()
        
        print(f"{C.MAGENTA}🚀 Memulai siklus pengecekan & claim reward...{C.RESET}")

        tasks = [
            process_account_tick(batch_id, session, acc, all_progress, progress_lock, global_pause)
            for acc in batch_accounts
        ]
        await asyncio.gather(*tasks)

        elapsed = time.time() - start_time
        sleep_needed = max(0, COOLDOWN_SECONDS - elapsed)

        print(f"{C.GREEN}✔️  Siklus selesai. Menunggu jeda agar tidak terdeteksi spam ({round(sleep_needed)} detik)...{C.RESET}")

        for _ in range(int(sleep_needed)):
            await asyncio.sleep(1)

async def main():
    print_main_banner()

    accounts = load_tokens()
    if len(accounts) == 0:
        print(f"{C.RED}{C.BOLD}❌ File token.json kosong atau tidak ditemukan!{C.RESET}")
        print(f"{C.YELLOW}Silakan buat file token.json terlebih dahulu dan isi dengan cookie kamu.{C.RESET}")
        sys.exit(1)

    print(f"{C.GREEN}✅ Berhasil membaca data dari 'token.json'{C.RESET}\n")

    batches = [accounts[i : i + BATCH_SIZE] for i in range(0, len(accounts), BATCH_SIZE)]
    all_progress = load_progress()

    progress_lock = asyncio.Lock()
    global_pause = asyncio.Event()
    global_pause.set()

    async with aiohttp.ClientSession() as session:
        workers = [
            asyncio.create_task(batch_worker(batch_idx, batch_accs, session, all_progress, progress_lock, global_pause))
            for batch_idx, batch_accs in enumerate(batches, start=1)
        ]
        await asyncio.wait(workers)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}⚠️  Program dihentikan oleh pengguna. Progress tersimpan!{C.RESET}")
        sys.exit(0)
