#!/usr/bin/env python
# encoding=utf-8

import glob
import os
import subprocess

import gobject
import gtk
import pango
import pygtk

# ~/src/tmradio-client-gtk/simple.py


class Toolbar(gtk.HBox):
    def __init__(self, parent):
        gtk.HBox.__init__(self)
        self.main = parent

        self.btn_connected = gtk.ToggleButton("Online")
        self.btn_connected.set_tooltip_text("Starts darkice, you go online.")
        self.pack_start(self.btn_connected, expand=False)

        self.ctl_duration = gtk.Label("00:13")
        self.ctl_duration.set_padding(5, 0)
        self.ctl_duration.set_tooltip_text("You're online for this long.")
        self.pack_start(self.ctl_duration, expand=False)

        self.btn_mute = gtk.ToggleButton("Mute")
        self.btn_mute.set_tooltip_text("Disables sending your voice to the server.")
        self.pack_start(self.btn_mute, expand=False)

        self.ctl_stop = gtk.Button("Stop")
        self.ctl_stop.set_tooltip_text("Stops the audio file you're playing.")
        self.pack_start(self.ctl_stop, expand=False)

        self.ctl_progress = gtk.ProgressBar()
        self.ctl_progress.set_fraction(0.13)
        self.ctl_progress.set_text(u"Огоньки, 0:13 / 4:47")
        self.pack_start(self.ctl_progress, expand=True)


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
        self.player_jingle = None
        self.player_music = None

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Simple Broadcasting Console")
        self.window.connect("delete_event", self.on_quit)

        self.vbox = gtk.VBox(False, 2)
        self.window.add(self.vbox)
        self.vbox.pack_start(self.setup_menu(), expand=False, fill=True)
        self.vbox.pack_start(self.setup_toolbar(), expand=False, fill=True)
        self.vbox.pack_start(self.setup_main_view(), expand=True, fill=True)

        self.window.resize(800, 380)

    def setup_menu(self):
        self.menu_bar = MainMenu(on_exit=lambda x: self.on_quit(None, None))
        return self.menu_bar

    def setup_toolbar(self):
        return Toolbar(self)

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

        self.music = self.setup_music()
        buttons.pack_start(self.music, expand=True, fill=True)

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
                hbox.pack_start(self.get_audio_button(text, self.on_jingle), expand=True, fill=True)
            del files[:3]
            jingles.pack_start(hbox, expand=False, fill=True)

        return jingles

    def setup_music(self):
        """Sets up the music playlist."""
        files = gtk.VBox(False, spacing=0)
        for filename in self.get_audio_files("~/.config/yasbc/music"):
            files.pack_start(self.get_audio_button(filename, self.on_music), expand=False, fill=True)
        return files

    def get_audio_button(self, filename, handler):
        ctl = gtk.Button(os.path.splitext(os.path.basename(filename))[0].replace("_", "__"))
        ctl.set_tooltip_text(filename)
        ctl.set_can_focus(False)
        ctl.connect("clicked", handler)
        return ctl

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
        return self.on_audio(widget, "jingle")

    def on_music(self, widget):
        return self.on_audio(widget, "music")

    def on_audio(self, widget, mode):
        """Starts playing an audio file which corresponds to the specified
        widget.  If mode is "music", playing another such file will stop the
        previous one.  Other types are uncontrollable."""
        prop = "player_jingle"
        if mode == "music":
            prop = "player_music"
            if self.player_music:
                print "Killing previous player."
                self.player_music.kill()
                self.player_music = None

        filename = widget.get_tooltip_text()
        print "Playing %s %s" % (mode, filename)

        child = subprocess.Popen(["mplayer", filename], stdout=subprocess.PIPE)
        setattr(self, prop, child)

    def on_quit(self, widget, event, data=None):
        """Ends the main GTK event loop."""
        if self.player_music:
            self.player_music.kill()
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
