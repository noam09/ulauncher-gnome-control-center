"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import logging
import subprocess
import distutils.spawn
from xdg import IconTheme

glob = {
  'theme': 1
}

altName = {
  'universal-access': 'accessibility',
  'datetime': 'preferences-system-time',
  'connectivity': 'globe',
  'background': 'wallpaper',
  'applications': 'apps',
  'user-accounts': 'system-users',
  'default-apps': 'starred',
  'diagnostics': 'help',
  'location': 'mark-location',
  'mouse': 'input-mouse',
  'sound': 'music',
  'ubuntu': 'ubuntu-panel',
  'printers': 'printer',
  'info-overview': 'details',
  'lock': 'lock-screen',
  'wifi': 'network-wireless',
  'wacom': 'input-tablet',
  'region': 'locale',
  'removable-media': 'media-removable'
}

def get_icon(icon):
  return  IconTheme.getIconPath("preferences-desktop-%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath("preferences-system-%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath("preferences-%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath("%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath("preferences-desktop-%s-symbolic" % (altName.get(icon) or ''), theme=get_selected_theme()) or\
          IconTheme.getIconPath("preferences-system-%s-symbolic" % (altName.get(icon) or ''), theme=get_selected_theme()) or\
          IconTheme.getIconPath("preferences-%s-symbolic" % (altName.get(icon) or ''), theme=get_selected_theme()) or\
          IconTheme.getIconPath("system-%s-symbolic" % (altName.get(icon) or ''), theme=get_selected_theme()) or\
          IconTheme.getIconPath("system-%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath("%s-symbolic" % (altName.get(icon) or ''), theme=get_selected_theme()) or\
          IconTheme.getIconPath("%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath("gnome-%s-symbolic" % (altName.get(icon) or ''), theme=get_selected_theme()) or\
          IconTheme.getIconPath("gnome-%s-symbolic" % icon, theme=get_selected_theme()) or\
          IconTheme.getIconPath(altName.get(icon) or '', theme=get_selected_theme()) or\
          IconTheme.getIconPath(icon, theme=get_selected_theme()) or\
          'images/{}.svg'.format(icon)

def get_selected_theme():
  if (glob.get('theme') is 1):
    glob['theme'] = try_get_xfce_default_theme() or\
            try_get_cinnamon_default_theme() or\
            try_get_mate_default_theme() or\
            try_get_gnome_default_theme()
  return glob['theme']

def try_get_gnome_default_theme():
  return try_get_gsetting_default_theme("gnome")
def try_get_cinnamon_default_theme():
  return try_get_gsetting_default_theme("cinnamon")
def try_get_mate_default_theme():
  return try_get_gsetting_default_theme("mate")

def try_get_gsetting_default_theme(type):
  """Try to get the default icon theme

  Args:
      type (str): the gsetting address to look for

  Returns:
      str|None: The icon theme or None if not found
  """
  try:
    gspath = distutils.spawn.find_executable('gsettings')
    if gspath is None or gspath == '':
      return None
    theme = subprocess.check_output([gspath, "get", "org.%s.desktop.interface" % type, "icon-theme"]).decode().strip().strip("'").strip()
    if(theme == ""):
      return None
    return theme.strip()
  except Exception as e:
    return None

def try_get_xfce_default_theme():
  """Try to get the default icon theme

  Args:
      type (str): the gsetting address to look for

  Returns:
      str|None: The icon theme or None if not found
  """
  try:
    xfconf = distutils.spawn.find_executable('xfconf-query')
    if xfconf is None or xfconf == '':
      return None
    theme = subprocess.check_output([xfconf, "-lvc", "xsettings", "-p", "/Net/ThemeName"]).decode()
    if(theme == ""):
      return None
    return theme
  except Exception as e:
    return None