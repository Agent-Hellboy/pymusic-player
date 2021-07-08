from os import system, name, path, environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import sys
import pygame 
from mutagen.mp3 import MP3 
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession

completer = WordCompleter(['play', 'exit', 'resume', 'pause', 'stop', 'clear', 'restart', 'length', 'vol', 'setvol', 'progress', 'status'], ignore_case=True)

session = PromptSession(completer=completer)

def clear():
    if name == "nt":
        system('cls')
    else:
        system('clear')

pygame.init()
clear()

class MP3Player:
    def __init__(self,file):
        self.file = file
    def play(self):
        pygame.mixer.music.load(self.file)
        pygame.mixer.music.play()
    def stop(self):
        pygame.mixer.music.stop()
    def unpause(self):
        pygame.mixer.music.unpause()
    def pause(self):
        pygame.mixer.music.pause()
    def get_music_length(self):
        return round(MP3(self.file).info.length)
    def get_pos(self):
        return pygame.mixer.music.get_pos()
    def restart(self):
        pygame.mixer.music.rewind()
    def get_volume(self):
        return pygame.mixer.music.get_volume()
    def set_volume(self, volume):
        pygame.mixer.music.set_volume(float(volume))
    def queue(self, file):
        pygame.mixer.music.queue(file)

class Terminal:
    def __init__(self) -> None:
        self.player = None
        self.help = lambda: 'https://github.com/TheLegendBeacon/pymusic-player/blob/3f38001e40d00e613f57813cf26c0e022a243432/README.md'
        self.playing = False
        self.paused = False
        self.volume = 1.0 
        self.functions = {
            'exit': sys.exit,
            'play': self.play,
            'resume': self.resume,
            'pause': self.pause,
            'stop': self.stop,
            'restart': self.restart,
            'progress': self.progress,
            'clear': self.clear,
            'length': self.length,
            'vol': self.vol,
            'setvol': self.set_volume,
            'status': self.status,
            'help': self.help
        }
    
    def clear(self):
        clear()

    def status(self):
        if self.playing:
            return f"Playing: {self.player.file}, Paused: {self.paused}\n{self.progress()}"
        else:
            return "Not playing anything."

    def toolbar_string(self):
        return f'''<b>[play]</b> play <b>[stop]</b> stop  <b>[pause]</b> pause <b>[exit]</b> exit <b>[resume]</b> resume <b>[clear]</b> clear <b>|</b> volume: {int(self.volume*100)}%'''

    def play(self, filepath):
        if path.isfile(filepath):
            if self.playing:
                self.stop()

            filepath.replace("\\", "/")
            self.player = MP3Player(filepath)
            self.player.play()
            self.player.set_volume(self.volume)
            self.playing = True
            self.paused = False
            return "Started playing."
        else:
            return "Error: File Not Found."
    
    def stop(self):
        if self.playing:
            self.player.stop()
            self.playing = False
            self.paused = False
            return "Stopped."
        else:
            return "Nothing is playing right now."
    
    def pause(self):
        if self.playing:
            if self.paused:
                return "You are already paused."
            else:
                self.player.pause()
                self.paused = True
                return "Paused the track."
        else:
            return "You are not playing anything."

    def resume(self):
        if self.playing:
            if self.paused:
                self.player.unpause()
                self.paused = False
                return "Successfully resumed."
            else:
                return "You are already playing."
        else:
            return "Nothing is playing right now."

    def restart(self):
        if self.playing:
            self.player.restart()
            return "Restarted the track."
        else:
            return "Nothing is playing right now."

    def length(self):
        if self.playing:
            seclength = self.player.get_music_length()
            minlength, seclength = seclength//60, seclength%60 
            hourlength, minlength = minlength//60, minlength%60

            if hourlength == 0:
                return f"{minlength} minutes and {seclength} seconds"
            else:
                return f"{hourlength} hours, {minlength} minutes and {seclength} seconds"
        else:
            return "Nothing is playing right now."
    
    def vol(self):
        return f"{str(int(self.volume*100))}%"
    
    def set_volume(self, volume):
        volume = volume.replace("%", '')
        if int(float(volume)) > 100:
            return "You need a value smaller or equal than 100%."
        else:
            self.volume = int(float(volume))/100
            pygame.mixer.music.set_volume(self.volume)
            return f"Set volume to {100*self.volume}"

    def progress(self):
        if self.playing:
            progressBar = ['-' for x in range(50)]
            length = self.player.get_music_length()
            pos = self.player.get_pos() // 1000
            ratio = round(pos/length * 50)
            for x in range(ratio):
                progressBar[x] = "█"
            return f"\n|{''.join(progressBar)}| {pos}/{length} seconds, {length-pos} sec ETA\n"
        else:
            return "You are not playing anything."

    def parse(self, inp):
        
        inWords = inp.split()
        if not inWords:
            return " "
        commas = [inWords.index(x) for x in [x for x in inWords if '"' in x]]
        if len(inWords) > 2:
            inWords = [inWords[0], " ".join([inWords[x] for x in range(commas[0], commas[1]+1)])]

        inWords[0] = inWords[0].lower()
        keywords = ['play', 'exit', 'resume', 'pause', 'stop', 'clear', 'restart', 'length', 'vol', 'setvol', 'progress', 'status', 'help']

        if inWords[0] in keywords:
            if len(inWords) == 1:
                if inWords[0] == 'exit':
                    sys.exit()
                else:
                    try:
                        result = self.functions[inWords[0]]()
                        return result
                    except:
                        return f"Invalid Syntax: {inp}"
            else:
                try:
                    result = self.functions[inWords[0]](inWords[1])
                    return result
                except:
                    return f"Invalid Syntax: {inp}"
            
        else:
            return f"Invalid Syntax: {inp}: Not a valid keyword."

kb = KeyBindings()
terminal = Terminal()

@kb.add('c-u')
def _(*args):
    if terminal.paused == True:
        terminal.resume()
    else:
        terminal.pause()

@kb.add('c-x')
def _(*args):
    terminal.stop()

@kb.add('c-r')
def _(*args):
    terminal.restart()

@kb.add('c-up')
def _(*args):
    terminal.set_volume(str(terminal.volume*100 + 10))

@kb.add('c-down')
def _(*args):
    terminal.set_volume(str(terminal.volume*100 - 10))

while True:
    try:
        inp = session.prompt("\n❯ ", bottom_toolbar=HTML(terminal.toolbar_string()), key_bindings=kb)
        output = terminal.parse(inp)
        output = [output if output is not None else " "][0]
        print(output)
    except (KeyboardInterrupt, EOFError):
        print("\nThanks For Using!")
        sys.exit()
    except:
        print("There was an error.")
        sys.exit()
