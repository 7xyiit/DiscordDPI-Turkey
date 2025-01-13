import argparse
import re
import logging

class Config:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 8080
        self.chunk_size = 8192
        self.window_size = 64
        self.timeout = 30
        self.debug = False
        self.patterns = []
        self.dns_addr = "8.8.8.8"
        self.dns_port = 53
        self.enable_doh = False
        
    @staticmethod
    def parse_args():
        """Komut satırı argümanlarını işle"""
        parser = argparse.ArgumentParser(description="DPI Bypass Proxy")
        
        parser.add_argument("--host", 
            default="127.0.0.1",
            help="Proxy sunucusu host adresi"
        )
        
        parser.add_argument("--port",
            type=int,
            default=8080,
            help="Proxy sunucusu port numarası"
        )
        
        parser.add_argument("--chunk-size",
            type=int,
            default=8192,
            help="Veri okuma/yazma boyutu"
        )
        
        parser.add_argument("--window-size",
            type=int,
            default=64,
            help="DPI bypass pencere boyutu"
        )
        
        parser.add_argument("--timeout",
            type=int,
            default=30,
            help="Bağlantı zaman aşımı süresi"
        )
        
        parser.add_argument("--debug",
            action="store_true",
            help="Debug modunu etkinleştir"
        )
        
        parser.add_argument("--pattern",
            action="append",
            help="DPI bypass için domain pattern (birden fazla kullanılabilir)"
        )
        
        parser.add_argument("--dns-addr",
            default="8.8.8.8",
            help="Özel DNS sunucu adresi"
        )
        
        parser.add_argument("--dns-port",
            type=int,
            default=53,
            help="Özel DNS sunucu portu"
        )
        
        parser.add_argument("--enable-doh",
            action="store_true",
            help="DNS-over-HTTPS kullanımını etkinleştir"
        )
        
        args = parser.parse_args()
        
        # Debug modu için logging ayarları
        if args.debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            
        # Pattern kontrolü
        if args.pattern:
            for pattern in args.pattern:
                try:
                    re.compile(pattern)
                except re.error:
                    parser.error(f"Geçersiz regex pattern: {pattern}")
                    
        return args
        
    def load_args(self, args):
        """Argümanları yapılandırma nesnesine yükle"""
        self.host = args.host
        self.port = args.port
        self.chunk_size = args.chunk_size
        self.window_size = args.window_size
        self.timeout = args.timeout
        self.debug = args.debug
        self.patterns = args.pattern if args.pattern else []
        self.dns_addr = args.dns_addr
        self.dns_port = args.dns_port
        self.enable_doh = args.enable_doh 