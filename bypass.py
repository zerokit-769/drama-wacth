import asyncio
from playwright.async_api import async_playwright

# Konfigurasi Target (Sesuai dengan drama.center)
TARGET_URL = "https://drama.center"
# Sitekey Cloudflare drama.center
SITEKEY = "0x4AAAAAAE5Imx2BMLN5ABSD"

class C:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

async def get_turnstile_token():
    print(f"{C.CYAN}[*] Menjalankan browser otomatis (Playwright)...{C.RESET}")
    
    # Membuka instance Playwright
    async with async_playwright() as p:
        # headless=True agar berjalan di latar belakang (tidak buka jendela). 
        # Ubah ke False jika ingin melihat prosesnya.
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"{C.YELLOW}[*] Membuka {TARGET_URL} untuk mencocokkan asal (origin)...{C.RESET}")
        await page.goto(TARGET_URL, wait_until="commit")

        print(f"{C.YELLOW}[*] Menyuntikkan (Injecting) Widget Turnstile...{C.RESET}")
        
        # Ini adalah script JS dari fotomu yang aku sempurnakan
        await page.evaluate(f"""
            (() => {{
                if (document.getElementById('_ts')) return;
                
                // Siapkan variabel global penampung token
                window._tok = null;
                
                // Buat elemen visual penampung widget
                const d = document.createElement('div');
                d.id = '_ts';
                d.style = 'position:fixed;top:20px;left:20px;z-index:2147483647;background:#111;padding:12px;border-radius:8px;';
                document.body.appendChild(d);
                
                // Fungsi untuk merender widget Turnstile
                window._ld = function() {{
                    turnstile.render('#_ts', {{
                        sitekey: '{SITEKEY}',
                        theme: 'dark',
                        callback: function(t) {{ 
                            // Saat berhasil, simpan token ke window._tok
                            window._tok = t; 
                        }}
                    }});
                }};
                
                // Panggil file API Cloudflare secara paksa
                const s = document.createElement('script');
                s.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?onload=_ld&render=explicit';
                document.head.appendChild(s);
            }})();
        """)

        print(f"{C.YELLOW}[*] Menunggu Cloudflare menyelesaikan challenge (Maks 15 detik)...{C.RESET}")
        
        token = None
        # Polling: Cek setiap 1 detik apakah token sudah didapatkan
        for _ in range(15):
            await asyncio.sleep(1)
            try:
                # Menarik nilai window._tok dari browser ke Python
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
        print(f"\n{C.GREEN}[+] SUKSES! Token Turnstile berhasil dibuat secara gratis:{C.RESET}")
        print(f"{token}")
        
        # Nanti kamu bisa teruskan token ini ke sistem login web3/Supabase-mu
    else:
        print(f"\n{C.RED}[-] Gagal mendapatkan token. Cobalah mematikan mode headless (headless=False) untuk melihat kendalanya.{C.RESET}")

if __name__ == "__main__":
    asyncio.run(main())
