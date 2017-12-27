#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   spinner.py por:
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

from gi.repository import Gtk
from gi.repository import Pango
from gi.repository import GObject

from sugar3.graphics import style


class Spinner(Gtk.ToolItem):

    __gsignals__ = {
        "value-changed": (GObject.SignalFlags.RUN_LAST, None, [int]),
    }

    def __init__(self, value, min_value, max_value):
        Gtk.ToolItem.__init__(self)

        self.actual_value = value
        self.min_value = min_value
        self.max_value = max_value

        if style.zoom(100) == 100:
            subcell_size = 15
            default_padding = 6

        else:
            subcell_size = 11
            default_padding = 4

        vbox = Gtk.VBox()
        self.add(vbox)

        hbox = Gtk.HBox()
        hbox.set_spacing(0)
        hbox.set_can_focus(True)
        vbox.pack_start(hbox, True, True, default_padding)

        self.button_down = Gtk.Button()
        self.button_down.set_can_focus(False)
        self.button_down.set_size_request(30, -1)
        self.button_down.connect("clicked", self.__number_changed, False)
        hbox.pack_start(self.button_down, False, False, 5)

        label = Gtk.Label("-")
        label.modify_font(Pango.FontDescription("Bold 14"))
        self.button_down.add(label)

        self.label = Gtk.Label()
        self.label.set_text(str(self.actual_value))
        self.label.set_size_request(20, -1)
        self.label.modify_font(Pango.FontDescription("Bold 14"))
        hbox.pack_start(self.label, False, False, 10)

        self.button_up = Gtk.Button()
        self.button_up.set_can_focus(False)
        self.button_up.set_size_request(30, -1)
        self.button_up.connect("clicked", self.__number_changed, True)
        hbox.pack_start(self.button_up, False, False, 5)

        label = Gtk.Label("+")
        label.modify_font(Pango.FontDescription("Bold 14"))
        self.button_up.add(label)

        radius = 2 * subcell_size
        theme_up = \
            "GtkButton {border-radius:0px %dpx %dpx 0px;}" % (radius, radius)
        css_provider_up = Gtk.CssProvider()
        css_provider_up.load_from_data(theme_up)

        style_context = self.button_up.get_style_context()
        style_context.add_provider(
            css_provider_up, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        theme_down = \
            "GtkButton {border-radius: %dpx 0px 0px %dpx;}" % (radius, radius)
        css_provider_down = Gtk.CssProvider()
        css_provider_down.load_from_data(theme_down)

        style_context = self.button_down.get_style_context()
        style_context.add_provider(
            css_provider_down, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.show_all()

    def __number_changed(self, button, increment):
        if increment and self.actual_value < self.max_value:
            self.actual_value += 1

        elif not increment and self.actual_value > self.min_value:
            self.actual_value -= 1

        self.button_up.set_sensitive(self.actual_value < self.max_value)
        self.button_down.set_sensitive(self.actual_value > self.min_value)
        self.label.set_text(str(self.actual_value))
        self.emit("value-changed", self.actual_value)
