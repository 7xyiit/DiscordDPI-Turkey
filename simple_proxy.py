import socket
import threading
import logging
import sys
import time
import random
import struct
import netifaces
import dns.resolver
import errno

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_local_ip():
    """Aktif ağ arayüzünün IP adresini bul"""
    try:
        gateways = netifaces.gateways()
        if 'default' not in gateways or netifaces.AF_INET not in gateways['default']:
            raise Exception("Varsayılan ağ geçidi bulunamadı!")
            
        default_interface = gateways['default'][netifaces.AF_INET][1]
        
        addrs = netifaces.ifaddresses(default_interface)
        if netifaces.AF_INET not in addrs:
            raise Exception("IPv4 adresi bulunamadı!")
            
        return addrs[netifaces.AF_INET][0]['addr']
    except Exception as e:
        logging.error(f"IP adresi bulma hatası: {str(e)}")
        return '0.0.0.0'

class SimpleProxy:
    def __init__(self, local_port=8080):
        self.local_port = local_port
        self.buffer_size = 65536
        self.local_ip = get_local_ip()
        self.dns_servers = [
            '1.1.1.1',     # Cloudflare (en hızlı)
            '1.0.0.1',     # Cloudflare (yedek)
            '8.8.8.8',     # Google (yedek)
        ]
        
        # DNS önbelleği oluştur
        self.dns_cache = {}
        self.dns_cache_timeout = 300  # 5 dakika
        
        logging.info(f"DNS Sunucuları: {', '.join(self.dns_servers)}")
        
        self.discord_domains = [
            'discord.com',
            'discord.gg',
            'discordapp.com',
            'discord.media',
            'gateway.discord.gg',
            'cdn.discordapp.com',
            'media.discordapp.net',
            'status.discord.com',
            'dl.discordapp.net',
            'media.discordapp.net',
            'images-ext-1.discordapp.net',
            'images-ext-2.discordapp.net',
            # Web sürümü için ek domainler
            'discord.co',
            'discord.dev',
            'discord.new',
            'discord.gift',
            'discord.gifts',
            'discord.media',
            'discord.store',
            'discord.tools',
            'dis.gd',
            'canary.discord.com',
            'ptb.discord.com',
            'support.discord.com',
            'support-dev.discord.com',
            'click.discord.com',
            'media.discordapp.com',
            'images.discordapp.net',
            'i.discord.com',
            'cdn.dis.gd',
            'remote-auth-gateway.discord.gg',
            'api.discord.com',
            'latency.discord.media',
            'router.discordapp.net',
            'health.discord.com',
            'url-preview.discordapp.com',
            'streamkit.discord.com',
            'merch.discord.com',
            'printer.discord.com',
            'apps.discord.com',
            'pax.discord.com',
            'safety.discord.com',
            'feedback.discord.com',
            'bugs.discord.com',
            'experiments.discord.com',
            'staging.discord.co',
            'staging.discord.gg',
            'watchanimeattheoffice.com',  # Discord'un alternatif domaini
            'bigbeans.solutions',         # Discord'un alternatif domaini
            'hammerandchisel.ssl.zendesk.com'  # Discord destek sistemi
        ]

    def resolve_dns(self, hostname):
        """DNS çözümleme işlemi"""
        try:
            # Önce DNS önbelleğini kontrol et
            if hostname in self.dns_cache:
                cache_time, ip = self.dns_cache[hostname]
                if time.time() - cache_time < self.dns_cache_timeout:
                    return ip
            
            # Sadece Cloudflare DNS'i kullan (en hızlısı)
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [self.dns_servers[0]]  # Sadece 1.1.1.1
            resolver.timeout = 1
            resolver.lifetime = 2
            answers = resolver.resolve(hostname, 'A')
            ip = str(answers[0])
            
            # DNS önbelleğini güncelle
            self.dns_cache[hostname] = (time.time(), ip)
            return ip
                
        except Exception as e:
            logging.error(f"DNS çözümleme hatası ({hostname}): {str(e)}")
            # Yedek DNS sunucularını dene
            try:
                ip = socket.gethostbyname(hostname)
                self.dns_cache[hostname] = (time.time(), ip)
                return ip
            except:
                return None

    def create_connection(self, dst_addr, dst_port):
        # DNS çözümlemesi yap
        if not dst_addr.replace('.', '').isdigit():  # IP adresi değilse
            resolved_ip = self.resolve_dns(dst_addr)
            if not resolved_ip:
                return None
            dst_addr = resolved_ip
            logging.info(f"DNS Çözümleme: {dst_addr} -> {resolved_ip}")
        
        # Farklı kaynak portları dene
        for _ in range(5):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)  # Timeout süresini artır
                
                # TCP optimizasyonları
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 262144)  # Daha büyük tampon
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 262144)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                
                if hasattr(socket, 'TCP_KEEPIDLE'):  # Linux
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                elif hasattr(socket, 'TCP_KEEPALIVE'):  # macOS
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, 60)
                if hasattr(socket, 'TCP_KEEPINTVL'):
                    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 60)
                
                # Rastgele kaynak portu
                src_port = random.randint(10000, 65000)
                sock.bind((self.local_ip, src_port))
                
                # Bağlantıyı kur
                sock.connect((dst_addr, dst_port))
                return sock
            except Exception as e:
                logging.error(f"Bağlantı hatası ({dst_addr}:{dst_port}): {str(e)}")
                try:
                    sock.close()
                except:
                    pass
                continue
        return None

    def handle_socks4(self, client_socket):
        """SOCKS4 protokolü desteği"""
        try:
            header = client_socket.recv(8)
            if len(header) < 8:
                return
            
            version, command, port = struct.unpack(">BBH", header[:4])
            ip = socket.inet_ntoa(header[4:8])
            
            if version != 4 or command != 1:
                client_socket.send(struct.pack(">BBH", 0, 91, 0) + b"\x00\x00\x00\x00")
                return
            
            remote_socket = self.create_connection(ip, port)
            if not remote_socket:
                client_socket.send(struct.pack(">BBH", 0, 91, 0) + b"\x00\x00\x00\x00")
                return
            
            client_socket.send(struct.pack(">BBH", 0, 90, port) + socket.inet_aton(ip))
            
            is_discord = any(domain in ip for domain in self.discord_domains)
            threading.Thread(target=self.forward_data, args=(client_socket, remote_socket, is_discord)).start()
            threading.Thread(target=self.forward_data, args=(remote_socket, client_socket, is_discord)).start()
            
        except Exception as e:
            logging.error(f"SOCKS4 hatası: {str(e)}")
            try:
                client_socket.close()
            except:
                pass

    def handle_tcp_connection(self, client_socket):
        try:
            first_byte = client_socket.recv(1, socket.MSG_PEEK)
            if not first_byte:
                return
                
            if first_byte[0] == 4:
                self.handle_socks4(client_socket)
                return
            
            data = client_socket.recv(self.buffer_size)
            if not data:
                return

            if data.startswith(b'CONNECT'):
                first_line = data.split(b'\r\n')[0].decode('utf-8')
                host_port = first_line.split(' ')[1]
                host, port = host_port.split(':')
                port = int(port)
                
                is_discord = any(domain in host for domain in self.discord_domains)
                logging.info(f"Bağlantı isteği: {host}:{port} ({'Discord' if is_discord else 'Normal'})")
                
                remote_socket = self.create_connection(host, port)
                if not remote_socket:
                    client_socket.close()
                    return
                
                # HTTP/2 ve WebSocket desteğini belirt
                response = (
                    b'HTTP/1.1 200 Connection Established\r\n'
                    b'Connection: Upgrade, Keep-Alive\r\n'
                    b'Upgrade: h2c, websocket\r\n'
                    b'Keep-Alive: timeout=15, max=100\r\n'
                    b'\r\n'
                )
                client_socket.send(response)
                
                threading.Thread(target=self.forward_data, args=(client_socket, remote_socket, is_discord)).start()
                threading.Thread(target=self.forward_data, args=(remote_socket, client_socket, is_discord)).start()
            else:
                first_line = data.split(b'\r\n')[0].decode('utf-8')
                method, full_path, _ = first_line.split(' ')
                
                # URL'yi parçala
                if full_path.startswith('http://'):
                    full_path = full_path[7:]
                elif full_path.startswith('https://'):
                    full_path = full_path[8:]
                
                # Host ve path'i ayır
                if '/' in full_path:
                    host = full_path[:full_path.find('/')]
                    path = full_path[full_path.find('/'):]
                else:
                    host = full_path
                    path = '/'
                
                # Port kontrolü
                if ':' in host:
                    host, port = host.split(':')
                    port = int(port)
                else:
                    port = 80 if method != 'CONNECT' else 443
                
                # Host header'ını güncelle
                headers = []
                found_host = False
                for header in data.split(b'\r\n')[1:]:
                    if not header:
                        break
                    if header.lower().startswith(b'host:'):
                        headers.append(f'Host: {host}'.encode())
                        found_host = True
                    else:
                        headers.append(header)
                
                if not found_host:
                    headers.append(f'Host: {host}'.encode())
                
                # İsteği yeniden oluştur
                new_request = f'{method} {path} HTTP/1.1\r\n'.encode()
                new_request += b'\r\n'.join(headers) + b'\r\n\r\n'
                
                is_discord = any(domain in host for domain in self.discord_domains)
                logging.info(f"HTTP isteği: {host}{path} ({'Discord' if is_discord else 'Normal'})")
                
                remote_socket = self.create_connection(host, port)
                if not remote_socket:
                    client_socket.close()
                    return
                
                remote_socket.send(new_request)
                
                threading.Thread(target=self.forward_data, args=(client_socket, remote_socket, is_discord)).start()
                threading.Thread(target=self.forward_data, args=(remote_socket, client_socket, is_discord)).start()
                
        except Exception as e:
            logging.error(f"Bağlantı hatası: {str(e)}")
            try:
                client_socket.close()
            except:
                pass

    def forward_data(self, source, destination, is_discord):
        try:
            source.settimeout(30)
            destination.settimeout(30)
            
            while True:
                try:
                    data = source.recv(self.buffer_size)
                    if not data:
                        break
                        
                    if is_discord:
                        try:
                            chunks = self.split_data(data)
                            for chunk in chunks:
                                if destination._closed:
                                    return
                                destination.send(chunk)
                        except Exception as e:
                            if any(err in str(e).lower() for err in ["yuva olmayan", "not a socket", "timed out", "iptal edildi", "cancelled"]):
                                break
                            logging.error(f"Veri gönderme hatası: {str(e)}")
                            break
                    else:
                        try:
                            if destination._closed:
                                return
                            destination.send(data)
                        except:
                            break
                except socket.error as e:
                    if e.errno in [errno.ECONNRESET, errno.EBADF, errno.ENOTCONN, errno.ETIMEDOUT, errno.ECONNABORTED]:
                        break
                    if "timed out" in str(e) or "cancelled" in str(e):
                        break
                    raise
        except Exception as e:
            if not any(err in str(e).lower() for err in ["10038", "timed out", "cancelled"]):
                logging.error(f"Veri iletim hatası: {str(e)}")
        finally:
            try:
                if not source._closed:
                    source.close()
            except:
                pass
            try:
                if not destination._closed:
                    destination.close()
            except:
                pass

    def split_data(self, data):
        """TLS paketlerini özel olarak işle"""
        if len(data) < 5:
            return [data]
            
        # TLS paketini kontrol et
        is_tls = (data[0] == 0x16 and data[1] == 0x03)
        
        if not is_tls:
            # TLS değilse büyük parçalar halinde gönder
            chunks = []
            chunk_size = 8192
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                chunks.append(chunk)
            return chunks
            
        try:
            # TLS Client Hello paketini kontrol et
            if data[5] == 0x01:  # Client Hello
                chunks = []
                # TLS Header'ı gönder
                chunks.append(data[:5])
                # Kalan veriyi büyük parçalar halinde gönder
                remaining_data = data[5:]
                chunk_size = 4096
                for i in range(0, len(remaining_data), chunk_size):
                    chunk = remaining_data[i:i + chunk_size]
                    chunks.append(chunk)
                return chunks
            
        except:
            pass
            
        # TLS paketi ama Client Hello değilse
        chunks = []
        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            chunks.append(chunk)
        return chunks

    def start(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            server.bind(('0.0.0.0', self.local_port))
            server.listen(5)
            
            logging.info(f"Proxy sunucusu başlatıldı - IP: {self.local_ip}, Port: {self.local_port}")
            logging.info("Discord DPI Bypass aktif...")
            
            while True:
                try:
                    client_socket, addr = server.accept()
                    logging.info(f"Yeni bağlantı: {addr}")
                    threading.Thread(target=self.handle_tcp_connection, args=(client_socket,)).start()
                except Exception as e:
                    logging.error(f"Bağlantı kabul hatası: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Sunucu hatası: {str(e)}")
            sys.exit(1)
        finally:
            try:
                server.close()
            except:
                pass

if __name__ == "__main__":
    proxy = SimpleProxy()
    proxy.start() 