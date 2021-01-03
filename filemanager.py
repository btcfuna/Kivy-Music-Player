__all__ = ("MDFileManager",)

import locale
import os

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.modalview import ModalView

from kivymd import images_path
from kivymd.theming import ThemableBehavior
from kivymd.uix.behaviors import CircularRippleBehavior
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import BaseListItem, ContainerSupport
from kivymd.utils.fitimage import FitImage

ACTIVITY_MANAGER = """
#:import os os


<BodyManager@BoxLayout>
    icon: "folder"
    path: ""
    background_normal: ""
    background_down: ""
    dir_or_file_name: ""
    _selected: False
    events_callback: lambda x: None
    orientation: "vertical"

    ModifiedOneLineIconListItem:
        text: root.dir_or_file_name
        bg_color: self.theme_cls.bg_darkest if root._selected else self.theme_cls.bg_normal
        on_release: root.events_callback(root.path, root)

        IconLeftWidget:
            icon: root.icon
            theme_text_color: "Custom"
            text_color: self.theme_cls.primary_color

    MDSeparator:


<LabelContent@MDLabel>
    size_hint_y: None
    height: self.texture_size[1]
    shorten: True
    shorten_from: "center"
    halign: "center"
    text_size: self.width, None


<BodyManagerWithPreview>
    name: ""
    path: ""
    realpath: ""
    type: "folder"
    events_callback: lambda x: None
    _selected: False
    orientation: "vertical"
    size_hint_y: None
    hright: root.height
    padding: dp(20)

    IconButton:
        mipmap: True
        source: root.path
        bg_color: app.theme_cls.bg_darkest if root._selected else app.theme_cls.bg_normal
        on_release:
            root.events_callback(\
            os.path.join(root.path if root.type != "folder" else root.realpath, \
            root.name), root)

    LabelContent:
        text: root.name


<FloatButton>
    anchor_x: "right"
    anchor_y: "bottom"
    size_hint_y: None
    height: dp(56)
    padding: dp(10)

    MDFloatingActionButton:
        size_hint: None, None
        size:dp(56), dp(56)
        icon: root.icon
        opposite_colors: True
        elevation: 8
        on_release: root.callback()
        md_bg_color: root.md_bg_color


<MDFileManager>
    md_bg_color: root.theme_cls.bg_normal

    BoxLayout:
        orientation: "vertical"
        spacing: dp(5)

        MDToolbar:
            id: toolbar
            title: root.current_path
            right_action_items: [["close-box", lambda x: root.exit_manager(1)]]
            left_action_items: [["chevron-left", lambda x: root.back()]]
            elevation: 10

        RecycleView:
            id: rv
            key_viewclass: "viewclass"
            key_size: "height"
            bar_width: dp(4)
            bar_color: root.theme_cls.primary_color
            #on_scroll_stop: root._update_list_images()

            RecycleGridLayout:
                padding: dp(10)
                cols: 3 if root.preview else 1
                default_size: None, dp(48)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height


<ModifiedOneLineIconListItem>

    BoxLayout:
        id: _left_container
        size_hint: None, None
        x: root.x + dp(16)
        y: root.y + root.height / 2 - self.height / 2
        size: dp(48), dp(48)
"""


class BodyManagerWithPreview(MDBoxLayout):
    """Base class for folder icons and thumbnails images in ``preview`` mode."""


class IconButton(CircularRippleBehavior, ButtonBehavior, FitImage):
    """Folder icons/thumbnails images in ``preview`` mode."""


class FloatButton(AnchorLayout):
    callback = ObjectProperty()
    md_bg_color = ListProperty([1, 1, 1, 1])
    icon = StringProperty()


class ModifiedOneLineIconListItem(ContainerSupport, BaseListItem):
    _txt_left_pad = NumericProperty("72dp")
    _txt_top_pad = NumericProperty("16dp")
    _txt_bot_pad = NumericProperty("15dp")
    _num_lines = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(48)


class MDFileManager(ThemableBehavior, MDFloatLayout):
    icon = StringProperty("check")
    icon_folder = StringProperty(f"{images_path}folder.png")
    exit_manager = ObjectProperty(lambda x: None)
    select_path = ObjectProperty(lambda x: None)
    ext = ListProperty()
    search = OptionProperty("all", options=["all", "dirs", "files"])
    current_path = StringProperty(os.getcwd())
    use_access = BooleanProperty(True)
    preview = BooleanProperty(False)
    show_hidden_files = BooleanProperty(False)
    sort_by = OptionProperty(
        "name", options=["nothing", "name", "date", "size", "type"]
    )
    sort_by_desc = BooleanProperty(False)
    selector = OptionProperty("any", options=["any", "file", "folder", "multi"])
    selection = ListProperty([])

    _window_manager = None
    _window_manager_open = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        toolbar_label = self.ids.toolbar.children[1].children[0]
        toolbar_label.font_style = "Subtitle1"

        if (
            self.selector == "any"
            or self.selector == "multi"
            or self.selector == "folder"
        ):
            self.add_widget(
                FloatButton(
                    callback=self.select_directory_on_press_button,
                    md_bg_color=self.theme_cls.primary_color,
                    icon=self.icon,
                )
            )

        if self.preview:
            self.ext = [".png", ".jpg", ".jpeg"]

    def __sort_files(self, files):
        def sort_by_name(files):
            files.sort(key=locale.strxfrm)
            files.sort(key=str.casefold)

            return files

        if self.sort_by == "name":
            sorted_files = sort_by_name(files)

        elif self.sort_by == "date":
            _files = sort_by_name(files)
            _sorted_files = [os.path.join(self.current_path, f) for f in _files]
            _sorted_files.sort(key=os.path.getmtime, reverse=True)

            sorted_files = [os.path.basename(f) for f in _sorted_files]

        elif self.sort_by == "size":
            _files = sort_by_name(files)
            _sorted_files = [os.path.join(self.current_path, f) for f in _files]
            _sorted_files.sort(key=os.path.getsize, reverse=True)

            sorted_files = [os.path.basename(f) for f in _sorted_files]

        elif self.sort_by == "type":
            _files = sort_by_name(files)

            sorted_files = sorted(
                _files,
                key=lambda f: (os.path.splitext(f)[1], os.path.splitext(f)[0]),
            )

        else:
            sorted_files = files

        if self.sort_by_desc:
            sorted_files.reverse()

        return sorted_files

    def show(self, path):
        self.current_path = path
        self.selection = []
        dirs, files = self.get_content()
        manager_list = []

        if dirs == [] and files == []:  # selected directory
            pass
        elif not dirs and not files:  # directory is unavailable
            return

        if self.preview:
            for name_dir in self.__sort_files(dirs):
                manager_list.append(
                    {
                        "viewclass": "BodyManagerWithPreview",
                        "path": self.icon_folder,
                        "realpath": os.path.join(path),
                        "type": "folder",
                        "name": name_dir,
                        "events_callback": self.select_dir_or_file,
                        "height": dp(150),
                        "_selected": False,
                    }
                )
            for name_file in self.__sort_files(files):
                if (
                    os.path.splitext(os.path.join(path, name_file))[1]
                    in self.ext
                ):
                    manager_list.append(
                        {
                            "viewclass": "BodyManagerWithPreview",
                            "path": os.path.join(path, name_file),
                            "name": name_file,
                            "type": "files",
                            "events_callback": self.select_dir_or_file,
                            "height": dp(150),
                            "_selected": False,
                        }
                    )
        else:
            for name in self.__sort_files(dirs):
                _path = os.path.join(path, name)
                access_string = self.get_access_string(_path)
                if "r" not in access_string:
                    icon = "folder-lock"
                else:
                    icon = "folder"

                manager_list.append(
                    {
                        "viewclass": "BodyManager",
                        "path": _path,
                        "icon": icon,
                        "dir_or_file_name": name,
                        "events_callback": self.select_dir_or_file,
                        "_selected": False,
                    }
                )
            for name in self.__sort_files(files):
                if self.ext and os.path.splitext(name)[1] not in self.ext:
                    continue

                manager_list.append(
                    {
                        "viewclass": "BodyManager",
                        "path": name,
                        "icon": "file-outline",
                        "dir_or_file_name": os.path.split(name)[1],
                        "events_callback": self.select_dir_or_file,
                        "_selected": False,
                    }
                )
        self.ids.rv.data = manager_list

        if not self._window_manager:
            self._window_manager = ModalView(
                size_hint=(1, 1), auto_dismiss=False
            )
            self._window_manager.add_widget(self)
        if not self._window_manager_open:
            self._window_manager.open()
            self._window_manager_open = True

    def get_access_string(self, path):
        access_string = ""
        if self.use_access:
            access_data = {"r": os.R_OK, "w": os.W_OK, "x": os.X_OK}
            for access in access_data.keys():
                access_string += (
                    access if os.access(path, access_data[access]) else "-"
                )
        return access_string

    def get_content(self):
        try:
            files = []
            dirs = []

            for content in os.listdir(self.current_path):
                if os.path.isdir(os.path.join(self.current_path, content)):
                    if self.search == "all" or self.search == "dirs":
                        if (not self.show_hidden_files) and (
                            content.startswith(".")
                        ):
                            continue
                        else:
                            dirs.append(content)

                else:
                    if self.search == "all" or self.search == "files":
                        if len(self.ext) != 0:
                            try:
                                files.append(
                                    os.path.join(self.current_path, content)
                                )
                            except IndexError:
                                pass
                        else:
                            if (
                                not self.show_hidden_files
                                and content.startswith(".")
                            ):
                                continue
                            else:
                                files.append(content)

            return dirs, files

        except OSError:
            return None, None

    def close(self):
        self._window_manager.dismiss()
        self._window_manager_open = False

    def select_dir_or_file(self, path, widget):
        if os.path.isfile(os.path.join(self.current_path, path)):
            if self.selector == "multi":
                file_path = os.path.join(self.current_path, path)
                if file_path in self.selection:
                    widget._selected = False
                    self.selection.remove(file_path)
                else:
                    widget._selected = True
                    self.selection.append(file_path)
            elif self.selector == "folder":
                return
            else:
                self.select_path(os.path.join(self.current_path, path))

        else:
            self.current_path = path
            self.show(path)

    def back(self):
        path, end = os.path.split(self.current_path)

        if not end:
            self.close()
            self.exit_manager(1)

        else:
            self.show(path)

    def select_directory_on_press_button(self, *args):
        if self.selector == "multi":
            if len(self.selection) > 0:
                self.select_path(self.selection)
        else:
            if self.selector == "folder" or self.selector == "any":
                self.select_path(self.current_path)


Builder.load_string(ACTIVITY_MANAGER)
