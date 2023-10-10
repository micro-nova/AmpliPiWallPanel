import json

VERSION = '0.2.16'
MIN_AMPLIPI_VERSION = '0.2.0'

WALL_PANEL_REPO = 'micro-nova/AmpliPiWallPanel'

_AMPLIPI_LOCAL_DOMAIN = 'amplipi.local'  # for mDNS

def get_amplipi_local_domain():
    try:
        with open('mdns_override.txt') as file:
            return json.load(file)['mdns']
    except OSError:
        return _AMPLIPI_LOCAL_DOMAIN