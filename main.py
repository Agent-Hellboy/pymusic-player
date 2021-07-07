import time
from pygame import mixer
from mutagen.mp3 import MP3
from rich.console import Console
from rich.live import Live
from rich.progress import Progress, BarColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.prompt import Prompt

window = Console(width=100)
player_bar = Progress(
    TimeElapsedColumn(),
    BarColumn(),
    TimeRemainingColumn(),
)

mixer.init()
mixer.music.load("bensound-dubstep.mp3")
musiclength = round(MP3("bensound-dubstep.mp3").info.length, 2)
print(musiclength)

window.rule("[bold blue]CLI Music Player", style="red")
print()

action = Prompt.ask("[blink yellow]Press 'p' to start playing", console=window)
while action != 'p':
    action = Prompt.ask("[blink yellow]Press 'p' to start playing", console=window)

window.clear()

window.rule("[bold blue]CLI Music Player", style="red")
print()
window.print("[bold red]Currently playing: [blink yellow]DubStep")
mixer.music.play()
with player_bar:
    task = player_bar.add_task("",total=musiclength)
    while not player_bar.finished:
        player_bar.update(task, advance=1)
        time.sleep(1)

