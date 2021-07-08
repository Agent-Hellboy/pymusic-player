from os import system, name, path, environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import sys
import pygame 
from mutagen.mp3 import MP3 
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession

bottom_toolbar = HTML(' <b>[play]</b> play <b>[stop]</b> stop  <b>[pause]</b> pause <b>[exit]</b> exit <b>[resume]</b> resume <b>[clear]</b> clear')

completer = WordCompleter(['play', 'exit', 'resume', 'pause', 'stop', 'progress', 'restart'], ignore_case=True)

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
        return round(MP3(self.file).info.length, 2)
    def get_pos(self):
        return pygame.mixer.music.get_pos()
    def restart(self):
        pygame.mixer.music.rewind()

class Terminal:
    def __init__(self) -> None:
        self.player = None
        self.playing = False
        self.paused = False 
        self.functions = {
            'exit': sys.exit,
            'play': self.play,
            'resume': self.resume,
            'pause': self.pause,
            'stop': self.stop,
            'restart': self.restart,
            #'progress': self.progress,
            'clear': self.clear
        }
    
    def clear(self):
        clear()

    def play(self, filepath):
        if path.isfile(filepath):
            if self.playing:
                self.stop()

            filepath.replace("\\", "/")
            self.player = MP3Player(filepath)
            self.player.play()
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

    def parse(self, input):
        
        inWords = input.split()
        if not inWords:
            return " "
        inWords[0] = inWords[0].lower()
        keywords = ['play', 'exit', 'resume', 'pause', 'stop', 'clear', 'restart']

        if inWords[0] in keywords:
            if len(inWords) == 1:
                if inWords[0] == 'exit':
                    sys.exit()
                else:
                    try:
                        result = self.functions[inWords[0]]()
                        return result
                    except:
                        return f"Invalid Syntax: {input}"
            else:
                try:
                    result = self.functions[inWords[0]](inWords[1])
                    return result
                except:
                    return f"Invalid Syntax: {input}"
            
        else:
            return f"Invalid Syntax: {input}"



# Create custom key bindings first.
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

while True:
    try:
        inp = session.prompt("\n❯ ", bottom_toolbar=bottom_toolbar, key_bindings=kb)
        output = terminal.parse(inp)
        output = [output if output is not None else " "][0]
        print(output)
    except:
        print("\nThanks For Using!")
        sys.exit()