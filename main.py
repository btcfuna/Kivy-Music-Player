from logging import root
from kivy import animation
from kivy.core import audio
from kivy.uix.image import Image, AsyncImage, CoreImage
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDFlatButton, MDRectangleFlatIconButton, MDRoundFlatButton, MDFloatingActionButton, MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.list import ImageLeftWidget, TwoLineIconListItem, MDList, IconLeftWidget, TwoLineAvatarListItem, OneLineAvatarListItem
from kivymd.uix.card import MDCard
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.audio import SoundLoader
from kivymd.uix.bottomsheet import MDGridBottomSheet
from kivymd.uix.taptargetview import MDTapTargetView
from kivy.storage.jsonstore import JsonStore
from kivy.loader import Loader
from kivy.lang import Builder
##############################
#Window.size = (390, 650)
import threading
import requests
import base64
import json
import os
import io
import shutil
import time
import webbrowser
from pyDes import *
from mutagen.mp4 import MP4, MP4Cover
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3

if platform == 'android':
    import android
    from android.permissions import request_permissions, Permission, check_permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])


search_base_url = "https://www.jiosaavn.com/api.php?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query="
song_details_base_url = "https://www.jiosaavn.com/api.php?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids="


class MyApp(MDApp):
    title = "Black Hole"
    status = True
    last_screen = 'MainScreen'
    def build(self):
        if self.user_data.exists('theme'):
            self.theme_cls.theme_style = self.user_data.get('theme')['mode']
        else:
            self.user_data.put('theme', mode='Light')
        if self.user_data.exists('accent'):
            self.theme_cls.primary_palette = self.user_data.get('accent')['color']
        if self.theme_cls.theme_style == "Dark":
            self.root.ids.dark_mode_switch.active = True
        #self.theme_cls.primary_hue = "A400"
        self.theme_cls.accent_palette = self.theme_cls.primary_palette
        #self.theme_cls.bg_darkest
        Loader.loading_image = 'cover.jpg'
        #return Builder.load_string(main)

    def tap_target_start(self):
        if self.tap_target_view.state == "close":
            self.tap_target_view.start()
        else:
            self.tap_target_view.stop()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_data_path = os.path.join(self.user_data_dir, 'data.json')
        self.user_data = JsonStore(self.user_data_path)
        Window.bind(on_keyboard=self.events)
        if self.user_data.exists('download_path'):
            self.path = self.user_data.get('download_path')['path']
        else:
            self.path = os.path.join(os.getenv('EXTERNAL_STORAGE'), 'Songs')
        self.data_path = os.path.join(self.user_data_dir, 'cache')
        #self.user_data.put('accent', color='Blue')
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        self.file_manager.ext = [".m4a", ".mp3"]
        if os.path.exists(self.path):
            pass
        else:
            os.mkdir(self.path)
        if os.path.exists(self.data_path):
            pass
        else:
            os.mkdir(self.data_path)
        if not os.path.exists(self.user_data_path):
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
        lst = OneLineAvatarListItem(text=item, on_press=lambda x: self.play_song(os.path.join(self.path, item)))
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
        self.change_screen('SongListScreen', 'left')
        self.dia.open()
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
        self.sound = SoundLoader.load(self.song_dwn_url)
        self.root.ids.SongDetailsScreen.add_widget(MDLabel(text=self.convert_sec(self.sound.length), halign='right', theme_text_color='Secondary', padding_x='20dp', pos_hint={"top":0.725}))
        self.play_stamp = (MDLabel(text=self.convert_sec(self.sound.get_pos()), halign='left', theme_text_color='Secondary', padding_x='20dp', pos_hint={"top":0.725}))
        self.root.ids.SongDetailsScreen.add_widget(self.play_stamp)
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
        self.fetch_thread = threading.Thread(target=self.fetch_details)
        self.fetch_thread.start()
        self.details_screen.add_widget(MDIconButton(icon='chevron-left', pos_hint={"center_x":0.05, "center_y":0.95}, on_press=lambda x: self.change_screen('SongListScreen', 'right')))
        song_image = AsyncImage(source=self.image_url, pos_hint={"center_x":0.5, "center_y":0.5}, allow_stretch=True)
        card = MDCard(orientation='vertical', pos_hint={"center_x":0.5, "center_y":0.65}, size_hint=(None, None), size=(Window.size[0]*0.9, Window.size[0]*0.9))
        card.add_widget(song_image)
        self.details_screen.add_widget(card)
        self.details_screen.add_widget(MDLabel(text=self.song_name, halign='center', theme_text_color='Primary', font_style='H4', bold=True, pos_hint={"top":0.85}))
        self.details_screen.add_widget(MDLabel(text=self.artist_name, halign='center', theme_text_color='Secondary', font_style='H6', pos_hint={"top":0.8}))
        #self.details_screen.add_widget(MDLabel(text=self.album, halign='center', theme_text_color='Hint', font_style='H6', pos_hint={"top":0.9}))
        self.heart_icon = MDIconButton(icon='heart-outline', user_font_size="30sp", theme_text_color= 'Secondary', pos_hint={"center_x":0.1, "center_y":0.15}, on_press=lambda x: self.add_fav())
        self.details_screen.add_widget(self.heart_icon)
        self.play_progress = MDProgressBar(pos_hint = {'center_x':0.5, 'center_y':0.25}, size_hint_x = 0.9, value = 0, color = self.theme_cls.primary_color)
        self.details_screen.add_widget(self.play_progress)
        self.tap_target_view = MDTapTargetView(
            widget=self.heart_icon,
            title_text="Add to Favorites",
            description_text="Feature currently under development",
            widget_position="left_bottom",
        )
        self.details_screen.add_widget(MDIconButton(icon="chevron-double-left", pos_hint={"center_x": .3, "center_y": .15}, user_font_size="55sp", on_release=lambda x: self.rewind()))
        self.details_screen.add_widget(MDIconButton(icon="chevron-double-right", pos_hint={"center_x": .7, "center_y": .15}, user_font_size="55sp", on_release=lambda x: self.forward()))
        self.play_btn = MDFloatingActionButton(icon='play', pos_hint={'center_x':0.5, "center_y":0.15}, user_font_size="50sp", md_bg_color=(1,1,1,1), elevation_normal=10, on_press=lambda x: self.play_song_online())#self.tap_target_start())
        self.details_screen.add_widget(self.play_btn)
        self.details_screen.add_widget(MDIconButton(icon='arrow-collapse-down', user_font_size="30sp", theme_text_color= 'Secondary', pos_hint={'center_x':0.9, "center_y":0.15}, on_press=lambda x: self.download_bar()))
        
    def add_fav(self):
        if self.heart_icon.icon == 'heart-outline':
            self.heart_icon.icon = 'heart'
            self.heart_icon.theme_text_color = "Custom"
            self.heart_icon.text_color = (1,0,0,1)
            self.tap_target_view.start()
            #toast("Feature under development")

        elif self.heart_icon.icon == 'heart':
            #self.heart_icon.icon = 'heart-broken'
            self.heart_icon.icon = 'heart-outline'
            self.heart_icon.theme_text_color = 'Secondary'
            #self.heart_icon.text_color = self.theme_cls.text_color
            toast("Removed from Favorites")

    def change_screen(self, screen, direction):
        self.last_screen = self.root.ids.screen_manager.current
        self.root.ids.screen_manager.transition.direction = direction
        self.root.ids.screen_manager.current = screen
        if self.last_screen == 'SongDetailsScreen' or self.last_screen == 'PlayScreen':
            if self.sound.status == 'play':
                self.sound.stop()
    
    def cancel(self):
        self.download_progress.color = 1, 0, 0, 1
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
        self.download_progress = MDProgressBar(pos_hint = {'center_x':0.5, 'center_y':0.5}, size_hint_x = 0.8, value = 0, color = self.theme_cls.primary_color)
        self.dia = MDDialog(title='Downloading', buttons=[MDFlatButton(text="CANCEL", text_color=self.theme_cls.primary_color, on_press=lambda x: self.cancel())])
        #self.dia.add_widget(IconLeftWidget(icon='download', pos_hint={'center_x': .1, 'center_y': .1}))
        self.dia.add_widget(self.download_progress)
        self.dia.open()
        t2 = threading.Thread(target=self.download_song)
        t2.start()

    def play_song_online(self):
        self.fetch_thread.join()
        if self.sound:
            #print("Sound found at %s" % self.sound.source)
            #print("Sound is %.3f seconds" % self.sound.length)
            if self.sound.state == 'stop':
                self.play_btn.icon = 'pause'
                self.sound.play()
                lnth = self.sound.length
                t2 = threading.Thread(target=self.online_play_bar, args=(lnth,))
                t2.start()
            elif self.sound.state == 'play':
                self.play_btn.icon = 'play'
                self.sound.stop()
        else:
            time.sleep(0.5)
            self.play_song_online
    
    def online_play_bar(self, length):
        while True:
            self.play_progress.value = 100*(self.sound.get_pos())/length
            #print(self.progress.value)
            time.sleep(1)
            self.play_stamp.text = self.convert_sec(self.sound.get_pos())
            if self.sound.state == 'stop':
                print('breaked loop')
                break

    def play_song(self, link):
        self.change_screen("PlayScreen", "left")
        self.sound = SoundLoader.load(link)
        if link.endswith('.m4a'):
            self.audio = MP4(link)
            self.play_song_name = self.audio.get('\xa9nam', ['Unknown'])[0]
            #print(audio['\xa9alb'])
            self.play_art_name = self.audio.get('\xa9ART',['Unknown'])[0]
            #print(audio['\xa9day'])
            #print(audio['\xa9gen'])
            try:
                self.img_data = self.audio["covr"][0]
            except:
                with open('cover.jpg', 'rb') as f:
                    self.img_data = f.read()
        elif link.endswith('.mp3'):
            self.audio = MP3(link, ID3=EasyID3)
            self.audio_tags = ID3(link)
            self.play_song_name = self.audio.get('title', ['Unknown'])[0]
            self.play_art_name = self.audio.get('artist',['Unknown'])[0]
            try:
                self.img_data = self.audio_tags.get("APIC:").data
            except:
                with open('cover.jpg', 'rb') as f:
                    self.img_data = f.read()
        else:
            with open('cover.jpg', 'rb') as f:
                self.img_data = f.read()
                self.play_song_name = 'Unknown'
                self.play_art_name = 'Unknown'
        
        play_image_data = io.BytesIO(self.img_data)
        img=CoreImage(play_image_data, ext="jpg").texture
        song_image= Image(allow_stretch=True)
        song_image.texture= img
        self.root.ids.PlayScreen.clear_widgets()
        self.root.ids.PlayScreen.add_widget(MDIconButton(icon='chevron-left', pos_hint={"center_x":0.05, "center_y":0.95}, on_press=lambda x: self.change_screen('DownloadsScreen', 'right')))
        card = MDCard(orientation='vertical', pos_hint={"center_x":0.5, "center_y":0.65}, size_hint=(None, None), size=(Window.size[0]*0.9, Window.size[0]*0.9))
        card.add_widget(song_image)
        self.root.ids.PlayScreen.add_widget(card)
        self.root.ids.PlayScreen.add_widget(MDLabel(text=self.play_song_name, halign='center', theme_text_color='Primary', font_style='H4', bold=True, pos_hint={"top":0.85}))
        self.root.ids.PlayScreen.add_widget(MDLabel(text=self.play_art_name, halign='center', theme_text_color='Secondary', font_style='H6', pos_hint={"top":0.8}))
        self.play_progress = MDProgressBar(pos_hint = {'center_x':0.5, 'center_y':0.25}, size_hint_x = 0.9, value = 0, color = self.theme_cls.primary_color)
        self.root.ids.PlayScreen.add_widget(self.play_progress)
        self.root.ids.PlayScreen.add_widget(MDIconButton(icon="chevron-double-left", pos_hint={"center_x": .3, "center_y": .15}, user_font_size="55sp", on_release=lambda x: self.rewind()))
        self.root.ids.PlayScreen.add_widget(MDIconButton(icon="chevron-double-right", pos_hint={"center_x": .7, "center_y": .15}, user_font_size="55sp", on_release=lambda x: self.forward()))
        self.root.ids.PlayScreen.add_widget(MDIconButton(icon="volume-plus", pos_hint={"center_x": .85, "center_y": .15}, user_font_size="40sp", on_release=lambda x: self.increase()))
        self.root.ids.PlayScreen.add_widget(MDIconButton(icon="volume-minus", pos_hint={"center_x": .15, "center_y": .15}, user_font_size="40sp", on_release=lambda x: self.decrease()))
        self.play_btn = MDFloatingActionButton(icon='play', pos_hint={'center_x':0.5, "center_y":0.15}, user_font_size="50sp", md_bg_color=(1,1,1,1), elevation_normal=10, on_press=lambda x: self.play_song_offline())
        self.root.ids.PlayScreen.add_widget(self.play_btn)
        self.root.ids.PlayScreen.add_widget(MDLabel(text=self.convert_sec(self.sound.length), halign='right', theme_text_color='Secondary', padding_x='20dp', pos_hint={"top":0.725}))
        self.play_stamp = (MDLabel(text=self.convert_sec(self.sound.get_pos()), halign='left', theme_text_color='Secondary', padding_x='20dp', pos_hint={"top":0.725}))
        self.root.ids.PlayScreen.add_widget(self.play_stamp)

            
    def play_song_offline(self):
        if self.sound:
            #print("Sound found at %s" % self.sound.source)
            #print("Sound is %.3f seconds" % self.sound.length)
            if self.sound.state == 'stop':
                self.play_btn.icon = 'pause'
                self.sound.play()
                lnth = self.sound.length
                t2 = threading.Thread(target=self.online_play_bar, args=(lnth,))
                t2.start()
            elif self.sound.state == 'play':
                self.play_btn.icon = 'play'
                self.sound.stop()
        else:
            time.sleep(0.5)
            self.play_song_offline

    def convert_sec(self, lnth):
        try:
            if int(lnth-(60*(lnth//60))) < 10:
                return("{}:0{}".format(int(lnth//60), int(lnth-(60*(lnth//60)))))
            else:
                return("{}:{}".format(int(lnth//60), int(lnth-(60*(lnth//60)))))
        except:
            print('Error: Length is {}'.format(lnth))

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
        self.sound.volume += 0.2
    def decrease(self):
        self.sound.volume -= 0.2
    #def stop_song(self):
    #    self.sound.stop()
    #    if self.last_screen == 'DownloadsScreen':
    #        self.change_screen('DownloadsScreen', 'right')
    #    else:
    #        self.change_screen(self.last_screen, 'right')
    #    self.root.ids.PlayScreen.remove_widget(self.title_play_label)

    def save_settings(self):
        toast("Settings saved")
    
    def callback_for_about(self, *args):
        toast('Opening ' + args[0])
        webbrowser.open_new(args[0])
            
    def contact_us(self):
        bottom_sheet_menu = MDGridBottomSheet(radius=15,radius_from='top')
        data = [
            {"name":"Telegram", "icon":"telegram", "link":"https://t.me/sangwan5688"},
            {"name":"Instagram", "icon":"instagram", "link":"https://www.instagram.com/sangwan5688/"},
            {"name":"Twitter", "icon":"twitter-box", "link":"https://twitter.com/sangwan5688"},
            {"name":"Mail", "icon":"gmail", "link":"https://mail.google.com/mail/?view=cm&fs=1&to=blackholeyoucantescape@gmail.com&su=Regarding+Mobile+App"},
            {"name":"Facebook", "icon":"facebook-box", "link":"https://www.facebook.com/ankit.sangwan.5688"},
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
                        self.download_progress.value += 100/total
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

    def set_nav_color(self, item):
        for child in self.root.ids.nav_list.children:
            print(child.text)
            #if child.text_color == self.theme_cls.primary_color:
            #    child.text_color = self.theme_cls.text_color
            #    break
            if child.text == item:
                child.text_color = self.theme_cls.primary_color
                break
                
        

    def file_manager_open(self):
        self.file_manager.show(self.path)  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        if os.path.isdir(path):
            self.path = path
            toast("Songs will be downloaded to: "+path)
            self.user_data.put('download_path', path=self.path)
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
                self.change_screen('DownloadsScreen', 'right')
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
