from kivy.core import handle_win_lib_import_error
from kivy.uix.behaviors import button
from kivy.uix.image import Image
import kivymd
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDFlatButton, MDRectangleFlatIconButton, MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import ImageLeftWidget, TwoLineIconListItem, MDList, IconLeftWidget, TwoLineAvatarListItem
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.core.window import Window
#from kivymd.uix.spinner import MDSpinner
##############################
Window.size = (360, 640)
##############################

from helpers import *
import jiosaavn
import requests
import tqdm
import os
from mutagen.mp4 import MP4, MP4Cover


class MyApp(MDApp):
    title = "Black Hole"
    lyr = False
    obj = ObjectProperty(None)
    path = './Songs'
    def build(self):
        self.theme_cls.theme_style = "Light"#Dark"
        self.theme_cls.bg_darkest
        return Builder.load_string(main)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )
        if os.path.exists(self.path):
            pass
        else:
            os.mkdir(self.path)
        if os.path.exists('./Black Hole'):
            pass
        else:
            os.mkdir('./Black Hole')

    def spin(self):
        temp = self.root.ids.spinner
        temp.active = True
        self.show_data()

    def show_data(self):
        temp = self.root.ids.spinner
        close_btn = MDFlatButton(text="Close", on_release=self.close_dialog)
        #more_btn = MDFlatButton(text="More")
        #self.dia = MDDialog(title="Error", text=self.search_field.text, size_hint=(0.7,1), buttons=[close_btn])
        if self.root.ids.song_name.text == '':
            self.dia = MDDialog(title="Invalid Name", text="Please enter a song name", size_hint=(0.7,1), buttons=[close_btn])
            self.dia.open()
        
        else:
            self.show_result()
        temp.active = False

    
    def show_result(self):
        list_view = self.root.ids.container
        list_view.clear_widgets()
        lyrics = False
        self.song_data = jiosaavn.search_song(self.root.ids.song_name.text, lyrics)
        #print(song_data)
        for i in range(len(self.song_data)):
            song_name = self.song_data[i]['song']
            artist_name = self.song_data[i]['primary_artists']
            image_url = self.song_data[i]['image']#.replace('500x500', '150x150')
            response = requests.get(image_url)
            song_id = self.song_data[i]['id']
            if os.path.exists('./Black Hole/'+song_id+'.jpg'):
                print('already exists')
            else:
                with open('./Black Hole/'+song_id+'.jpg', 'wb') as f:
                    f.write(response.content)

            img = ImageLeftWidget(source='./Black Hole/'+song_id+'.jpg')
            #print("{}. {} by {}".format(i+1, song_name, artist_name))
            
            lst = TwoLineAvatarListItem(text=song_name, secondary_text=artist_name, on_press=lambda x: self.song_details(0))
            lst.add_widget(img)
            list_view.add_widget(lst)
            #os.remove('./Black Hole/'+song_id+'.jpg')

    def song_details(self, i):
        self.s_manager = self.root.ids.screen_manager
        self.s_manager.transition.direction = 'left'
        self.s_manager.current = 'SongDetailsScreen'
        self.details_screen = self.root.ids.SongDetailsScreen
        self.details_screen.clear_widgets()
        self.song_name = self.song_data[i]['song']
        self.artist_name = self.song_data[i]['primary_artists']
        self.featured_artist = self.song_data[i]['featured_artists']
        self.album = self.song_data[i]['album']
        self.year = self.song_data[i]['year']
        lang = (self.song_data[i]['language'])
        lang = lang[0].upper() + lang[1:]
        self.genre = lang
        self.song_id = self.song_data[i]['id']
        self.song_dwn_url = self.song_data[i]['media_url']
        #image_url = self.song_data[i]['image'].replace('500x500', '150x150')
        #response = requests.get(image_url)
        # with open('./Black Hole/'+song_id+'.jpg', 'wb') as f:
        #     f.write(response.content)
        self.details_screen.add_widget(Image(source='./Black Hole/'+self.song_id+'.jpg', pos_hint={"center_x":0.5, "center_y":0.8}))
        self.details_screen.add_widget(MDLabel(text=self.song_name, halign='center', font_style='H4', pos_hint={"top":0.95}))
        self.details_screen.add_widget(MDLabel(text=self.artist_name, halign='center', theme_text_color='Secondary', font_style='H6', pos_hint={"top":0.9}))
        self.details_screen.add_widget(MDRoundFlatButton(text='Download', pos_hint={'center_x':0.5, "center_y":0.3}, on_press=lambda x: self.download_song()))
        self.details_screen.add_widget(MDRoundFlatButton(text='Back', pos_hint={'center_x':0.5, "center_y":0.2}, on_press=lambda x: self.change_screen()))
        
    def change_screen(self):
        self.root.ids.screen_manager.transition.direction = 'right'
        self.root.ids.screen_manager.current = 'SongListScreen'
    
    def download_song(self):
        with requests.get(self.song_dwn_url, stream=True) as r, open("{}/{}.mp4".format(self.path, self.song_id), "wb") as f:
            file_size = int(r.headers['Content-Length'])
            for chunk in tqdm.tqdm(
            r.iter_content(chunk_size=1024),
            total= int(file_size / 1024),
            unit = 'KB',
            desc = "Downloading {} by {}".format(self.song_name, self.artist_name),
            leave = True
            ):
                f.write(chunk)
        os.rename("{}/{}.mp4".format(self.path, self.song_id), "{}/{}.m4a".format(self.path, self.song_id))
        self.save_metadata()

    def save_metadata(self):
        audio_path = "{}/{}.m4a".format(self.path, self.song_id)
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
        with open('./Black Hole/'+self.song_id+'.jpg', "rb") as f:
            audio["covr"] = [
                MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)
            ]
        audio.save()
        fname = "{}/{} - {}.m4a".format(self.path, self.artist_name, self.song_name)
        os.rename("{}/{}.m4a".format(self.path, self.song_id), "{}".format(fname))
        toast("Song Downloaded Successfully!")

    def file_manager_open(self):
        self.file_manager.show('/')  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        self.exit_manager()
        toast("Songs will be downloaded to: "+path)
        self.path = path

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def close_dialog(self, obj):
        self.dia.dismiss()

    def show_details(self, obj):
        pass
        #print(self.)

if __name__ == '__main__':
    MyApp().run()