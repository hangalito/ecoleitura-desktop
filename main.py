import pygame
from gtts import (
    gTTS,
    gTTSError
)
from pathlib import Path
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.dialog import MDDialog
from kivy.core.audio import SoundLoader
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.bottomsheet import MDListBottomSheet


pygame.init()
audio = "audio.mp3"


class HomeScreen(MDFloatLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_path = Path(MDApp.get_running_app().user_data_dir)
        self.selected_idiom = self.idiom_code = None
        self.old_text = self.old_lang = ''

    # alerts about the selected idiom
    def callback_for_menu_items(self, *args):
        toast(args[0])
        self.selected_idiom = args[0].split()[0]
        self.idiom_code = self.get_lang_code(self.selected_idiom)
        self.ids.language_identifier.text = self.selected_idiom
    
    def open_nav_drawer(self, *args):
        self.ids.nav_drawer.elevation = 4
        self.ids.nav_drawer.set_state("open")
    
    # shows the list of idioms in bottom sheet
    def show_list_bottom_sheet(self):
        self.ids.nav_drawer.closing_time = .1
        self.ids.nav_drawer.set_state('closed')

        bottom_sheet_menu = MDListBottomSheet(radius=30, radius_from='top',)
        idioms = ['Português', 'Inglês', 'Espanhol', 'Italiano', 'Francês']
        idioms.sort()
        # generates the list of languages available
        for idiom in idioms:
            bottom_sheet_menu.add_item(
                f"{idiom}",
                lambda x, y=idiom: self.callback_for_menu_items(
                    f"{y} selecionado",
                ),
            )
        bottom_sheet_menu.open()
        self.ids.nav_drawer.closing_time = .37

    # method that returns the code of the selected idiom
    def get_lang_code(self, *args) -> str:
        spin_text = self.ids.language_identifier.text
        lang = str()
        if spin_text == "Português":
            lang = 'pt'
        elif spin_text == 'Inglês':
            lang = 'en'
        elif spin_text == 'Italiano':
            lang = 'it'
        elif spin_text == 'Francês':
            lang = 'fr'
        elif spin_text == 'Espanhol':
            lang = 'es'
        return lang

    def get_lang(self, *args, ) -> str:
        lang_code = self.get_lang_code()
        lang = ''
        if lang_code == 'pt':
            lang = 'Português'
        elif lang_code == 'en':
            lang = 'Inglês'
        elif lang_code == 'it':
            lang = 'Italiano'
        elif lang_code == 'fr':
            lang = 'Francês'
        elif lang_code == 'es':
            lang = 'Espanhol'
        return lang

    # plays the provided text
    def play_text(self, *args) -> bool | None:
        def load_audio():
            pygame.mixer_music.load(f"{self.data_path}{audio}")
            pygame.mixer_music.play()

        lang = self.get_lang_code()
        text = self.ids.text_input.text.strip()

        if text:
            if self.old_text is text and self.old_lang is lang:
                load_audio()
                return

        try:
            audio_sample = gTTS(text=text, lang=self.get_lang_code(), slow=False)
            # noinspection PyTypeChecker
            audio_sample.save(f"{self.data_path}{audio}")
            load_audio()
        except gTTSError:
            self.internet_connection_exception()
            # self.old_text = text = ''
            return False
        except AssertionError:
            pass

        self.old_text = text
        self.old_lang = lang

    def internet_connection_exception(self, *args):
        self.dialog = MDDialog(
            title='Falha na conexão',
            text='Certifique-se de que o seu dispositivo tem conexão a internet e tente novamente',
            buttons=[MDRaisedButton(
                text="OK",
                theme_text_color="Primary",
                on_release=self.dismiss_dialog
            )],
            radius=[27, 27, 27, 27],
            shadow_softness=74,
            shadow_offset=[10, 10]
        )
        self.dialog.open()
        self.old_text = ''

    def dismiss_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def callback_for_saved_audio(self, *args):
        audio_file: Path = self.data_path.joinpath(audio)
        user_path: Path = Path.home().joinpath("Eco Leitura")
        if Path.exists(user_path):
            Path.rename(
             audio_file,
             user_path.joinpath(audio)
            )
        else:
            toast("Não há nada para salvar")


class EcoLeitura(MDApp):
    screen = path = None

    def build(self) -> object:
        self.theme_cls.material_style = 'M3'
        self.path = Path(self.user_data_dir)
        self.screen = HomeScreen()
        return self.screen

    def on_start(self) -> None:
        super().on_start()
        self.screen.ids.language_identifier.text = self.load_language()
        if self.load_theme() is True:
            self.screen.ids.switch_color.active = True
            self.set_dark_theme()
    
    def on_stop(self):
        super().on_stop()
        language_file = self.path.joinpath("language")
        theme_file = self.path.joinpath("theme")

        language = self.screen.ids.language_identifier.text
        theme = str(self.screen.ids.switch_color.active)

        # Save the language
        with open(language_file, 'w') as file:
            file.write(language)
        
        # Save the theme 
        with open(theme_file, 'w') as file:
            file.write(theme)

    def load_language(self, *args) -> str:
        file = self.path.joinpath("language")
        try:
            with open(file, 'r') as file:
                language = file.read()
                if not language:
                    language = 'Português'
            return language
        except FileNotFoundError:
            Path.touch(file)
            self.load_language()

    def load_theme(self, *args):
        file = self.path.joinpath('theme')
        value = None
        try:
            with open(file, 'r') as file:
                theme = file.read()
                if theme == 'True':
                    value = True
                else:
                    value = False
            return value
        except FileNotFoundError:
            Path.touch(file)
            self.load_theme()

    def set_dark_theme(self, *args):
        if self.screen.ids.switch_color.active:
            self.theme_cls.theme_style = "Dark"
            self.screen.ids.drawer_menu_title.title_color = "#FFFFFF"
            self.screen.ids.color_label.text_color = self.screen.ids.drawer_menu_title.title_color
            self.screen.ids.save_button.text_color = self.screen.ids.drawer_menu_title.title_color
            self.screen.ids.change_language.text_color = self.screen.ids.drawer_menu_title.title_color
            self.screen.ids.language_identifier.text_color = self.screen.ids.drawer_menu_title.title_color
        else:
            self.theme_cls.theme_style = "Light"
            self.screen.ids.drawer_menu_title.title_color = "#333333"
            self.screen.ids.color_label.text_color = self.screen.ids.drawer_menu_title.title_color
            self.screen.ids.save_button.text_color = self.screen.ids.drawer_menu_title.title_color
            self.screen.ids.change_language.text_color = self.screen.ids.drawer_menu_title.title_color
            self.screen.ids.language_identifier.text_color = self.screen.ids.drawer_menu_title.title_color


if __name__ == '__main__':
    EcoLeitura(title="Eco Leitura").run()
