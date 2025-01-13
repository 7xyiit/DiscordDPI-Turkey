import subprocess
import logging

def set_chrome_proxy(host, port):
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
        chrome_cmd = f'start chrome --incognito --proxy-server="http://{host}:{port}" --ignore-certificate-errors'
        subprocess.Popen(chrome_cmd, shell=True)
        logging.info(f"[*] Chrome gizli modda başlatıldı ve proxy ayarları güncellendi: {host}:{port}")
    except Exception as e:
        logging.error(f"Chrome proxy ayarları güncellenirken hata: {e}")

def unset_chrome_proxy():
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True)
        subprocess.Popen('start chrome --incognito', shell=True)
        logging.info("[*] Chrome gizli modda yeniden başlatıldı")
    except Exception as e:
        logging.error(f"Chrome proxy ayarları sıfırlanırken hata: {e}") 