import os, subprocess, shutil
from configparser import ConfigParser
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from constants import POSSIBLE_INSTALL_LOCATIONS, CONFIG_FILE, PALETTE_DARK


def apply_dark_theme(app):
    """
    Apply custom dark mode to Qt application when not using KDE Plasma
    and a dark GTK theme is selected (name ends with '-dark')
    """
    theme = config_theme()

    if theme == 'light':
        app.setStyle('Fusion')
        app.setPalette(QStyleFactory.create('fusion').standardPalette())
    elif theme == 'dark':
        app.setStyle('Fusion')
        app.setPalette(PALETTE_DARK())
    else:
        is_plasma = 'plasma' in os.environ.get('DESKTOP_SESSION', '')
        darkmode_enabled = False
        try:
            ret = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True).stdout.decode('utf-8').strip().strip("'").lower()
            if ret.endswith('-dark'):
                darkmode_enabled = True
        except:
            pass
        if not is_plasma and darkmode_enabled:
            app.setStyle('Fusion')
            app.setPalette(PALETTE_DARK())
        elif is_plasma:
            pass


def config_theme(theme=None):
    """
    Return Type: str
    """
    config = ConfigParser()

    if theme:
        config.read(CONFIG_FILE)
        if not config.has_section('pupgui2'):
            config.add_section('pupgui2')
        config['pupgui2']['theme'] = theme
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as file:
            config.write(file)
    elif os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if config.has_option('pupgui2', 'theme'):
            return config['pupgui2']['theme']
    return theme


def create_steam_compatibilitytools_folder():
    """
    Create Steam compatibilitytools.d folder if Steam is installed but folder doesn't exist
    """
    for loc in POSSIBLE_INSTALL_LOCATIONS:
        if loc['launcher'] == 'steam':
            install_dir = os.path.expanduser(loc['install_dir'])
            if os.path.exists(install_dir.replace('compatibilitytools.d/', '')) and not os.path.exists(install_dir):
                os.mkdir(install_dir)


def available_install_directories():
    """
    List available install directories
    Return Type: str[]
    """
    available_dirs = []
    for loc in POSSIBLE_INSTALL_LOCATIONS:
        install_dir = os.path.expanduser(loc['install_dir'])
        if os.path.exists(install_dir):
            available_dirs.append(install_dir)
    return available_dirs


def get_install_location_from_directory_name(install_dir):
    """
    Get install location dict from install directory name
    Return Type: dict
    """
    for loc in POSSIBLE_INSTALL_LOCATIONS:
        if os.path.expanduser(install_dir) == os.path.expanduser(loc['install_dir']):
            return loc
    return {'install_dir': install_dir, 'display_name': 'unknown', 'launcher': ''}


# modified install_directory function from protonup 0.1.4
def install_directory(target=None):
    """
    Custom install directory
    Return Type: str
    """
    config = ConfigParser()

    if target and target.lower() != 'get':
        if target.lower() == 'default':
            target = POSSIBLE_INSTALL_LOCATIONS[0]['install_dir']
        if not target.endswith('/'):
            target += '/'
        config.read(CONFIG_FILE)
        if not config.has_section('pupgui'):
            config.add_section('pupgui')
        config['pupgui']['installdir'] = target
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as file:
            config.write(file)
    elif os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if config.has_option('pupgui', 'installdir'):
            target = os.path.expanduser(config['pupgui']['installdir'])

    if target in available_install_directories():
        return target
    elif len(available_install_directories()) > 0:
        install_directory(available_install_directories()[0])
        return available_install_directories()[0]
    return ''


def list_installed_ctools(install_dir):
        """
        List installed compatibility tool versions
        Return Type: str[]
        """
        versions_found = []

        if os.path.exists(install_dir):
            folders = os.listdir(install_dir)
            for folder in folders:
                ver_file = os.path.join(install_dir, folder, 'VERSION.txt')
                if os.path.exists(ver_file):
                    with open(ver_file, 'r') as f:
                        ver = f.read()
                    versions_found.append(folder + ' - ' + ver.strip())
                else:
                    versions_found.append(folder)

        return versions_found


def remove_ctool(ver, install_dir):
    """
    Remove compatibility tool folder
    Return Type: bool
    """
    target = os.path.join(install_dir, ver.split(' - ')[0])
    if os.path.exists(target):
        shutil.rmtree(target)
        return True
    return False
