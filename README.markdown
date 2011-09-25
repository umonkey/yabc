Yet Another Broadcast Console
=============================

This is a simple GTK program which helps you broadcast to an icecast server,
play some jingles and music, mute and unmute some sources.  It doesn't work with
the audio itself; [mplayer][1] is used to play audio files and [darkice][2] is
used to broadcast the output.  You will probably need [JACK][3] to use this.

How it works:

- Jingles are MP3/OGG/WAV/FLAC files located in `~/.config/yabc/jingles`.
- Songs are located in `~/.config/yabc/music`.
- When you go online, `~/.config/yabc/commands/connect` is executed; when you go
  offline, `~/.config/yabc/commands/disconnect` is executed.
- When you press the mute button, `~/.config/yabc/commands/mute` is executed;
  when you unpress it, `~/.config/yabc/commands/unmute` is executed.

[1]: http://www.mplayerhq.hu/
[2]: http://code.google.com/p/darkice/
[3]: http://www.jackaudio.org/
