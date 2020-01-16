from kivy.uix.button import Button


class RoundedButton(Button):

    def __init__(self, text="", on_release=None, size_hint=(None, None), size=(None, None), pos_hint={'center_x': .5},
                 color=(1, 1, 1, 1), background_color=(0, 0, 0, 1), font_size=12, border_radius=[50,50,5,5]):
        super().__init__()
        self.text = text
        self.on_release = on_release
        self.size_hint = size_hint
        self.size = size
        self.pos_hint = pos_hint
        self.color = color
        self.back_color = background_color
        self.font_size = font_size
        self.border_radius = border_radius

    def build(self):
        return self
