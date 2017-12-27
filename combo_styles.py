#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   combo_styles.py por:
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

import globals as G

from gi.repository import Gtk
from gi.repository import GObject


class ComboStyles(Gtk.ToolItem):

    __gsignals__ = {
        "theme-changed": (GObject.SIGNAL_RUN_FIRST, None, [str])
    }

    def __init__(self, selected_style="classic"):
        Gtk.ToolItem.__init__(self)

        self.style_manager = G.STYLE_MANAGER
        self.styles = G.STYLES
        self.combo = Gtk.ComboBoxText()

        for style in self.styles:
            self.combo.append_text(style)

        self.combo.set_active(self.styles.index(selected_style))
        self.combo.connect("changed", self.__theme_changed)

        self.add(self.combo)
        self.show_all()

    def __theme_changed(self, widget):
        self.emit("theme-changed", self.styles[self.combo.get_active()])
