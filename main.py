from kivy.core import handle_win_lib_import_error
from kivy.uix.behaviors import button
from kivy.uix.image import Image, AsyncImage
import kivymd
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDFlatButton, MDRectangleFlatIconButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import ImageLeftWidget, TwoLineIconListItem, MDList, IconLeftWidget, TwoLineAvatarListItem
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.loader import Loader
from kivy.app import App
from kivy.base import ExceptionManager, ExceptionHandler
#from kivymd.uix.spinner import MDSpinner
##############################
#Window.size = (360, 640)
##############################
from concurrent.futures import ThreadPoolExecutor
import threading
import requests
import base64
import json
import os
import shutil
from pyDes import *
from mutagen.mp4 import MP4, MP4Cover



#    import android
#    from android.permissions import request_permissions, Permission
#    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])



#class CrashHandler(ExceptionHandler):
#    def handle_exception(self, inst):
#        print(inst)
#        return ExceptionManager.PASS
#ExceptionManager.add_handler(CrashHandler())
search_base_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
song_details_base_url = "https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids="

class MyApp(MDApp):
    title = "Black Hole"
    lyr = False
#    obj = ObjectProperty(None)
#    path = download_dir_path
    def build(self):
        self.theme_cls.theme_style = "Light"#Dark"
        self.theme_cls.bg_darkest
        #Loader.loading_image = 'temp.jpg'#'giphy.gif'
        #return Builder.load_string(main)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.path = os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Songs')
        self.data_path = os.path.join(self.user_data_dir, 'cache')
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        self.file_manager.ext = [".m4a"]
        if os.path.exists(self.path):
            pass
        else:
            os.mkdir(self.path)
        if os.path.exists(self.data_path):
            pass
        else:
            os.mkdir(self.data_path)


    def spin(self):
        #print('pass')
        self.root.ids.spinner.active = True
        #Clock.schedule_once(self.show_data)
        #self.show_data()

    def show_data(self, *args):
        close_btn = MDFlatButton(text="Close", on_release=self.close_dialog)
        if self.root.ids.song_name.text == '':
            self.dia = MDDialog(title="Invalid Name", text="Please enter a song name", size_hint=(0.7,1), buttons=[close_btn])
            self.dia.open()
        
        else:
            #self.schedule_fun = Clock.schedule_once(self.spin)
            #Clock.schedule_once(self.stop_spin, 5)
            self.spin()
            self.change_screen('SongListScreen', 'left')
            self.list_view = self.root.ids.container
            self.list_view.clear_widgets()
            #self.img_lst = []
            self.search_data = json.loads(requests.get(search_base_url+self.root.ids.song_name.text).text.replace("&quot;","'").replace("&amp;", "&").replace("&#039;", "'"))['songs']['data']
            #for i in range(len(self.search_data)):
            #executor.submit(self.down_img)
            #self.down_img()
            for i in range(len(self.search_data)):
                self.down_img(i)
            #t1 = threading.Thread(target=self.down_img(i))
            #t1.start()
            #t1.join()
            #self.root.ids.spinner.active = False
            #executor = ThreadPoolExecutor(max_workers=10)
            #executor.submit(self.add_img)
            #executor.shutdown()

    def fetch_details(self):
        print('started fetching details')
        self.song_data = json.loads(requests.get(song_details_base_url+self.song_id).text.replace("&quot;","'").replace("&amp;", "&").replace("&#039;", "'"))[self.song_id]
        try:
            url = self.song_data['media_preview_url']
            url = url.replace("preview", "aac")
            if self.song_data['320kbps']=="true":
                url = url.replace("_96_p.mp4", "_320.mp4")
            else:
                url = url.replace("_96_p.mp4", "_160.mp4")
            self.song_dwn_url = url
        except KeyError or TypeError:
            self.song_data['media_url'] = self.decrypt_url(self.song_data['encrypted_media_url'])
            if self.song_data['320kbps']!="true":
                self.song_dwn_url = self.song_data['media_url'].replace("_320.mp4","_160.mp4")

        self.song_name = self.song_data['song']
        self.album = self.song_data['album']
        self.artist_name = self.song_data["primary_artists"]
        self.featured_artist = self.song_data["featured_artists"]
        self.year = self.song_data["year"]
        self.genre = (self.song_data["language"]).capitalize()

    def decrypt_url(url):
        des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0",pad=None, padmode=PAD_PKCS5)
        enc_url = base64.b64decode(url.strip())
        dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
        dec_url = dec_url.replace("_96.mp4", "_320.mp4")
        return dec_url

    def down_img(self, i):
        #image_url = self.search_data[i]['image'].replace('50x50', '500x500')
        #song_id = self.search_data[i]['id']
        #image_name = os.path.join(self.data_path,song_id+'.jpg')
        lst = TwoLineAvatarListItem(text=self.search_data[i]['title'], secondary_text=self.search_data[i]['more_info']['primary_artists'], on_press=lambda x: self.song_details(i))
        lst.add_widget(IconLeftWidget(icon='music'))
        self.list_view.add_widget(lst)
        #self.img_lst.append((image_url, image_name))

    def song_details(self, i):
        self.s_manager = self.root.ids.screen_manager
        self.s_manager.transition.direction = 'left'
        self.s_manager.current = 'SongDetailsScreen'
        self.details_screen = self.root.ids.SongDetailsScreen
        self.details_screen.clear_widgets()
        self.song_name = self.search_data[i]['title']
        self.song_id = self.search_data[i]['id']
        self.artist_name = self.search_data[i]['more_info']['primary_artists']
        self.image_url = self.search_data[i]['image'].replace('50x50', '500x500')
        #self.image_path = os.path.join(self.data_path,self.song_id+'.jpg')

        self.details_screen.add_widget(AsyncImage(source=self.image_url, pos_hint={"center_x":0.5, "center_y":0.8}))
        self.details_screen.add_widget(MDLabel(text=self.song_name, halign='center', font_style='H4', pos_hint={"top":0.95}))
        self.details_screen.add_widget(MDLabel(text=self.artist_name, halign='center', theme_text_color='Secondary', font_style='H6', pos_hint={"top":0.9}))
        self.details_screen.add_widget(MDRoundFlatButton(text='Play', pos_hint={'center_x':0.5, "center_y":0.3}, on_press=lambda x: self.play_song()))
        self.details_screen.add_widget(MDRoundFlatButton(text='Download', pos_hint={'center_x':0.5, "center_y":0.2}, on_press=lambda x: self.download_song()))
        
    def change_screen(self, screen, direction):
        self.root.ids.screen_manager.transition.direction = direction
        self.root.ids.screen_manager.current = screen
    
    def download_bar(self):
        self.progress_val = 0
        self.dia = MDDialog(text="Downloading ...", size_hint=(0.7,1))
        self.dia.add_widget(MDProgressBar(pos_hint = {'center_x':0.5, 'center_y':0.5}, size_hint_x = 0.5, value = self.progress_val))
        self.dia.open()

    def play_song(self):
        close_btn = MDFlatButton(text="Close", on_release=self.close_dialog)
        self.dia = MDDialog(text="Feature under development!", size_hint=(0.7,1), buttons=[close_btn])
        self.dia.open()
    
    def download_song(self):
        self.fetch_details()
        #t2 = threading.Thread(target=self.fetch_details)
        #t2.start()
        #t2.join()
        print('started downloading song')
        #print(self.song_dwn_url)
        fname = "{}/{} - {}.m4a".format(self.data_path, self.song_name, self.artist_name)
        self.download_bar()
        with requests.get(self.song_dwn_url, stream=True) as r, open(fname, "wb") as f:
            file_size = int(r.headers['Content-Length'])
            total= int(file_size / 1024)
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)
                self.progress_val += 100/total
        print('finished downloading song')
        self.save_metadata()

    def save_metadata(self):
        print('getting metadata')
        audio_path = os.path.join(self.data_path, "{} - {}.m4a".format(self.song_name, self.artist_name))
        audio = MP4(audio_path)
        audio['\xa9nam'] = self.song_name
        audio['\xa9alb'] = self.album
        audio['aART'] = self.artist_name
        if self.featured_artist != '':
            audio['\xa9ART'] = self.artist_name + ", " + self.featured_artist
        else:
            audio['\xa9ART'] = self.artist_name
        audio['\xa9day'] = self.year
        audio['\xa9gen'] = self.genre
        with open(os.path.join(self.data_path, self.song_id+'.jpg'), "rb") as f:
            audio["covr"] = [
                MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)
            ]
        audio.save()
        shutil.move(audio_path, audio_path.replace(self.data_path, self.path))
        print('finished getting metadata')
        #close_btn = MDFlatButton(text="OK", on_release=self.close_dialog)
        close_btn = MDIconButton(icon='checkbox-marked-circle-outline', on_release=self.close_dialog)
        self.dia = MDDialog(title="Download Complete", text="Song Downloaded Successfully!", size_hint=(0.7,1), buttons=[close_btn])
        self.dia.open()
        #toast("Song Downloaded Successfully!")

    def file_manager_open(self):
        self.file_manager.show(self.path)  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        toast("Songs will be downloaded to: "+path)
        self.path = path

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        #print(keyboard)
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        if keyboard == 27:
            if self.root.ids.screen_manager.current == 'SongDetailsScreen':
                self.change_screen('SongListScreen', 'right')
            else:
                self.change_screen('MainScreen', 'right')
        if keyboard == 13:
            if self.root.ids.screen_manager.current == 'MainScreen':
                self.show_data()
            else:
                pass
        return True

    def close_dialog(self, obj):
        self.dia.dismiss()

if __name__ == '__main__':
    MyApp().run()
