from collections import defaultdict
from urllib.parse import urlparse
import re

from Logs.logger import logger

BANNERS = {
    'telegram': {
        'html': '''
            <div class="telegram-banner" style="
                position: fixed;
                top: 20px;  
                right: 20px;
                padding: 12px;
                background: #fff;
                border: 2px solid #0088cc;
                border-radius: 8px;
                z-index: 9999;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            ">
                <img src="/static/mathmech.jpg"
                 style="width:40px;height:40px;"/>
                <a href="https://t.me/matmehurfu"
                   target="_blank"
                   style="
                       text-decoration: none;
                       color: #0088cc;
                       font-weight: bold;
                       font-size: 20px;
                   ">
                    Ссылка на МатМех
                </a>
            </div>

        ''',
        'triggers': ['ads.', 'tracking.', 'adfox.']
    },
    'The_White_House': {
        'html': '''
        <div class="white_house_banner" style="
            position: fixed;
            bottom: 20px;
            top: 20px;
            right: 20px;
            padding: 12px;
            background: #fff;
            border: 2px solid #cc0022;
            border-radius: 8px;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <a href="https://www.whitehouse.gov/" 
               target="_blank" 
               style="
                   text-decoration: none;
                   color: #cc0022;
                   font-weight: bold;
                   font-size: 20px;
               ">
                Белый дом бахнули
            </a>
        </div>
        ''',
        'triggers': ['casino', 'poker', 'gambling']
    },
    'lirili_larila': {
        'html': '''   <div class="shopping_banner" style="
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px;
            background: #fff;
            border: 2px solid #00cc44;
            border-radius: 8px;
            z-index: 9999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        ">
            <a href="https://t.me/matmehurfu" 
               target="_blank" 
               style="
                   text-decoration: none;
                   color: #0088cc;
                   font-weight: bold;
                   font-size: 20px;
               ">
                 Ссылка на каку-то хрень
            </a>
        </div> ''',
        'triggers': ['shop', 'buy', 'deal']
    },
    'default': {
        'html': '''
            <a 
               target="_blank" 
               style="
                   text-decoration: none;
                   color: #000000;
                   font-weight: bold;
                   font-size: 20px;
               ">
                 Реклама заблокирована
            </a>
        </div> ''',
        'triggers': ['shop', 'buy', 'deal']
    }

}


def change_banners(banners: dict, flag: int) -> str:
    mapping = {0: 'default', 1: 'telegram', 2: 'The_White_House', 3: 'lirili_larila'}
    key = mapping.get(flag, 'default')
    banner_data = banners.get(key) or banners.get('default')
    return banner_data.get('html', '')

