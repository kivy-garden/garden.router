# coding=utf-8
"""
Simple Router example
=====================

What you should look for:
- Our SimpleApp subclass AppRouter, set the root widget to a MainRouter, and
  then set the current route to "/"
- MainRouter is a Router widget, that you could be styling if you want. In this
  one, we declare 3 routes
- Each route must return a view to display. It can be either a simple widget of
  your own, or directly a Screen
- See how you can change the route from kv (search on_release: )
- See how you can back depending where the user came from (search history_back)

"""
from kivy.garden.router import AppRouter, Router, route
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

Builder.load_string("""
<MenuScreen>:
    AnchorLayout:
        GridLayout:
            cols: 1
            size_hint: .5, None
            height: self.minimum_height
            row_default_height: "48dp"
            spacing: "4dp"

            Button:
                text: "Settings"
                on_release: app.route = "/settings"

            Button:
                text: "About"
                on_release: app.route = "/about"

<AboutScreen>:
    BoxLayout:
        orientation: "vertical"
        Button:
            text: "Back"
            on_release: app.history_back()
            size_hint_y: None
            height: "48dp"

        Label:
            text: "About this app."

<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"
        Button:
            text: "Back"
            on_release: app.history_back()
            size_hint_y: None
            height: "48dp"

        Label:
            text: "Settings"
""")


class MenuScreen(Screen):
    pass


class AboutScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


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
