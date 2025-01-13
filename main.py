import signal
import sys
import logging
import atexit
from src.config import Config
from src.dpi_bypass import DPIBypass
from src.chrome_utils import set_chrome_proxy, unset_chrome_proxy
from src.utils import signal_handler
from src.banner import print_banner

def cleanup():
    """Program kapatılırken yapılacak temizlik işlemleri"""
    try:
        unset_chrome_proxy()
        logging.info("[*] Chrome proxy ayarları temizlendi")
    except:
        pass

def main():
    """Ana program başlangıç noktası"""
    # Temizlik fonksiyonunu kaydet
    atexit.register(cleanup)
    
    try:
        # Banner'ı göster
        print_banner()
        
        # Yapılandırmayı yükle
        config = Config()
        args = config.parse_args()
        config.load_args(args)
        
        # Ctrl+C sinyalini yakala
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # DPI Bypass proxy'sini başlat
        proxy = DPIBypass(config)
        
        # Chrome proxy ayarlarını güncelle
        set_chrome_proxy(config.host, config.port)
        
        # Proxy sunucusunu başlat
        proxy.start()
        
    except Exception as e:
        logging.error(f"Program hatası: {str(e)}")
        sys.exit(1)
        
if __name__ == "__main__":
    main() 