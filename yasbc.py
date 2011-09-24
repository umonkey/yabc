#!/usr/bin/env python
# encoding=utf-8

import glob
import os

import gobject
import gtk
import pango
import pygtk

# ~/src/tmradio-client-gtk/simple.py


class JinglePane(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 2)

        self.row1 = gtk.HBox(False, 3)

        self.btn1 = gtk.Button("1")
        self.row1.pack_start(self.btn1, expand=False)

        self.btn2 = gtk.Button("2")
        self.row1.pack_start(self.btn2, expand=False)

        self.btn3 = gtk.Button("3")
        self.row1.pack_start(self.btn3, expand=False)

    
class NotesView(gtk.TextView):
    def __init__(self, scroll_window=None, **kwargs):
        gtk.TextView.__init__(self)


class MainView(gtk.HPaned):
    def __init__(self):
        gtk.HPaned.__init__(self)

        self.text_scroll = gtk.ScrolledWindow()
        self.text_scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.notes_pane = NotesView(scrolled_window=self.text_scroll)
        self.text_scroll.add(self.notes_pane)
        self.add1(self.text_scroll)

        self.jingle_pane = JinglePane()
        self.add2(self.jingle_pane)


class MainMenu(gtk.MenuBar):
    def __init__(self, on_exit=None):
        gtk.MenuBar.__init__(self)

        submenu = gtk.Menu()

        item = gtk.MenuItem("Exit")
        item.connect("activate", on_exit)
        submenu.append(item)

        menu = gtk.MenuItem("Root Menu")
        menu.set_submenu(submenu)
        self.append(menu)


class MainWindow:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Simple Broadcasting Console")
        self.window.connect("delete_event", self.on_quit)

        self.vbox = gtk.VBox(False, 2)
        self.window.add(self.vbox)
        self.vbox.pack_start(self.setup_menu(), expand=False, fill=True)
        self.vbox.pack_start(self.setup_main_view(), expand=True, fill=True)

        self.window.resize(800, 380)

    def setup_menu(self):
        self.menu_bar = MainMenu(on_exit=lambda x: self.on_quit(None, None))
        return self.menu_bar

    def setup_main_view(self):
        self.main_hbox = gtk.HBox(False, 2)

        self.notes = NotesView()
        self.main_hbox.pack_start(self.notes, expand=True, fill=True)

        self.buttons = self.setup_buttons()
        self.main_hbox.pack_start(self.buttons, expand=False, fill=True)

        return self.main_hbox

    def setup_buttons(self):
        buttons = gtk.VBox(False, 2)

        self.jingles = self.setup_jingles()
        buttons.pack_start(self.jingles, expand=False, fill=True)

        return buttons

    def setup_jingles(self):
        """Sets up the jingle buttons.

        Looks for audio files in the jingles folder and adds the buttons to the
        right pane, 3 files in a row.  Each jingle is a button which, when
        clicked, calls the on_jingle method."""
        jingles = gtk.VBox(False, spacing=0)

        files = self.get_audio_files("~/.config/yasbc/jingles")
        while files:
            tmp = files[:3]
            hbox = gtk.HBox(False, spacing=0)
            for text in tmp:
                ctl = gtk.Button(os.path.splitext(os.path.basename(text))[0])
                ctl.connect("clicked", self.on_jingle)
                hbox.pack_start(ctl, expand=True, fill=True)
            del files[:3]
            jingles.pack_start(hbox, expand=False, fill=True)

        return jingles

    def get_audio_files(self, folder):
        """Returns names of audio files in the specified folder."""
        folder = os.path.expanduser(folder)
        if not os.path.exists(folder):
            return []

        names = []
        for fn in sorted(glob.glob(os.path.join(folder, "*"))):
            if os.path.splitext(fn.lower())[1] in (".mp3", ".ogg", ".wav", ".flac"):
                names.append(fn)
        return names

    def on_jingle(self, widget):
        """Plays a jingle when the corresponding button is clicked.

        The name of the file is in the tooltip.  It must be the base name, the
        folder where the jingles are located is specified in the config
        file."""
        print "on_jingle: %s" % widget

    def on_quit(self, widget, event, data=None):
        """Ends the main GTK event loop."""
        gtk.main_quit()
        return False

    def run(self):
        """Shows the main window and starts the main GTK event loop."""
        self.window.show_all()
        gtk.main()


def run_app():
    gobject.threads_init()
    MainWindow().run()


# КАПЧУ надо выводить ПОСЛЕ приёма отправляемого сообщения!


if __name__ == "__main__":
    run_app()
    print "Bye."
