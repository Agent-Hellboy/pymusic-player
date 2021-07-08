import time

from mutagen.mp3 import MP3
from pygame import mixer
from pynput import keyboard
from rich import print
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import (BarColumn, Progress, ProgressColumn, TimeRemainingColumn)
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

class KeyBinder():

    def __init__(self, keybinds) -> None:
        self.keybinds = keybinds
        self._pressed_vks = set()
    
    def _get_vk(self, key):
        return key.vk if hasattr(key, 'vk') else key.value.vk

    def _is_combination_pressed(self, combination):
        return all([self._get_vk(key) in self._pressed_vks for key in combination])

    def _on_press(self, key):
        vk = self._get_vk(key)
        self._pressed_vks.add(vk)

        for combination in self.keybinds:
            if self._is_combination_pressed(combination):
                self.keybinds[combination]()

    def _on_release(self, key):
        vk = self._get_vk(key)
        self._pressed_vks.remove(vk)
    
    def start(self):
        listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        ).start()

class MP3Player():
    def __init__(self,file):
        self.file=file
        self.duration = round(MP3(self.file).info.length, 2)
        mixer.init()

    def load(self, file=None):
        if file is None:
            file = self.file
        mixer.music.load(file)

    def unload(self):
        mixer.music.unload()

    def get_length(self):
        return self.duration

    def start(self):
        mixer.music.play()

    def play(self):
        mixer.music.unpause()
    
    def pause(self):
        mixer.music.pause()
       
    def replay(self):
        mixer.music.rewind()

def makelayouts():
    "Creates all necesory layout"

    layout = Layout(name="root")
    player = Layout(name="root")
    layout.split_column(
        Layout(name="head", size=2),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="player", ratio=2),
        Layout(name="input")
    )
    
    player.split_column(
        Layout(name="player-info", size=None),
        Layout(name="player-bar", size=1)
    )
    player["player-bar"].split_row(
        Layout(name="bar-comp", size=8, ratio=1),
        Layout(name="bar", size=None),
        Layout(name="bar-left", size=8, ratio=1),
        
    )

    return layout, player
    
def getinput():
    pass

def formatTime(seconds = None):
    if seconds < 60:
        if seconds < 10:
            return f"[grey62]0:00:0{seconds}"
        return f"[grey62]0:00:{seconds}"
    min = float(seconds / 60).__floor__()
    sec = seconds % 60
    if sec < 10:
        sec = f"0{sec}"
    if min < 60:
        if min < 10:
            return f"[grey62]0:0{min}:{sec}"
        return f"[grey62]0:{min}:{sec}"
    hr = float(min / 60).__floor__()
    min = min % 60
    if min < 10:
        min = f"0{min}"
    
    return f"[grey62]{hr}:{min}:{sec}"

def main() -> None:
    # Initialize Console and music player
    global dur_comp
    dur_comp = 0
    dur_left = 0
    completed = False
    global paused
    paused = False
    window = Console()
    mp3_player = MP3Player("bensound-dubstep.mp3")

    # Create renderebles
    player_bar = Progress(
        BarColumn(bar_width=None)
    )
    player_bar_id = player_bar.add_task("", total=mp3_player.duration)

    player = Table.grid(expand=True)
    player.add_row("[bold red]Currently playing: [blink blue]DubStep")
    player.add_row(f"[bold red]Duration: [blink blue]{round(mp3_player.duration)} Seconds")

    command_list = Table.grid(expand=True)
    command_list.add_column(style="", justify="right")
    command_list.add_column(no_wrap=True)
    command_list.add_row("[dark_orange]Play:", " [bold dark_orange]shift + p")
    command_list.add_row("[dark_orange]Pause:", " [bold dark_orange]shift + z")
    command_list.add_row("[dark_orange]Replay:", " [bold dark_orange]shift + r")

    # Initialize Layout
    root_layout, player_layout = makelayouts()
    root_layout["head"].update(Rule("[bold blue]CLI Music Player", style="red"))
    root_layout["input"].update(Panel(Align.center(command_list, vertical="middle"), title="[yellow]Command List", border_style="green"))
    player_layout["player-info"].update(player)
    player_layout["bar-comp"].update(Align.left("-:--:--"))
    player_layout["bar"].update(Align.center(player_bar))
    player_layout["bar-left"].update(Align.right("-:--:--"))
    root_layout["player"].update(Panel(player_layout, title="[yellow]Player", border_style="green"))

    # Start music (this is for now as of testing)
    mp3_player.load()
    mp3_player.start()

    def play():
        global paused
        if paused:
            mp3_player.play()
            paused = False

    def pause():
        global paused
        if not paused:
            mp3_player.pause()
            paused = True

    def restart():
        global dur_comp
        mp3_player.replay()
        player_bar.reset(player_bar_id)
        dur_comp = 0

    keybinds = {
        frozenset([keyboard.KeyCode(vk=160), keyboard.KeyCode(vk=80)]): play,  # ctrl + p
        frozenset([keyboard.KeyCode(vk=160), keyboard.KeyCode(vk=90)]): pause,  # ctrl + z
        frozenset([keyboard.KeyCode(vk=160), keyboard.KeyCode(vk=82)]): restart,  # ctrl + r
    }
    keybinder = KeyBinder(keybinds)
    # Render the Layout
    with Live(root_layout, refresh_per_second=10, console=window, screen=True):
        keybinder.start()
        while True:
            while not player_bar.finished and not paused:
                dur_comp += 1
                dur_left = mp3_player.duration.__floor__() - dur_comp + 1
                player_layout["bar-comp"].update(Align.left(formatTime(dur_comp)))
                player_layout["bar-left"].update(Align.right(formatTime(dur_left)))
                player_bar.advance(player_bar_id, 1)
                time.sleep(1)
            if player_bar.finished and not completed:
                completed = True

if __name__=='__main__':
    main()
