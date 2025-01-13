import socket
import logging

def handle_http(config, client_socket, initial_data):
    server_socket = None
    try:
        request_lines = initial_data.split(b"\r\n")
        first_line = request_lines[0].decode()
        method, path, version = first_line.split(" ")
        
        if config.debug:
            logging.debug(f"[+] HTTP İstek: {method} {path}")
        
        host = None
        port = 80
        for line in request_lines[1:]:
            if line.lower().startswith(b"host: "):
                host = line[6:].decode().strip()
                if ":" in host:
                    host, port = host.split(":")
                    port = int(port)
                break
                
        if not host:
            return
            
        if config.debug:
            logging.debug(f"[+] Hedef: {host}:{port}")
            
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(10)
        server_socket.connect((host, port))
        server_socket.send(initial_data)
        
        if config.debug:
            logging.debug(f"[+] Bağlantı kuruldu: {host}:{port}")
        
        return server_socket
        
    except Exception as e:
        logging.error(f"HTTP işleme hatası: {e}")
        if server_socket:
            try:
                server_socket.close()
            except:
                pass
        return None

def read_http_packet(config, conn):
    """HTTP isteğini parse et ve detayları çıkar"""
    try:
        request = conn.recv(config.chunk_size).decode()
        request = "\n".join([line.strip() for line in request.splitlines()])
        method, path, version = request.splitlines()[0].split()
        
        # Host başlığını bul
        host_line = next((line for line in request.splitlines() if line.lower().startswith("host: ")), None)
        if not host_line:
            return None
            
        # Host ve port'u ayır
        host = host_line[6:].strip()
        port = "80"
        if ":" in host:
            host, port = host.split(":")
            
        if config.debug:
            logging.debug(f"[+] HTTP İstek:\n{request}")
            
        return {
            "method": method,
            "domain": host,
            "port": port,
            "version": version,
            "path": path,
            "raw": request
        }
    except Exception as e:
        logging.error(f"HTTP istek parse hatası: {e}")
        return None 