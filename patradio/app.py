#!/usr/bin/env python3
"""PatRadio - portail personnel d'écoute radio (sans réception locale)."""
import json
import os
import sys
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QLineEdit, QComboBox,
    QMessageBox, QFrame
)

APP_NAME = 'PatRadio'
CONFIG_DIR = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'patradio'
CONFIG_FILE = CONFIG_DIR / 'favorites.json'
STATIONS = [
    {'id': 'twente', 'name': 'WebSDR Twente', 'category': 'Radioamateurs', 'detail': 'Ondes courtes · Récepteur aux Pays-Bas', 'url': 'http://websdr.ewi.utwente.nl:8901/'},
    {'id': 'twente7120', 'name': 'Twente · 7 120 kHz LSB', 'category': 'Radioamateurs', 'detail': 'Fréquence testée · voix en LSB', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=7120lsb'},
    {'id': 'twente14200', 'name': 'Twente · 14 200 kHz USB', 'category': 'Radioamateurs', 'detail': 'Bande des 20 mètres · USB', 'url': 'http://websdr.ewi.utwente.nl:8901/?tune=14200usb'},
    {'id': 'websdr', 'name': 'Annuaire WebSDR', 'category': 'Radioamateurs', 'detail': 'Récepteurs publics disponibles dans le monde', 'url': 'https://www.websdr.org/'},
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
        self.setWindowTitle('PatRadio v0.2 — Centre d’écoute mondial')
        self.resize(860, 630)
        self.setMinimumSize(650, 490)
        container = QWidget()
        self.setCentralWidget(container)
        root = QVBoxLayout(container)
        root.setContentsMargins(25, 22, 25, 18)
        root.setSpacing(14)

        title = QLabel('📻  PatRadio')
        title.setObjectName('title')
        root.addWidget(title)
        subtitle = QLabel('Ton centre d’écoute mondial · Deepin Linux · 100 % gratuit')
        subtitle.setObjectName('subtitle')
        root.addWidget(subtitle)

        filters = QHBoxLayout()
        self.category = QComboBox()
        self.category.addItems(['Toutes les catégories', '⭐ Favoris', 'Radioamateurs', 'Aviation', 'Marine', 'Radios du monde'])
        self.category.currentIndexChanged.connect(self.refresh)
        filters.addWidget(self.category, 1)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Rechercher une station…')
        self.search.textChanged.connect(self.refresh)
        filters.addWidget(self.search, 2)
        root.addLayout(filters)

        self.list = QListWidget()
        self.list.setAlternatingRowColors(True)
        self.list.currentRowChanged.connect(self.update_details)
        self.list.itemDoubleClicked.connect(lambda _: self.open_selected())
        root.addWidget(self.list, 1)

        self.detail = QLabel('Choisis une station pour afficher ses informations.')
        self.detail.setWordWrap(True)
        self.detail.setObjectName('detail')
        root.addWidget(self.detail)

        actions = QHBoxLayout()
        self.open_button = QPushButton('▶  Ouvrir dans Firefox')
        self.open_button.setObjectName('primary')
        self.open_button.clicked.connect(self.open_selected)
        actions.addWidget(self.open_button)
        self.favorite_button = QPushButton('☆  Ajouter aux favoris')
        self.favorite_button.clicked.connect(self.toggle_favorite)
        actions.addWidget(self.favorite_button)
        root.addLayout(actions)

        note = QLabel('Les flux sont fournis par des sites tiers : aucune réception radio locale ni disponibilité garantie.')
        note.setWordWrap(True)
        note.setObjectName('subtitle')
        root.addWidget(note)
        self.statusBar().showMessage('Prêt · Double-clique sur une station pour l’ouvrir')
        self.setStyleSheet('''
          QMainWindow, QWidget { background:#101923; color:#e4eef5; font-size:14px; }
          QLabel#title { font-size:32px; font-weight:800; color:#44d1e6; }
          QLabel#subtitle { color:#9db3c4; font-size:12px; }
          QLabel#detail { background:#1b2936; border:1px solid #304454; border-radius:9px; padding:12px; }
          QComboBox, QLineEdit, QListWidget { background:#192634; color:#eaf5fc; border:1px solid #375065; border-radius:8px; padding:8px; }
          QListWidget::item { padding:13px; border-bottom:1px solid #2a3b4c; }
          QListWidget::item:selected { background:#195269; color:white; }
          QListWidget::item:alternate { background:#14212d; }
          QComboBox QAbstractItemView { background:#192634; color:white; selection-background-color:#195269; }
          QPushButton { background:#263c4b; color:#edf8ff; padding:12px; border:1px solid #456176; border-radius:8px; font-weight:600; }
          QPushButton#primary { background:#067a91; border-color:#159fb9; }
          QPushButton:hover { background:#36718a; }
          QPushButton:disabled { color:#698191; background:#202c36; }
          QStatusBar { color:#97b1bf; }
        ''')
        self.refresh()

    def selected(self):
        i = self.list.currentRow()
        return self.visible_stations[i] if 0 <= i < len(self.visible_stations) else None

    def refresh(self):
        previous = self.selected()
        prev_id = previous['id'] if previous else None
        category = self.category.currentText()
        search = self.search.text().casefold().strip()
        self.visible_stations = [s for s in STATIONS if
            (category == 'Toutes les catégories' or
             (category == '⭐ Favoris' and s['id'] in self.favorites) or
             s['category'] == category) and
            search in (' '.join((s['name'], s['category'], s['detail']))).casefold()]
        self.list.clear()
        for s in self.visible_stations:
            icon = '★' if s['id'] in self.favorites else '☆'
            self.list.addItem(QListWidgetItem(f"{icon}   {s['name']}    ·    {s['category']}"))
        index = next((i for i, s in enumerate(self.visible_stations) if s['id'] == prev_id), 0)
        if self.visible_stations:
            self.list.setCurrentRow(index)
        self.update_details()

    def update_details(self, *_):
        station = self.selected()
        self.open_button.setEnabled(bool(station))
        self.favorite_button.setEnabled(bool(station))
        if station:
            self.detail.setText(f"{station['name']}\n{station['detail']}\n{station['url']}")
            self.favorite_button.setText('★  Retirer des favoris' if station['id'] in self.favorites else '☆  Ajouter aux favoris')
        else:
            self.detail.setText('Aucune station trouvée.')
            self.favorite_button.setText('☆  Ajouter aux favoris')

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
        # Le navigateur par défaut de Deepin est utilisé (Firefox s'il est défini par défaut).
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
