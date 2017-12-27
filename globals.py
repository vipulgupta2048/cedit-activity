#!/usr/bin/env python

import os
from gettext import gettext as _
from ConfigParser import ConfigParser

from gi.repository import Gdk
from gi.repository import GtkSource

from sugar3 import env

TEXT_FILE_NOT_SAVED = _("This file has not saved.")
TEXT_MUST_SAVE = _("You must save this file to print.")
TEXT_SAVE_FILE = _("Save changes to document **** before closing?")
TEXT_IF_NOT_SAVE = _("If you do not save, changes will be lost forever.")
TEXT_HAVE_NOT_PERMISSIONS = _("You do not have sufficient permissions to write this file")
TEXT_SAVE_CHANGES_QUESTION = _("Save changes to document **** before closing?")
TEXT_LOST_FOREVER = _("If you do not save, changes will be lost forever.")
TEXT_FILE_NOT_EXISTS1 = _("This file not exists.")
TEXT_FILE_NOT_EXISTS2 = _("Apparently you've selected a file that does not exist.")
TEXT_ERROR_CREATING_FOLDER = _("Error creating the folder.")
TEXT_FILE_ALREADY_EXISTS = _("This file is already exists.")
TEXT_OVERWRITE_QUESTION = _("**** already exists. Overwrite it?")

ICONS = os.path.join(os.path.dirname(__file__), "icons/")

FOLDER = os.path.join(ICONS, "folder.svg")
HOME = os.path.join(ICONS, "folder-home.svg")
DESKTOP = os.path.join(ICONS, "folder-desktop.svg")
DOCUMENTS = os.path.join(ICONS, "folder-documents.svg")
DOWNLOAD = os.path.join(ICONS, "folder-download.svg")
PICTURES = os.path.join(ICONS, "folder-pictures.svg")
MUSIC = os.path.join(ICONS, "folder-music.svg")
VIDEO = os.path.join(ICONS, "folder-video.svg")
MOUNT = os.path.join(ICONS, "pendrive.svg")

TEXT = os.path.join(ICONS, "plain.svg")
PYTHON = os.path.join(ICONS, "python.svg")
EXECUTABLE = os.path.join(ICONS, "executable.svg")
PDF = os.path.join(ICONS, "pdf.svg")
COMPRESSED = os.path.join(ICONS, "compressed.svg")
FOLDER_LINK = os.path.join(ICONS, "inode-symlink.svg")
UNKNOWN = os.path.join(ICONS, "unknown.svg")

IMAGES = {
    "user-home": HOME,
    "user-desktop": DESKTOP,
    "folder-documents": DOCUMENTS,
    "folder-download": DOWNLOAD,
    "folder-pictures": PICTURES,
    "folder-music": MUSIC,
    "folder-videos": VIDEO,
    "folder": FOLDER,

    "text-x-generic": TEXT,
    "text-x-python": PYTHON,
    "application-x-python-bytecode": PYTHON,
    "application-x-executable": EXECUTABLE,
    "application-x-shellscript": EXECUTABLE,
    "application-x-m4": EXECUTABLE,
    "text-x-script": EXECUTABLE,
    "package-x-generic": COMPRESSED,
    "inode-symlink": FOLDER_LINK,
    "application-pdf": PDF
}


LANGUAGE_MANAGER = GtkSource.LanguageManager()
LANGUAGES = LANGUAGE_MANAGER.get_language_ids()
STYLE_MANAGER = GtkSource.StyleSchemeManager()
STYLES = STYLE_MANAGER.get_scheme_ids()

STYLES_PATH = os.path.join(os.path.dirname(__file__), "styles/")
STYLE_MANAGER = GtkSource.StyleSchemeManager()
STYLE_MANAGER.append_search_path(STYLES_PATH)
STYLES = STYLE_MANAGER.get_scheme_ids()

# FIXME: Maybe there are many more exceptions.
BAD_LANGUAGES = {
    "c++": "cpp",
    ".desktop": "desktop",
    "marcar": "markdown"
}

screen = Gdk.Screen().get_default()
WIDTH = (screen.get_width() / 6) * 5
HEIGHT = (screen.get_height() / 6) * 5

DEFAULT_FONTS = ["Sans", "Serif", "Monospace"]
USER_FONTS_FILE_PATH = env.get_profile_path("fonts")
GLOBAL_FONTS_FILE_PATH = "/etc/sugar_fonts"

