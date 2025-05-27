import asyncio
import aiohttp
import os
import sys
import subprocess
import colorama
from colorama import Fore, Style
import ctypes
import shutil

colorama.init()

GITHUB_USER = "UnknownDestroyer2"
REPO_NAME = "Gh0stCopy-Source"
BRANCH = "main"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/git/trees/{BRANCH}?recursive=1"
TARGET_MAIN = "main1.py"
EXE_URL = "https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10051/gs10051w64.exe"
EXE_NAME = "gs10051w64.exe"
TARGET_FOLDER = "GhostScript"

# Running script name (örn. a1c1.py)
SCRIPT_NAME = os.path.basename(__file__)

# Files to exclude from moving, including Ubuntu-B.ttf
EXCLUDE_FILES = {EXE_NAME, TARGET_FOLDER, SCRIPT_NAME, TARGET_MAIN, "Ubuntu-B.ttf"}


def message_box(text, title="Info"):    
    MB_OK = 0
    ctypes.windll.user32.MessageBoxW(0, text, title, MB_OK)


async def download_file(session, url, save_as):
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                content = await resp.read()
                with open(save_as, "wb") as f:
                    f.write(content)
                print(f"{Fore.GREEN}[+] İndirildi: {save_as}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}[-] İndirilemedi: {save_as} (HTTP {resp.status}){Style.RESET_ALL}")
                return False
    except Exception as e:
        print(f"{Fore.RED}[-] HATA: {save_as} | {e}{Style.RESET_ALL}")
        return False


async def download_github_files():
    print(f"{Fore.CYAN}[*] {REPO_NAME} dosyaları hızlıca indiriliyor...{Style.RESET_ALL}")
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as resp:
            if resp.status != 200:
                print(f"{Fore.RED}[!] GitHub API'den dosya listesi alınamadı: {resp.status}{Style.RESET_ALL}")
                return False
            data = await resp.json()
            if "tree" not in data:
                print(f"{Fore.RED}[!] Repo yapısı beklenmedik!{Style.RESET_ALL}")
                return False

            files = [item['path'] for item in data['tree'] if item['type'] == 'blob']
            tasks = []
            for file_path in files:
                local_path = file_path.replace("/", os.sep)
                base = os.path.basename(local_path)
                # main1.py varsa sil ve indir
                if base == TARGET_MAIN and os.path.exists(local_path):
                    try:
                        os.remove(local_path)
                        print(f"{Fore.YELLOW}[-] {TARGET_MAIN} silindi ve yenisi indirilecek...{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}[-] {TARGET_MAIN} silinemedi: {e}{Style.RESET_ALL}")
                # diğer dosyalar varsa atla
                elif os.path.exists(local_path):
                    print(f"{Fore.CYAN}[*] Atlandı (zaten var): {local_path}{Style.RESET_ALL}")
                    continue
                folder = os.path.dirname(local_path)
                if folder:
                    os.makedirs(folder, exist_ok=True)
                url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{file_path}"
                tasks.append(download_file(session, url, local_path))

            await asyncio.gather(*tasks)
    return True


def run_exe(exe_path):
    try:
        subprocess.Popen(exe_path, shell=True)
        print(f"{Fore.CYAN}[+] {exe_path} çalıştırıldı.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[-] {exe_path} çalıştırılamadı: {e}{Style.RESET_ALL}")


# Move all files except ones in EXCLUDE_FILES into TARGET_FOLDER
def move_files_to_folder(folder_name):
    cwd = os.getcwd()
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for item in os.listdir(cwd):
        if item in EXCLUDE_FILES or item.endswith('.tff'):
            continue
        src = os.path.join(cwd, item)
        dst = os.path.join(cwd, folder_name, item)
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"{Fore.RED}[-] Taşıma hatası: {item} | {e}{Style.RESET_ALL}")


def launch_main():
    target_path = os.path.join(TARGET_FOLDER, TARGET_MAIN)
    if os.path.exists(target_path):
        print(f"{Fore.CYAN}[*] {TARGET_MAIN} başlatılıyor...{Style.RESET_ALL}")
        subprocess.Popen([sys.executable, target_path])
        if os.name == "nt":
            os.system("echo off")
            os.system("cls")
    else:
        print(f"{Fore.RED}[-] {TARGET_MAIN} bulunamadı.{Style.RESET_ALL}")


async def main():
    # 1. Exe var mı kontrol et
    if os.path.exists(EXE_NAME):
        print(f"{Fore.CYAN}[*] {EXE_NAME} zaten var, direkt çalıştırılıyor...{Style.RESET_ALL}")
        run_exe(EXE_NAME)
    else:
        print(f"{Fore.CYAN}[*] {EXE_NAME} indiriliyor...{Style.RESET_ALL}")
        async with aiohttp.ClientSession() as session:
            success = await download_file(session, EXE_URL, EXE_NAME)
        if not success:
            print(f"{Fore.RED}[-] {EXE_NAME} indirilemedi, iptal.{Style.RESET_ALL}")
            return
        run_exe(EXE_NAME)

    message_box("Kurulumu yapıp tamamladıktan sonra CMD penceresine dönün ve ENTER tuşuna basın.", "Kurulum")
    input(f"{Fore.YELLOW}[*] Enter tuşuna bas ve dosyalar indirilsin...{Style.RESET_ALL}")

    await download_github_files()
    move_files_to_folder(TARGET_FOLDER)
    launch_main()

if __name__ == "__main__":
    asyncio.run(main())
