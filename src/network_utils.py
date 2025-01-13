import socket
import select
import logging
from src.utils import running

def serve(client_socket, server_socket, config):
    """İki soket arasında veri transferini yönet"""
    try:
        while running:
            # Okuma için hazır olan soketleri kontrol et
            readable, _, _ = select.select([client_socket, server_socket], [], [], 1)
            
            if not readable:
                # Sadece detaylı debug modunda timeout mesajını göster
                if config.debug and hasattr(config, 'verbose'):
                    logging.debug("[-] Bağlantı zaman aşımı")
                continue
                
            for sock in readable:
                # Hangi soketten veri okuyacağımızı belirle
                other = server_socket if sock is client_socket else client_socket
                
                try:
                    data = sock.recv(config.chunk_size)
                except Exception as e:
                    if config.debug:
                        logging.debug(f"[-] Veri okuma hatası: {str(e)}")
                    return
                    
                if not data:
                    return
                    
                try:
                    other.send(data)
                except Exception as e:
                    if config.debug:
                        logging.debug(f"[-] Veri gönderme hatası: {str(e)}")
                    return
                    
    except Exception as e:
        if config.debug:
            logging.debug(f"[-] Bağlantı hatası: {str(e)}")
    finally:
        try:
            client_socket.close()
            server_socket.close()
        except:
            pass

def transfer_data(source, destination, chunk_size):
    """İki soket arasında tek yönlü veri transferi yap"""
    try:
        while running:
            data = source.recv(chunk_size)
            if not data:
                break
            destination.send(data)
    except:
        pass 