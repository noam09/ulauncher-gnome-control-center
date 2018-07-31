import os
import logging
import subprocess
import distutils.spawn
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.SmallResultItem import SmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction

logging.basicConfig()
logger = logging.getLogger(__name__)

# Initialize items cache and gnome-control-center path
items_cache = []
gcpath = ''
# Locate gnome-control-center
gcpath = distutils.spawn.find_executable('gnome-control-center')
# This extension is useless without gnome-control-center
if gcpath is None or gcpath == '':
    logger.error('gnome-control-center path could not be determined')
    exit()


class GnomeControlExtension(Extension):
    def __init__(self):
        panels = []
        try:
            # Get list of panel names from gnome-control-center
            panel_list = subprocess.check_output([gcpath, "--list"])
            # Get sorted list of panels without empty items and without
            # irrelevant help text
            panels = sorted([i.strip() for i in panel_list.split('\n')
                             if not i.startswith("Available") and len(i) < 1])
        except Exception as e:
            print('Failed getting panel names, fallback to standard names')
        # Load default panels if they could not be retrieved
        if len(panels) < 2:
            panels = ['background',
                      'bluetooth',
                      'color',
                      'datetime',
                      'display',
                      'info-overview',
                      'default-apps',
                      'removable-media',
                      'keyboard',
                      'mouse',
                      'network',
                      'wifi',
                      'notifications',
                      'online-accounts',
                      'power',
                      'printers',
                      'privacy',
                      'region',
                      'search',
                      'sharing',
                      'sound',
                      'universal-access',
                      'user-accounts',
                      'wacom']

        for p in panels:
            # Capitalize words to form item title
            title = " ".join(w.capitalize() for w in p.split('-'))
            items_cache.append(create_item(title, p, p, title, p))

        super(GnomeControlExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # Get query
        term = (event.get_argument() or '').lower()
        # Display all items when query empty
        if term == "":
            items = [i for name, i in items_cache]
        # Only display items containing query substring
        else:
            items = [i for name, i in items_cache if term in name]
        return RenderResultListAction(items)


def create_item(name, icon, keyword, description, on_enter):
    return (
        keyword,
        ExtensionResultItem(
            name=name,
            # description=description,
            icon='images/{}.svg'.format(icon),
            on_enter=RunScriptAction('#!/usr/bin/env bash\n{} {}\n'.format(gcpath, on_enter), None)
        )
    )


if __name__ == '__main__':
    GnomeControlExtension().run()
