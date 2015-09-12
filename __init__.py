# coding=utf-8
"""
Router for Kivy application
===========================

.. author:: Mathieu Virbel <mat@meltingrocks.com>

"""

from kivy.app import App
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.logger import Logger
import re

Builder.load_string("""
<Router>:
    ScreenManager:
        id: screenmanager
""")

# Taken from werkzeug/routing.py
_rule_re = re.compile(r'''
    (?P<static>[^<]*)                           # static rule data
    <
    (?:
        (?P<converter>[a-zA-Z_][a-zA-Z0-9_]*)   # converter name
        (?:\((?P<args>.*?)\))?                  # converter arguments
        \:                                      # variable delimiter
    )?
    (?P<variable>[a-zA-Z_][a-zA-Z0-9_]*)        # variable name
    >
''', re.VERBOSE)


def parse_rule(rule):
    pos = 0
    end = len(rule)
    do_match = _rule_re.match
    used_names = set()
    while pos < end:
        m = do_match(rule, pos)
        if m is None:
            break
        data = m.groupdict()
        if data['static']:
            yield None, None, data['static']
        variable = data['variable']
        converter = data['converter'] or 'default'
        if variable in used_names:
            raise ValueError('variable name %r used twice.' % variable)
        used_names.add(variable)
        yield converter, data['args'] or None, variable
        pos = m.end()
    if pos < end:
        remaining = rule[pos:]
        if '>' in remaining or '<' in remaining:
            raise ValueError('malformed url rule: %r' % rule)
        yield None, None, remaining


class BaseConverter(object):
    regex = '[^/]/'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class PathConverter(BaseConverter):
    regex = '[^/].*?'

    def to_python(self, value):
        if not value.startswith("/"):
            return "/{}".format(value)
        return value


class IntegerConverter(BaseConverter):
    regex = r'\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return '{}'.format(value)


class UnicodeConverter(BaseConverter):
    regex = '[^/]{1,}'


CONVERTERS = {
    "path": PathConverter,
    "int": IntegerConverter,
    "default": UnicodeConverter
}


def regex_rule(rule):
    regex_parts = []
    url_parts = list(parse_rule(rule))
    for converter, args, variable in url_parts:
        if converter is None:
            regex_parts.append(re.escape(variable))
        else:
            conv = CONVERTERS.get(converter)()
            regex_parts.append('(?P<%s>%s)' % (variable, conv.regex))
    regex = r'^%s$' % (u''.join(regex_parts))
    return (url_parts, re.compile(regex, re.UNICODE))


def route(rule):
    url_parts, regex = regex_rule(rule)
    def decorator(f):
        if not hasattr(f, "router_rules"):
            f.router_rules = [(rule, regex, url_parts)]
        else:
            f.router_rules.append((rule, regex, url_parts))
        return f

    return decorator


def route_options(**options):
    def decorator(f):
        f.router_options = options
        return f
    return decorator


class AppRouter(App):
    route = StringProperty("")
    history = ListProperty([])
    max_history = NumericProperty(20)

    def on_route(self, instance, route):
        Logger.info("AppRouter: Route is '{}'".format(route))
        self.root.route = self.route
        history = self.history
        if (not history) or (history[-1] != route):
            history.append(self.route)
        self.history = history[-self.max_history:]

    def history_back(self):
        self.history.pop(-1)
        if self.history:
            self.route = self.history[-1]


class Router(RelativeLayout):
    route = StringProperty("")

    def __init__(self, **kwargs):
        assert(route not in kwargs)
        self.router_rules = {}
        self.init_routes()
        super(Router, self).__init__(**kwargs)

    def init_routes(self):
        for key in dir(self):
            func = getattr(self, key)
            if not callable(func) or not hasattr(func, "router_rules"):
                continue
            for rule, regex, url_parts in func.router_rules:
                options = None
                if hasattr(func, "router_options"):
                    options = func.router_options
                self.add_route(rule, func, regex=regex, url_parts=url_parts, options=options)

    def add_route(self, rule, func, regex=None, url_parts=None, options=None):
        if regex is None:
            url_parts, regex = regex_rule(rule)
        Logger.debug("{}: Add route {}".format(
            self.__class__.__name__, rule))
        url_parts, regex = regex_rule(rule)
        self.router_rules[regex] = (url_parts, func, options)

    def on_route(self, instance, route):
        for regex, info in self.router_rules.items():
            result = regex.match(route)
            if not result:
                continue
            url_parts, func, options = info
            name = route
            # convert url variables/value to kwargs
            kwargs = self._result_to_variables(result, url_parts)

            if options:
                # get the default name of this route for the screen
                name = options.get("name", route)

                # should we pass the previous view?
                if options.get("with_view"):
                    sm = self.ids.screenmanager
                    view = None
                    if sm.has_screen(name):
                        view = sm.get_screen(name)._router_view
                    kwargs["view"] = view

            view = func(**kwargs)
            return self.switch_to_view(view, name=name)
        Logger.warning("{}: Unable to find a view for {}".format(
            self.__class__.__name__, route))

    def switch_to_view(self, view, name=None):
        sm = self.ids.screenmanager
        if isinstance(view, Screen):
            screen = view
            self.link(screen, view)
        else:
            if hasattr(view, "_router_screen"):
                screen = view._router_screen
            else:
                screen = Screen(name=name)
                screen.add_widget(view)
                self.link(screen, view)

        if sm.has_screen(name):
            previous_screen = sm.get_screen(name)
            if previous_screen is view._router_screen:
                return
            sm.remove_widget(previous_screen)
            self.unlink(screen=previous_screen)

        sm.switch_to(screen)

    def link(self, screen, view):
        screen._router_view = view
        view._router_screen = screen

    def unlink(self, screen):
        if screen._router_view:
            screen._router_view._router_screen = None
        screen._router_view = None

    def _result_to_variables(self, result, url_parts):
        kwargs = {}
        index = 1
        for converter, args, variable in url_parts:
            if converter is None:
                continue
            conv = CONVERTERS.get(converter)()
            value = result.group(index)
            kwargs[variable] = conv.to_python(value)
            index += 1
        return kwargs
