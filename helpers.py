main = '''
<Root@BoxLayout>
    orientation: 'vertical'

    MDToolbar:
        title: app.title

<Box@BoxLayout>:
    bg: 0, 0, 0, 0

    canvas:
        Color:
            rgba: root.bg
        Rectangle:
            pos: self.pos
            size: self.size

NavigationLayout:
    ScreenManager:
        id: screen_manager

        Screen:
            id: MainScreen
            name: 'MainScreen'
            song_name: song_name

            BoxLayout:
                orientation: 'vertical'

                MDToolbar:
                    title: app.title
                    elevation: 10
                    left_action_items: [['menu', lambda x: nav_drawer.toggle_nav_drawer()]]

                MDBottomAppBar:
                    MDToolbar:
                        text: "Location"
                        mode: 'end'
                        type: 'bottom'
                        icon: "folder"
                        icon_color: app.theme_cls.primary_color
                        on_action_button: app.file_manager_open()
                Widget:
            
            MDTextField:
                id: song_name
                hint_text: "Song name"
                helper_text: "Enter song name here"
                helper_text_mode: "on_focus"
                icon_right: "music-note"
                icon_right_color: app.theme_cls.primary_color
                pos_hint: {'center_x': 0.5, 'center_y': 0.7}
                size_hint:(0.5,0.08)
            
            MDRoundFlatButton:
                text: 'Search'
                pos_hint: {'center_x':0.5, 'y':0.5}
                on_press:
                    app.spin()
                    screen_manager.transition.direction = 'left'
                    screen_manager.current = 'SongListScreen'
                    

            MDSpinner:
                id: spinner
                padding: 10
                size_hint: None, None
                size: dp(46), dp(46)
                pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                active: False

        Screen:
            id: SongListScreen
            name: 'SongListScreen'
            BoxLayout:
                orientation: 'vertical'

                MDToolbar:
                    title: 'Results'
                    elevation: 10

                ScrollView:
                    size_hint: (1, 2.5)
                    MDList:
                        id: container
                
                Widget:
        
        Screen:
            id: SongDetailsScreen
            name: 'SongDetailsScreen'
            BoxLayout:
                id: detailsbox
                orientation: 'vertical'

        
        Screen:
            id: AboutScreen
            name: 'AboutScreen'
            
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1, 0.5
                pos_hint: {'center_x': 0.5, 'center_y': 0.75}

                MDToolbar:
                    elevation: 10
                    title: 'About'

                Image:
                    source: './made.png'

                MDRoundFlatButton:
                    text: 'Contact us'
                    pos_hint: {'center_x':0.5}
                    on_press:
                        screen_manager.transition.direction = 'right'
                        screen_manager.current = 'MainScreen'

    MDNavigationDrawer:
        id: nav_drawer
        BoxLayout:
            orientation: 'vertical'
            spacing: '8dp'
            padding: '8dp'

            Image:
                source: './bh-circle_cropped.png'

            ScrollView:
                MDList:
                    OneLineIconListItem:
                        text: 'Home'
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                        on_release:
                            nav_drawer.toggle_nav_drawer()
                            screen_manager.transition.direction = 'right'
                            screen_manager.current = 'MainScreen'
                        IconLeftWidget:
                            icon: 'home'
                            on_release:
                                nav_drawer.toggle_nav_drawer()
                                screen_manager.transition.direction = 'right'
                                screen_manager.current = 'MainScreen'
                        
                        
                    OneLineIconListItem:
                        text: 'Downloads'
                        on_release:
                            nav_drawer.toggle_nav_drawer()
                            print('pressed downloads')
                        IconLeftWidget:
                            icon: 'folder-download'
                    
                    OneLineIconListItem:
                        text: 'About'
                        on_release:
                            nav_drawer.toggle_nav_drawer()
                            screen_manager.transition.direction = 'left'
                            screen_manager.current = 'AboutScreen'
                        IconLeftWidget:
                            icon: 'help-rhombus'
                            on_release:
                                nav_drawer.toggle_nav_drawer()
                                screen_manager.transition.direction = 'left'
                                screen_manager.current = 'AboutScreen'

'''