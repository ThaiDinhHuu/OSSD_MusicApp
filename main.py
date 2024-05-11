import dearpygui.dearpygui as dpg
import ntpath
import json
from mutagen.mp3 import MP3
from tkinter import Tk,filedialog
import threading
import pygame
import time
import random
import os
import atexit
import webbrowser
import yt_dlp

dpg.create_context()
dpg.create_viewport(title="SGU Music",large_icon="icon.ico",small_icon="icon.ico")
pygame.mixer.init()
global state
state=None

global no
no = 0

_DEFAULT_MUSIC_VOLUME = 0.5
pygame.mixer.music.set_volume(0.5)


def update_volume(sender, app_data):
	pygame.mixer.music.set_volume(app_data / 100.0)

def load_database():
	songs = json.load(open("data/songs.json", "r+"))["songs"]
	for filename in songs:
		dpg.add_button(label=f"{ntpath.basename(filename)}", callback=play, width=-1,
					   height=25, user_data=filename.replace("\\", "/"), parent="list")
		
		dpg.add_spacer(height=2, parent="list")


def update_database(filename: str):
	data = json.load(open("data/songs.json", "r+"))
	if filename not in data["songs"]:
		data["songs"] += [filename]
	json.dump(data, open("data/songs.json", "r+"), indent=4)

def update_slider():
    while pygame.mixer.music.get_busy() or state == 'playing':
       
        dpg.set_value("pos", pygame.mixer.music.get_pos() / 1000)
        time.sleep(0.7)
    if state == 'paused':
        return
    state = "stopped"
    dpg.configure_item("cstate", default_value=f"State: Stopped")
    dpg.configure_item("csong", default_value="Now Playing : ")
    dpg.configure_item("play", label="Play")
    dpg.configure_item("pos", max_value=100)
    dpg.configure_item("pos", default_value=0)



def play(sender, app_data, user_data):
	global state,no,current_song
	if user_data:
		no = user_data
		pygame.mixer.music.load(user_data)
		audio = MP3(user_data)
		dpg.configure_item(item="pos",max_value=audio.info.length)
		pygame.mixer.music.play()
		current_song = user_data
		thread=threading.Thread(target=update_slider,daemon=False).start()
		if pygame.mixer.music.get_busy():
			dpg.configure_item("play",label="Pause")
			state="playing"
			dpg.configure_item("cstate",default_value=f"State: Playing")
			dpg.configure_item("csong",default_value=f"Now Playing : {ntpath.basename(user_data)}")

def play_pause():
	global state,no,current_song
	if state=="playing":
		state="paused"
		pygame.mixer.music.pause()
		dpg.configure_item("play",label="Play")
		dpg.configure_item("cstate",default_value=f"State: Paused")
	elif state=="paused":
		state="playing"
		pygame.mixer.music.unpause()
		dpg.configure_item("play",label="Pause")
		dpg.configure_item("cstate",default_value=f"State: Playing")
	else:
		song = json.load(open("data/songs.json", "r"))["songs"]
		if song:
			song=random.choice(song)
			no = song
			pygame.mixer.music.load(song)
			pygame.mixer.music.play()
			current_song = song
			thread=threading.Thread(target=update_slider,daemon=False).start()	
			dpg.configure_item("play",label="Pause")
			if pygame.mixer.music.get_busy():
				audio = MP3(song)
				dpg.configure_item(item="pos",max_value=audio.info.length)
				state="playing"
				dpg.configure_item("csong",default_value=f"Now Playing : {ntpath.basename(song)}")
				dpg.configure_item("cstate",default_value=f"State: Playing")

def pre():
	global state,no
	songs = json.load(open('data/songs.json','r'))["songs"]
	try:
		n = songs.index(no)
		if n == 0:
			n = len(songs)
		play(sender=any,app_data=any,user_data=songs[n-1])
	except:
		pass

def next():
	global state,no
	try:
		songs = json.load(open('data/songs.json','r'))["songs"]
		n = songs.index(no)
		if n == len(songs)-1:
			n = -1
		play(sender=any,app_data=any,user_data=songs[n+1])
	except:
		pass

def stop():
    global state
    pygame.mixer.music.stop()  
    state = "stopped"
    dpg.configure_item("cstate", default_value="State: Stopped")
    dpg.configure_item("csong", default_value="Now Playing: ")
    dpg.configure_item("play", label="Play")  # Đặt lại nhãn nút play

def add_files():
	data=json.load(open("data/songs.json","r"))
	root=Tk()
	root.withdraw()
	filename=filedialog.askopenfilename(filetypes=[("Music Files", ("*.mp3","*.wav","*.ogg"))])
	root.quit()
	if filename.endswith(".mp3" or ".wav" or ".ogg"):
		if filename not in data["songs"]:
			update_database(filename)
			dpg.add_button(label=f"{ntpath.basename(filename)}",callback=play,width=-1,height=25,user_data=filename.replace("\\","/"),parent="list")
			dpg.add_spacer(height=2,parent="list")

def add_folder():
	data=json.load(open("data/songs.json","r"))
	root=Tk()
	root.withdraw()
	folder=filedialog.askdirectory()
	root.quit()
	for filename in os.listdir(folder):
		if filename.endswith(".mp3" or ".wav" or ".ogg"):
			if filename not in data["songs"]:
				update_database(os.path.join(folder,filename).replace("\\","/"))
				dpg.add_button(label=f"{ntpath.basename(filename)}",callback=play,width=-1,height=25,user_data=os.path.join(folder,filename).replace("\\","/"),parent="list")
				dpg.add_spacer(height=2,parent="list")

def search(sender, app_data, user_data):
	songs = json.load(open("data/songs.json", "r"))["songs"]
	dpg.delete_item("list", children_only=True)
	for index, song in enumerate(songs):
		if app_data in song.lower():
			dpg.add_button(label=f"{ntpath.basename(song)}", callback=play,width=-1, height=25, user_data=song, parent="list")
			dpg.add_spacer(height=2,parent="list")

def removeall():
	global state
	songs = json.load(open("data/songs.json", "r"))
	songs["songs"].clear()
	json.dump(songs,open("data/songs.json", "w"),indent=4)
	dpg.delete_item("list", children_only=True)
	dpg.configure_item("csong", default_value="Now Playing: ")
	dpg.configure_item("cstate", default_value="State: Stopped")
	dpg.configure_item("play", label="Play")
	state = "stopped"
	if pygame.mixer.music.get_busy():
        	pygame.mixer.music.stop()


def removethis(json_file_path):
    global current_song, state
    if current_song is None:
        return "No song is currently playing."

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    try:

        with open(json_file_path, "r") as f:
            data = json.load(f)

        playlist = data.get("songs", [])

        if current_song in playlist:
            playlist.remove(current_song)

            # Ghi lại danh sách đã cập nhật
            with open(json_file_path, "w") as f:
                json.dump(data, f, indent=4)

            # Đặt lại bài nhạc hiện tại
            current_song = None
            
            # Xóa tất cả các mục con trong danh sách phát trong GUI
            dpg.delete_item("list", children_only=True)

            state = "stopped"
            dpg.configure_item("csong", default_value="Now Playing: ")
            dpg.configure_item("cstate", default_value="State: Stopped")
            dpg.configure_item("play", label="Play")
            # Tải lại danh sách phát vào GUI
            load_database()
    
    except json.JSONDecodeError:
        return "Error decoding the playlist file."
    except Exception as e:
        return f"An error occurred: {e}"

youtube_url = ""  # Đảm bảo biến này được khởi tạo

# Đường dẫn đến tệp JSON và thư mục lưu trữ
download_path = "data/music"
json_file_path = "data/songs.json"


def set_youtube_url(sender, app_data, user_data):
    global youtube_url
    youtube_url = app_data  # Lưu URL từ ô nhập liệu
    print(f"Updated YouTube URL: {youtube_url}")  # In để kiểm tra giá trị
# Hàm để tải xuống tệp MP3 từ YouTube
def download_youtube_audio(video_url, download_path):
    ydl_opts = {
        'format': 'bestaudio/best',  # Tải xuống âm thanh tốt nhất
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',  # Chuyển đổi sang MP3
            'preferredquality': '192',  # Chất lượng
        }],
        'outtmpl': os.path.join(download_path, '%(title)s.mp3'),  # Đảm bảo định dạng là ".mp3"
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])  # Tải xuống từ YouTube
    
    # Đảm bảo phần mở rộng là ".mp3"
    return os.path.join(download_path, ydl.prepare_filename(ydl.extract_info(video_url, download=False)).replace('.m4a', '.mp3'))

# Hàm để thêm bài nhạc vào danh sách phát
def add_to_playlist(json_file_path, song_path):
    try:
        # Đọc tệp JSON
        with open(json_file_path, "r") as f:
            data = json.load(f)

        playlist = data.get("songs", [])

        # Thêm bài nhạc vào danh sách phát nếu chưa có
        if song_path not in playlist:
            playlist.append(song_path)  # Đảm bảo phần mở rộng là ".mp3"
            with open(json_file_path, "w") as f:
                json.dump(data, f, indent=4)

            return "Song added to playlist."
        else:
            return "Song already in playlist."
    
    except Exception as e:
        return f"An error occurred: {e}"

# Kiểm tra tên tệp trước khi thêm vào danh sách phát
def download_and_add():
    global youtube_url
    if not youtube_url.startswith("https://www.youtube.com"):
        print("Please enter a valid YouTube URL.")
        return
    
    try:
        # Tải xuống tệp MP3 từ YouTube
        filename = download_youtube_audio(youtube_url, download_path)  # Đảm bảo là MP3
        
        # Thêm vào danh sách phát
        # result = add_to_playlist(json_file_path, filename)  # Đảm bảo là ".mp3"
        # print(result)
    
    except Exception as e:
        print(f"Error during download: {e}")

# Xây dựng giao diện trong Dear PyGui
with dpg.window(label="YouTube Downloader"):
    # Ô nhập liệu văn bản để nhập đường dẫn YouTube
    dpg.add_input_text(
        label="Enter YouTube URL", 
        callback=set_youtube_url,
        width=-1
    )
    
    # Nút để tải xuống và thêm vào danh sách phát
    dpg.add_button(
        label="Download and Add to Playlist",
        callback=download_and_add,
        width=-1
    )



with dpg.theme(tag="base"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_Button, (130, 142, 250))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (137, 142, 255, 95))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (137, 142, 255))
		dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
		dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 4)
		dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 4, 4)
		dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 4, 4)
		dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.50, 0.50)
		dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize,0)
		dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,10,14)
		dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (25, 25, 25))
		dpg.add_theme_color(dpg.mvThemeCol_Border, (0,0,0,0))
		dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0,0,0,0))
		dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (130, 142, 250))
		dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (221, 166, 185))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (172, 174, 197))

with dpg.theme(tag="slider_thin"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250,99))
		dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
		dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.theme(tag="slider"):
	with dpg.theme_component():
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (130, 142, 250,99))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (255, 255, 255))
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (130, 142, 250,99))
		dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 3)
		dpg.add_theme_style(dpg.mvStyleVar_GrabMinSize, 30)

with dpg.theme(tag="songs"):
	with dpg.theme_component():
		dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 2)
		dpg.add_theme_color(dpg.mvThemeCol_Button, (89, 89, 144,40))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0,0,0,0))

with dpg.font_registry():
	monobold = dpg.add_font("fonts/MonoLisa-Bold.ttf", 12)
	head = dpg.add_font("fonts/MonoLisa-Bold.ttf", 15)

with dpg.window(tag="main",label="window title"):
	with dpg.child_window(autosize_x=True,height=45,no_scrollbar=True):
		dpg.add_text(f"Now Playing : ",tag="csong")
	dpg.add_spacer(height=2)

	with dpg.group(horizontal=True):
		with dpg.child_window(width=200,tag="sidebar"):
			dpg.add_text("SGU Musicart",color=(137, 142, 255))
			
			dpg.add_spacer(height=2)
			dpg.add_button(label="Support", width=-1, height=23, callback=lambda: webbrowser.open(url="https://www.facebook.com/profile.php?id=100010994175862"))
			dpg.add_spacer(height=5)
			dpg.add_separator()
			dpg.add_spacer(height=5)
			dpg.add_button(label="Add File",width=-1,height=28,callback=add_files)
			dpg.add_button(label="Add Folder",width=-1,height=28,callback=add_folder)
			dpg.add_button(label="Remove This Song", width=-1, height=28, callback=lambda: removethis("data/songs.json"))
			dpg.add_button(label="Remove All Songs",width=-1,height=28,callback=removeall)
			dpg.add_spacer(height=5)
			dpg.add_separator()
			dpg.add_spacer(height=5)
			dpg.add_text(f"State: {state}",tag="cstate")
			dpg.add_spacer(height=5)
			dpg.add_separator()

		with dpg.child_window(autosize_x=True,border=False):
			with dpg.child_window(autosize_x=True,height=80,no_scrollbar=True):
				with dpg.group(horizontal=True):
					with dpg.group(horizontal=True):
						dpg.add_button(label="Play",width=65,height=30,tag="play",callback=play_pause)
						dpg.add_button(label="Pre",width=65,height=30,show=True,tag="pre",callback=pre)
						dpg.add_button(label="Next",tag="next",show=True,callback=next,width=65,height=30)
						dpg.add_button(label="Stop",callback=stop,width=65,height=30)
					dpg.add_slider_float(tag="volume", width=120,height=15,pos=(10,59),format="%.0f%.0%",default_value=_DEFAULT_MUSIC_VOLUME * 100,callback=update_volume)
					dpg.add_slider_float(tag="pos",width=-1,pos=(140,59),format="")

			with dpg.child_window(autosize_x=True,delay_search=True):
				with dpg.group(horizontal=True,tag="query"):
					dpg.add_input_text(hint="Search for a song",width=-1,callback=search)
				dpg.add_spacer(height=5)
				with dpg.child_window(autosize_x=True,delay_search=True,tag="list"):
					load_database()

	dpg.bind_item_theme("volume","slider_thin")
	dpg.bind_item_theme("pos","slider")
	dpg.bind_item_theme("list","songs")

dpg.bind_theme("base")
dpg.bind_font(monobold)

def safe_exit():
	pygame.mixer.music.stop()
	pygame.quit()

atexit.register(safe_exit)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main",True)
dpg.maximize_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
