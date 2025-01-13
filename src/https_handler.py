import socket
import logging
import time
from src.utils import pattern_matches

def handle_https(config, client_socket, initial_data, resolver):
    server_socket = None
    try:
        # CONNECT isteğini parse et
        connect_lines = initial_data.split(b"\r\n")
        first_line = connect_lines[0].decode()
        
        # İlk satırı daha güvenli bir şekilde parse et
        parts = first_line.split()
        if len(parts) < 3:
            if config.debug:
                logging.debug(f"[-] Geçersiz CONNECT isteği: {first_line}")
            return None, False
        
        method, target = parts[0], parts[1]
        if method != "CONNECT":
            if config.debug:
                logging.debug(f"[-] CONNECT metodu beklendi ama {method} alındı")
            return None, False
        
        # Host ve port'u ayır
        if ":" in target:
            host, port = target.split(":")
            port = int(port)
        else:
            host = target
            port = 443  # Varsayılan HTTPS portu
        
        if config.debug:
            logging.debug(f"[+] HTTPS Hedef: {host}:{port}")
        
        # DNS çözümlemesi
        ip = resolver.lookup(host)
        if not ip:
            if config.debug:
                logging.debug(f"[-] DNS çözümlemesi başarısız: {host}")
            return None, False
        
        try:
            # Doğrudan bağlantı kur
            server_socket = socket.create_connection((ip, port), timeout=config.timeout)
            
            # Bağlantı başarılı, istemciye OK gönder
            response = b"HTTP/1.1 200 Connection established\r\n\r\n"
            client_socket.send(response)
            
            if config.debug:
                logging.debug(f"[+] Bağlantı kuruldu: {ip}:{port}")
            
            # Domain pattern kontrolü
            matched = pattern_matches(config, host)
            
            return server_socket, matched
            
        except Exception as e:
            if config.debug:
                logging.debug(f"[-] Bağlantı hatası: {str(e)}")
            return None, False
            
    except Exception as e:
        logging.error(f"HTTPS işleme hatası: {e}")
        if server_socket:
            try:
                server_socket.close()
            except:
                pass
        return None, False

def handle_dpi_connection(config, client_socket, server_socket):
    try:
        # İlk client hello'yu al
        client_socket.settimeout(2)
        initial_data = client_socket.recv(config.chunk_size)
        
        if not initial_data:
            return False
            
        # Veriyi parçala ve gönder
        if len(initial_data) > config.window_size:
            first_chunk = initial_data[:config.window_size]
            rest_chunk = initial_data[config.window_size:]
            
            # İlk parçayı gönder
            server_socket.send(first_chunk)
            time.sleep(0.1)  # Küçük gecikme
            
            # Kalan parçayı gönder
            if rest_chunk:
                server_socket.send(rest_chunk)
        else:
            server_socket.send(initial_data)
        
        return True
            
    except Exception as e:
        if config.debug:
            logging.debug(f"[-] DPI bağlantı hatası: {str(e)}")
        return False 