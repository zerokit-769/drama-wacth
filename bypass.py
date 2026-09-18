import asyncio
from playwright.async_api import async_playwright

# === KONFIGURASI PROXY (UBAH DI SINI) ===
# Ganti dengan alamat proxy kamu, format: http://host:port
PROXY_SERVER = "http://80.208.225.245:7001
# =======================================

TARGET_URL = "https://drama.center"
SITEKEY = "0x4AAAAAAE5Imx2BMLN5ABSD"

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

async def get_turnstile_token():
    print(f"{C.CYAN}[*] Menjalankan browser otomatis (Visual Mode + Proxy)...{C.RESET}")
    print(f"{C.YELLOW}[!] Menggunakan proxy: {PROXY_SERVER.split('@')[-1]}{C.RESET}")
    
    async with async_playwright() as p:
        # Konfigurasi browser agar berjalan visual dan menggunakan proxy
        browser = await p.chromium.launch(
            headless=False,
            proxy={"server": PROXY_SERVER},
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # JUBANG GAIB: Sembunyikan status 'webdriver'
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print(f"{C.YELLOW}[*] Membuka {TARGET_URL} (Tunggu, mungkin lambat karena proxy)...{C.RESET}")
        try:
            # Tambahkan timeout agar tidak menunggu selamanya jika proxy mati
            await page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"{C.RED}[-] Gagal memuat halaman (Proxy mati/timeout): {e}{C.RESET}")
            await browser.close()
            return None

        print(f"{C.YELLOW}[*] Menyuntikkan Widget Turnstile...{C.RESET}")
        await page.evaluate(f"""
            (() => {{
                if (document.getElementById('_ts')) return;
                window._tok = null;
                const d = document.createElement('div');
                d.id = '_ts';
                d.style = 'position:fixed;top:20px;left:20px;z-index:2147483647;background:#111;padding:12px;border-radius:8px;';
                document.body.appendChild(d);
                
                window._ld = function() {{
                    turnstile.render('#_ts', {{
                        sitekey: '{SITEKEY}',
                        theme: 'dark',
                        callback: function(t) {{ window._tok = t; }}
                    }});
                }};
                const s = document.createElement('script');
                s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?onload=_ld&render=explicit';
                document.head.appendChild(s);
            }})();
        """)

        print(f"{C.YELLOW}[*] Menunggu Cloudflare memproses challenge (Maks 30 detik)...{C.RESET}")
        
        token = None
        for _ in range(30):
            await asyncio.sleep(1)
            try:
                token = await page.evaluate("window._tok || null")
                if token:
                    break
            except Exception:
                pass

        await browser.close()
        return token

async def main():
    print(f"{C.GREEN}=== LOCAL TURNSTILE SOLVER with PROXY ==={C.RESET}")
    
    # Cek apakah konfigurasi proxy sudah diubah
    if "host:port" in PROXY_SERVER:
        print(f"\n{C.RED}[!] Silakan ubah variabel PROXY_SERVER di dalam file bypass.py dengan proxy milik Anda terlebih dahulu.{C.RESET}")
        return

    token = await get_turnstile_token()
    
    if token:
        print(f"\n{C.GREEN}[+] SUKSES! Token Turnstile berhasil didapatkan:{C.RESET}\n")
        print(f"{token}")
    else:
        print(f"\n{C.RED}[-] Gagal mendapatkan token. Cloudflare masih memblokir IP/Browser atau proxy bermasalah.{C.RESET}")

if __name__ == "__main__":
    asyncio.run(main())
