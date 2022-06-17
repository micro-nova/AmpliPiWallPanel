import json

VERSION = '0.1.24'
MIN_AMPLIPI_VERSION = '1.7'

WALL_PANEL_REPO = 'micro-nova/AmpliPiWallPanel'

_AMPLIPI_LOCAL_DOMAIN = 'amplipi.local'  # for mDNS

def get_amplipi_local_domain():
    try:
        with open('mdns_override.txt') as file:
            return json.load(file)['mdns']
    except OSError:
        return _AMPLIPI_LOCAL_DOMAIN