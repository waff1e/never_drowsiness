import vlc
import threading

isPlaying = 0
dir_sound = "sound_file"

player = vlc.MediaPlayer()

def playTimer():
    timer = threading.Timer(0.01, playTimer)
    timer.name = "Detefector_Timer"
    timer.daemon = True

    global isPlaying
    isPlaying = player.is_playing()

    timer.start()

playTimer()

def AlertSound(i):
    if isPlaying is 0:
        media = vlc.Media(f"{dir_sound}/step{i}.mp3")
        player.set_media(media)
        player.play()