#!/bin/bash
set -e

# Packaging script for NASA Cyber Terminal
# This creates a basic .deb package

APP_NAME="nasa-cyber-terminal"
VERSION="1.0.0"
BUILD_DIR="build_deb"
PKG_DIR="${BUILD_DIR}/${APP_NAME}_${VERSION}_amd64"

# Create directory structure
mkdir -p ${PKG_DIR}/DEBIAN
mkdir -p ${PKG_DIR}/opt/${APP_NAME}
mkdir -p ${PKG_DIR}/usr/share/applications/
mkdir -p ${PKG_DIR}/usr/bin/

# Copy application files
cp -r ../src ../main.py ../requirements.txt ../assets ${PKG_DIR}/opt/${APP_NAME}/

# Setup desktop shortcut
cp nasa-cyber-terminal.desktop ${PKG_DIR}/usr/share/applications/

# Create a symlink in /usr/bin
ln -s /opt/${APP_NAME}/main.py ${PKG_DIR}/usr/bin/nasa-cyber-terminal
chmod +x ${PKG_DIR}/opt/${APP_NAME}/main.py

# Create DEBIAN/control file
cat <<EOF > ${PKG_DIR}/DEBIAN/control
Package: nasa-cyber-terminal
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt6, python3-pip
Maintainer: NASA Terminal Team
Description: Modern futuristic terminal emulator for Linux using PyQt6.
 Features glassmorphism UI, animated cursor, tabs, split panes,
 theming, and full settings panel.
EOF

# Build the .deb
dpkg-deb --build ${PKG_DIR}

echo "Done! The .deb package is located in ${BUILD_DIR}/"
