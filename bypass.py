import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async  # Plugin penyamaran

TARGET_URL = "https://drama.center"
SITEKEY = "0x4AAAAAAE5Imx2BMLN5ABSD"

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

async def get_turnstile_token():
    print(f"{C.CYAN}[*] Menjalankan browser otomatis (Mode Stealth)...{C.RESET}")
    
    async with async_playwright() as p:
        # Tambahan argumen agar tidak terdeteksi sebagai robot automation
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # Menerapkan jubah gaib (stealth) ke halaman web
        await stealth_async(page)

        print(f"{C.YELLOW}[*] Membuka {TARGET_URL}...{C.RESET}")
        await page.goto(TARGET_URL, wait_until="domcontentloaded")

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

        print(f"{C.YELLOW}[*] Menunggu Cloudflare memproses challenge (Maks 20 detik)...{C.RESET}")
        
        token = None
        # Tambah waktu tunggu jadi 20 detik karena stealth kadang butuh waktu
        for _ in range(20):
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
    print(f"{C.GREEN}=== LOCAL TURNSTILE SOLVER ==={C.RESET}")
    token = await get_turnstile_token()
    
    if token:
        print(f"\n{C.GREEN}[+] SUKSES! Token Turnstile berhasil didapatkan:{C.RESET}\n")
        print(f"{token}")
    else:
        print(f"\n{C.RED}[-] Gagal mendapatkan token. Cloudflare masih memblokir IP/Browser ini.{C.RESET}")

if __name__ == "__main__":
    asyncio.run(main())
