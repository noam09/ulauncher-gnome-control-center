"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import os
import locale
import gettext

dir_path = os.path.dirname(os.path.realpath(__file__))
current_locale, encoding = locale.getdefaultlocale()
trans = gettext.translation('gnome-control-center-2.0', None, [current_locale], fallback=True)
trans.install()

__= trans.gettext
