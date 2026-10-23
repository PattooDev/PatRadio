"""Centre de contrôle indépendant : vols OpenSky, positions réelles."""
import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QPushButton, QVBoxLayout, QWidget


URL = 'https://opensky-network.org/api/states/all?lamin=41&lamax=52&lomin=-6&lomax=10'


class FlightsFetch(QThread):
    success = pyqtSignal(list, int)
    error = pyqtSignal(str)

    def run(self):
        try:
            req = Request(URL, headers={'User-Agent': 'PatRadio/0.5', 'Accept': 'application/json'})
            with urlopen(req, timeout=18) as response:
                data = json.load(response)
            flights = []
            for s in data.get('states') or []:
                if len(s) >= 11 and s[5] is not None and s[6] is not None:
                    flights.append(dict(icao=s[0], name=(s[1] or '').strip() or s[0],
                                        origin=s[2] or 'Inconnu', lon=s[5], lat=s[6],
                                        altitude=s[7], ground=s[8], speed=s[9]))
            self.success.emit(flights, int(data.get('time') or time.time()))
        except HTTPError as e:
            self.error.emit('Quota OpenSky dépassé (HTTP 429).' if e.code == 429
                            else f'OpenSky : erreur HTTP {e.code}.')
        except (URLError, TimeoutError, ValueError, OSError) as e:
            self.error.emit(f'Données indisponibles : {e}')


class AirMap(QWidget):
    def __init__(self):
        super().__init__()
        self.flights = []
        self.selected = None
        self.setMinimumSize(440, 320)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor('#0a2336'))
        w, h = self.width(), self.height()
        p.setPen(QPen(QColor('#30566d'), 1))
        for longitude in range(-6, 11, 2):
            x = int((longitude + 6) / 16 * w)
            p.drawLine(x, 0, x, h)
        for latitude in range(42, 53, 2):
            y = int((52 - latitude) / 11 * h)
            p.drawLine(0, y, w, y)
        p.setPen(QColor('#a8c4d5'))
        p.drawText(12, 20, 'EUROPE OCCIDENTALE · GRILLE GÉOGRAPHIQUE')
        p.drawText(12, h - 12, 'Positions OpenSky, sans fond cartographique')
        for f in self.flights:
            x = int((f['lon'] + 6) / 16 * w)
            y = int((52 - f['lat']) / 11 * h)
            p.setPen(QColor('#fbbf24' if f['icao'] == self.selected else '#58d6f6'))
            p.setBrush(QColor('#fbbf24' if f['icao'] == self.selected else '#58d6f6'))
            p.drawEllipse(x - 3, y - 3, 6, 6)
            if f['icao'] == self.selected:
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(x - 10, y - 10, 20, 20)


class ControlCenter(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('PatRadio · Centre de contrôle')
        self.resize(1080, 650)
        self.flights = []
        self.last_query = 0.0
        self.worker = None
        self.setStyleSheet("""
            QDialog { background:#081321; color:#e9f2fa; }
            QLabel { color:#c8e0ee; }
            QListWidget { background:#102638; color:#e9f2fa; border:1px solid #34546c; }
            QPushButton { background:#175678; color:white; padding:10px;
                          border:1px solid #419bb9; border-radius:6px; }
            QPushButton:disabled { background:#344553; color:#91a3ae; }
        """)
        root = QVBoxLayout(self)
        root.addWidget(QLabel('◉  PATRADIO CONTROL CENTER · PREMIÈRE SOURCE : OPENSKY'))
        root.addWidget(QLabel('Avions réellement détectés · aucune position fictive'))
        row = QHBoxLayout()
        root.addLayout(row, 1)
        self.map = AirMap()
        row.addWidget(self.map, 3)
        sidebar = QVBoxLayout()
        row.addLayout(sidebar, 2)
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self.select_flight)
        sidebar.addWidget(self.list)
        self.details = QLabel('Clique sur « Actualiser » puis sélectionne un avion.')
        self.details.setWordWrap(True)
        sidebar.addWidget(self.details)
        self.button = QPushButton('↻  Actualiser les avions')
        self.button.clicked.connect(self.refresh)
        sidebar.addWidget(self.button)
        self.status = QLabel('Prêt · actualisation manuelle espacée de 15 minutes.')
        self.status.setWordWrap(True)
        root.addWidget(self.status)

    def refresh(self):
        remaining = 900 - (time.monotonic() - self.last_query)
        if self.last_query and remaining > 0:
            self.status.setText(f'Protection du quota : attendre {int(remaining / 60) + 1} min.')
            return
        self.last_query = time.monotonic()
        self.button.setEnabled(False)
        self.status.setText('Interrogation OpenSky…')
        self.worker = FlightsFetch()
        self.worker.success.connect(self.received)
        self.worker.error.connect(self.failed)
        self.worker.finished.connect(lambda: self.button.setEnabled(True))
        self.worker.start()

    def received(self, flights, timestamp):
        self.flights = flights
        self.list.clear()
        self.list.addItems([f"{f['name']} · {f['origin']}" for f in flights])
        self.map.flights = flights
        self.map.selected = None
        self.map.update()
        self.details.setText('Sélectionne un avion pour sa fiche.')
        stamp = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(timestamp))
        self.status.setText(f'{len(flights)} avions · données datées du {stamp} · source OpenSky')

    def failed(self, message):
        self.status.setText(message + ' Aucune nouvelle position affichée.')

    def select_flight(self, index):
        if not 0 <= index < len(self.flights):
            return
        f = self.flights[index]
        self.map.selected = f['icao']
        self.map.update()
        altitude = ('au sol' if f['ground'] else f"{f['altitude']:.0f} m"
                    if f['altitude'] is not None else 'inconnue')
        speed = f"{f['speed'] * 3.6:.0f} km/h" if f['speed'] is not None else 'inconnue'
        self.details.setText(
            f"{f['name']} ({f['icao']})\nOrigine : {f['origin']}\n"
            f"Latitude : {f['lat']:.4f}°\nLongitude : {f['lon']:.4f}°\n"
            f"Altitude : {altitude}\nVitesse : {speed}"
        )
