# PatRadio v0.2 — Stations préréglées

Application indépendante pour Deepin 25, basée sur Python et PyQt6. Les réglages connus de la v0.1 sont conservés.

## Installation / mise à jour

Ferme PatRadio, puis lance `./installer.sh` dans ce dossier. Le lanceur existant est mis à jour.

**Favoris préservés** : `~/.config/patradio/favorites.json` n'est ni effacé ni modifié par l'installateur. Les identifiants des stations v0.1 sont inchangés.

## Nouveautés

- 14 raccourcis supplémentaires avec fréquence et mode présélectionnés sur WebSDR Twente.
- Couverture des bandes radioamateurs 80 m, 40 m, 20 m, 15 m et 10 m.
- Quelques fréquences en AM, pour essayer les ondes courtes.
- Recherche, filtres et favoris persistants restent inchangés.
- Double-clic sur une ligne ou bouton « Ouvrir dans Firefox ».

**Attention :** ce sont des fréquences d'exploration, pas des stations fixes ni la promesse d'émissions en permanence. Certaines fréquences peuvent être muettes. Les liens WebSDR sont en HTTP, comme le récepteur Twente utilisé lors des essais.

## Dépendances

`python3-pyqt6`. Aucune modification de PatDesk, aucun privilège administrateur demandé par l'installateur lui-même.

## Licence

© 2026 Patrick « Pattoo » Ventresque (PattooDev). GNU GPL v3 ou ultérieure. Voir LICENSE.
