#!/usr/bin/env python3
"""PatRadio - portail personnel d'écoute radio (sans réception locale)."""
import json
import os
import sys
import webbrowser
from pathlib import Path
from html import escape
from urllib.parse import urlparse

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QComboBox,
    QMessageBox, QFrame, QStatusBar, QGridLayout
)

APP_NAME = 'PatRadio'
def config_directory():
    """Répertoire utilisateur adapté à chaque système, sans déplacer les favoris Linux."""
    if sys.platform == 'win32':
        base = os.environ.get('APPDATA')
        return (Path(base) if base else Path.home() / 'AppData' / 'Roaming') / 'PatRadio'
    return Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'patradio'


CONFIG_DIR = config_directory()
CONFIG_FILE = CONFIG_DIR / 'favorites.json'
STATIONS = [
    {'id': 'bordeaux7100', 'name': 'Bordeaux · 7 100 kHz LSB (manuel)', 'category': 'Radioamateurs', 'detail': '40 mètres · régler manuellement 7100 kHz en LSB dans le WebSDR Bordeaux (aucun préréglage automatique)', 'url': 'http://ham.websdrbordeaux.fr:8000/'},
    {'id': 'bordeaux3605', 'name': 'Bordeaux · 3 605 kHz LSB (manuel)', 'category': 'Radioamateurs', 'detail': '80 mètres · fréquence de conversations parfois signalées ; régler manuellement 3605 kHz en LSB', 'url': 'http://ham.websdrbordeaux.fr:8000/'},
    {'id': 'bordeaux14250', 'name': 'Bordeaux · 14 250 kHz USB (manuel)', 'category': 'Radioamateurs', 'detail': '20 mètres · régler manuellement 14250 kHz en USB ; réception et couverture variables', 'url': 'http://ham.websdrbordeaux.fr:8000/'},
    {'id': 'bordeaux-openwebrx-277625', 'name': 'OpenWebRX Bordeaux · 27 762,5 kHz USB', 'category': 'Radioamateurs', 'detail': '27,7625 MHz · USB · squelch -46 · lien avec réglages demandés ; récepteur parfois indisponible', 'url': 'https://openwebrx.websdrbordeaux.fr/#freq=27762500,mod=usb,sql=-46'},
    {'id': 'bordeaux', 'name': 'WebSDR Bordeaux', 'category': 'Radioamateurs', 'detail': 'Récepteur radioamateur de Bordeaux · accès public (disponibilité à vérifier)', 'url': 'http://ham.websdrbordeaux.fr:8000/'},
    {'id': 'twente', 'name': 'WebSDR Twente', 'category': 'Radioamateurs', 'detail': 'Ondes courtes · Récepteur aux Pays-Bas', 'url': 'http://websdr.ewi.utwente.nl:8901/'},
    {'id': 'twente7120', 'name': 'Twente · 7 120 kHz LSB', 'category': 'Radioamateurs', 'detail': 'Fréquence testée · voix en LSB', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=7120lsb'},
    {'id': 'twente14200', 'name': 'Twente · 14 200 kHz USB', 'category': 'Radioamateurs', 'detail': 'Bande des 20 mètres · USB', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=14200usb'},
    {'id': 'websdr', 'name': 'Annuaire WebSDR', 'category': 'Radioamateurs', 'detail': 'Récepteurs publics disponibles dans le monde', 'url': 'https://www.websdr.org/'},
    {'id': 'radiosondy-meb801267', 'name': 'Radiosondy · Sonde MEB801267', 'category': 'Radiosondes météo', 'detail': 'Fiche de suivi d’une radiosonde météorologique · informations variables selon les données disponibles', 'url': 'https://radiosondy.info/sonde.php?sondenumber=MEB801267'},
    {'id': 'radiosondy-meb801258', 'name': 'Radiosondy · Sonde MEB801258', 'category': 'Radiosondes météo', 'detail': 'Fiche de la deuxième radiosonde de Bordeaux · une trajectoire à la fois', 'url': 'https://radiosondy.info/sonde.php?sondenumber=MEB801258'},
    {'id': 'radiosondy-global', 'name': 'Radiosondy · Carte mondiale', 'category': 'Radiosondes météo', 'detail': 'Suivi des ballons-sondes météorologiques et recherche par numéro de sonde', 'url': 'https://radiosondy.info/'},
    {'id': 'aprs-bordeaux', 'name': 'APRS.fi · Bordeaux', 'category': 'Suivi APRS', 'detail': 'Carte APRS centrée sur Bordeaux · balises et positions transmises par stations participantes ; pas un flux audio', 'url': 'https://aprs.fi/#!mt=roadmap&z=11&lat=44.83990&lng=-0.49290'},
    {'id': 'bordeaux-adsb', 'name': 'ADS-B Bordeaux · Suivi des avions', 'category': 'Suivi aérien', 'detail': 'Carte des avions détectés autour de Bordeaux · positions ADS-B, sans audio', 'url': 'https://adsb.websdrbordeaux.fr/?icao=4a8b28'},
    {"id":"flightradar24","name":"Flightradar24","category":"Aviation","detail":"Carte mondiale des vols · certaines fonctions limitées","url":"https://www.flightradar24.com/"},
    {"id":"airplaneslive","name":"Airplanes.live","category":"Aviation","detail":"Suivi ADS-B communautaire · carte du trafic aérien","url":"https://airplanes.live/"},
    {"id":"adsbexchange","name":"ADS-B Exchange","category":"Aviation","detail":"Carte ADS-B mondiale avec filtres avancés","url":"https://globe.adsbexchange.com/"},
    {"id": "n2yo", "name": "N2YO · Suivi des satellites", "category": "Suivi satellites", "detail": "Position orbitale, carte et prévisions de passage", "url": "https://www.n2yo.com/"},
    {"id": "heavens-above", "name": "Heavens-Above · Passages visibles", "category": "Suivi satellites", "detail": "ISS, satellites visibles et horaires de passage selon le lieu", "url": "https://www.heavens-above.com/main.aspx"},
    {"id": "satflare", "name": "Satflare · Trajectoires orbitales", "category": "Suivi satellites", "detail": "Cartes et visualisation des trajectoires de satellites", "url": "https://www.satflare.com/track.asp?cchart=1"},
    {"id": "satnogs", "name": "SatNOGS · Réseau radio satellite", "category": "Suivi satellites", "detail": "Observations radio de satellites par stations au sol", "url": "https://network.satnogs.org/"},
    {'id': 'jfk', 'name': 'New York JFK · LiveATC', 'category': 'Aviation', 'detail': 'Tour, sol, approche · choisir LISTEN sur le site', 'url': 'https://www.liveatc.net/search/?icao=KJFK'},
    {'id': 'atc', 'name': 'LiveATC · Tous les aéroports', 'category': 'Aviation', 'detail': 'Annuaire des communications aériennes', 'url': 'https://www.liveatc.net/feedindex.php'},
    {'id': 'marine-ny', 'name': 'Marine · New York / New Jersey', 'category': 'Marine', 'detail': 'Flux VHF maritime · disponibilité variable', 'url': 'https://www.broadcastify.com/listen/feed/17329'},
    {'id': 'marine-seattle', 'name': 'Marine · Seattle', 'category': 'Marine', 'detail': 'Récepteurs des communications maritimes', 'url': 'https://seattleboatradio.com/'},
    {'id': 'garden', 'name': 'Radio Garden', 'category': 'Radios du monde', 'detail': 'Radios publiques et musicales du monde entier', 'url': 'https://radio.garden/'},
    # Préréglages HF : points de départ, transmissions non garanties.
    {'id': 'twente3690', 'name': 'Twente · 3 690 kHz LSB', 'category': 'Radioamateurs', 'detail': '80 mètres · activité vocale possible en soirée/nuit', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=3690lsb'},
    {'id': 'twente3725', 'name': 'Twente · 3 725 kHz LSB', 'category': 'Radioamateurs', 'detail': '80 mètres · recherche de conversations européennes', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=3725lsb'},
    {'id': 'twente7090', 'name': 'Twente · 7 090 kHz LSB', 'category': 'Radioamateurs', 'detail': '40 mètres · centre d’activité SSB faible puissance', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=7090lsb'},
    {'id': 'twente7135', 'name': 'Twente · 7 135 kHz LSB', 'category': 'Radioamateurs', 'detail': '40 mètres · conversations possibles en Europe', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=7135lsb'},
    {'id': 'twente7150', 'name': 'Twente · 7 150 kHz LSB', 'category': 'Radioamateurs', 'detail': '40 mètres · explorer les échanges vocaux', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=7150lsb'},
    {'id': 'twente7175', 'name': 'Twente · 7 175 kHz LSB', 'category': 'Radioamateurs', 'detail': '40 mètres · liaisons internationales possibles', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=7175lsb'},
    {'id': 'twente14195', 'name': 'Twente · 14 195 kHz USB', 'category': 'Radioamateurs', 'detail': '20 mètres · zone utilisée pour expéditions DX, éviter de perturber les appels', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=14195usb'},
    {'id': 'twente14250', 'name': 'Twente · 14 250 kHz USB', 'category': 'Radioamateurs', 'detail': '20 mètres · écoute internationale en journée', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=14250usb'},
    {'id': 'twente14285', 'name': 'Twente · 14 285 kHz USB', 'category': 'Radioamateurs', 'detail': '20 mètres · centre d’activité SSB faible puissance', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=14285usb'},
    {'id': 'twente21250', 'name': 'Twente · 21 250 kHz USB', 'category': 'Radioamateurs', 'detail': '15 mètres · réception dépendante de la propagation', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=21250usb'},
    {'id': 'twente28450', 'name': 'Twente · 28 450 kHz USB', 'category': 'Radioamateurs', 'detail': '10 mètres · plutôt lorsque la propagation est favorable', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=28450usb'},
    {'id': 'twente198am', 'name': 'Twente · 198 kHz AM', 'category': 'Radios du monde', 'detail': 'Grandes ondes · fréquence historique, émission non garantie', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=198am'},
    {'id': 'twente6070am', 'name': 'Twente · 6 070 kHz AM', 'category': 'Radios du monde', 'detail': 'Ondes courtes · diffusion internationale possible', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=6070am'},
    {'id': 'twente10000am', 'name': 'Twente · 10 000 kHz AM', 'category': 'Radios du monde', 'detail': 'Ondes courtes · signaux horaires possibles selon propagation', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=10000am'},
]


def load_favorites():
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))
        if isinstance(data, list):
            ids = {s['id'] for s in STATIONS}
            return {x for x in data if isinstance(x, str) and x in ids}
    except (OSError, ValueError, TypeError):
        pass
    return {'twente7120', 'jfk', 'marine-ny'}


def save_favorites(favorites):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    temp = CONFIG_FILE.with_suffix('.tmp')
    temp.write_text(json.dumps(sorted(favorites), ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(CONFIG_FILE)


class PatRadio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.favorites = load_favorites()
        self.visible_stations = []
        self.active_category = 'Toutes les catégories'
        self.category_buttons = {}
        self.setWindowTitle('PatRadio v0.4 — Centre d’exploration mondial')
        self.resize(1080, 730)
        self.setMinimumSize(740, 540)
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 14)
        root.setSpacing(12)

        hero = QFrame()
        hero.setObjectName('hero')
        banner = QVBoxLayout(hero)
        banner.setContentsMargins(26, 21, 26, 20)
        title = QLabel('◉  PatRadio')
        title.setObjectName('title')
        banner.addWidget(title)
        intro = QLabel('LE MONDE À PORTÉE D’OREILLE   •   RADIO  /  AVIATION  /  MARINE  /  CARTES')
        intro.setObjectName('intro')
        intro.setWordWrap(True)
        banner.addWidget(intro)
        stats = QHBoxLayout()
        self.stats_label = QLabel()
        self.stats_label.setObjectName('stats')
        stats.addWidget(self.stats_label)
        stats.addStretch()
        banner.addLayout(stats)
        root.addWidget(hero)

        universe_panel = QFrame()
        universe_panel.setObjectName('panel')
        universe_layout = QVBoxLayout(universe_panel)
        universe_layout.setContentsMargins(15, 13, 15, 13)
        universe_layout.setSpacing(9)
        universe_heading = QLabel('CHOISIS TON UNIVERS')
        universe_heading.setObjectName('section')
        universe_layout.addWidget(universe_heading)
        universe_grid = QGridLayout()
        universe_grid.setSpacing(8)
        universes = [
            ('📡', 'Radioamateurs'), ('✈', 'Aviation'),
            ('🛩', 'Suivi aérien'), ('📍', 'Suivi APRS'),
            ('🎈', 'Radiosondes météo'), ('🛰', 'Suivi satellites'),
            ('⚓', 'Marine'), ('🌍', 'Radios du monde'),
        ]
        for index, (symbol, category) in enumerate(universes):
            button = QPushButton(f'{symbol}  {category}')
            button.setObjectName('universe')
            button.setCheckable(True)
            button.setMinimumHeight(40)
            button.clicked.connect(lambda checked=False, name=category: self.set_category(name))
            universe_grid.addWidget(button, index // 4, index % 4)
            self.category_buttons[category] = button
        universe_layout.addLayout(universe_grid)
        tools_bar = QHBoxLayout()
        self.all_button = QPushButton('Tout voir')
        self.all_button.setObjectName('quick')
        self.all_button.clicked.connect(lambda: self.set_category('Toutes les catégories'))
        tools_bar.addWidget(self.all_button)
        self.fav_filter_button = QPushButton('★ Favoris')
        self.fav_filter_button.setObjectName('quick')
        self.fav_filter_button.clicked.connect(lambda: self.set_category('⭐ Favoris'))
        tools_bar.addWidget(self.fav_filter_button)
        self.search = QLineEdit()
        self.search.setPlaceholderText('⌕  Rechercher dans les stations…')
        self.search.textChanged.connect(self.refresh)
        tools_bar.addWidget(self.search, 1)
        universe_layout.addLayout(tools_bar)
        root.addWidget(universe_panel)

        panes = QHBoxLayout()
        panes.setSpacing(12)
        root.addLayout(panes, 1)
        left = QFrame()
        left.setObjectName('panel')
        ll = QVBoxLayout(left)
        ll.setContentsMargins(15, 15, 15, 15)
        heading = QLabel('RADIOAMATEURS')
        self.list_heading = heading
        heading.setObjectName('section')
        ll.addWidget(heading)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self.update_details)
        self.list.itemDoubleClicked.connect(lambda _: self.open_selected())
        ll.addWidget(self.list, 1)
        panes.addWidget(left, 3)

        right = QFrame()
        right.setObjectName('panel')
        rr = QVBoxLayout(right)
        rr.setContentsMargins(18, 16, 18, 18)
        label = QLabel('DÉTAILS & ACCÈS')
        label.setObjectName('section')
        rr.addWidget(label)
        self.detail = QLabel('Sélectionne une station pour la découvrir.')
        self.detail.setObjectName('detail')
        self.detail.setWordWrap(True)
        self.detail.setTextFormat(Qt.TextFormat.RichText)
        rr.addWidget(self.detail, 1)
        self.open_button = QPushButton('↗  Ouvrir dans le navigateur')
        self.open_button.setObjectName('primary')
        self.open_button.clicked.connect(self.open_selected)
        rr.addWidget(self.open_button)
        self.favorite_button = QPushButton('☆  Ajouter aux favoris')
        self.favorite_button.clicked.connect(self.toggle_favorite)
        rr.addWidget(self.favorite_button)
        hint = QLabel('Double-clic pour ouvrir · Les sites externes peuvent parfois être indisponibles.')
        hint.setObjectName('hint')
        hint.setWordWrap(True)
        rr.addWidget(hint)
        panes.addWidget(right, 2)

        self.statusBar().showMessage('Prêt • Explore le monde depuis ton ordinateur')
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#081321; color:#e9f2fa; font-size:14px; }
            QFrame#hero { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #10243d,stop:1 #195678);
                border:1px solid #2c627f; border-radius:18px; }
            QLabel#title { font-size:36px; font-weight:800; color:#f0fbff; background:transparent; }
            QLabel#intro { font-size:12px; font-weight:700; letter-spacing:1px; color:#aee9f7; background:transparent; }
            QLabel#stats { font-size:13px; color:#a4ffdf; background:transparent; padding-top:6px; }
            QFrame#panel { background:#102033; border:1px solid #28435b; border-radius:15px; }
            QLabel#section { color:#76dbef; font-weight:800; font-size:13px; padding:5px; background:transparent; }
            QListWidget, QLineEdit, QComboBox { background:#0b1a2b; color:#f0f8ff;
                border:1px solid #31536e; border-radius:9px; padding:9px; }
            QListWidget::item { padding:12px; margin:3px 0; border-radius:7px; }
            QListWidget::item:selected { background:#1b5e79; color:white; }
            QComboBox QAbstractItemView { background:#102033; color:white; selection-background-color:#1b5e79; }
            QLabel#detail { color:#d7eaf5; background:#0c192a; border:1px solid #28435b;
                border-radius:12px; padding:16px; }
            QLabel#hint { color:#8daabe; font-size:12px; background:transparent; }
            QPushButton { background:#20374e; color:white; border:1px solid #426580;
                border-radius:9px; padding:13px; font-weight:700; }
            QPushButton#primary { background:#087f9c; border-color:#39cee7; }
            QPushButton:hover { background:#2b5771; }
            QPushButton#primary:hover { background:#069abd; }
            QPushButton#universe { background:#142c43; border:1px solid #345570; padding:9px 5px; }
            QPushButton#universe:checked { background:#176783; border:2px solid #64d8ed; color:white; }
            QPushButton#universe:hover { background:#235370; }
            QPushButton#quick { padding:9px 14px; }
            QPushButton#quick[active='true'] { background:#176783; border:1px solid #64d8ed; }
            QPushButton:disabled { color:#72899a; background:#1a2a39; }
            QStatusBar { background:#081321; color:#8ab5cc; }
        """)
        self.refresh()

    def selected(self):
        i = self.list.currentRow()
        return self.visible_stations[i] if 0 <= i < len(self.visible_stations) else None

    def set_category(self, category):
        self.active_category = category
        self.refresh()

    def refresh(self):
        old = self.selected()
        previous_id = old['id'] if old else None
        category = self.active_category
        query = self.search.text().casefold().strip()
        self.visible_stations = [
            station for station in STATIONS
            if (category == 'Toutes les catégories'
                or (category == '⭐ Favoris' and station['id'] in self.favorites)
                or station['category'] == category)
            and query in (' '.join((station['name'], station['category'], station['detail']))).casefold()
        ]
        self.list_heading.setText(category.upper() if category != 'Toutes les catégories' else 'TOUS LES UNIVERS')
        for name, button in self.category_buttons.items():
            button.setChecked(name == category)
        self.all_button.setProperty('active', category == 'Toutes les catégories')
        self.fav_filter_button.setProperty('active', category == '⭐ Favoris')
        for button in (self.all_button, self.fav_filter_button):
            button.style().unpolish(button)
            button.style().polish(button)
        self.list.blockSignals(True)
        self.list.clear()
        for station in self.visible_stations:
            star = '★' if station['id'] in self.favorites else '☆'
            self.list.addItem(QListWidgetItem(f"{star}   {station['name']}\n      {station['category']}  ·  {station['detail']}"))
        selected_index = next((i for i, item in enumerate(self.visible_stations) if item['id'] == previous_id), 0)
        if self.visible_stations:
            self.list.setCurrentRow(selected_index)
        self.list.blockSignals(False)
        self.stats_label.setText(
            f"◉  {len(STATIONS)} raccourcis      ✦  {len(set(x['category'] for x in STATIONS))} univers      ★  {len(self.favorites)} favoris")
        self.update_details()

    def update_details(self, *_):
        station = self.selected()
        self.open_button.setEnabled(bool(station))
        self.favorite_button.setEnabled(bool(station))
        if not station:
            self.detail.setText('Aucune station trouvée. Modifie ta recherche.')
            self.favorite_button.setText('☆  Ajouter aux favoris')
            return
        name = escape(station['name'])
        category = escape(station['category'])
        detail = escape(station['detail'])
        address = escape(station['url'])
        self.detail.setText(
            f"<p style='font-size:21px;color:#ffffff;font-weight:700'>{name}</p>"
            f"<p style='color:#72dded'>{category}</p>"
            f"<p style='color:#d4e6f4'>{detail}</p>"
            f"<p style='font-size:11px;color:#87aabc;overflow-wrap:anywhere'>{address}</p>"
        )
        self.favorite_button.setText(
            '★  Retirer des favoris' if station['id'] in self.favorites else '☆  Ajouter aux favoris')

    def toggle_favorite(self):
        station = self.selected()
        if not station:
            return
        if station['id'] in self.favorites:
            self.favorites.remove(station['id'])
        else:
            self.favorites.add(station['id'])
        try:
            save_favorites(self.favorites)
        except OSError as exc:
            QMessageBox.warning(self, 'PatRadio', f'Impossible de sauvegarder les favoris : {exc}')
        self.refresh()

    def open_selected(self):
        station = self.selected()
        if not station:
            return
        url = station['url']
        if urlparse(url).scheme not in ('http', 'https'):
            QMessageBox.warning(self, 'PatRadio', 'Adresse non prise en charge.')
            return
        # Utilise le navigateur par défaut de Windows, Linux ou macOS.
        if not QDesktopServices.openUrl(QUrl(url)):
            QMessageBox.warning(self, 'PatRadio', 'Ouverture impossible. Vérifie le navigateur par défaut.')
        else:
            self.statusBar().showMessage(f"Ouverture : {station['name']}", 5000)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = PatRadio()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
