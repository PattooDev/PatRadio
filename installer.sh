#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"
if ! /usr/bin/python3 -c 'from PyQt6.QtWidgets import QApplication' 2>/dev/null; then
  echo 'PyQt6 manque. Sur Deepin, essayer : sudo apt install python3-pyqt6'
  echo 'Puis relancer ./installer.sh'
  exit 1
fi
TARGET="${HOME}/.local/share/patradio"
mkdir -p "$TARGET" "${HOME}/.local/bin" "${HOME}/.local/share/applications"
cp patradio/app.py "$TARGET/app.py"
cat > "${HOME}/.local/bin/patradio" <<'EOF'
#!/usr/bin/env bash
exec /usr/bin/python3 "${HOME}/.local/share/patradio/app.py" "$@"
EOF
chmod +x "${HOME}/.local/bin/patradio"
cat > "${HOME}/.local/share/applications/patradio.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PatRadio
Comment=Centre d'écoute mondial par Pattoo
Exec=${HOME}/.local/bin/patradio
Icon=audio-headphones
Terminal=false
Categories=Audio;AudioVideo;Network;
StartupNotify=true
EOF
chmod +x "${HOME}/.local/share/applications/patradio.desktop"
echo 'PatRadio est installé dans le menu des applications.'
echo "Lancement : ${HOME}/.local/bin/patradio"
