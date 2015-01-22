#!/usr/bin/env python

import os
from gettext import gettext as _
from ConfigParser import ConfigParser

from gi.repository import Gio
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GtkSource

TEXT_FILE_NOT_SAVED = _('This file has not saved.')
TEXT_MUST_SAVE = _('You must save this file to print.')
TEXT_SAVE_FILE = _('Save changes to document **** before closing?')
TEXT_IF_NOT_SAVE = _('If you do not save, changes will be lost forever.')
TEXT_HAVE_NOT_PERMISSIONS = _(
    'You do not have sufficient permissions to write this file')
TEXT_SAVE_CHANGES_QUESTION = _('Save changes to document **** before closing?')
TEXT_LOST_FOREVER = _('If you do not save, changes will be lost forever.')
TEXT_FILE_NOT_EXISTS1 = _('This file not exists.')
TEXT_FILE_NOT_EXISTS2 = _(
    "Apparently you've selected a file that does not exist.")
TEXT_ERROR_CREATING_FOLDER = _('Error creating the folder.')
TEXT_FILE_ALREADY_EXISTS = _('This file is already exists.')
TEXT_OVERWRITE_QUESTION = _('**** already exists, Overwrite it?')

ICONS = os.path.join(os.path.dirname(__file__), 'icons/')

FOLDER = os.path.join(ICONS, 'folder.svg')
HOME = os.path.join(ICONS, 'folder-home.svg')
DESKTOP = os.path.join(ICONS, 'folder-desktop.svg')
DOCUMENTS = os.path.join(ICONS, 'folder-documents.svg')
DOWNLOAD = os.path.join(ICONS, 'folder-download.svg')
PICTURES = os.path.join(ICONS, 'folder-pictures.svg')
MUSIC = os.path.join(ICONS, 'folder-music.svg')
VIDEO = os.path.join(ICONS, 'folder-video.svg')
MOUNT = os.path.join(ICONS, 'pendrive.svg')

TEXT = os.path.join(ICONS, 'plain.svg')
PYTHON = os.path.join(ICONS, 'python.svg')
EXECUTABLE = os.path.join(ICONS, 'executable.svg')
PDF = os.path.join(ICONS, 'pdf.svg')
COMPRESSED = os.path.join(ICONS, 'compressed.svg')
FOLDER_LINK = os.path.join(ICONS, 'inode-symlink.svg')
UNKNOWN = os.path.join(ICONS, 'unknown.svg')

IMAGES = {'user-home': HOME,
          'user-desktop': DESKTOP,
          'folder-documents': DOCUMENTS,
          'folder-download': DOWNLOAD,
          'folder-pictures': PICTURES,
          'folder-music': MUSIC,
          'folder-videos': VIDEO,
          'folder': FOLDER,

          'text-x-generic': TEXT,
          'text-x-python': PYTHON,
          'application-x-python-bytecode': PYTHON,
          'application-x-executable': EXECUTABLE,
          'application-x-shellscript': EXECUTABLE,
          'application-x-m4': EXECUTABLE,
          'text-x-script': EXECUTABLE,
          'package-x-generic': COMPRESSED,
          'inode-symlink': FOLDER_LINK,
          'application-pdf': PDF}


LANGUAGE_MANAGER = GtkSource.LanguageManager()
LANGUAGES = LANGUAGE_MANAGER.get_language_ids()
STYLE_MANAGER = GtkSource.StyleSchemeManager()
STYLES = STYLE_MANAGER.get_scheme_ids()

STYLES_PATH = os.path.join(os.path.dirname(__file__), 'styles/')
STYLE_MANAGER = GtkSource.StyleSchemeManager()
STYLE_MANAGER.append_search_path(STYLES_PATH)
STYLES = STYLE_MANAGER.get_scheme_ids()

# FIXME: There must be many more exceptions.
BAD_LANGUAGES = {'c++': 'cpp',
                 '.desktop': 'desktop',
                 'marcar': 'markdown'}


def get_pixbuf_from_path(path, size=62):
    icon_theme = Gtk.IconTheme()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(UNKNOWN, size, size)

    if '/' in path:
        _file = Gio.File.new_for_path(path)
        info = _file.query_info(
            'standard::icon', Gio.FileQueryInfoFlags.NOFOLLOW_SYMLINKS, None)
        icon = info.get_icon()
        types = icon.get_names()

        # print path, types

        if os.path.ismount(path):
            return GdkPixbuf.Pixbuf.new_from_file_at_size(MOUNT, size, size)

        if 'image-x-generic' in types:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)

        for tipo in types:
            if tipo in IMAGES.keys():
                return GdkPixbuf.Pixbuf.new_from_file_at_size(
                    IMAGES[tipo], size, size)

        if path.endswith('.desktop'):
            cfg = ConfigParser.ConfigParser()
            cfg.read([path])

            if cfg.has_option('Desktop Entry', 'Icon'):
                if '/' in cfg.get('Desktop Entry', 'Icon'):
                    d = cfg.get('Desktop Entry', 'Icon')
                    return GdkPixbuf.Pixbuf.new_from_file_at_size(d, size, size)

                else:
                    return icon_theme.load_icon(
                        cfg.get('Desktop Entry', 'Icon'), size, 0)

            else:
                return icon_theme.load_icon(icon, size, 0)

        else:
            try:
                return icon_theme.choose_icon(types, size, 0).load_icon()

            except:
                #pixbuf = icon_theme.load_icon(icon, size, 0)
                pass

    return pixbuf


def get_language_from_file(path):
    language = LANGUAGE_MANAGER.guess_language(path, None)

    if not language:
        type = Gio.content_type_guess(path, [])[0]

        if 'x-' in type:
            type = type.replace('x-', '')
        if 'text/' in type:
            type = type.replace('text/', '')
        if type == 'shellscript':
            type = 'sh'

        language = LANGUAGE_MANAGER.get_language(type)

    return language


def get_path_access(path):
    #  R_OK = Readable, W_OK = Writable
    return os.access(path, os.R_OK), os.access(path, os.W_OK)
