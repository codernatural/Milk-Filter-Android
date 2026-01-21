import os
import random
import traceback
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.animation import Animation
from kivy.factory import Factory
from PIL import Image as PilImage

try:
    from plyer import filechooser
except:
    filechooser = None

KV = """
#:set accent_color (1, 0.25, 0.25, 1)      # Красный
#:set bg_color (0.96, 0.96, 0.96, 1)       # Серый фон
#:set card_bg (1, 1, 1, 1)                 # Белый
#:set input_bg (0.92, 0.92, 0.92, 1)       # Серый инпут
#:set text_dark (0.2, 0.2, 0.2, 1)
#:set switch_off (0.8, 0.8, 0.8, 1)

<StylizedSwitch>:
    size_hint: None, None
    size: dp(50), dp(30)
    canvas.before:
        Color:
            rgba: accent_color if root.active else switch_off
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]
        Color:
            rgba: (1, 1, 1, 1)
        Ellipse:
            pos: self.thumb_x, self.y + dp(2)
            size: self.height - dp(4), self.height - dp(4)
    
    Button:
        background_color: 0,0,0,0
        pos: root.pos
        size: root.size
        on_press: root.toggle()

<PillButton>:
    font_size: '18sp'
    bold: True
    color: (1,1,1,1) if root.bg_type == 'accent' else text_dark
    canvas.before:
        Color:
            rgba: accent_color if root.bg_type == 'accent' else input_bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.height / 2]

<ModernSliderBox>:
    orientation: 'vertical'
    size_hint_y: None
    height: '70dp'
    padding: [15, 5, 15, 5]
    canvas.before:
        Color:
            rgba: input_bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15]
    Label:
        text: root.title
        color: (0.5, 0.5, 0.5, 1)
        font_size: '12sp'
        size_hint_y: 0.4
        halign: 'left'
        text_size: self.size
    Slider:
        id: sld
        min: 0
        max: 100
        value: 0
        cursor_size: (25, 25)
        background_width: '4dp'
        cursor_image: ''
        canvas.after:
            Color:
                rgba: accent_color
            Ellipse:
                pos: (self.value_pos[0] - 12.5, self.center_y - 12.5)
                size: (25, 25)

<ModeSelector>:
    spacing: '10dp'
    size_hint_y: None
    height: '50dp'
    PillButton:
        id: btn_m1
        text: 'Milk 1'
        bg_type: 'accent'
        on_press: root.select(1)
    PillButton:
        id: btn_m2
        text: 'Milk 2'
        bg_type: 'grey'
        on_press: root.select(2)

<MainScreen>:
    # Связь переменных (ObjectProperty)
    display_widget: display_img
    status_label: status_lbl
    slider_widget: slider_box.ids.sld
    slider_title_widget: slider_box
    noise_switch: custom_switch
    action_button: btn_action

    canvas.before:
        Color:
            rgba: bg_color
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: accent_color
        RoundedRectangle:
            pos: self.x, self.height * 0.65
            size: self.width, self.height * 0.4
            radius: [0, 0, 60, 60]

    Label:
        text: "Milk Filter"
        font_size: '32sp'
        bold: True
        color: (1,1,1,1)
        pos_hint: {'center_x': 0.5, 'top': 0.94}
        size_hint: (None, None)
        size: (200, 50)

    BoxLayout:
        orientation: 'vertical'
        padding: '20dp'
        spacing: '15dp'
        size_hint: (0.9, 0.8)
        pos_hint: {'center_x': 0.5, 'center_y': 0.46}
        canvas.before:
            Color:
                rgba: (0, 0, 0, 0.1)
            RoundedRectangle:
                pos: self.x + 5, self.y - 5
                size: self.width, self.height
                radius: [25]
            Color:
                rgba: card_bg
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [25]

        BoxLayout:
            size_hint_y: 0.45
            padding: '5dp'
            canvas.before:
                Color:
                    rgba: (0.9, 0.9, 0.9, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [18]
            Image:
                id: display_img
                source: ''
                allow_stretch: True
                keep_ratio: True
                nocache: True

        PillButton:
            text: 'Выбрать фото'
            bg_type: 'grey'
            size_hint_y: None
            height: '50dp'
            on_press: app.choose_file()

        ModernSliderBox:
            id: slider_box
            title: 'Качество сжатия: 100%'

        ModeSelector:
            id: mode_select

        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Label:
                text: 'Эффект шума (Pointillism)'
                color: text_dark
                halign: 'left'
                text_size: self.size
                valign: 'middle'
            
            StylizedSwitch:
                id: custom_switch
                active: False

        PillButton:
            id: btn_action
            text: 'ПРИМЕНИТЬ'
            bg_type: 'accent'
            size_hint_y: None
            height: '60dp'
            on_press: app.apply_filter_async()
        
        Label:
            id: status_lbl
            text: 'Готово к работе'
            color: (0.6, 0.6, 0.6, 1)
            font_size: '12sp'
            size_hint_y: None
            height: '20dp'
"""


class StylizedSwitch(BoxLayout):
    active = BooleanProperty(False)
    thumb_x = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.update_thumb_pos, 0)
        self.bind(pos=self.update_thumb_pos, size=self.update_thumb_pos)

    def update_thumb_pos(self, *args):
        padding = self.height * 0.1
        if self.active:
            self.thumb_x = self.x + self.width - self.height + padding
        else:
            self.thumb_x = self.x + padding

    def toggle(self):
        self.active = not self.active
        padding = self.height * 0.1
        target_x = (self.x + self.width - self.height + padding) if self.active else (self.x + padding)
        anim = Animation(thumb_x=target_x, duration=0.2, t='out_quad')
        anim.start(self)

class PillButton(ButtonBehavior, Label):
    bg_type = StringProperty('grey')

class ModernSliderBox(BoxLayout):
    title = StringProperty('')

class ModeSelector(BoxLayout):
    def select(self, mode):
        app = App.get_running_app()
        app.set_mode(mode)
        if mode == 1:
            self.ids.btn_m1.bg_type = 'accent'
            self.ids.btn_m2.bg_type = 'grey'
        else:
            self.ids.btn_m1.bg_type = 'grey'
            self.ids.btn_m2.bg_type = 'accent'

class MainScreen(FloatLayout):
    display_widget = ObjectProperty(None)
    status_label = ObjectProperty(None)
    slider_widget = ObjectProperty(None)
    slider_title_widget = ObjectProperty(None)
    noise_switch = ObjectProperty(None)
    action_button = ObjectProperty(None)


Factory.register('StylizedSwitch', cls=StylizedSwitch)
Factory.register('PillButton', cls=PillButton)
Factory.register('ModernSliderBox', cls=ModernSliderBox)
Factory.register('ModeSelector', cls=ModeSelector)
Factory.register('MainScreen', cls=MainScreen)

class MilkFilterApp(App):
    def build(self):
        try:
            Builder.load_string(KV)
            self.root_widget = MainScreen()
            self.root_widget.slider_widget.bind(value=self.update_slider_text)
            
            self.source_image_path = None
            self.img_pil = None
            self.milk_mode = 1
            self.temp_path = os.path.join(self.user_data_dir, 'temp.png')
            self.save_state = False

            return self.root_widget
        except Exception as e:
            return Label(text=f"CRASH:\n{traceback.format_exc()}", color=(1,0,0,1), font_size='20sp')

    def on_start(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_MEDIA_IMAGES
                ])
            except Exception as e:
                self.root_widget.status_label.text = f"Perm Err: {e}"

    def update_slider_text(self, instance, value):
        q = 100 - int(value)
        self.root_widget.slider_title_widget.title = f"Качество сжатия: {q}%"

    def set_mode(self, mode):
        self.milk_mode = mode

    def choose_file(self):
        try:
            if filechooser:
                filechooser.open_file(on_selection=self.on_file_selected)
            else:
                self.root_widget.status_label.text = "Filechooser не найден"
        except Exception as e:
            self.root_widget.status_label.text = f"Err: {e}"

    def on_file_selected(self, selection):
        if selection:
            try:
                self.source_image_path = selection[0]
                self.root_widget.display_widget.source = self.source_image_path
                self.root_widget.status_label.text = "Фото загружено"
                
                self.save_state = False
                self.root_widget.action_button.text = "ПРИМЕНИТЬ"
                self.root_widget.action_button.bg_type = 'accent'
            except Exception as e:
                self.root_widget.status_label.text = f"Load Err: {e}"

    def apply_filter_async(self):
        if self.save_state:
            self.save_to_gallery()
            return
        if not self.source_image_path:
            self.root_widget.status_label.text = "Сначала выберите фото!"
            return
        self.root_widget.status_label.text = "Обработка..."
        self.root_widget.action_button.text = "ЖДИТЕ..."
        Clock.schedule_once(self.run_logic, 0.1)

    def run_logic(self, dt):
        try:
            try:
                img = PilImage.open(self.source_image_path).convert('RGB')
                img.thumbnail((800, 800)) 
            except MemoryError:
                self.root_widget.status_label.text = "Слишком большое фото!"
                self.root_widget.action_button.text = "ПРИМЕНИТЬ"
                return

            q = 100 - int(self.root_widget.slider_widget.value)
            if q < 100:
                import io
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=q)
                img = PilImage.open(buffer)

            width, height = img.size
            pixels = img.load()
            punt = 70 if self.root_widget.noise_switch.active else 100
            
            for x in range(width):
                for y in range(height):
                    R, G, B = pixels[x, y]
                    br = (R + G + B) // 3
                    if self.milk_mode == 1:
                        if br <= 25: c = (0,0,0)
                        elif 25<br<=70: c = (0,0,0) if random.random()<punt/100 else (102,0,31)
                        elif 70<br<120: c = (102,0,31) if random.random()<punt/100 else (0,0,0)
                        elif 120<=br<200: c = (102,0,31)
                        elif 200<=br<230: c = (137,0,146) if random.random()<punt/100 else (102,0,31)
                        else: c = (137,0,146)
                    else:
                        if br <= 25: c = (0,0,0)
                        elif 25<br<=70: c = (0,0,0) if random.random()<punt/100 else (92,36,60)
                        elif 70<br<90: c = (92,36,60) if random.random()<punt/100 else (0,0,0)
                        elif 90<=br<150: c = (92,36,60)
                        elif 150<=br<200: c = (203,43,43) if random.random()<punt/100 else (92,36,60)
                        else: c = (203,43,43)
                    pixels[x, y] = c

            img.save(self.temp_path)
            self.img_pil = img
            self.root_widget.display_widget.source = self.temp_path
            self.root_widget.display_widget.reload()
            
            self.root_widget.status_label.text = "Готово!"
            self.root_widget.action_button.text = "СОХРАНИТЬ В ГАЛЕРЕЮ"
            self.root_widget.action_button.bg_type = 'grey'
            self.save_state = True
            
        except Exception as e:
            self.root_widget.status_label.text = f"Err: {str(e)[:40]}"
            print(traceback.format_exc())
            self.root_widget.action_button.text = "ПРИМЕНИТЬ"

    def save_to_gallery(self):
        if not self.img_pil: return
        fn = f"Milk_{random.randint(1000,9999)}.jpg"
        
        try:
            if platform == 'android':
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).getAbsolutePath()
                full_path = os.path.join(path, fn)
                self.img_pil.save(full_path, quality=95)
                
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                File = autoclass('java.io.File')
                intent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE)
                intent.setData(Uri.fromFile(File(full_path)))
                PythonActivity.mActivity.sendBroadcast(intent)
                
                self.root_widget.status_label.text = "Сохранено!"
                
                self.save_state = False
                self.root_widget.action_button.text = "ПРИМЕНИТЬ СНОВА"
                self.root_widget.action_button.bg_type = 'accent'
                
            else:
                self.img_pil.save(fn)
                self.root_widget.status_label.text = "Сохранено на ПК"
                self.save_state = False
                self.root_widget.action_button.text = "ПРИМЕНИТЬ СНОВА"
                self.root_widget.action_button.bg_type = 'accent'

        except Exception as e:
            self.root_widget.status_label.text = f"Save Err: {str(e)}"

if __name__ == '__main__':
    MilkFilterApp().run()