import os
import pygame
import time

class AudioEngine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        self.players = {} # Alias for client.py compatibility
        self.channels = {} # { "1": pygame.mixer.Channel(0), "2": pygame.mixer.Channel(1) }
        self.sounds = {}   # { "1": pygame.mixer.Sound }
        self.volumes = { "1": 1.0, "2": 1.0 }
        self.is_playing = { "1": False, "2": False }
        self.start_times = { "1": 0, "2": 0 }
        self.accumulated_times = { "1": 0, "2": 0 }
        self.durations = { "1": 0, "2": 0 }
        
        # Initialize fixed channels
        self.channels["1"] = pygame.mixer.Channel(0)
        self.channels["2"] = pygame.mixer.Channel(1)
        self.players = self.channels # Shared reference
        
        print("Pygame Audio Engine Initialized successfully.")

    def is_ready(self):
        return True

    def play(self, channel, filepath, loop=True):
        ch_str = str(channel)
        if ch_str not in self.channels:
            print(f"Error: Unsupported channel {ch_str}")
            return

        try:
            sound = pygame.mixer.Sound(filepath)
            self.sounds[ch_str] = sound
            self.durations[ch_str] = sound.get_length() * 1000 # to ms
            
            # Start playing
            loops = -1 if loop else 0
            self.channels[ch_str].play(sound, loops=loops)
            self.start_times[ch_str] = time.time()
            self.accumulated_times[ch_str] = 0
            self.is_playing[ch_str] = True
            
            # Re-apply volume/panning
            self.set_volume(ch_str, self.volumes[ch_str] * 100)
            
            print(f"Playing {filepath} on channel {ch_str} (Panned to {'Left' if ch_str=='1' else 'Right'})")
        except Exception as e:
            print(f"Error playing {filepath}: {e}")

    def pause(self, channel):
        ch_str = str(channel)
        if ch_str in self.channels and self.is_playing[ch_str]:
            self.channels[ch_str].pause()
            self.accumulated_times[ch_str] += (time.time() - self.start_times[ch_str]) * 1000
            self.is_playing[ch_str] = False

    def resume(self, channel):
        ch_str = str(channel)
        if ch_str in self.channels and not self.is_playing[ch_str]:
            self.channels[ch_str].unpause()
            self.start_times[ch_str] = time.time()
            self.is_playing[ch_str] = True

    def stop(self, channel):
        ch_str = str(channel)
        if ch_str in self.channels:
            self.channels[ch_str].stop()
            self.is_playing[ch_str] = False
            self.accumulated_times[ch_str] = 0

    def restart(self, channel):
        ch_str = str(channel)
        if ch_str in self.sounds:
            self.channels[ch_str].play(self.sounds[ch_str], loops=-1)
            self.start_times[ch_str] = time.time()
            self.accumulated_times[ch_str] = 0
            self.is_playing[ch_str] = True

    def set_volume(self, channel, level):
        ch_str = str(channel)
        vol = float(level) / 100.0
        self.volumes[ch_str] = vol
        
        if ch_str in self.channels:
            # Independent Panning: (Left, Right)
            if ch_str == "1":
                self.channels[ch_str].set_volume(vol, 0.0) # ONLY LEFT
            elif ch_str == "2":
                self.channels[ch_str].set_volume(0.0, vol) # ONLY RIGHT
            print(f"Volume for channel {ch_str} set to {level}% (Panned)")

    def get_status(self, channel):
        ch_str = str(channel)
        if ch_str in self.channels:
            current_time = self.accumulated_times[ch_str]
            if self.is_playing[ch_str]:
                current_time += (time.time() - self.start_times[ch_str]) * 1000
            
            # Handle looping
            if self.durations[ch_str] > 0:
                current_time = current_time % self.durations[ch_str]

            return {
                'playing': self.channels[ch_str].get_busy(),
                'volume': int(self.volumes[ch_str] * 100),
                'time': int(current_time),
                'duration': int(self.durations[ch_str])
            }
        return None

audio_engine = AudioEngine()
