import socket
import threading
import logging
import sys
import os
from src.dns_resolver import DNSResolver
from src.http_handler import handle_http, read_http_packet
from src.https_handler import handle_https, handle_dpi_connection
from src.network_utils import serve
from src.utils import pattern_matches, running, set_proxy

class DPIBypass:
    def __init__(self, config):
        self.config = config
        self.resolver = DNSResolver(config)
        self.server_socket = None
        self.clients = []
        self._lock = threading.Lock()
        set_proxy(self)  # Global proxy referansını ayarla
        
    def start(self):
        """Proxy sunucusunu başlat"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config.host, self.config.port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1)  # 1 saniyelik timeout
            
            logging.info(f"[+] Proxy sunucusu başlatıldı - {self.config.host}:{self.config.port}")
            
            while running:
                try:
                    client_socket, address = self.server_socket.accept()
                    client_socket.settimeout(self.config.timeout)
                    
                    if self.config.debug:
                        logging.debug(f"[+] Bağlantı kabul edildi: {address[0]}:{address[1]}")
                    
                    client_handler = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket,)
                    )
                    client_handler.daemon = True
                    client_handler.start()
                    
                    with self._lock:
                        self.clients.append(client_handler)
                        # Bitmiş thread'leri temizle
                        self.clients = [c for c in self.clients if c.is_alive()]
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if running and self.config.debug:
                        logging.debug(f"[-] Bağlantı kabul hatası: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Sunucu hatası: {str(e)}")
            
        finally:
            self.stop()
                
    def handle_client(self, client_socket):
        """İstemci bağlantısını yönet"""
        server_socket = None
        
        try:
            initial_data = client_socket.recv(self.config.chunk_size)
            
            if not initial_data:
                return
                
            if initial_data.startswith(b"CONNECT"):
                # HTTPS bağlantısı
                server_socket, use_dpi = handle_https(
                    self.config,
                    client_socket,
                    initial_data,
                    self.resolver
                )
                
                if not server_socket:
                    return
                    
                if use_dpi:
                    if not handle_dpi_connection(self.config, client_socket, server_socket):
                        return
                        
            else:
                # HTTP bağlantısı
                server_socket = handle_http(
                    self.config,
                    client_socket,
                    initial_data
                )
                
                if not server_socket:
                    return
                    
            # Veri transferini başlat
            serve(client_socket, server_socket, self.config)
            
        except Exception as e:
            if self.config.debug:
                logging.debug(f"[-] İstemci işleme hatası: {str(e)}")
                
        finally:
            try:
                if server_socket:
                    server_socket.close()
                client_socket.close()
            except:
                pass
                
    def stop(self):
        """Proxy sunucusunu durdur"""
        logging.info("[*] Proxy durduruluyor...")
        
        # Ana soketi kapat
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
                self.server_socket.close()
            except:
                pass
            self.server_socket = None
                
        # Aktif thread'leri bekle
        with self._lock:
            active_clients = [c for c in self.clients if c.is_alive()]
            for client in active_clients:
                try:
                    client.join(0.1)  # Her thread için en fazla 0.1 saniye bekle
                except:
                    pass
            self.clients.clear()
            
        logging.info("[*] Proxy durduruldu")
        os._exit(0)  # Programı anında sonlandır 