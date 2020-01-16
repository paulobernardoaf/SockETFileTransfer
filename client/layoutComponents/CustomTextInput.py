from kivy.uix.textinput import TextInput


class CustomTextInput(TextInput):

    def __init__(self, on_text_validate, text="", size_hint=(None, None), size=(None, None), pos_hint={'center_x': .5, 'center_y': .5},
                 color=(0, 0, 0, 1), background_color=(0, 0, 0, 0), font_size=14, multiline=False, unfocus_on_touch=False,
                hint_text=""):
        super().__init__()
        self.text = text
        self.size_hint = size_hint
        self.size = size
        self.pos_hint = pos_hint
        self.color = color
        self.background_color = background_color
        self.font_size = font_size
        self.multiline = multiline
        self.unfocus_on_touch = unfocus_on_touch
        self.hint_text = hint_text
        self.on_text_validate = on_text_validate

    def build(self):
        return self
