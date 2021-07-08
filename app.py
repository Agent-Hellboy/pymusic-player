import os
import signal
import time

import pygame
from mutagen.mp3 import MP3
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.shortcuts import yes_no_dialog


class MP3Player:
    def __init__(self, file):
        self.file = file

    def play(self):
        pygame.init()
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play()

    def stop(self):
        pygame.mixer.music.stop()

    def unpause(self):
        pygame.mixer.music.unpause()

    def pause(self):
        pygame.mixer.music.pause()

    def get_music_length(self):
        return round(MP3(self.file).info.length, 2)

    def get_pos(self):
        return pygame.mixer.music.get_pos()

    def restart(self):
        pygame.mixer.music.rewind()


bottom_toolbar = HTML(
    " <b>[p]</b> play <b>[x]</b> stop  <b>[u]</b> pause <b>[z]</b> unpause"
)

# Create custom key bindings first.
kb = KeyBindings()
mp3_player = mp3_player = MP3Player("music/Audio Examples _ SoundHelix.mp3")

cancel = False


@kb.add("x")
def _(event):
    cancel = True
    mp3_player.stop()


@kb.add("u")
def _(event):
    mp3_player.pause()


@kb.add("z")
def _(event):
    mp3_player.unpause()


@kb.add("p")
def _(event):
    mp3_player.play()


title = HTML(
    'You can hear till 800 sec <style bg="yellow" fg="black"> press keys and enjoy </style>'
)
with patch_stdout():
    with ProgressBar(key_bindings=kb, bottom_toolbar=bottom_toolbar, title=title) as pb:
        for i in pb(range(800)):
            time.sleep(1)

            # Stop when the cancel flag has been set.
            if cancel:
                break
