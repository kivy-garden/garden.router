# coding=utf-8
"""
Nested router example
=====================

This example show how we can have nested router: here, instead of Settings
beeing a simple widget or a Screen, it's a Router too. We capture the left
over of the "/settings" url to pass it to the route of our Settings.

This way, when either "/settings/audio" or "/settings/video" is called, the
same widget Settings is used, and only the content of Settings will change.

By default, the name of screens are from the name of the route itself. If
there is multiple route for the same function, it will be considered as
different screen. By using @route_options, you can tell which name your screen
must have, and ask for giving you the view that you created before.
Using this approach prevent the creation of a new screen.

"""

from kivy.garden.router import Router, AppRouter, route, route_options
from kivy.uix.label import Label
from kivy.lang import Builder

Builder.load_string("""
<-MainRouter>:
    BoxLayout:
        orientation: "vertical"

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "48dp"
            padding: "2dp"
            spacing: "2dp"
            Button:
                text: "Index"
                on_release: app.route = "/"

            Button:
                text: "Settings"
                on_release: app.route = "/settings"

            Button:
                text: "Credits"
                on_release: app.route = "/credits"

        ScreenManager:
            id: screenmanager

<-SettingsRouter>:
    BoxLayout:
        orientation: "vertical"

        BoxLayout:
            orientation: "horizontal"
            size_hint_y: None
            height: "48dp"
            padding: "2dp"
            spacing: "2dp"
            Button:
                text: "Audio"
                on_release: app.route = "/settings/audio"

            Button:
                text: "Video"
                on_release: app.route = "/settings/video"

        ScreenManager:
            id: screenmanager
""")

class SettingsRouter(Router):
    @route("/audio")
    def audio(self):
        return Label(text="audio settings")

    @route("/video")
    def video(self):
        return Label(text="video settings")

class MainRouter(Router):
    @route("/")
    def index(self):
        return Label(text="index")

    @route("/settings")
    @route("/settings/<path:subroute>")
    @route_options(name="settings", with_view=True)
    def settings(self, view, subroute="/audio"):
        if not view:
            view = SettingsRouter()
        view.route = subroute
        return view

    @route("/credits")
    def credits(self):
        return Label(text="credits")

class TestAppRouter(AppRouter):
    def build(self):
        self.root = MainRouter()
        self.route = "/settings/video"

TestAppRouter().run()
