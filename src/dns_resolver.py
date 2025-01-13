import socket
import dns.resolver
import requests
import logging

class DNSResolver:
    def __init__(self, config):
        self.config = config
        self.resolver = dns.resolver.Resolver()
        if hasattr(self.config, 'dns_addr') and hasattr(self.config, 'dns_port'):
            self.resolver.nameservers = [self.config.dns_addr]
            self.resolver.port = self.config.dns_port
            
    def system_lookup(self, domain):
        """Sistem DNS'ini kullanarak domain çözümlemesi yap"""
        try:
            return socket.gethostbyname(domain)
        except Exception as e:
            if self.config.debug:
                logging.debug(f"[-] Sistem DNS hatası ({domain}): {str(e)}")
            return None
            
    def custom_lookup(self, domain):
        """Özel DNS sunucusunu kullanarak domain çözümlemesi yap"""
        try:
            answers = self.resolver.resolve(domain, 'A')
            return str(answers[0])
        except Exception as e:
            if self.config.debug:
                logging.debug(f"[-] Özel DNS hatası ({domain}): {str(e)}")
            return None
            
    def doh_lookup(self, domain):
        """DNS-over-HTTPS kullanarak domain çözümlemesi yap"""
        try:
            url = f"https://cloudflare-dns.com/dns-query"
            headers = {
                "accept": "application/dns-json"
            }
            params = {
                "name": domain,
                "type": "A"
            }
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if "Answer" in data:
                return data["Answer"][0]["data"]
            return None
            
        except Exception as e:
            if self.config.debug:
                logging.debug(f"[-] DoH hatası ({domain}): {str(e)}")
            return None
            
    def lookup(self, domain):
        """Tüm DNS çözümleme metodlarını dene"""
        if hasattr(self.config, 'enable_doh') and self.config.enable_doh:
            ip = self.doh_lookup(domain)
            if ip:
                return ip
                
        if hasattr(self.config, 'dns_addr'):
            ip = self.custom_lookup(domain)
            if ip:
                return ip
                
        return self.system_lookup(domain) 