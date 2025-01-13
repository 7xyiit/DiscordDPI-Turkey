import logging

def setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(asctime)s - %(levelname)s - %(message)s' if not debug else \
                '%(asctime)s - %(levelname)s - [%(threadName)s] %(message)s'
    logging.basicConfig(
        level=level,
        format=format_str
    )
    
    if debug:
        logging.debug("[*] Debug modu aktif")
        logging.debug("[*] Detaylı loglar gösterilecek") 