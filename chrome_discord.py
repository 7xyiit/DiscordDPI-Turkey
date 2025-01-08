import os
import sys
import time
import logging
import psutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_logging():
    """Loglama ayarlarını yapılandır"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def kill_existing_chrome():
    """Varolan Chrome işlemlerini sonlandır"""
    for proc in psutil.process_iter(['name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    time.sleep(2)

def get_chrome_driver():
    """Chrome WebDriver'ı yapılandır ve başlat"""
    try:
        chrome_options = Options()
        chrome_options.add_argument('--proxy-server=127.0.0.1:8080')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--start-maximized')
        
        # Yeni profil dizini oluştur
        profile_dir = os.path.join(os.getcwd(), 'chrome-profile')
        os.makedirs(profile_dir, exist_ok=True)
        chrome_options.add_argument(f'--user-data-dir={profile_dir}')
        
        # WebDriver'ı başlat
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logging.error(f"WebDriver başlatma hatası: {str(e)}")
        return None

def start_proxy():
    """Proxy sunucusunu başlat"""
    try:
        proxy_path = os.path.join(os.getcwd(), 'discord_proxy.exe')
        if os.path.exists(proxy_path):
            return subprocess.Popen([proxy_path])
        else:
            proxy_script = os.path.join(os.getcwd(), 'simple_proxy.py')
            if os.path.exists(proxy_script):
                return subprocess.Popen([sys.executable, proxy_script])
            else:
                logging.error("Proxy dosyası bulunamadı!")
                return None
    except Exception as e:
        logging.error(f"Proxy başlatma hatası: {str(e)}")
        return None

def main():
    """Ana program döngüsü"""
    setup_logging()
    logging.info("Discord DPI Bypass başlatılıyor...")
    
    try:
        # Mevcut Chrome işlemlerini sonlandır
        kill_existing_chrome()
        
        # Proxy'yi başlat
        proxy_proc = start_proxy()
        if not proxy_proc:
            logging.error("Proxy başlatılamadı!")
            input("Devam etmek için bir tuşa basın...")
            return
        
        time.sleep(2)  # Proxy'nin başlaması için bekle
        
        # Chrome'u başlat
        driver = get_chrome_driver()
        if not driver:
            logging.error("Chrome başlatılamadı!")
            proxy_proc.terminate()
            input("Devam etmek için bir tuşa basın...")
            return
        
        # Discord'a git
        logging.info("Discord Web açılıyor...")
        driver.get("https://discord.com/")
        
        try:
            # Programın çalışır durumda kalması için ana döngü
            while True:
                # Proxy çalışıyor mu kontrol et
                if proxy_proc.poll() is not None:
                    logging.error("Proxy beklenmedik şekilde kapandı!")
                    break
                    
                # Chrome açık mı kontrol et
                try:
                    driver.current_url
                except:
                    logging.info("Chrome kapatıldı!")
                    break
                    
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("\nProgram sonlandırılıyor...")
        finally:
            # Temizlik işlemleri
            try:
                driver.quit()
            except:
                pass
            try:
                proxy_proc.terminate()
            except:
                pass
            kill_existing_chrome()
    
    except Exception as e:
        logging.error(f"Beklenmeyen hata: {str(e)}")
    
    # Programın hemen kapanmaması için bekle
    input("\nProgramı kapatmak için bir tuşa basın...")

if __name__ == "__main__":
    main() 