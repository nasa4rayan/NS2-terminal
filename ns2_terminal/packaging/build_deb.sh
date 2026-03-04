#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════
# NS2 Terminal – Debian Package Builder
# ═══════════════════════════════════════════════════════════════════════

APP_NAME="ns2-terminal"
VERSION="2.0.0"
BUILD_DIR="build_deb"
PKG_DIR="${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64"

echo "🔷 Building NS2 Terminal v${VERSION} .deb package..."

# Clean old builds
rm -rf ${BUILD_DIR}

# Create directory structure
mkdir -p ${PKG_DIR}/DEBIAN
mkdir -p ${PKG_DIR}/opt/${APP_NAME}
mkdir -p ${PKG_DIR}/usr/share/applications/
mkdir -p ${PKG_DIR}/usr/bin/

# Copy application files
cp -r \
    ../main.py \
    ../config_manager.py \
    ../__init__.py \
    ../requirements.txt \
    ../core \
    ../themes \
    ../settings \
    ../ui \
    ../assets \
    ${PKG_DIR}/opt/${APP_NAME}/

# Desktop entry
cp ns2-terminal.desktop ${PKG_DIR}/usr/share/applications/

# Launcher script
cat <<'LAUNCHER' > ${PKG_DIR}/usr/bin/ns2-terminal
#!/bin/bash
cd /opt/ns2-terminal
exec python3 -m ns2_terminal.main "$@"
LAUNCHER
chmod +x ${PKG_DIR}/usr/bin/ns2-terminal

# Make main.py executable too
chmod +x ${PKG_DIR}/opt/${APP_NAME}/main.py

# DEBIAN control file
cat <<EOF > ${PKG_DIR}/DEBIAN/control
Package: ns2-terminal
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.10), python3-pyqt6, python3-pip
Maintainer: NS2 Terminal Team
Description: NS2 Terminal – Premium Futuristic Terminal Emulator
 A next-generation terminal emulator for Linux featuring glassmorphism UI,
 animated cursor, tabs, split panes, command palette, particle effects,
 multiple themes, and full customization via settings panel.
 Built with PyQt6 and pyte.
Homepage: https://github.com/ns2-terminal
EOF

# Build .deb
dpkg-deb --build ${PKG_DIR}

echo ""
echo "✅ Package built: ${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb"
echo ""
echo "Install with:"
echo "  sudo apt install ./${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64.deb"
