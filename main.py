from logging import root
from kivy import animation
from kivy.uix.image import Image, AsyncImage
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDFlatButton, MDRectangleFlatIconButton, MDRoundFlatButton, MDFloatingActionButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import ImageLeftWidget, TwoLineIconListItem, MDList, IconLeftWidget, TwoLineAvatarListItem, OneLineAvatarListItem
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.audio import SoundLoader
from kivymd.uix.bottomsheet import MDGridBottomSheet
from kivymd.uix.taptargetview import MDTapTargetView
from kivy.storage.jsonstore import JsonStore
##############################
import threading
import requests
import base64
import json
import os
import shutil
import time
import webbrowser
from pyDes import *
from mutagen.mp4 import MP4, MP4Cover


if platform == 'android':
    import android
    from android.permissions import request_permissions, Permission, check_permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path
    ext_path = primary_external_storage_path()


search_base_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
song_details_base_url = "https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids="

class MyApp(MDApp):
    title = "Black Hole"
    status = True
    last_screen = 'MainScreen'
    def build(self):
        #self.theme_cls = ThemeManager()
        
        #store.delete('tito')
        if self.user_data.exists('theme'):
            self.theme_cls.theme_style = self.user_data.get('theme')['mode']
        else:
            self.user_data.put('theme', mode='Light')
        if self.user_data.exists('accent'):
            self.theme_cls.primary_palette = self.user_data.get('accent')['color']
        if self.theme_cls.theme_style == "Dark":
            self.root.ids.dark_mode_switch.active = True
        #self.theme_cls.primary_hue = "A400"
        self.theme_cls.accent_palette = self.theme_cls.primary_palette#'Blue'
        #self.theme_cls.bg_darkest
        #Loader.loading_image = 'blank.jpg'#'giphy.gif'
        #return Builder.load_string(main)

    def tap_target_start(self):
        if self.tap_target_view.state == "close":
            self.tap_target_view.start()
        else:
            self.tap_target_view.stop()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.path = os.path.join(os.getenv(ext_path, 'Songs'))#'songs'#os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Songs')
        self.data_path = os.path.join(self.user_data_dir, 'cache')
        self.user_data = JsonStore(os.path.join(self.user_data_dir, 'data.json'))
        #self.user_data.put('accent', color='Blue')
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
        if not os.path.exists(os.path.join(self.user_data_dir, 'data.json')):
            self.user_data.put('theme', mode='Light')
            self.user_data.put('accent', color='Blue')

    def change_theme(self):
        if self.root.ids.dark_mode_switch.active == True:
            self.theme_cls.theme_style = "Dark"
            self.user_data.put('theme', mode='Dark')
        else:
            self.theme_cls.theme_style = "Light"
            self.user_data.put('theme', mode='Light')

    def download_list(self):
        self.down_list = self.root.ids.downloadlist
        self.down_list.clear_widgets()
        td = threading.Thread(target=self.add_songs_downlist)
        td.start()
    
    def add_songs_downlist(self):
        for items in os.listdir(self.path):
            self.add_down_song(items)
    
    def add_down_song(self, item):
        lst = OneLineAvatarListItem(text=item.strip('.m4a'), on_press=lambda x: self.play_song(item.split('-')[0], '-'.join(item.split('-')[1:]).strip('.m4a'),os.path.join(self.path, item)))
        lst.add_widget(IconLeftWidget(icon='music'))
        self.down_list.add_widget(lst)

    def show_data(self, *args):
        close_btn = MDFlatButton(text="Close", on_release=self.close_dialog)
        if self.root.ids.song_name.text == '':
            self.dia = MDDialog(title="Invalid Name", text="Please enter a song name", size_hint=(0.7,1), buttons=[close_btn])
            self.dia.open()
        
        else:
            self.dia = MDDialog(text="Searching for songs ...", size_hint=(0.7,1))
            t1 = threading.Thread(target=self.show_list)
            t1.start()

    def show_list(self):
        self.dia.open()
        self.change_screen('SongListScreen', 'left')
        self.list_view = self.root.ids.container
        self.list_view.clear_widgets()
        self.search_data = json.loads(requests.get(search_base_url+self.root.ids.song_name.text).text.replace("&quot;","'").replace("&amp;", "&").replace("&#039;", "'"))['songs']['data']
        for i in range(len(self.search_data)):
            self.down_img(i)
        self.dia.dismiss()

    def down_img(self, i):
        lst = TwoLineAvatarListItem(text=self.search_data[i]['title'], secondary_text=self.search_data[i]['more_info']['primary_artists'], on_press=lambda x: self.song_details(i))
        lst.add_widget(IconLeftWidget(icon='music'))
        self.list_view.add_widget(lst)

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
        print('finished fetching details')

    def decrypt_url(url):
        des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0",pad=None, padmode=PAD_PKCS5)
        enc_url = base64.b64decode(url.strip())
        dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode('utf-8')
        dec_url = dec_url.replace("_96.mp4", "_320.mp4")
        return dec_url

    def song_details(self, i):
        self.s_manager = self.root.ids.screen_manager
        self.s_manager.transition.direction = 'left'
        self.s_manager.current = 'SongDetailsScreen'
        self.details_screen = self.root.ids.SongDetailsScreen
        self.details_screen.clear_widgets()
        self.song_name = self.search_data[i]['title']
        self.song_id = self.search_data[i]['id']
        self.artist_name = self.search_data[i]['more_info']['primary_artists']
        self.album = self.search_data[i]['album']
        self.image_url = self.search_data[i]['image'].replace('50x50', '500x500')
        self.image_path = os.path.join(self.data_path,self.song_id+'.jpg')
        t1 = threading.Thread(target=self.fetch_details)
        t1.start()

        self.details_screen.add_widget(AsyncImage(source=self.image_url, pos_hint={"center_x":0.5, "center_y":0.8}))
        self.details_screen.add_widget(MDLabel(text=self.song_name, halign='center', theme_text_color='Primary', font_style='H4', pos_hint={"top":1}))
        self.details_screen.add_widget(MDLabel(text=self.artist_name, halign='center', theme_text_color='Secondary', font_style='H6', pos_hint={"top":0.95}))
        self.details_screen.add_widget(MDLabel(text=self.album, halign='center', theme_text_color='Hint', font_style='H6', pos_hint={"top":0.9}))
        self.play_btn = MDFloatingActionButton(icon='play', pos_hint={'center_x':0.9, "center_y":0.6}, md_bg_color=(1,1,1,1), on_press=lambda x: self.play_song(self.song_name, self.artist_name, self.song_dwn_url))#self.tap_target_start())
        self.details_screen.add_widget(self.play_btn)
        self.tap_target_view = MDTapTargetView(
            widget=self.play_btn,
            title_text="Listen to songs online",
            description_text="This feature is currently under development",
            widget_position="right_top",
        )
        self.details_screen.add_widget(MDRoundFlatButton(text='Download', pos_hint={'center_x':0.5, "center_y":0.2}, on_press=lambda x: self.download_bar()))
        
        
    def change_screen(self, screen, direction):
        self.last_screen = self.root.ids.screen_manager.current
        self.root.ids.screen_manager.transition.direction = direction
        self.root.ids.screen_manager.current = screen
    
    def cancel(self):
        self.progress.color = 1, 0, 0, 1
        self.status = False
        t3=threading.Thread(target=self.cancel2)
        t3.start()
    
    def cancel2(self):
        time.sleep(0.5)
        try:
            os.remove("{}/{} - {}.m4a".format(self.data_path, self.song_name, self.artist_name))
            print('removed')
        except:
            print('failed to remove')
            pass
        self.dia.dismiss()
        self.status=True

    def download_bar(self):
        self.progress = MDProgressBar(pos_hint = {'center_x':0.5, 'center_y':0.5}, size_hint_x = 0.5, value = 0, color = self.theme_cls.primary_color)
        self.dia = MDDialog(title='Downloading', buttons=[MDFlatButton(text="CANCEL", text_color=self.theme_cls.primary_color, on_press=lambda x: self.cancel())])
        #self.dia.add_widget(IconLeftWidget(icon='download', pos_hint={'center_x': .1, 'center_y': .1}))
        self.dia.add_widget(self.progress)
        #self.dia.add_widget(IconLeftWidget(icon='download', pos_hint={'center_x':0.2, 'center_y':0.5}))
        self.dia.open()
        t2 = threading.Thread(target=self.download_song)
        t2.start()


    def play_song(self, song, artist, link):
        self.change_screen("PlayScreen", "left")
        self.sound = SoundLoader.load(link)
        #close_btn = MDFlatButton(text="Close", on_release=lambda x: self.stop_song())
        #self.dia = MDDialog(title="Playing", text = "Feature under development!", size_hint=(0.7,1), buttons=[close_btn])
        self.title_play_label = (MDLabel(text=song+' - '+artist, halign='center', theme_text_color='Primary', font_style='H4', pos_hint={"top":1.1}))
        self.root.ids.PlayScreen.add_widget(self.title_play_label)
        self.progress = MDProgressBar(pos_hint = {'center_x':0.5, 'center_y':0.55}, size_hint_x = 0.5, value = 0, color = self.theme_cls.primary_color)
        self.root.ids.PlayScreen.add_widget(self.progress)
        #self.dia.add_widget(self.progress)
        
        #self.dia.add_widget(MDIconButton(icon="pause", pos_hint={"x": .5, "center_y": .5}, theme_text_color="Custom", text_color=self.theme_cls.primary_color, on_release=lambda x: self.pause()))
        #self.dia.add_widget(MDIconButton(icon="play", pos_hint={"x": .5, "center_y": .5}, theme_text_color="Custom", text_color=self.theme_cls.primary_color, on_release=lambda x: self.play()))
        #self.dia.add_widget(MDIconButton(icon="rewind-5", pos_hint={"x": .4, "y": .5}, on_release=lambda x: self.rewind()))
        #self.dia.add_widget(MDIconButton(icon="fast-forward-5", pos_hint={"x": .6, "center_y": .5}, on_release=lambda x: self.forward()))
        #self.dia.add_widget(MDIconButton(icon="volume-plus", pos_hint={"x": .7, "center_y": .5}, on_release=lambda x: self.increase()))
        #self.dia.add_widget(MDIconButton(icon="volume-minus", pos_hint={"x": .3, "center_y": .5}, on_release=lambda x: self.decrease()))
        #self.dia.open()
        #print(self.song_dwn_url)

        if self.sound:
            #print("Sound found at %s" % self.sound.source)
            print("Sound is %.3f seconds" % self.sound.length)
            self.sound.play()
        lnth = self.sound.length
        t2 = threading.Thread(target=self.play_bar, args=(lnth,))
        t2.start()
    def convert_sec(self, lnth):
        if int(lnth-(60*(lnth//60))) < 10:
            return("{}:0{}".format(int(lnth//60), int(lnth-(60*(lnth//60)))))
        else:
            return("{}:{}".format(int(lnth//60), int(lnth-(60*(lnth//60)))))

    def play(self):
        if self.sound:
            self.sound.play()
    def pause(self):
    	if self.sound:
        	self.sound.stop()
    def forward(self):
        if self.sound:
            self.sound.seek(self.sound.get_pos() + 10)
    def rewind(self):
        if self.sound.get_pos() >= 5:
            self.sound.seek(self.sound.get_pos() - 10)
    def increase(self):
        self.sound.volume += 0.1
    def decrease(self):
        self.sound.volume -= 0.1
    def stop_song(self):
        self.sound.stop()
        if self.last_screen == 'DownloadsScreen':
            self.change_screen('DownloadsScreen', 'right')
        else:
            self.change_screen(self.last_screen, 'right')
        self.root.ids.PlayScreen.remove_widget(self.title_play_label)

    def play_bar(self, length):
        count = 0
        while True:
            temp = MDLabel(text="{}/{}".format(self.convert_sec(self.sound.get_pos()), self.convert_sec(length)), halign="right", theme_text_color='Primary', pos_hint={"top":1.05})
            self.root.ids.PlayScreen.add_widget(temp)
            self.progress.value = 100*(self.sound.get_pos())/length
            #print(self.progress.value)
            time.sleep(1)
            self.root.ids.PlayScreen.remove_widget(temp)
            if self.progress.value == 0:
                if count >0:
                    print('breaked loop')
                    break
                else:
                    count+=1
        #self.dia.dismiss()

    def save_settings(self):
        toast("Settings saved")
    
    def callback_for_about(self, *args):
        toast('Opening ' + args[0])
        webbrowser.open_new(args[0])
            
    def contact_us(self):
        bottom_sheet_menu = MDGridBottomSheet(radius=15,radius_from='top', animation=True)
        data = [
            {"name":"Telegram", "icon":"telegram", "link":"https://t.me/sangwan5688"},
#            {"name":"Instagram", "icon":"instagram", "link":"www.instagram.com"},
#            {"name":"Twitter", "icon":"twitter-box", "link":"www.twitter.com"},
            {"name":"Mail", "icon":"gmail", "link":"https://mail.google.com/mail/?view=cm&fs=1&to=blackholeyoucantescape@gmail.com&su=Regarding+Mobile+App"},
            {"name":"Facebook", "icon":"facebook-box", "link":"www.facebook.com"},
        ]
        for item in data:
            bottom_sheet_menu.add_item(
                item["name"],
                lambda x, y=item["link"]: self.callback_for_about(y),
                icon_src=item["icon"],
            )
        bottom_sheet_menu.open()

    def download_song(self):
        #if self.status:
        #    self.fetch_details()
        if self.status:
            print('started downloading song')
            fname = "{}/{} - {}.m4a".format(self.data_path, self.song_name, self.artist_name)
            #self.download_bar()
            with requests.get(self.song_dwn_url, stream=True) as r, open(fname, "wb") as f:
                file_size = int(r.headers['Content-Length'])
                total= int(file_size / 1024)
                self.dia.add_widget(MDLabel(text='{:.2f} MB'.format(file_size/(1024*1024)), halign='right'))
                for chunk in r.iter_content(chunk_size=1024):
                    if self.status:
                        f.write(chunk)
                        self.progress.value += 100/total
                    else:
                        #print('Download cancelled')
                        break
            print('finished downloading song')
        if self.status:
            self.save_metadata()

    def save_metadata(self):
        with open(self.image_path, 'wb') as f:
            f.write(requests.get(self.image_url).content)
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
        self.dia.dismiss()
        os.remove(os.path.join(self.data_path, self.song_id+'.jpg'))
        close_btn = MDIconButton(icon='checkbox-marked-circle-outline', theme_text_color="Custom", text_color=self.theme_cls.primary_color, on_release=self.close_dialog)
        self.dia = MDDialog(title="Download Complete", text="Song Downloaded Successfully!", size_hint=(0.7,1), buttons=[close_btn])
        self.dia.open()
        #toast("Song Downloaded Successfully!")

    def file_manager_open(self):
        self.file_manager.show(self.path)  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        if os.path.isdir(path):
            self.path = path
            toast("Songs will be downloaded to: "+path)
        else:
            toast("No directory selected")

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
            elif self.root.ids.screen_manager.current == 'PlayScreen':
                self.stop_song()
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
