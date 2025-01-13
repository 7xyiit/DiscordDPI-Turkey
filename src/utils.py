import re
import logging
import sys

# Global değişkenler
running = True
proxy_instance = None

def set_proxy(proxy):
    """Global proxy referansını ayarla"""
    global proxy_instance
    proxy_instance = proxy

def signal_handler(signum, frame):
    """Ctrl+C sinyalini yakala"""
    global running, proxy_instance
    running = False
    logging.info("\n[*] Ctrl+C algılandı, kapatılıyor...")
    
    if proxy_instance:
        proxy_instance.stop()
    else:
        sys.exit(0)

def pattern_matches(config, domain):
    """Domain pattern eşleşmesi kontrol et"""
    if not config.patterns:
        return True
        
    # Domain'i string'e çevir
    if isinstance(domain, bytes):
        domain = domain.decode('utf-8', errors='ignore')
        
    # Her pattern için kontrol et
    for pattern in config.patterns:
        try:
            if re.search(pattern, domain):
                return True
        except:
            continue
            
    return False 