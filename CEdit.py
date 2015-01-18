#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   CEdit.py por:
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

import os
import sys
import time
import datetime

from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GtkSource

from widgets import View
from widgets import Spinner
from widgets import InfoBar
from widgets import FontSize
from widgets import ComboStyles
from widgets import FontComboBox
from widgets import FileChooserOpen
from widgets import FileChooserSave

from sugar3.activity import activity
from sugar3.graphics.alert import Alert
from sugar3.graphics.alert import TimeoutAlert
from sugar3.graphics.iconentry import IconEntry
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbarbox import ToolbarButton
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.activity.widgets import EditToolbar
from sugar3.activity.widgets import _create_activity_icon as ActivityIcon


class CEdit(activity.Activity):

    def __init__(self, handle):
        activity.Activity.__init__(self, handle)

        self.get_conf()

        self.reopen = True
        self.vbox = Gtk.VBox()
        self.infobar = InfoBar()

        self.make_toolbar()
        self.make_notebook()

        self.infobar.connect('language-changed', self.set_language)

        self.vbox.pack_end(self.infobar, False, False, 0)
        self.set_canvas(self.vbox)
        self.show_all()

    def get_conf(self):
        if 'saved' in self.metadata:
            self.conf = {}
            self.conf['font'] = str(self.metadata['font'])
            self.conf['font-size'] = int(self.metadata['font-size'])
            self.conf['show-line-numbers'] = bool(
                int(self.metadata['show-line-numbers']))
            self.conf['tab-width'] = int(self.metadata['tab-width'])
            self.conf['use-spaces'] = bool(int(self.metadata['use-spaces']))
            self.conf['theme'] = str(self.metadata['theme'])
            self.conf['right-line-pos'] = int(self.metadata['right-line-pos'])
            self.conf['show-right-line'] = bool(
                int(self.metadata['show-right-line']))
            self.conf['wrap-mode'] = str(self.metadata['wrap-mode'])

        else:
            self.conf = {'font': 'Monospace',
                         'font-size': 14,
                         'show-line-numbers': True,
                         'tab-width': 4,
                         'use-spaces': True,
                         'theme': 'classic',
                         'right-line-pos': 80,
                         'show-right-line': False,
                         'wrap-mode': 'none'}

    def make_toolbar(self):
        def make_separator(toolbar, expand=True):
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = not expand
            separator.set_expand(expand)
            toolbar.insert(separator, -1)

        toolbar_box = ToolbarBox()
        toolbar = toolbar_box.toolbar

        activity_button = ToolButton()
        activity_button.set_icon_widget(ActivityIcon(None))
        toolbar.insert(activity_button, -1)

        toolbar.insert(Gtk.SeparatorToolItem(), -1)

        toolbar_file = Gtk.Toolbar()
        boton_toolbar_file = ToolbarButton(page=toolbar_file, icon_name='txt')
        toolbar.add(boton_toolbar_file)

        toolbar_edit = EditToolbar()
        button_toolbar_edit = ToolbarButton(
            page=toolbar_edit, icon_name='toolbar-edit')
        toolbar.insert(button_toolbar_edit, -1)

        toolbar_view = Gtk.Toolbar()
        boton_toolbar_view = ToolbarButton(
            page=toolbar_view, icon_name='toolbar-view')
        toolbar.insert(boton_toolbar_view, -1)

        self.button_undo = toolbar_edit.undo
        self.button_undo.props.accelerator = '<Ctrl>Z'
        self.button_undo.set_sensitive(False)
        toolbar_edit.undo.connect('clicked', self.undo)

        self.button_redo = toolbar_edit.redo
        self.button_redo.props.accelerator = '<Ctrl><Mayus>Z'
        self.button_redo.set_sensitive(False)
        self.button_redo.connect('clicked', self.redo)

        self.entry_search = IconEntry()
        item_entry = Gtk.ToolItem()
        self.entry_search.set_size_request(250, -1)
        self.entry_search.set_placeholder_text('Search...')
        self.entry_search.set_icon_from_name(
            Gtk.EntryIconPosition.SECONDARY, 'search')
        self.entry_search.connect('changed', self.search_text)
        self.entry_search.connect('activate', self.search_text, True)
        item_entry.add(self.entry_search)
        toolbar_edit.insert(item_entry, -1)

        self.entry_replace = IconEntry()
        item_entry = Gtk.ToolItem()
        self.entry_replace.set_size_request(250, -1)
        self.entry_replace.set_placeholder_text('Replace...')
        self.entry_replace.connect('activate', self.replace_text)
        item_entry.add(self.entry_replace)
        toolbar_edit.insert(item_entry, -1)

        button_new = ToolButton('new-file')
        button_new.props.accelerator = '<Ctrl>N'
        button_new.connect('clicked', lambda w: self.new_page())
        button_new.set_tooltip(_('New file'))
        toolbar_file.insert(button_new, -1)

        button_open = ToolButton('fileopen')
        button_open.props.accelerator = '<Ctrl>O'
        button_open.set_tooltip(_('Open file from file system'))
        button_open.connect('clicked', self.file_chooser_open)
        toolbar_file.insert(button_open, -1)

        self.button_save = ToolButton('filesave')
        self.button_save.props.accelerator = '<Ctrl>S'
        self.button_save.set_tooltip(_('Save file to the file system'))
        self.button_save.connect('clicked', self.file_chooser_save)
        toolbar_file.insert(self.button_save, -1)

        button_save_as = ToolButton('save-as')
        button_save_as.props.accelerator = '<Ctrl><Mayus>S'
        button_save_as.set_tooltip(_('Save as file to the file system'))
        button_save_as.connect('clicked', self.file_chooser_save, True)
        toolbar_file.insert(button_save_as, -1)

        make_separator(toolbar_file, False)

        button_print = ToolButton('printer')
        button_print.props.accelerator = '<Ctrl>I'
        button_print.set_tooltip(_('Print file'))
        button_print.connect('clicked', self.print_file)
        toolbar_file.insert(button_print, -1)

        make_separator(toolbar_edit, False)

        button_clock = ToolButton('clock')
        button_clock.props.accelerator = '<Ctrl>T'
        button_clock.set_tooltip(_('Insert date and time'))
        button_clock.connect('clicked', self.insert_date_and_time)
        toolbar_edit.insert(button_clock, -1)

        button_wrap_none = Gtk.RadioToolButton()
        button_wrap_none.set_icon_name('wrap-none')
        button_wrap_none.connect("toggled", self.wrap_mode_changed, 'none')
        toolbar_view.insert(button_wrap_none, -1)

        button_wrap_char = Gtk.RadioToolButton.new_from_widget(button_wrap_none)
        button_wrap_char.set_icon_name('format-justify-fill')
        button_wrap_char.connect("toggled", self.wrap_mode_changed, 'char')
        toolbar_view.insert(button_wrap_char, -1)

        button_wrap_word = Gtk.RadioToolButton.new_from_widget(button_wrap_none)
        button_wrap_word.set_icon_name('format-justify-left')
        button_wrap_word.connect("toggled", self.wrap_mode_changed, 'word')
        toolbar_view.insert(button_wrap_word, -1)

        if self.conf['wrap-mode'] == 'none':
            button_wrap_none.set_active(True)

        elif self.conf['wrap-mode'] == 'char':
            button_wrap_none.set_active(True)

        elif self.conf['wrap-mode'] == 'word':
            button_wrap_none.set_active(True)

        make_separator(toolbar_view, False)

        item_font_size = FontSize()
        item_font_size.set_font_size(self.conf['font-size'])
        item_font_size.connect('changed', self.font_size_changed)
        toolbar_view.insert(item_font_size, -1)

        combo_font = FontComboBox(self.conf['font'])
        combo_font.connect('changed', self.font_changed)
        toolbar_view.insert(combo_font, -1)

        make_separator(toolbar_view, False)

        button_numbers = ToggleToolButton('show-numbers')
        button_numbers.props.accelerator = '<Ctrl><Mayus>N'
        button_numbers.set_tooltip(_('Show line numbers'))
        button_numbers.set_active(self.conf['show-line-numbers'])
        button_numbers.connect('toggled', self.show_numbers_changed)
        toolbar_view.insert(button_numbers, -1)

        button_right_line = ToggleToolButton('show-right-line')
        button_right_line.props.accelerator = '<Ctrl>L'
        button_right_line.set_tooltip(_('Show a line in a specific position'))
        button_right_line.set_active(self.conf['show-right-line'])
        button_right_line.connect('toggled', self.show_right_line_changed)
        toolbar_view.insert(button_right_line, -1)

        self.spinner_right_line = Spinner(self.conf['right-line-pos'], 1, 150)
        self.spinner_right_line.set_sensitive(self.conf['show-right-line'])
        self.spinner_right_line.connect(
            'value-changed', self.right_line_pos_changed)
        toolbar_view.insert(self.spinner_right_line, -1)

        make_separator(toolbar_view, False)

        combo_styles = ComboStyles(self.conf['theme'])
        combo_styles.connect('theme-changed', self.theme_changed)
        toolbar_view.insert(combo_styles, -1)

        make_separator(toolbar, True)

        button_stop = ToolButton('activity-stop')
        button_stop.props.accelerator = '<Ctrl>Q'
        button_stop.connect('clicked', self._exit)
        toolbar.insert(button_stop, -1)

        toolbar_file.show_all()
        toolbar_edit.show_all()
        toolbar_view.show_all()

        toolbar_edit.copy.hide()
        toolbar_edit.paste.hide()

        self.set_toolbar_box(toolbar_box)

    def make_notebook(self):
        self.notebook = Gtk.Notebook()
        button_add = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
        button_add.connect('clicked', lambda w: self.new_page())

        self.notebook.set_scrollable(True)
        self.notebook.set_show_tabs(True)
        self.notebook.set_action_widget(button_add, Gtk.PackType.END)

        self.notebook.add_events(Gdk.EventMask.SCROLL_MASK |
                                 Gdk.EventMask.SMOOTH_SCROLL_MASK)

        self.notebook.connect('switch-page', self.update_buttons)
        self.notebook.connect('scroll-event', self.notebook_scrolled)
        self.notebook.connect('page-removed', self.page_removed)

        self.vbox.pack_start(self.notebook, True, True, 2)
        self.new_page()
        button_add.show()
        self.show_all()

    def page_removed(self, notebook, scroll, page):
        if not self.reopen:
            return

        if len(self.notebook.get_children()) == 0:
            self.new_page()

    def set_language(self, infobar, language):
        buffer = self.get_view().buffer
        buffer.set_language_from_string(language)

    def set_language_from_buffer(self, buffer, language):
        self.infobar.set_language(language)

    def notebook_scrolled(self, widget, event):
        if event.get_scroll_direction()[1] == Gdk.ScrollDirection.UP:
            self.notebook.prev_page()
        elif event.get_scroll_direction()[1] == Gdk.ScrollDirection.DOWN:
            self.notebook.next_page()

    def update_buttons(self, notebook=None, scrolled=None, *args):
        if not isinstance(scrolled, Gtk.ScrolledWindow):
            view = self.get_view()
        
        else:
            view = scrolled.get_children()[0]

        buffer = view.get_buffer()

        self.button_undo.set_sensitive(buffer.can_undo())
        self.button_redo.set_sensitive(buffer.can_redo())
        self.button_save.set_sensitive(buffer.get_modified())
        self.entry_search.set_sensitive(bool(buffer.get_all_text()))
        self.entry_replace.set_sensitive(bool(buffer.get_all_text()))
        self.spinner_right_line.set_sensitive(self.conf['show-right-line'])
        self.infobar.set_language(buffer.get_language_str())
        self.update_cursor_position(buffer)

    def new_page(self, view=None, label=None):
        if not view:
            view = View(self.conf)
            view.buffer.connect('changed', self.update_buttons)
            view.buffer.connect('mark-set', self.update_cursor_position)
            view.buffer.connect(
                'language-changed', self.set_language_from_buffer)

        if not label:
            label = view.get_file_name()

        if type(label) == str:
            label = Gtk.Label(label)
            label.modify_font(Pango.FontDescription('15 bold'))

        view.connect('title-changed', self.change_title_from_view)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolled.add(view)

        hbox = Gtk.HBox()
        hbox.set_size_request(-1, 20)

        hbox.pack_start(label, False, False, 0)

        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_size_request(12, 12)
        button.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
        button.connect('clicked', self.remove_page_from_widget, scrolled)
        hbox.pack_start(button, False, False, 0)

        self.notebook.append_page(scrolled, hbox)
        self.notebook.set_tab_reorderable(scrolled, True)

        view.grab_focus()
        hbox.show_all()
        self.show_all()

        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)
        return view

    def update_cursor_position(self, buffer, *args):
        iter = buffer.get_iter_at_mark(buffer.get_insert())
        line = iter.get_line() + 1
        column = iter.get_line_offset() + 1
        self.infobar.set_pos(line, column)

    def file_chooser_open(self, widget):
        path = self.get_view().get_file()
        file_chooser = FileChooserOpen(self, path)
        file_chooser.connect('open-file', self._open_file_from_chooser)
        file_chooser.show_all()

    def file_chooser_save(self, widget, force=False, close=False):
        # Force is for "save as"

        idx = self.notebook.get_current_page()
        view = self.get_view()

        if view.get_file() and not force:
            self.save_file(idx=idx, path=view.get_file())
            return

        file_chooser = FileChooserSave()
        file_chooser.connect('save-file', self._save_file_from_chooser, close)
        file_chooser.show_all()

    def begin_print(self, operation, context, compositor):
        while not compositor.paginate(context):
            pass

        n_pages = compositor.get_n_pages()
        operation.set_n_pages(n_pages)

    def draw_page(self, operation, context, page_nr, compositor):
        compositor.draw_page(context, page_nr)

    def print_file(self, widget):
        def _alert_response(alert, response):
            self.vbox.remove(alert)

        view = self.get_view()
        buffer = view.get_buffer()
        path = view.get_file()

        if not path:
            alert = TimeoutAlert(10)
            alert.props.title = _('This file has not saved.')
            alert.props.msg = _('You must save this file to print.')
            hbox = alert.get_children()[0]
            buttonbox = hbox.get_children()[1]
            button = buttonbox.get_children()[0]
            buttonbox.remove(button)

            alert.connect('response', _alert_response)

            self.vbox.pack_start(alert, False, False, 0)
            self.vbox.reorder_child(alert, 0)

            return

        compositor = GtkSource.PrintCompositor.new_from_view(view)
        compositor.set_wrap_mode(view.get_wrap_mode())
        compositor.set_highlight_syntax(buffer.get_highlight_syntax())
        compositor.set_print_line_numbers(self.conf['show-line-numbers'])

        if view.buffer.language:
            compositor.set_header_format(False, '%s - %s' % (
                view.buffer.get_language_str(), view.get_file()), None, None)

        compositor.set_footer_format(True, '%T', path, 'Page %N/%Q')
        compositor.set_print_header(True)
        compositor.set_print_footer(True)

        operation = Gtk.PrintOperation()
        operation.set_job_name(path)

        operation.connect('begin-print', self.begin_print, compositor)
        operation.connect('draw-page', self.draw_page, compositor)

        res = operation.run(Gtk.PrintOperationAction.PRINT_DIALOG, None)
        if res == Gtk.PrintOperationResult.ERROR:
            dialog = Gtk.MessageDialog(
                self,
                Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                'Error to print the file: %s' % path)

            dialog.run()
            dialog.destroy()

    def _open_file_from_chooser(self, widget, path):
        children = self.notebook.get_children()
        for scrolled in children:
            view = scrolled.get_children()[0]
            if view.get_file() == path:
                idx = children.index(scrolled)
                self.notebook.set_current_page(idx)
                return

        view = self.get_view()

        if view.get_file():
            self.new_page(label=view.get_file_name())
            view = self.get_view(idx=-1)

        view.set_file(path)

    def _save_file_from_chooser(self, widget, path, close=False):
        view = self.get_view()
        view.save_file(path)

        if close:
            view = self.get_view()
            scrolled = view.get_parent()
            idx = self.notebook.get_children().index(scrolled)
            self.notebook.remove_page(idx)

    def save_file(self, widget=None, idx=None, path=None):
        if idx is not None:
            idx = self.notebook.get_current_page()

        scrolled = self.notebook.get_children()[idx]
        view = scrolled.get_children()[0]
        view.save_file(view.get_file())

    def remove_page_from_widget(self, widget, scrolled, force=False):
        view = scrolled.get_children()[0]
        buffer = view.get_buffer()
        idx = self.notebook.get_children().index(scrolled)

        if not buffer.get_modified() or force:
            self.notebook.remove_page(idx)

        else:
            name = view.get_file_name()
            title = _('Save changes to document "%s" before closing?' % name)
            msg = _('If you do not save, changes will be lost forever.')
            cancel = Gtk.Image.new_from_icon_name(
                'dialog-cancel', Gtk.IconSize.MENU)
            no = Gtk.Image.new_from_icon_name(
                'activity-stop', Gtk.IconSize.MENU)
            save = Gtk.Image.new_from_icon_name('filesave', Gtk.IconSize.MENU)

            self.alert = Alert()
            self.alert.props.title = title
            self.alert.props.msg = msg

            button1 = self.alert.add_button(
                Gtk.ResponseType.CANCEL, _('Cancel'), icon=cancel)
            button2 = self.alert.add_button(
                Gtk.ResponseType.NO, _('No save'), icon=no)
            button3 = self.alert.add_button(
                Gtk.ResponseType.YES, _('Save'), icon=save)

            self.alert.connect('response', self._alert_response, scrolled)

            self.vbox.pack_start(self.alert, False, False, 0)
            self.vbox.reorder_child(self.alert, 0)
            self.vbox.show_all()

    def change_title_from_view(self, view=None, label=None):
        if not view:
            view = self.get_view()
        if not label:
            label = view.get_file_name()

        scrolled = view.get_parent()
        hbox = self.notebook.get_tab_label(scrolled)
        widget = hbox.get_children()[0]
        changed = view.get_buffer().get_modified()

        widget.set_label(label)

        color = '#FF0000' if changed else '#FFFFFF'
        widget.modify_fg(Gtk.StateType.NORMAL, Gdk.color_parse(color))
        self.update_buttons()

    def get_view(self, idx=None):
        if idx is None:
            idx = self.notebook.get_current_page()

        scrolled = self.notebook.get_children()[idx]
        return scrolled.get_children()[0]

    def undo(self, widget):
        self.get_view().undo()
        self.change_title_from_view()

    def redo(self, widget):
        self.get_view().redo()
        self.change_title_from_view()

    def search_text(self, entry, enter=False):
        text = entry.get_text()
        self.get_view().search(text, enter)

    def replace_text(self, entry):
        text_search = self.entry_search.get_text()
        text_replace = entry.get_text()
        self.get_view().replace(text_search, text_replace)

    def wrap_mode_changed(self, widget, mode):
        self.conf['wrap-mode'] = mode
        self.set_conf_to_views()

    def font_size_changed(self, widget, font_size):
        self.conf['font-size'] = font_size
        self.set_conf_to_views()

    def font_changed(self, widget, font):
        self.conf['font'] = font
        self.set_conf_to_views()

    def show_numbers_changed(self, widget):
        self.conf['show-line-numbers'] = widget.get_active()
        self.set_conf_to_views()

    def show_right_line_changed(self, widget):
        self.conf['show-right-line'] = widget.get_active()
        self.update_buttons()
        self.set_conf_to_views()

    def right_line_pos_changed(self, widget, value):
        self.conf['right-line-pos'] = value
        self.set_conf_to_views()

    def theme_changed(self, widget, theme):
        self.conf['theme'] = theme
        self.set_conf_to_views()

    def tab_width_changed(self, widget, tab_width):
        self.conf['tab-width'] = tab_width
        self.set_conf_to_views()

    def set_conf_to_views(self):
        for scrolled in self.notebook.get_children():
            view = scrolled.get_children()[0]
            view.set_conf(self.conf)

    def insert_date_and_time(self, widget):
        view = self.get_view()
        day = datetime.date.today()
        date = day.strftime('%d/%m/%y')
        hour = time.strftime('%H:%M:%S')
        text = date + ' ' + hour

        view.buffer.insert_interactive_at_cursor(text, -1, True)

    def _alert_response(self, widget, response, scrolled):
        if response == Gtk.ResponseType.NO:
            self.remove_page_from_widget(None, scrolled, force=True)
        elif response == Gtk.ResponseType.YES:
            self.file_chooser_save(None, False, True)

        self.vbox.remove(self.alert)

    def write_file(self, file_path):
        files = []

        for scrolled in self.notebook.get_children():
            view = scrolled.get_children()[0]
            if view.get_file():
                files.append(view.get_file)

        self.metadata['saved'] = True
        self.metadata['font'] = self.conf['font']
        self.metadata['font-size'] = self.conf['font-size']
        self.metadata['show-line-numbers'] = self.conf['show-line-numbers']
        self.metadata['tab-width'] = self.conf['tab-width']
        self.metadata['use-spaces'] = self.conf['use-spaces']
        self.metadata['theme'] = self.conf['theme']
        self.metadata['right-line-pos'] = self.conf['right-line-pos']
        self.metadata['show-right-line'] = self.conf['show-right-line']
        self.metadata['wrap-mode'] = self.conf['wrap-mode']

    def _exit(self, *args):
        def _remove_page(widget, scrolled):
            if scrolled in self.notebook.get_children():
                idx = self.notebook.get_children().index(scrolled)
                self.notebook.remove_page(idx)

            check_modified()

        def _alert_response(alert, response, scrolled):
            self.vbox.remove(alert)
            
            if response == Gtk.ResponseType.YES:
                view = scrolled.get_children()[0]

                if view.get_file():
                    idx = self.notebook.get_children()
                    self.save_file(idx=idx, path=view.get_file())
                    self.remove_page_from_widget(None, scrolled, force=True)
                    return

                file_chooser = FileChooserSave()
                file_chooser.connect('save-file', self._save_file_from_chooser, True)
                file_chooser.connect('destroy', _remove_page, scrolled)
                file_chooser.show_all()

            else:
                self.remove_page_from_widget(None, scrolled, force=True)
                check_modified()

        def _create_alert(name, scrolled):
            title = _(
                'Save changes to document "%s" before closing?' % name)
            msg = _('If you do not save, changes will be lost forever.')

            no = Gtk.Image.new_from_icon_name(
                'activity-stop', Gtk.IconSize.MENU)
            save = Gtk.Image.new_from_icon_name('filesave',
                Gtk.IconSize.MENU)

            alert = Alert()
            alert.props.title = title
            alert.props.msg = msg

            button1 = alert.add_button(
                Gtk.ResponseType.NO, _('No save'), icon=no)
            button2 = alert.add_button(
                Gtk.ResponseType.YES, _('Save'), icon=save)

            alert.connect('response', _alert_response, scrolled)

            self.vbox.pack_start(alert, False, False, 0)
            self.vbox.reorder_child(alert, 0)
            self.vbox.show_all()

        def check_modified():
            if not self.notebook.get_children():
                _close()
                return

            self.notebook.set_current_page(self.notebook.get_n_pages() - 1)
            scrolled = self.notebook.get_children()[-1]
            view = scrolled.get_children()[0]
            buffer = view.get_buffer()

            if buffer.get_modified():
                name = view.get_file_name()
                _create_alert(name, scrolled)

            else:
                self.remove_page_from_widget(None, scrolled, force=True)
                check_modified()

        def _close():
            self.close()

        self.reopen = False
        check_modified()
