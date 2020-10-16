import os
import json
import logging
import subprocess
import distutils.spawn
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.SmallResultItem import SmallResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.RunScriptAction import RunScriptAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from i18n import __
from icontheme import get_icon


logging.basicConfig()
logger = logging.getLogger(__name__)

# Initialize items cache and gnome-control-center path
items_cache = []
global usage_cache
usage_cache = {}

# Usage tracking
script_directory = os.path.dirname(os.path.realpath(__file__))
usage_db = os.path.join(script_directory, 'usage.json')
if os.path.exists(usage_db):
    with open(usage_db, 'r') as db:
        # Read JSON string
        raw = db.read()
        # JSON to dict
        usage_cache = json.loads(raw)

gcpath = ''
# Locate gnome-control-center
gcpath = distutils.spawn.find_executable('gnome-control-center')
# This extension is useless without gnome-control-center
if gcpath is None or gcpath == '':
    logger.error('gnome-control-center path could not be determined')
    exit()


class GnomeControlExtension(Extension):
    def __init__(self):
        dictPanels = { # init with correct translatable strings
            'default-apps': 'Default Applications',
            'display': 'Display Configuration',
            'info-overview': 'About',
            'keyboard': 'Keyboard Shortcuts',
            'lock': 'Lock screen',
            'user-accounts': 'Users',
            'datetime': 'Date & Time',
            'ubuntu': 'Appearance'
        }
        panels = []
        try:
            # Get list of panel names from gnome-control-center
            panel_list = subprocess.check_output([gcpath, "--list"])
            # Get sorted list of panels without empty items and without
            # irrelevant help text
            panels = sorted([i.strip() for i in panel_list.decode().split(os.linesep)
                            if (':' not in i and len(i))])
        except Exception as e:
            print('Failed getting panel names, fallback to standard names')
        # Load default panels if they could not be retrieved
        if len(panels) < 2:
            panels = [
                'applications',
                'background',
                'bluetooth',
                'color',
                'connectivity',
                'datetime',
                'default-apps',
                'diagnostics',
                'display',
                'info-overview',
                'keyboard',
                'location',
                'lock',
                'mouse',
                'network',
                'notifications',
                'online-accounts',
                'power',
                'printers',
                'region',
                'removable-media',
                'search',
                'sharing',
                'sound',
                'thunderbolt',
                'ubuntu',
                'universal-access',
                'usage',
                'user-accounts',
                'wacom',
                'wifi']

        for p in panels:
            # Capitalize words to form item title
            title = " ".join(w.capitalize() for w in p.split('-'))
            if(p in dictPanels):
                title = dictPanels.get(p)
            title = __(title)
            items_cache.append(create_item(title, p, p, title, p))

        super(GnomeControlExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # Get query
        term = (event.get_argument() or '').lower()

        items = []

        # Display all items when query empty
        if term == "":
            items = sorted([i for i in items_cache],
                           key=sort_by_usage,
                           reverse=True)
        # Only display items containing query substring
        else:
            items = sorted([i for i in items_cache if term in i._name.lower()],
                           key=sort_by_usage,
                           reverse=True)
        return RenderResultListAction(items[:8])


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        global usage_cache
        # Get query
        data = event.get_data()
        b = data['id']
        # Check usage and increment
        if b in usage_cache:
            usage_cache[b] = usage_cache[b]+1
        else:
            usage_cache[b] = 1
        # Update usage JSON
        with open(usage_db, 'w') as db:
            db.write(json.dumps(usage_cache, indent=2))

        return RunScriptAction('#!/usr/bin/env bash\n{} {}\n'.format(gcpath, b), None).run()


def create_item(name, icon, keyword, description, on_enter):
    return ExtensionResultItem(
            name=name,
            icon=get_icon(icon),
            on_enter=ExtensionCustomAction(
                 {'id': on_enter})
            )


def sort_by_usage(i):
    global usage_cache
    # Convert item name to ID format
    j = i._name.lower().replace(' ', '-')
    # Return score according to usage
    if j in usage_cache:
        return usage_cache[j]
    # Default is 0 (no usage rank / unused)
    return 0


if __name__ == '__main__':
    GnomeControlExtension().run()
