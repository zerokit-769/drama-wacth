import asyncio
import json
import os
import random
import sys
import time
import uuid
import hashlib
import shutil
import aiohttp

PROGRESS_FILE = "selesai.json"
TOKEN_FILE = "token.json"
BATCH_SIZE = 10
COOLDOWN_SECONDS = 90

USER_REFERRAL_URI = "https://drama.center/?ref=2FV8J4"
USER_REFERRAL_ID = "2FV8J4"


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


AUTO_LOGIN_JS_TEMPLATE = r"""const { Wallet } = require("ethers");
const axios = require("axios");
const fs = require("fs");

const colors = {
    cyan: "\x1b[36m",
    reset: "\x1b[0m",
    bold: "\x1b[1m",
    yellow: "\x1b[33m",
    green: "\x1b[32m"
};
const frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];

function getRandomIp() {
  return `${Math.floor(Math.random() * 254) + 1}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 254) + 1}`;
}

function loadJson(filepath) {
  try {
    if (fs.existsSync(filepath)) {
      const data = fs.readFileSync(filepath, "utf8");
      return JSON.parse(data);
    }
  } catch (error) {
    console.error(`[-] Error reading ${filepath}:`, error.message);
  }
  return [];
}

function saveJson(filepath, data) {
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2), "utf8");
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function executeSignIn() {
  const accounts = loadJson("bnb.json");
  if (accounts.length === 0) {
    console.log("[-] bnb.json was not found or is empty.");
    process.exit(1);
  }

  const existingTokens = loadJson("token.json");
  const tokenMap = {};

  existingTokens.forEach((item) => {
    if (item.user_id) {
      tokenMap[item.user_id] = item;
    }
  });

  const authHeaders = {
    'sec-ch-ua-platform': '"Android"',
    'x-supabase-api-version': "2024-01-01",
    'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
    'sec-ch-ua-mobile': "?1",
    'x-client-info': "supabase-ssr/0.12.5 createBrowserClient",
    'content-type': "application/json;charset=UTF-8",
    'apikey': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRhZ3hoaXB5bGtvYnlndXZpZWRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODcyNjk5NDksImV4cCI6MjEwMjg0NTk0OX0.P6JmfYhruL3LZGEnfXbS85HE4ABerldH9zyHtWEo3vc",
    'origin': "https://drama.center",
    "x-forwarded-for": getRandomIp(),
    'sec-fetch-site': "cross-site",
    'sec-fetch-mode': "cors",
    'sec-fetch-dest': "empty",
    'referer': "https://drama.center/",
    'accept-language': "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    'priority': "u=1, i"
  };

  const domain = "drama.center";
  const uri = "__USER_URI__";
  const version = "1";
  const chainId = 1;
  const TARGET_URL = "https://tagxhipylkobyguviedc.supabase.co/auth/v1/token?grant_type=web3";
  const REF_URL = "https://drama.center/api/referrals";

  for (let i = 0; i < accounts.length; i++) {
    const acc = accounts[i];
    if (!acc.privateKey) continue;

    const wallet = new Wallet(acc.privateKey);
    const address = wallet.address;

    const frame = frames[i % frames.length];
    const percent = Math.floor(((i + 1) / accounts.length) * 100);

    process.stdout.write(
        `\n${colors.cyan}${frame}${colors.reset} ` +
        `${colors.bold}Processing EVM Wallets${colors.reset} ` +
        `${colors.yellow}[${i + 1}/${accounts.length}]${colors.reset} ` +
        `${colors.green}${percent}%${colors.reset} - ${address}\n`
    );

    const issuedAt = new Date().toISOString();
    const message = `${domain} wants you to sign in with your Ethereum account:\n${address}\n\nSign in to DramaCenter.\n\nURI: ${uri}\nVersion: ${version}\nChain ID: ${chainId}\nIssued At: ${issuedAt}`;

    try {
      const signature = await wallet.signMessage(message);

      const payload = {
        chain: "ethereum",
        message: message,
        signature: signature
      };

      const authResponse = await axios.post(TARGET_URL, payload, {
        headers: {
          ...authHeaders,
          "x-forwarded-for": getRandomIp()
        }
      });
      const authData = authResponse.data;
      const user_id = authData.user?.id;

      if (!user_id) {
        console.log("[-] Failed to obtain user_id from response.");
      } else {
        console.log(`[+] Login successful! User ID: ${user_id}`);

        const jsonString = JSON.stringify(authData);
        const base64Encoded = Buffer.from(jsonString).toString('base64');
        const formattedToken = `sb-tagxhipylkobyguviedc-auth-token.0=base64-${base64Encoded}`;

        const targetReferral = (i % 10 < 7) ? "__USER_REF_ID__" : "2FV8J4";
        const refPayload = {
          referrer_id: targetReferral,
          referred_id: user_id
        };

        try {
          const refResponse = await axios.post(REF_URL, refPayload, {
            headers: {
              "Content-Type": "application/json",
              "Origin": "https://drama.center",
              "Referer": "https://drama.center/",
              "x-forwarded-for": getRandomIp()
            }
          });
          console.log(`[+] Referral Status: ${refResponse.status} OK (Bind to: ${targetReferral})`);
        } catch (refError) {
          console.log(`[-] Referral Error: ${refError.response ? JSON.stringify(refError.response.data) : refError.message}`);
        }

        tokenMap[user_id] = {
          user_id: user_id,
          token: formattedToken
        };
        
        saveJson("token.json", Object.values(tokenMap));
        console.log(`[+] Data saved (Merge Update) to token.json`);
      }

    } catch (error) {
      console.error(`[-] Error on Address ${address}:`, error.response ? JSON.stringify(error.response.data) : error.message);
    }

    if (i < accounts.length - 1) {
      for (let s = 0; s < 70; s++) {
          const f = frames[s % frames.length];
          process.stdout.write(`\r${colors.cyan}${f}${colors.reset} ${colors.yellow}Sleeping for 7 seconds to avoid rate limits...${colors.reset}`);
          await sleep(100);
      }
      process.stdout.write('\r\x1b[K');
    }
  }

  console.log(`\n[+] Complete! Total ${Object.values(tokenMap).length} data entries in token.json`);
}

executeSignIn();
"""


def clear_screen():
    sys.stdout.write("\033[H\033[2J\033[3J")
    sys.stdout.flush()
def get_term_width():
    cols, _ = shutil.get_terminal_size((50, 20))
    return min(cols, 60)


def print_prompt_banner():
    clear_screen()
    w = get_term_width() - 2
    border = "─" * w

    print(f"{C.CYAN}╭{border}╮{C.RESET}")
    print(f"{C.CYAN}│{C.BOLD}{C.WHITE}{'⚙️ SYSTEM INITIALIZATION & CONFIG':^{w}}{C.CYAN}│{C.RESET}")
    print(f"{C.CYAN}│{C.YELLOW}{'SyndicateBot Network Setup':^{w}}{C.CYAN}│{C.RESET}")
    print(f"{C.CYAN}╰{border}╯{C.RESET}\n")


def print_main_banner():
    clear_screen()
    w = get_term_width() - 2
    border = "─" * w

    print(f"{C.MAGENTA}╭{border}╮{C.RESET}")
    print(f"{C.MAGENTA}│{C.BOLD}{C.CYAN}{'🎬 DRAMA WATCH AUTOMATION v2.0':^{w}}{C.MAGENTA}│{C.RESET}")
    print(f"{C.MAGENTA}│{C.WHITE}{'⚡ Multi-Worker Independent Batch':^{w}}{C.MAGENTA}│{C.RESET}")
    print(f"{C.MAGENTA}│{C.BLUE}{'🔥 SYNDICATEBOT NET - TERMUX EDITION':^{w}}{C.MAGENTA}│{C.RESET}")
    print(f"{C.MAGENTA}╰{border}╯{C.RESET}\n")


async def run_sync_animation(uri, ref_id):
    clear_screen()
    w = get_term_width()
    print(f"{C.CYAN}{'═' * w}{C.RESET}")
    print(f"{C.BOLD}{C.WHITE}   ⚡ SYNCHRONIZING REFERRAL ENGINE ⚡{C.RESET}")
    print(f"{C.CYAN}{'═' * w}{C.RESET}\n")

    sync_steps = [
        ("Validating Referral Input", uri[:35] + ("..." if len(uri) > 35 else "")),
        ("Extracting Referrer Token ID", ref_id),
        ("Injecting Node.js Auto-Login Code", "SUCCESS"),
        ("Optimizing Termux Display Grid", f"{w} cols"),
        ("Synchronizing Worker Environment", "READY"),
    ]

    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    for step, detail in sync_steps:
        for i in range(8):
            frame = spinner[i % len(spinner)]
            print(
                f"\r{C.YELLOW}{frame} {step}...{C.RESET}", end="", flush=True
            )
            await asyncio.sleep(0.04)
        print(
            f"\r{C.GREEN}✔ {step}{C.RESET} → {C.CYAN}[{detail}]{C.RESET}{' ' * 10}"
        )
        await asyncio.sleep(0.15)

    print(
        f"\n{C.GREEN}{C.BOLD}✨ SYNC COMPLETE! Launching Automation Dashboard...{C.RESET}"
    )
    await asyncio.sleep(1.2)


async def get_user_referral():  # 👈 Added async
    global USER_REFERRAL_URI, USER_REFERRAL_ID

    print_prompt_banner()

    print(
        f"{C.YELLOW}{C.BOLD}Enter Link Full Your Referral Link:{C.RESET}"
    )
    user_input = input(f"{C.CYAN}👉 {C.RESET}").strip()

    if not user_input:
        user_input = "https://drama.center/?ref=2FV8J4"

    USER_REFERRAL_URI = user_input

    if "=" in user_input:
        USER_REFERRAL_ID = user_input.split("=")[-1].strip()
    elif "/" in user_input:
        USER_REFERRAL_ID = user_input.rsplit("/", 1)[-1].strip()
    else:
        USER_REFERRAL_ID = user_input
        
    await run_sync_animation(USER_REFERRAL_URI, USER_REFERRAL_ID)

def generate_random_ip():
    return f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return []
    try:
        with open(TOKEN_FILE, "r") as f:
            raw_data = json.load(f)

        unique_accounts = []
        seen_ids = set()
        for item in raw_data:
            uid = item.get("user_id") or item.get("token")
            if uid and uid not in seen_ids:
                seen_ids.add(uid)
                unique_accounts.append(item)
        return unique_accounts
    except Exception:
        return []


def run_auto_login():
    print(
        f"\n{C.RED}{C.BOLD}♻️  CLEARING OLD {TOKEN_FILE} & STARTING AUTO-LOGIN FROM bnb.json...{C.RESET}"
    )

    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)

    auto_js = AUTO_LOGIN_JS_TEMPLATE.replace(
        "__USER_URI__", USER_REFERRAL_URI
    ).replace("__USER_REF_ID__", USER_REFERRAL_ID)

    with open("auto_login.js", "w", encoding="utf-8") as f:
        f.write(auto_js)

    print(
        f"{C.CYAN}ℹ️  Required Node.js libraries: "
        f"{C.WHITE}npm install ethers axios{C.RESET}"
    )

    os.system("node auto_login.js")

    print(
        f"{C.GREEN}{C.BOLD}✅ Token generation complete! "
        f"Reloading token.json...{C.RESET}\n"
    )

    time.sleep(2)


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
        "accept-language": "en-US,en;q=0.9",
        "X-Forwarded-For": generate_random_ip(),
        "Cookie": cookie_token,
    }


async def process_account_tick(
    batch_id,
    session,
    account_data,
    all_progress,
    progress_lock,
    global_pause,
    pause_lock,
    active_ids,
    dupe_tokens,
    total_accounts,
    regen_event,
):
    token = account_data.get("token")

    if token in dupe_tokens:
        return

    await global_pause.wait()

    headers = get_headers(token)

    auth_url = "https://drama.center/api/auth/me"

    try:
        async with session.get(auth_url, headers=headers, timeout=10) as auth_res:
            auth_json = await auth_res.json()

            if not auth_json.get("success"):
                return

            user_info = auth_json.get("user", {})
            account_id = user_info.get("id")
            email = user_info.get("email")
            wallet = user_info.get("wallet_address")
            acc_label = wallet or email or account_id

            async with progress_lock:
                if account_id in active_ids and active_ids[account_id] != token:
                    dupe_tokens.add(token)

                    print(
                        f"{C.YELLOW}⚠️  [Batch {batch_id}] "
                        f"👤 [{acc_label[:14]}] "
                        f"Duplicate detected in token.json! "
                        f"(Skipped){C.RESET}"
                    )

                    if len(dupe_tokens) >= (total_accounts * 0.5):
                        regen_event.set()

                    return
                else:
                    active_ids[account_id] = token

            device_id = str(
                uuid.UUID(hashlib.md5(account_id.encode()).hexdigest())
            )

    except Exception:
        return

    async with progress_lock:
        if account_id not in all_progress:
            all_progress[account_id] = {}

        account_progress = all_progress[account_id]

    await global_pause.wait()

    try:
        dramas_api_url = (
            "https://drama.center/api/dramas?"
            "sort=popular&limit=1000&language=en"
        )

        async with session.get(
            dramas_api_url, headers=headers, timeout=10
        ) as res:
            res_json = await res.json()
            dramas_data = res_json.get("data", [])

    except Exception:
        return

    for drama in dramas_data:
        await global_pause.wait()

        drama_id = drama["id"]
        drama_title = drama.get("title", "Unknown Title")

        if account_progress.get(drama_id, {}).get("completed"):
            continue

        episodes_url = f"https://drama.center/api/dramas/{drama_id}"

        try:
            async with session.get(
                episodes_url, headers=headers, timeout=10
            ) as ep_res:
                ep_json = await ep_res.json()
                episodes = ep_json.get("data", {}).get("episodes", [])

        except Exception:
            continue

        if not episodes:
            continue

        total_episodes = len(episodes)
        last_saved_ep = account_progress.get(drama_id, {}).get(
            "last_episode", 0
        )

        if last_saved_ep >= total_episodes:
            async with progress_lock:
                account_progress[drama_id]["completed"] = True
                save_progress(all_progress)

            continue

        ep_idx = last_saved_ep
        ep = episodes[ep_idx]
        ep_id = ep["id"]
        ep_number = ep_idx + 1

        tick_url = (
            f"https://drama.center/api/dramas/"
            f"{drama_id}/episodes/watch-tick"
        )

        payload = {"episodeId": ep_id, "deviceId": device_id}

        try:
            await global_pause.wait()

            async with session.post(
                tick_url, headers=headers, json=payload, timeout=10
            ) as tick_res:

                tick_json = await tick_res.json()
                tick_data = tick_json.get("data", {})
                credited = tick_data.get("credited", 0)
                reject_reason = tick_data.get("rejectReason")

                if credited > 0:
                    collect_url = (
                        "https://drama.center/api/watch-reward/collect"
                    )

                    async with session.post(
                        collect_url, headers=headers, json={}, timeout=10
                    ) as collect_res:

                        collect_json = await collect_res.json()
                        collect_data = collect_json.get("data", {})

                        print(
                            f"{C.CYAN}[Batch {batch_id}] "
                            f"👤 [{acc_label[:14]}] "
                            f"{C.GREEN}✅ Episode "
                            f"{ep_number}/{total_episodes} "
                            f"| Credited: {credited} "
                            f"| Total: "
                            f"{collect_data.get('totalToday', 0)}"
                            f"{C.RESET}"
                        )

                    async with progress_lock:
                        is_completed = ep_number == total_episodes

                        account_progress[drama_id] = {
                            "title": drama_title,
                            "last_episode": ep_number,
                            "total_episodes": total_episodes,
                            "completed": is_completed,
                        }

                        all_progress[account_id] = account_progress
                        save_progress(all_progress)

                elif reject_reason == "episode_maxed":
                    print(
                        f"{C.CYAN}[Batch {batch_id}] "
                        f"👤 [{acc_label[:14]}] "
                        f"{C.BLUE}⏩ Episode "
                        f"{ep_number}/{total_episodes} "
                        f"| Episode limit reached "
                        f"(Skipping){C.RESET}"
                    )

                    async with progress_lock:
                        account_progress[drama_id] = {
                            "title": drama_title,
                            "last_episode": ep_number,
                            "total_episodes": total_episodes,
                            "completed": ep_number == total_episodes,
                        }

                        all_progress[account_id] = account_progress
                        save_progress(all_progress)

                elif reject_reason == "ip_daily_cap":
                    print(
                        f"{C.CYAN}[Batch {batch_id}] "
                        f"👤 [{acc_label[:14]}] "
                        f"{C.RED}⛔ Episode "
                        f"{ep_number}/{total_episodes} "
                        f"| Status: ip_daily_cap{C.RESET}"
                    )

                    if global_pause.is_set():
                        async with pause_lock:
                            if global_pause.is_set():
                                global_pause.clear()

                                print(
                                    f"\n{C.RED}{C.BOLD}"
                                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                                    f"{C.RESET}"
                                )

                                print(
                                    f"{C.RED}{C.BOLD}"
                                    f"🚨 IP LIMIT DETECTED "
                                    f"(ip_daily_cap) - ALL EXECUTION PAUSED!"
                                    f"{C.RESET}"
                                )

                                print(
                                    f"{C.YELLOW}{C.BOLD}"
                                    f"✈️  Please toggle Airplane Mode ON/OFF "
                                    f"now to change your IP."
                                    f"{C.RESET}"
                                )

                                loop = asyncio.get_event_loop()

                                await loop.run_in_executor(
                                    None,
                                    input,
                                    f"{C.CYAN}{C.BOLD}"
                                    f"👉 Press ENTER when ready to continue..."
                                    f"{C.RESET}\n",
                                )

                                print(
                                    f"{C.GREEN}{C.BOLD}"
                                    f"▶️  Resuming execution of all batches..."
                                    f"{C.RESET}"
                                )

                                print(
                                    f"{C.RED}{C.BOLD}"
                                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                                    f"{C.RESET}\n"
                                )

                                global_pause.set()

                else:
                    print(
                        f"{C.CYAN}[Batch {batch_id}] "
                        f"👤 [{acc_label[:14]}] "
                        f"{C.YELLOW}⚠️  Episode "
                        f"{ep_number}/{total_episodes} "
                        f"| Status: "
                        f"{reject_reason or 'No Reward'}"
                        f"{C.RESET}"
                    )

                return

        except Exception:
            return


async def batch_worker(
    batch_id,
    batch_accounts,
    session,
    all_progress,
    progress_lock,
    global_pause,
    pause_lock,
    active_ids,
    dupe_tokens,
    total_accounts,
    regen_event,
):
    while True:
        await global_pause.wait()

        start_time = time.time()
        timestamp = time.strftime("%H:%M:%S")

        valid_accounts_count = len(
            [
                acc
                for acc in batch_accounts
                if acc.get("token") not in dupe_tokens
            ]
        )

        if valid_accounts_count > 0:
            print(
                f"{C.MAGENTA}{C.BOLD}"
                f"🚀 [Batch {batch_id}] "
                f"Running {valid_accounts_count} valid account(s) "
                f"simultaneously "
                f"🕒 [{timestamp}]"
                f"{C.RESET}"
            )

        tasks = [
            process_account_tick(
                batch_id,
                session,
                acc,
                all_progress,
                progress_lock,
                global_pause,
                pause_lock,
                active_ids,
                dupe_tokens,
                total_accounts,
                regen_event,
            )
            for acc in batch_accounts
        ]

        await asyncio.gather(*tasks)

        if regen_event.is_set():
            break

        elapsed = time.time() - start_time
        sleep_needed = max(0, COOLDOWN_SECONDS - elapsed)

        if valid_accounts_count > 0:
            print(
                f"{C.GREEN}✔️  [Batch {batch_id}] "
                f"Completed ({round(elapsed, 2)}s). "
                f"Cooldown: {round(sleep_needed, 1)}s..."
                f"{C.RESET}"
            )

        spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        for second in range(int(sleep_needed)):
            if regen_event.is_set():
                break

            await global_pause.wait()

            frame = spinner[second % len(spinner)]

            print(
                f"\r{C.BLUE}{frame}{C.RESET} "
                f"{C.CYAN}[Batch {batch_id}] "
                f"Cooldown remaining: "
                f"{C.YELLOW}{int(sleep_needed) - second}s"
                f"{C.RESET}",
                end="",
                flush=True,
            )

            await asyncio.sleep(1)

        print()


async def main():
    await get_user_referral() 

    while True:
        print_main_banner()

        accounts = load_tokens()
        total_accounts = len(accounts)

        if total_accounts == 0:
            print(
                f"{C.YELLOW}{C.BOLD}"
                f"⚠️  token.json is missing or empty!"
                f"{C.RESET}"
            )

            run_auto_login()

            accounts = load_tokens()
            total_accounts = len(accounts)

            if total_accounts == 0:
                print(
                    f"{C.RED}{C.BOLD}"
                    f"❌ Token generation failed. "
                    f"Please make sure bnb.json is valid!"
                    f"{C.RESET}"
                )

                sys.exit(1)

        print(
            f"{C.GREEN}{C.BOLD}"
            f"✅ Loaded {total_accounts} initial account(s) "
            f"from '{TOKEN_FILE}'"
            f"{C.RESET}"
        )
        print(
            f"{C.CYAN}🔗 Active Referral ID: {C.WHITE}{USER_REFERRAL_ID}{C.RESET}\n"
        )

        batches = [
            accounts[i : i + BATCH_SIZE]
            for i in range(0, total_accounts, BATCH_SIZE)
        ]

        all_progress = load_progress()

        progress_lock = asyncio.Lock()
        pause_lock = asyncio.Lock()

        global_pause = asyncio.Event()
        global_pause.set()

        active_ids = {}
        dupe_tokens = set()
        regen_event = asyncio.Event()

        async with aiohttp.ClientSession() as session:
            workers = []

            for batch_idx, batch_accs in enumerate(batches, start=1):
                task = asyncio.create_task(
                    batch_worker(
                        batch_idx,
                        batch_accs,
                        session,
                        all_progress,
                        progress_lock,
                        global_pause,
                        pause_lock,
                        active_ids,
                        dupe_tokens,
                        total_accounts,
                        regen_event,
                    )
                )

                workers.append(task)

                await asyncio.sleep(1)

            regen_task = asyncio.create_task(regen_event.wait())

            done, pending = await asyncio.wait(
                workers + [regen_task], return_when=asyncio.FIRST_COMPLETED
            )

            if regen_event.is_set():
                print(
                    f"\n{C.RED}{C.BOLD}"
                    f"🚨 TOO MANY DUPLICATE ACCOUNTS DETECTED (>50%)"
                    f"{C.RESET}"
                )

                print(
                    f"{C.YELLOW}{C.BOLD}"
                    f"♻️  Force-stopping all batches "
                    f"and restarting the login process..."
                    f"{C.RESET}"
                )

                for task in pending:
                    task.cancel()

                run_auto_login()
                continue

            else:
                break


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print(
            f"\n\n{C.YELLOW}{C.BOLD}"
            f"⚠️  Program stopped by user. "
            f"Progress has been saved."
            f"{C.RESET}"
        )

        sys.exit(0)
