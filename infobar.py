#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   infobar.py por:
#   Cristian García <cristian99garcia@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gettext import gettext as _

import globals as G

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GtkSource


class InfoBar(Gtk.HBox):

    __gsignals__ = {
        "language-changed": (GObject.SIGNAL_RUN_FIRST, None, [str])
    }

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.language = None
        self.languages = [_("Plain text")]
        self.language_manager = GtkSource.LanguageManager()
        self.languages.extend(
            self.language_manager.get_language_ids())

        self.combo = Gtk.ComboBoxText()

        for language in self.languages:
            self.combo.append_text(language)

        self.combo.set_active(0)
        self.combo.connect("changed", self.__combo_changed)
        self.pack_end(self.combo, False, False, 10)

        self.label_pos = Gtk.Label()
        self.pack_end(self.label_pos, False, False, 0)

        self.set_pos(1, 1)

    def set_pos(self, line, column):
        self.label_pos.set_label(_("Line: %s, Column: %s") % (line, column))

    def set_language(self, language):
        if language != _("Plain text"):
            language = language.lower()
            if language in G.BAD_LANGUAGES:
                language = G.BAD_LANGUAGES[language]

        self.language = language
        self.combo.set_active(self.languages.index(self.language))

    def __combo_changed(self, combo):
        if self.language == self.languages[combo.get_active()]:
            return

        self.language = self.languages[combo.get_active()]
        self.emit("language-changed", self.language)
