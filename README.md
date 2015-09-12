# Router

Router is a routing library for Kivy.

It keeps your UI sync to the url/route you asked for. It has a simple API which
can remind Flask.

## Installation

    garden install router

## Usage

```python
# Full example available in examples/simple.py

from kivy.garden.router import AppRouter, Router, route
# ...
Builder.load_string("""
<MenuScreen>:
    GridLayout:
        cols: 1
        Button:
            text: "Settings"
            on_release: app.route = "/settings"
        Button:
            text: "About"
            on_release: app.route = "/about"

<AboutScreen>:
    BoxLayout:
        Button:
            text: "Back"
            on_release: app.history_back()
        Label:
            text: "About this app."

<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"
        Button:
            text: "Back"
            on_release: app.history_back()
        Label:
            text: "Settings"
"""

# ...

class MainRouter(Router):
    @route("/")
    def index(self):
        return MenuScreen()

    @route("/about")
    def about(self):
        return AboutScreen()

    @route("/settings")
    def settings(self):
        return SettingsScreen()


class SimpleApp(AppRouter):
    def build(self):
        self.root = MainRouter()
        self.route = "/"

SimpleApp().run()
```
