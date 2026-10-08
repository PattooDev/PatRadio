# PatRadio v0.3 — Linux, Windows et macOS

**PatRadio** est un centre d'écoute radio gratuit en Python/PyQt6. Il ouvre dans le navigateur par défaut des récepteurs et flux publics (radioamateurs, aviation, marine, radios internationales).

## Fonctions
- Stations et fréquences préréglées, avec choix du mode quand le récepteur l'accepte
- Recherche, filtres et double-clic pour ouvrir une station
- Favoris enregistrés localement et conservés après fermeture
- Application indépendante, sans modification de PatDesk
- Aucun matériel radio supplémentaire nécessaire pour consulter les récepteurs distants

## Linux / Deepin 25 — testé
Conserver l'installation existante :
```bash
sudo apt install python3-pyqt6
./installer.sh
```
Les favoris sont conservés dans `~/.config/patradio/favorites.json` (ou sous `XDG_CONFIG_HOME`).

## Windows 10/11 — version source à tester
Installer Python 3 depuis python.org, avec le lanceur `py` disponible, puis télécharger/extraire ce dépôt et double-cliquer sur **lancer-windows.bat**. Le script crée un environnement Python local, installe PyQt6 et démarre PatRadio. Une connexion Internet est nécessaire à la première exécution.

Alternative en ligne de commande :
```powershell
py -m pip install PyQt6
py patradio/app.py
```
Les favoris Windows sont enregistrés dans `%APPDATA%\PatRadio\favorites.json`.

**Il n'existe pas encore de .exe autonome validé.** Cette méthode Windows n'a pas encore été testée sur une machine Windows réelle.

## macOS — version source à tester
Installer Python 3 et PyQt6, puis lancer :
```bash
python3 -m pip install PyQt6
python3 patradio/app.py
```
Sur macOS les favoris utilisent par défaut `~/.config/patradio/favorites.json`. Pas de paquet .app testé.

## Limites
PatRadio n'est pas un récepteur SDR local. Il dépend des sites externes, de leur disponibilité et de leurs conditions d'accès. L'audio est déclenché dans le navigateur si nécessaire. Les fréquences indiquées sont des points d'exploration et ne garantissent pas une conversation active.

## Licence
© 2026 Patrick « Pattoo » Ventresque (PattooDev). GNU GPL version 3 ou ultérieure. Voir [LICENSE](LICENSE).
