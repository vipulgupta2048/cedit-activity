#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import globals as G
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GdkX11
from gi.repository import GObject
from gi.repository import GdkPixbuf
from gi.repository import GtkSource

from sugar3 import env
from sugar3.graphics import style
from sugar3.graphics.icon import Icon
from sugar3.graphics.alert import Alert
from sugar3.graphics.alert import TimeoutAlert
from sugar3.graphics.palette import Palette
from sugar3.graphics.palette import ToolInvoker
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.palettemenu import PaletteMenuBox
from sugar3.graphics.palettemenu import PaletteMenuItem
from sugar3.graphics.toggletoolbutton import ToggleToolButton

screen = Gdk.Screen().get_default()
WIDTH = (screen.get_width() / 6) * 5
HEIGHT = (screen.get_height() / 6) * 5

DEFAULT_FONTS = ['Sans', 'Serif', 'Monospace']
USER_FONTS_FILE_PATH = env.get_profile_path('fonts')
GLOBAL_FONTS_FILE_PATH = '/etc/sugar_fonts'


class FileChooserOpen(Gtk.Window):

    __gsignals__ = {
        'open-file': (GObject.SIGNAL_RUN_FIRST, None, [str])
        }

    def __init__(self, activity, folder=None):
        Gtk.Window.__init__(self)

        self._activity = activity
        self.vbox = Gtk.VBox()
        self.view = Gtk.IconView()
        self.model = Gtk.ListStore(str, GdkPixbuf.Pixbuf)

        self.folder = folder or os.path.expanduser('~/')
        self.files = []
        self.show_hidden_files = False

        if os.path.isfile(self.folder):
            self.folder = self.go_up(self.folder, _return=True)

        self.set_modal(True)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(WIDTH, HEIGHT)
        self.set_border_width(style.LINE_WIDTH)
        self.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.modify_bg(Gtk.StateType.NORMAL, style.COLOR_WHITE.get_gdk_color())
        self.view.set_model(self.model)
        self.view.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.view.set_text_column(0)
        self.view.set_pixbuf_column(1)

        self.connect('key-release-event', self.__key_release_event_cb)
        self.view.connect('selection-changed', self.__selection_changed)
        self.view.connect('button-press-event', self.__button_press_event_cb)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.view)

        self.__make_toolbar()
        self.show_folder()

        self.vbox.pack_end(scrolled, True, True, 0)
        self.add(self.vbox)
        self.show_all()

        GObject.timeout_add(500, self.check_files)

    def __make_toolbar(self):
        self.toolbar = Gtk.Toolbar()
        self.toolbar.modify_bg(
            Gtk.StateType.NORMAL, style.COLOR_TOOLBAR_GREY.get_gdk_color())

        self.go_up_button = ToolButton(icon_name='go-up')
        self.go_up_button.props.accelerator = '<Alt>S'
        self.go_up_button.set_tooltip(_('Go to pather directory'))
        self.go_up_button.connect('clicked', self.go_up)
        self.toolbar.insert(self.go_up_button, -1)

        self.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        self.hidden_files_button = ToggleToolButton('show-hidden-files')
        self.hidden_files_button.props.accelerator = '<Ctrl>H'
        self.hidden_files_button.set_tooltip(_('Show hidden files'))
        self.hidden_files_button.connect('clicked', self.__show_hidden_files)
        self.toolbar.insert(self.hidden_files_button, -1)

        self.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        item = Gtk.ToolItem()
        self.entry = Gtk.Entry()
        self.entry.set_size_request(300, -1)
        self.entry.set_text(self.folder)
        self.entry.connect('activate', self.__open_path_from_entry)
        item.add(self.entry)
        self.toolbar.insert(item, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        self.toolbar.insert(separator, -1)

        self.button_open = ToolButton(icon_name='fileopen')
        self.button_open.set_tooltip(_('Open selected file'))
        self.button_open.set_sensitive(False)
        self.button_open.connect('clicked', self.__open_path)
        self.toolbar.insert(self.button_open, -1)

        self.close_button = ToolButton(icon_name='dialog-cancel')
        self.close_button.connect('clicked', self.close)
        self.toolbar.insert(self.close_button, -1)

        self.vbox.pack_start(self.toolbar, False, False, 0)

    def __key_release_event_cb(self, widget, event):
        if event.keyval == 65293:  # Enter
            self.__open_path()

    def go_up(self, button=None, _return=False):
        path = '/'
        folders = []

        if self.folder == '/':
            return

        for folder in self.folder.split('/'):
            if not folder:
                continue
            folders.append(folder)

        if not folders:
            return

        for folder in folders[:-1]:
            if folder:
                path += folder + '/'

        if not _return:
            self.folder = path
            self.check_files()
        else:
            return path

    def __show_hidden_files(self, button):
        self.show_hidden_files = button.get_active()
        self.show_folder()

    def __open_path(self, button=None):
        if len(self.view.get_selected_items()) == 1:
            if os.path.isdir(self.selected_path):
                self.folder = self.selected_path
                self.selected_path = None

            elif os.path.isfile(self.selected_path):
                self.emit('open-file', self.selected_path)

        else:
            files = []
            directory = None

            for item in self.view.get_selected_items():
                iter = self.model.get_iter(item)
                path = os.path.join(self.folder, self.model.get_value(iter, 0))

                if os.path.isfile(path):
                    files.append(path)

                elif os.path.isdir(path) and not directory:
                    directory = path

            if files:
                for path in files:
                    GObject.idle_add(self.emit, 'open-file', path)
                    self.emit('open-file', path)
                    self.selected_path = None
            
            else:
                if directory:
                    self.folder = directory
                    return  # Evit destroy

            self.destroy()

    def __open_path_from_entry(self, entry):
        path = self.entry.get_text()

        if not os.path.exists(path):
            self.create_alert(path)
            return

        if os.path.isdir(path):
            self.folder = path
            self.check_files()

        elif os.path.isfile(path):
            self.emit('open-file', path)
            self.destroy()

    def create_alert(self, path):
        alert = TimeoutAlert(10)
        alert.props.title = _('This file not exists.')
        alert.props.msg = _(
            "Apparently you've selected a file that does not exist.")
        image = Gtk.Image.new_from_stock(Gtk.STOCK_OK, Gtk.IconSize.MENU)
        alert.add_button(Gtk.ResponseType.NO, _('Ok'), icon=image)

        alert.connect('response', self.__alert_response)

        self.vbox.pack_start(alert, False, False, 0)
        self.vbox.reorder_child(alert, 1)

    def __alert_response(self, alert):
        self.vbox.remove(alert)

    def check_files(self):
        files = os.listdir(self.folder)
        files.sort()

        if files != self.files:
            self.selected_path = None

            self.entry.set_text(self.folder)
            self.go_up_button.set_sensitive(self.folder != '/')

            self.show_folder()

        return True

    def show_folder(self):
        self.files = os.listdir(self.folder)
        self.files.sort()
        self.model.clear()

        folders = []
        files = []

        for x in self.files:
            path = os.path.join(self.folder, x)
            if os.path.isdir(path):
                folders.append(path)

            elif os.path.isfile(path):
                files.append(path)

        for path in folders + files:
            if not self.show_hidden_files:
                if path.endswith('~') or path.split('/')[-1].startswith('.'):
                    continue

            pixbuf = G.get_pixbuf_from_path(path)
            self.model.append([path.split('/')[-1], pixbuf])

    def __selection_changed(self, view):
        if self.view.get_selected_items():
            path = self.view.get_selected_items()[0]
            iter = self.model.get_iter(path)
            self.selected_path = os.path.join(
                self.folder, self.model.get_value(iter, 0))
            self.button_open.set_sensitive(True)

        else:
            self.selected_path = None
            self.button_open.set_sensitive(False)

    def __button_press_event_cb(self, view, event):
        if event.button != 1:
            return

        try:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            iter = self.model.get_iter(path)
            directory = os.path.join(
                self.folder, self.model.get_value(iter, 0))

            if event.type.value_name == 'GDK_2BUTTON_PRESS':
                if os.path.isdir(directory):
                    self.folder = directory

                elif os.path.isfile(directory):
                    self.emit('open-file', directory)
                    self.destroy()

        except TypeError:
            self.selected_path = None
            self.button_open.set_sensitive(False)

    def close(self, button=None):
        self.destroy()


class FileChooserSave(Gtk.Window):

    __gsignals__ = {
        'save-file': (GObject.SIGNAL_RUN_FIRST, None, [str])
        }

    def __init__(self, folder=None):
        Gtk.Window.__init__(self)

        self.vbox = Gtk.VBox()
        self.view = Gtk.IconView()
        self.model = Gtk.ListStore(str, GdkPixbuf.Pixbuf)

        self.folder = folder or os.path.expanduser('~/')
        self.files = []
        self.show_hidden_files = False

        self.set_modal(True)
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(WIDTH, HEIGHT)
        self.set_border_width(style.LINE_WIDTH)
        self.add_events(Gdk.EventMask.KEY_RELEASE_MASK)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.modify_bg(Gtk.StateType.NORMAL, style.COLOR_WHITE.get_gdk_color())
        self.view.set_model(self.model)
        self.view.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.view.set_text_column(0)
        self.view.set_pixbuf_column(1)

        self.view.connect('selection-changed', self.__selection_changed)
        self.view.connect('button-press-event', self.__button_press_event_cb)

        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self.view)

        self.__make_toolbar()
        self.show_folder()

        self.vbox.pack_end(scrolled, True, True, 0)
        self.add(self.vbox)
        self.show_all()

        GObject.timeout_add(500, self.check_files)

    def __make_toolbar(self):
        self.toolbar = Gtk.Toolbar()
        self.toolbar.modify_bg(
            Gtk.StateType.NORMAL, style.COLOR_TOOLBAR_GREY.get_gdk_color())

        self.go_up_button = ToolButton(icon_name='go-up')
        self.go_up_button.connect('clicked', self.go_up)
        self.toolbar.insert(self.go_up_button, -1)

        self.toolbar.insert(Gtk.SeparatorToolItem(), -1)

        self.button_new_folder = ToolButton(icon_name='new-folder')
        self.button_new_folder.set_tooltip(_('Create a folder'))
        self.button_new_folder.connect('clicked', self.create_folder)
        self.toolbar.insert(self.button_new_folder, -1)

        item = Gtk.ToolItem()
        self.entry = Gtk.Entry()
        self.entry.set_size_request(300, -1)
        self.entry.set_text(self.folder)
        self.entry.connect('activate', self.__save_path_from_entry)
        item.add(self.entry)
        self.toolbar.insert(item, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        self.toolbar.insert(separator, -1)

        item = Gtk.ToolItem()
        self.entry_name = Gtk.Entry()
        self.entry_name.set_size_request(200, -1)
        self.entry_name.set_placeholder_text('Select a name for this file.')
        self.entry_name.connect('activate', self.__name_selected)
        item.add(self.entry_name)
        self.toolbar.insert(item, -1)

        self.button_save = ToolButton(icon_name='save-as')
        self.button_save.connect('clicked', self.__save_path_from_button)
        self.toolbar.insert(self.button_save, -1)

        self.close_button = ToolButton(icon_name='dialog-cancel')
        self.close_button.connect('clicked', self.close)
        self.toolbar.insert(self.close_button, -1)

        self.vbox.pack_start(self.toolbar, False, False, 0)

    def go_up(self, button=None, _return=False):
        path = '/'
        folders = []

        if self.folder == '/':
            return

        for folder in self.folder.split('/'):
            if not folder:
                continue
            folders.append(folder)

        if not folders:
            return

        for folder in folders[:-1]:
            if folder:
                path += folder + '/'

        if _return:
            return path

        self.folder = path
        self.check_files()

    def create_folder(self, widget):
        self.button_new_folder.set_sensitive(False)

        entry = Gtk.Entry()
        entry.set_placeholder_text('Select a name')
        entry.connect('activate', self.__create_new_folder)

        item = Gtk.ToolItem()
        item.add(entry)
        self.toolbar.insert(item, 4)
        self.toolbar.show_all()

    def __create_new_folder(self, entry):
        if entry.get_text():
            try:
                path = os.path.join(self.folder, entry.get_text())
                os.mkdir(path)
                self.folder = path

            except OSError as msg:
                alert = Alert()
                alert.props.title = _('Error creating the folder.')
                alert.props.msg = msg
                image = Gtk.Image.new_from_stock(
                    Gtk.STOCK_OK, Gtk.IconSize.MENU)
                alert.add_button(Gtk.ResponseType.NO, _('Ok'), icon=image)

                alert.connect('response', self.__alert_response)

                self.vbox.pack_start(alert, False, False, 0)
                self.vbox.reorder_child(alert, 1)

        item = entry.get_parent()
        self.toolbar.remove(item)
        self.button_new_folder.set_sensitive(True)

    def __save_path_from_button(self, button):
        self.__name_selected()

    def __name_selected(self, entry=None):
        path = os.path.join(self.folder, self.entry_name.get_text())
        self.__save_path_from_entry(path=path)

    def __save_path_from_entry(self, entry=None, path=None):
        if not path:
            path = self.entry.get_text()

        if os.path.exists(path):
            if os.path.isdir(path):
                self.folder = path

            elif os.path.isfile(path):
                self.create_alert(path)

        elif not os.path.exists(path):
            if os.path.isdir(self.go_up(path, _return=True)):
                self.emit('save-file', path)
                self.destroy()

    def create_alert(self, path):
        alert = Alert()
        alert.props.title = _('This file is already exists.')
        alert.props.msg = _('%s already exists, Overwrite it?' % path)
        cancel = Gtk.Image.new_from_icon_name(
            'dialog-cancel', Gtk.IconSize.MENU)
        save = Gtk.Image.new_from_icon_name('filesave', Gtk.IconSize.MENU)
        alert.add_button(Gtk.ResponseType.NO, _('Cancel'), icon=cancel)
        alert.add_button(Gtk.ResponseType.YES, _('Save'), icon=save)

        alert.connect('response', self.__alert_response, path)

        self.vbox.pack_start(alert, False, False, 0)
        self.vbox.reorder_child(alert, 1)

    def __alert_response(self, alert, response, path):
        if response == Gtk.ResponseType.NO:
            self.vbox.remove(alert)
        elif response == Gtk.ResponseType.YES:
            self.emit('save-file', path)
            self.destroy()

    def check_files(self):
        files = os.listdir(self.folder)
        files.sort()

        if files != self.files:
            self.selected_path = None

            self.entry.set_text(self.folder)
            self.go_up_button.set_sensitive(self.folder != '/')

            self.show_folder()

        return True

    def show_folder(self):
        self.files = os.listdir(self.folder)
        self.files.sort()

        self.model.clear()

        folders = []
        files = []

        for x in self.files:
            path = os.path.join(self.folder, x)
            if os.path.isdir(path):
                folders.append(path)

            elif os.path.isfile(path):
                files.append(path)

        for path in folders + files:
            if not self.show_hidden_files:
                if path.endswith('~') or path.split('/')[-1].startswith('.'):
                    continue

            pixbuf = G.get_pixbuf_from_path(path)
            self.model.append([path.split('/')[-1], pixbuf])

    def __selection_changed(self, view):
        if self.view.get_selected_items():
            path = self.view.get_selected_items()[0]
            iter = self.model.get_iter(path)
            name = self.model.get_value(iter, 0)
            if os.path.isfile(os.path.join(self.folder, name)):
                self.entry_name.set_text(name)

            else:
                self.entry_name.set_text('')

        else:
            self.entry_name.set_text('')

    def __button_press_event_cb(self, view, event):
        if event.button != 1:
            return

        try:
            path = view.get_path_at_pos(int(event.x), int(event.y))
            iter = self.model.get_iter(path)
            directory = os.path.join(self.folder, self.model.get_value(iter, 0))

            if event.type.value_name == 'GDK_2BUTTON_PRESS':
                if os.path.isdir(directory):
                    self.folder = directory
                    self.selected_path = None

                elif os.path.isfile(directory):
                    self.selected_path = directory
                    self.create_alert(directory)

            elif event.type.value_name == 'GDK_1BUTTON_PRESS':
                self.selected_path = directory

        except TypeError:
            self.selected_path = None

    def close(self, button=None):
        self.destroy()


class Buffer(GtkSource.Buffer):

    __gsignals__ = {
        'language-changed': (GObject.SIGNAL_RUN_FIRST, None, [str])
        }

    def __init__(self):
        GtkSource.Buffer.__init__(self)
        self.language = None
        self.language_setted = False
        self.languages = [_('Plain text')]
        self.language_manager = GtkSource.LanguageManager()
        self.languages.extend(self.language_manager.get_language_ids())

    def set_language_from_file(self, path):
        if self.language_setted and not G.get_language_from_file(path):
            # Maintaining the language set by the user.
            return

        self.language = G.get_language_from_file(path)

        if self.language:
            self.set_highlight_syntax(True)
            self.set_language(self.language)
            self.emit('language-changed', self.language.get_name())

        elif not self.language:
            self.set_highlight_syntax(False)
            self.emit('language-changed', _('Plain text'))

        self.language_setted = False

    def set_language_from_string(self, language):
        if language == _('Plain text'):
            self.language = None
            self.set_highlight_syntax(False)

        else:
            self.language = self.language_manager.get_language(language)
            self.set_highlight_syntax(True)
            self.set_language(self.language)

        self.language_setted = True

    def get_language(self):
        return self.language

    def get_language_str(self):
        if self.language:
            return self.language.get_name().lower()

        return _('Plain text')

    def get_all_text(self):
        start, end = self.get_bounds()
        return self.get_text(start, end, False)


class View(GtkSource.View):

    __gsignals__ = {
        'title-changed': (GObject.SIGNAL_RUN_FIRST, None, [str]),
        }

    def __init__(self, conf):
        GtkSource.View.__init__(self)

        self.buffer = Buffer()
        self.file = None
        self.conf = None
        self.tag_search = self.buffer.create_tag(
            'search', foreground='#5E82FF', background='#078D00')

        self.set_conf(conf)

        self.buffer.connect('modified-changed', self.buffer_changed)
        self.set_buffer(self.buffer)

    def undo(self):
        if self.buffer.can_undo():
            self.buffer.undo()

    def redo(self):
        if self.buffer.can_redo():
            self.buffer.redo()

    def buffer_changed(self, buffer):
        self.emit_title_changed()

    def set_conf(self, conf):
        self.conf = conf
        style_manager = GtkSource.StyleSchemeManager()
        font = '%s %d' % (conf['font'], conf['font-size'])

        if conf['wrap-mode'] == 'none':
            wrap_mode = Gtk.WrapMode.NONE

        elif conf['wrap-mode'] == 'char':
            wrap_mode = Gtk.WrapMode.CHAR

        elif conf['wrap-mode'] == 'word':
            wrap_mode = Gtk.WrapMode.WORD

        self.modify_font(Pango.FontDescription(font))
        self.set_tab_width(conf['tab-width'])
        self.set_insert_spaces_instead_of_tabs(conf['use-spaces'])
        self.buffer.set_style_scheme(style_manager.get_scheme(conf['theme']))
        self.set_show_line_numbers(conf['show-line-numbers'])
        self.set_show_right_margin(conf['show-right-line'])
        self.set_right_margin_position(conf['right-line-pos'])
        self.set_wrap_mode(wrap_mode)

    def search(self, text, enter):
        start, end = self.buffer.get_bounds()
        self.buffer.remove_tag(self.tag_search, start, end)
        cursor_mark = self.buffer.get_insert()
        start_mark = self.buffer.get_iter_at_mark(cursor_mark)

        if text:
            self.search_and_mark(text, start)
            self.select_text(text, start_mark, enter)

    def replace(self, text_search, text_replace):
        if not self.buffer.get_selection_bounds():
            if text_search:
                self.search(text_search, True)

            return

        else:
            start, end = self.buffer.get_selection_bounds()
            if self.buffer.get_text(start, end, False) == text_search:
                self.buffer.delete_selection(True, True)
                self.buffer.insert_interactive_at_cursor(text_replace, -1, True)

                self.search(text_search, True)

    def search_and_mark(self, text, start):
        _start, _end = self.buffer.get_bounds()

        end = self.buffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match != None:
            match_start, match_end = match
            self.buffer.apply_tag(self.tag_search, match_start, match_end)
            self.search_and_mark(text, match_end)

    def select_text(self, text, start, enter):
        end = self.buffer.get_end_iter()
        match = start.forward_search(text, 0, end)
        _start, _end = None, None

        if match:
            match_start, match_end = match

            if not enter:
                self.buffer.select_range(match_start, match_end)

            else:
                if self.buffer.get_selection_bounds():
                    _start, _end = self.buffer.get_selection_bounds()

                if _start is not None and _end is not None:
                    if match_end.get_offset() == _end.get_offset() and \
                        match_start.get_offset() == _start.get_offset():

                        self.select_text(text, _end, True)
                        return

                self.buffer.select_range(match_end, match_start)

            self.scroll_to_iter(match_end, 0.1, 1, 1, 1)

        else:
            start = self.buffer.get_start_iter()
            try:
                self.select_text(text, start, False)

            except RuntimeError:
                pass

    def set_file(self, path, _open=True):
        if os.path.isfile(path) and _open:
            with open(path, 'r') as file:
                text = file.read()

            self.buffer.set_text(text)
            self.buffer.set_language_from_file(path)
            self.buffer.begin_not_undoable_action()
            self.buffer.end_not_undoable_action()
            self.buffer.set_modified(False)

            self.file = path
            self.emit_title_changed()

    def save_file(self, path):
        self.buffer.set_modified(False)
        self.buffer.set_language_from_file(path)

        if self.file != path:
            self.file = path

        with open(self.file, 'w') as file:
            file.write(self.buffer.get_all_text())

        self.emit('title-changed', self.get_file_name())

    def get_file(self):
        return self.file

    def get_file_name(self):
        if self.file:
            return self.file.split('/')[-1]
        else:
            return _('New file')

    def emit_title_changed(self):
        self.emit('title-changed', self.get_file_name())


class ComboStyles(Gtk.ToolItem):

    __gsignals__ = {
        'theme-changed': (GObject.SIGNAL_RUN_FIRST, None, [str])
        }

    def __init__(self, selected_style='classic'):
        Gtk.ToolItem.__init__(self)

        style_manager = GtkSource.StyleSchemeManager()
        self.styles = style_manager.get_scheme_ids()
        self.combo = Gtk.ComboBoxText()

        for style in self.styles:
            self.combo.append_text(style)

        self.combo.set_active(self.styles.index(selected_style))
        self.combo.connect('changed', self.__theme_changed)

        self.add(self.combo)
        self.show_all()

    def __theme_changed(self, widget):
        self.emit('theme-changed', self.styles[self.combo.get_active()])


class InfoBar(Gtk.HBox):

    __gsignals__ = {
        'language-changed': (GObject.SIGNAL_RUN_FIRST, None, [str])
        }

    def __init__(self):
        Gtk.HBox.__init__(self)

        self.label_pos = Gtk.Label()
        self.combo = Gtk.ComboBoxText()
        self.language = None
        self.languages = [_('Plain text')]
        self.language_manager = GtkSource.LanguageManager()
        self.languages.extend(self.language_manager.get_language_ids())

        for language in self.languages:
            self.combo.append_text(language)

        self.set_pos(1, 1)
        self.combo.set_active(0)

        self.combo.connect('changed', self.__combo_changed)

        self.pack_end(self.combo, False, False, 10)
        self.pack_end(self.label_pos, False, False, 0)

    def set_pos(self, line, column):
        self.label_pos.set_label(_('Line: %s, Column: %s') % (line, column))

    def set_language(self, language):
        if language != _('Plain text'):
            language = language.lower()
            if language in G.BAD_LANGUAGES:
                language = G.BAD_LANGUAGES[language]

        self.language = language
        self.combo.set_active(self.languages.index(self.language))

    def __combo_changed(self, combo):
        if self.language == self.languages[combo.get_active()]:
            return

        self.language = self.languages[combo.get_active()]
        self.emit('language-changed', self.language)


class FontLabel(Gtk.Label):

    def __init__(self, default_font='Monospace'):
        Gtk.Label.__init__(self)

        self._font = None
        self.set_font(default_font)

    def set_font(self, font):
        if self._font != font:
            self.set_markup('<span font="%s">%s</span>' % (font, font))


class FontComboBox(Gtk.ToolItem):

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, [str]),
        }

    def __init__(self, font_name):
        Gtk.ToolItem.__init__(self)

        self._palette_invoker = ToolInvoker()
        self._font_label = FontLabel(font_name)
        self._font_name = font_name

        bt = Gtk.Button('')
        bt.set_can_focus(False)
        bt.remove(bt.get_children()[0])

        box = Gtk.HBox()
        icon = Icon(icon_name='font-text')
        box.pack_start(icon, False, False, 10)
        box.pack_start(self._font_label, False, False, 10)
        bt.add(box)

        self.add(bt)
        self.show_all()

        if style.zoom(100) == 100:
            subcell_size = 15
        else:
            subcell_size = 11

        radius = 2 * subcell_size
        theme = "GtkButton {border-radius: %dpx;}" % radius
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(theme)
        style_context = bt.get_style_context()
        style_context.add_provider(
            css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self._hide_tooltip_on_click = True
        self._palette_invoker.attach_tool(self)
        self._palette_invoker.props.toggle_palette = True

        self.palette = Palette(_('Select font'))
        self.palette.set_invoker(self._palette_invoker)

        self._menu_box = PaletteMenuBox()
        self.props.palette.set_content(self._menu_box)
        self._menu_box.show()

        context = self.get_pango_context()

        self._init_font_list()

        tmp_list = []
        for family in context.list_families():
            name = family.get_name()
            if name in self._font_white_list:
                tmp_list.append(name)
        for name in sorted(tmp_list):
            self._add_menu(name, self.__font_selected_cb)

        self._font_label.set_font(self._font_name)

    def _init_font_list(self):
        self._font_white_list = []
        self._font_white_list.extend(DEFAULT_FONTS)

        if not os.path.exists(USER_FONTS_FILE_PATH):
            if os.path.exists(GLOBAL_FONTS_FILE_PATH):
                shutil.copy(GLOBAL_FONTS_FILE_PATH, USER_FONTS_FILE_PATH)

        if os.path.exists(USER_FONTS_FILE_PATH):
            fonts_file = open(USER_FONTS_FILE_PATH)
            for line in fonts_file:
                self._font_white_list.append(line.strip())

            gio_fonts_file = Gio.File.new_for_path(USER_FONTS_FILE_PATH)
            self.monitor = gio_fonts_file.monitor_file(
                Gio.FileMonitorFlags.NONE, None)
            self.monitor.set_rate_limit(5000)
            self.monitor.connect('changed', self._reload_fonts)

    def _reload_fonts(self, monitor, gio_file, other_file, event):
        if event != Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            return
        self._font_white_list = []
        self._font_white_list.extend(DEFAULT_FONTS)
        fonts_file = open(USER_FONTS_FILE_PATH)
        for line in fonts_file:
            self._font_white_list.append(line.strip())

        for child in self._menu_box.get_children():
            self._menu_box.remove(child)
            child = None

        context = self.get_pango_context()
        tmp_list = []

        for family in context.list_families():
            name = family.get_name()
            if name in self._font_white_list:
                tmp_list.append(name)

        for name in sorted(tmp_list):
            self._add_menu(name, self.__font_selected_cb)

        return False

    def __font_selected_cb(self, menu, font_name):
        self._font_name = font_name
        self._font_label.set_font(font_name)
        self.emit('changed', self._font_name)

    def _add_menu(self, font_name, activate_cb):
        label = '<span font="%s">%s</span>' % (font_name, font_name)
        menu_item = PaletteMenuItem()
        menu_item.set_label(label)
        menu_item.connect('activate', activate_cb, font_name)
        self._menu_box.append_item(menu_item)
        menu_item.show()

    def __destroy_cb(self, icon):
        if self._palette_invoker is not None:
            self._palette_invoker.detach()

    def create_palette(self):
        return None

    def get_palette(self):
        return self._palette_invoker.palette

    def set_palette(self, palette):
        self._palette_invoker.palette = palette

    palette = GObject.property(
        type=object, setter=set_palette, getter=get_palette)

    def get_palette_invoker(self):
        return self._palette_invoker

    def set_palette_invoker(self, palette_invoker):
        self._palette_invoker.detach()
        self._palette_invoker = palette_invoker

    palette_invoker = GObject.property(
        type=object, setter=set_palette_invoker, getter=get_palette_invoker)

    def set_font_name(self, font_name):
        self._font_label.set_font(font_name)

    def get_font_name(self):
        return self._font_name


class FontSize(Gtk.ToolItem):

    __gsignals__ = {
        'changed': (GObject.SignalFlags.RUN_LAST, None, [int]),
        }

    def __init__(self):

        Gtk.ToolItem.__init__(self)

        self._font_sizes = [
            8, 9, 10, 11, 12, 14, 16, 20, 22, 24, 26, 28, 36, 48, 72]

        if style.zoom(100) == 100:
            subcell_size = 15
            default_padding = 6

        else:
            subcell_size = 11
            default_padding = 4

        vbox = Gtk.VBox()
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, True, True, default_padding)

        self._size_down = Gtk.Button()
        self._size_down.set_can_focus(False)
        icon = Icon(icon_name='resize-')
        self._size_down.set_image(icon)
        self._size_down.connect('clicked', self.__font_sizes_cb, False)
        hbox.pack_start(self._size_down, False, False, 5)

        self._default_size = 14
        self._font_size = self._default_size

        self._size_label = Gtk.Label(str(self._font_size))
        hbox.pack_start(self._size_label, False, False, 10)

        self._size_up = Gtk.Button()
        self._size_up.set_can_focus(False)
        icon = Icon(icon_name='resize+')
        self._size_up.set_image(icon)
        self._size_up.connect('clicked', self.__font_sizes_cb, True)
        hbox.pack_start(self._size_up, False, False, 5)

        radius = 2 * subcell_size
        theme_up = "GtkButton {border-radius:0px %dpx %dpx 0px;}" % (
            radius, radius)
        css_provider_up = Gtk.CssProvider()
        css_provider_up.load_from_data(theme_up)

        style_context = self._size_up.get_style_context()
        style_context.add_provider(css_provider_up,
                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

        theme_down = "GtkButton {border-radius: %dpx 0px 0px %dpx;}" % (
            radius, radius)
        css_provider_down = Gtk.CssProvider()
        css_provider_down.load_from_data(theme_down)
        style_context = self._size_down.get_style_context()
        style_context.add_provider(css_provider_down,
                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

        self.add(vbox)
        self.show_all()

    def __font_sizes_cb(self, button, increase):
        if self._font_size in self._font_sizes:
            i = self._font_sizes.index(self._font_size)
            if increase:
                if i < len(self._font_sizes) - 1:
                    i += 1
            else:
                if i > 0:
                    i -= 1
        else:
            i = self._font_sizes.index(self._default_size)

        self._font_size = self._font_sizes[i]
        self._size_label.set_text(str(self._font_size))
        self._size_down.set_sensitive(i != 0)
        self._size_up.set_sensitive(i < len(self._font_sizes) - 1)
        self.emit('changed', self._font_size)

    def set_font_size(self, size):
        if size not in self._font_sizes:
            for font_size in self._font_sizes:
                if font_size > size:
                    size = font_size
                    break
            if size > self._font_sizes[-1]:
                size = self._font_sizes[-1]

        self._font_size = size
        self._size_label.set_text(str(self._font_size))

        i = self._font_sizes.index(self._font_size)
        self._size_down.set_sensitive(i != 0)
        self._size_up.set_sensitive(i < len(self._font_sizes) - 1)
        self.emit('changed', self._font_size)

    def get_font_size(self):
        return self._font_size


class Spinner(Gtk.ToolItem):

    __gsignals__ = {
        'value-changed': (GObject.SignalFlags.RUN_LAST, None, [int]),
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
        hbox = Gtk.HBox()
        hbox.set_spacing(0)
        vbox.pack_start(hbox, True, True, default_padding)

        label = Gtk.Label('-')
        label.modify_font(Pango.FontDescription('Bold 14'))

        self.button_down = Gtk.Button()
        self.button_down.set_can_focus(False)
        self.button_down.set_size_request(30, -1)
        self.button_down.connect('clicked', self.__number_changed, False)
        self.button_down.add(label)
        hbox.pack_start(self.button_down, False, False, 5)

        self.label = Gtk.Label()
        self.label.set_text(str(self.actual_value))
        self.label.set_size_request(20, -1)
        self.label.modify_font(Pango.FontDescription('Bold 14'))
        hbox.pack_start(self.label, False, False, 10)

        label = Gtk.Label('+')
        label.modify_font(Pango.FontDescription('Bold 14'))

        self.button_up = Gtk.Button()
        self.button_up.set_can_focus(False)
        self.button_up.set_size_request(30, -1)
        self.button_up.connect('clicked', self.__number_changed, True)
        self.button_up.add(label)
        hbox.pack_start(self.button_up, False, False, 5)

        radius = 2 * subcell_size
        theme_up = "GtkButton {border-radius:0px %dpx %dpx 0px;}" % (
            radius, radius)
        css_provider_up = Gtk.CssProvider()
        css_provider_up.load_from_data(theme_up)

        style_context = self.button_up.get_style_context()
        style_context.add_provider(css_provider_up,
                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

        theme_down = "GtkButton {border-radius: %dpx 0px 0px %dpx;}" % (
            radius, radius)
        css_provider_down = Gtk.CssProvider()
        css_provider_down.load_from_data(theme_down)

        style_context = self.button_down.get_style_context()
        style_context.add_provider(css_provider_down,
                                   Gtk.STYLE_PROVIDER_PRIORITY_USER)

        hbox.set_can_focus(True)
        hbox.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        hbox.connect('button-press-event', self.__button_press_event_cb)

        self.add(vbox)
        self.show_all()

    def __button_press_event_cb(self, widget, event):
        print event.button

    def __number_changed(self, button, increment):
        if increment and self.actual_value < self.max_value:
            self.actual_value += 1

        elif not increment and self.actual_value > self.min_value:
            self.actual_value -= 1

        self.button_up.set_sensitive(self.actual_value < self.max_value)
        self.button_down.set_sensitive(self.actual_value > self.min_value)
        self.label.set_text(str(self.actual_value))
        self.emit('value-changed', self.actual_value)
