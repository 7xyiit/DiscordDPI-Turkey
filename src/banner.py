from colorama import init, Fore

def print_banner():
    """Program başlangıç banner'ını göster"""
    init()  # Colorama'yı başlat
    banner = f"""{Fore.CYAN}
    ██████╗ ██████╗ ██╗    ██████╗ ██╗   ██╗██████╗  █████╗ ███████╗███████╗
    ██╔══██╗██╔══██╗██║    ██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝
    ██║  ██║██████╔╝██║    ██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗
    ██║  ██║██╔═══╝ ██║    ██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║╚════██║╚════██║
    ██████╔╝██║     ██║    ██████╔╝   ██║   ██║     ██║  ██║███████║███████║
    ╚═════╝ ╚═╝     ╚═╝    ╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝
    
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                      Author: yiitgven7x                               ║
    ║                   Deep Packet Inspection Bypass                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝{Fore.RESET}
    """
    print(banner) 