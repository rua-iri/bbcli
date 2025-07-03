import os
import urwid
import webbrowser
import configparser

from .bbcapi import BBC
from datetime import datetime

_config = None


class BBCNews(object):

    def __init__(self, i, story):
        self.index = i + 1
        self.story = story

    @property
    def story_number(self):
        index = str(self.index)
        if len(index) == 1:
            return ''.join((' ', index))
        return self.index

    @property
    def story_title(self):
        return self.story.title

    @property
    def story_description(self):
        return self.story.description

    @property
    def story_link(self):
        return self.story.link

    @property
    def last_updated(self):
        return self.story.last_updated


def get_top_stories():
    bbc = BBC()
    news = bbc.get_top_stories()
    if news is None:
        pass
    else:
        for i, story in enumerate(news[:30]):
            yield BBCNews(i, story)


def open_browser(url):
    webbrowser.open(url, 2)


class ItemWidget(urwid.WidgetWrap):

    def __init__(self, s):
        self.story_link = s.story_link
        story_title = urwid.AttrWrap(
            urwid.Text(f'{s.story_number}. {s.story_title}'),
            'body',
            'focus'
        )
        story_description = urwid.AttrWrap(
            urwid.Text(f'    {s.story_description}'),
            'subtext',
            'focus'
        )
        story_last_updated = urwid.AttrWrap(
            urwid.Text(f'    {s.last_updated}'),
            'subtext',
            'focus'
        )
        pile = urwid.Pile([story_title, story_description, story_last_updated])
        self.item = [
            urwid.Padding(pile, left=1, right=1),
            (
                'flow',
                urwid.AttrWrap(
                    urwid.Text(' ', align="right"),
                    'body',
                    'focus'
                ))
        ]
        w = urwid.Columns(self.item, focus_column=0)
        super(ItemWidget, self).__init__(w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class UI(object):

    palette = [
        ('head', '', '', '', '#FFF', '#E00'),
        ('body', '', '', '', '#000', '#FFF'),
        ('offline', '', '', '', '#FFF', '#000'),
        ('offline_bg', '', '', '', '#FFF', '#000'),
        ('footer', '', '', '', '#000', 'g89'),
        ('focus', '', '', '', '#FFF', 'dark red'),
        ('subtext', '', '', '', 'g55', '#FFF'),
        ('breaking', '', '', '', '#FFF', '#E00'),
    ]

    header = [
        urwid.AttrWrap(
            urwid.Text(' BBC | NEWS', align='center'),
            'head'
        ),
        (
            'flow',
            urwid.AttrWrap(
                urwid.Text(' ', align="left"),
                'head'
            )),
    ]
    header = urwid.Columns(header)

    offlineHeader = [
        urwid.AttrWrap(
            urwid.Text(' BBC | NEWS (Offline)', align='center'),
            'head'
        ),
        (
            'flow',
            urwid.AttrWrap(
                urwid.Text(' ', align="left"),
                'head'
            )
        ),
    ]
    offlineHeader = urwid.Columns(offlineHeader)

    # defaults
    keys = {
        'quit': 'q',
        'open': 'w',
        'tabopen': 't',
        'refresh': 'r',
        'latest': 'l',
        'scroll_up': 'k',
        'scroll_down': 'j',
        'top': 'g',
        'bottom': 'G'
    }

    mouse_button = {
        'left': 1,
        'middle': 2,
        'right': 3,
        'wheel_up': 4,
        'wheel_down': 5
    }

    count = 2
    link = ""

    def run(self):
        self.make_screen()
        urwid.set_encoding('utf-8')
        try:
            self.loop.run()
        except KeyboardInterrupt:
            print("Keyboard interrupt received, quitting gracefully")
            raise urwid.ExitMainLoop

    def make_screen(self):
        self.view = urwid.Frame(
            urwid.AttrWrap(self.populate_stories(), 'body'),
            header=self.header
        )

        self.loop = urwid.MainLoop(
            self.view,
            self.palette,
            unhandled_input=self.handle_user_input
        )
        self.loop.screen.set_terminal_properties(colors=256)
        self.loop.set_alarm_in(200, self._wrapped_refresh)

    def get_stories(self):
        items = list()
        for story in get_top_stories():
            items.append(ItemWidget(story))
        return items

    def isOnline(self):
        if len(self.get_stories()) == 0:
            return False
        else:
            return True

    def alreadyOnline(self):
        if self.isOnline() is False:
            self.count = 0
            return False
        elif self.isOnline() is True:
            self.count = self.count + 1
        if self.count >= 2:
            self.count = 2
            return True
        else:
            return False

    def populate_stories(self):
        items = self.get_stories()
        self.walker = urwid.SimpleListWalker(items)
        self.listbox = urwid.ListBox(self.walker)
        return self.listbox

    def set_status_bar(self, msg):
        msg = f'{msg.rjust(len(msg)+1)}'
        self.view.set_footer(urwid.AttrWrap(urwid.Text(msg), 'footer'))

    def open_story_link(self):
        url = self.listbox.get_focus()[0].story_link
        open_browser(url)

    def scroll_up(self):
        if self.listbox.focus_position - 1 in self.walker.positions():
            self.listbox.set_focus(
                self.walker.prev_position(self.listbox.focus_position)
            )

    def scroll_down(self):
        if self.listbox.focus_position + 1 in self.walker.positions():
            self.listbox.set_focus(
                self.walker.next_position(self.listbox.focus_position)
            )

    def mouse_input(self, input):
        if input[1] == self.mouse_button['left']:
            self.open_story_link()
        elif input[1] == self.mouse_button['wheel_up']:
            self.scroll_up()
        elif input[1] == self.mouse_button['wheel_down']:
            self.scroll_down()

    def keystroke(self, input):
        if input in self.keys['quit'].lower():
            raise urwid.ExitMainLoop()
        if input is self.keys['open'] or input is self.keys['tabopen']:
            self.open_story_link()
        if input is self.keys['refresh']:
            self.set_status_bar('Refreshing for new stories...')
            self.loop.draw_screen()
            self.refresh_with_new_stories()
        if input is self.keys['latest']:
            open_browser(self.link)
        if input is self.keys['scroll_up']:
            self.scroll_up()
        if input is self.keys['scroll_down']:
            self.scroll_down()
        if input is self.keys['top']:
            if self.listbox.focus_position - 1 in self.walker.positions():
                self.listbox.set_focus(self.walker.positions()[0])
        if input is self.keys['bottom']:
            if self.listbox.focus_position + 1 in self.walker.positions():
                self.listbox.set_focus(self.walker.positions()[-1])

    def handle_user_input(self, input):
        if type(input) is tuple:
            self.mouse_input(input)
        elif type(input) is str:
            self.keystroke(input)

    def refresh_with_new_stories(self):
        items = self.get_stories()
        self.alreadyOnline()
        if self.count == 0:
            self.view.set_body(
                urwid.AttrWrap(self.populate_stories(), 'offline_bg')
            )
            self.view.set_header(header=self.offlineHeader)
            self.view.set_footer(
                urwid.AttrWrap(
                    urwid.Text(
                        "You are currently offline. Please check your internet connection."
                    ),
                    'offline'
                )
            )
        if self.count == 1:
            self.view.set_header(header=self.header)
            self.view.set_body(urwid.AttrWrap(self.populate_stories(), 'body'))
        else:
            self.walker[:] = items
            self.loop.draw_screen()

    def set_latest_links(self, link):
        self.link = link

    def _wrapped_refresh(self, loop, *args):
        online = self.isOnline()
        self.refresh_with_new_stories()
        ct = datetime.now().strftime('%H:%M:%S')
        if online is False:
            self.set_status_bar(
                'You are currently offline. Please check your internet connection.')
        else:
            self.set_status_bar(
                f'Automatically updated ticker and fetched new stories at: {ct}'
            )
        self.loop.set_alarm_in(200, self._wrapped_refresh)


def live():
    u = UI()
    u.run()
