from kivy.uix.boxlayout import BoxLayout


class BorderBox(BoxLayout):

    def __init__(self, orientation='', spacing=0, size_hint=(None, None), padding=(0, 0, 0, 0), final_x=50,
                 line_width=1):
        super().__init__()
        self.orientation = orientation
        self.spacing = spacing
        self.size_hint = size_hint
        self.padding = padding
        self.final_x = final_x
        self.line_width = line_width

    def build(self):
        return self
