# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os
import gettext

PluginLanguageDomain = 'OpenVisionSkinTools'
PluginLanguagePath = 'Extensions/OpenVisionSkinTools/locale'


def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    print('[OpenVisionSkinTools] set language to ', lang)
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    t = gettext.dgettext(PluginLanguageDomain, txt)
    if t == txt:
        print('[%s] fallback to default translation for %s' % (PluginLanguageDomain, txt))
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
