# -*- coding: utf-8 -*-

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

# for localized messages
from __init__ import _
from enigma import eTimer, getDesktop
from Components.ActionMap import ActionMap
from Components.config import *
from Tools.Directories import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Plugins.Plugin import PluginDescriptor
from Screens.SkinSelector import SkinSelector
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.LoadPixmap import LoadPixmap
from Tools.WeatherID import get_woeid_from_yahoo
from os import listdir, remove, rename, system, path, symlink, chdir, makedirs, mkdir
import shutil
import re

cur_skin = config.skin.primary_skin.value.replace('skin.xml', '').replace('/', '')

reswidth = getDesktop(0).size().width()

config.plugins.OpenVision = ConfigSubsection()
config.plugins.OpenVision.refreshInterval = ConfigNumber(default=10)
config.plugins.OpenVision.woeid = ConfigNumber(default=638242)
config.plugins.OpenVision.tempUnit = ConfigSelection(default="Celsius", choices=[
                                ("Celsius", _("Celsius")),
                                ("Fahrenheit", _("Fahrenheit"))
                                ])

REDC = '\033[31m'
ENDC = '\033[m'


def cprint(text):
    print(REDC + text + ENDC)


def Plugins(**kwargs):
    return [PluginDescriptor(name=_("OpenVision Skin Tools"), description=_("OpenVision Skin Tools"), where=PluginDescriptor.WHERE_MENU, fnc=menu)]


def menu(menuid, **kwargs):
    if config.skin.primary_skin.value == "AtileHD/skin.xml" or config.skin.primary_skin.value == "iFlatFHD/skin.xml" or config.skin.primary_skin.value == "Multibox/skin.xml":
        if menuid == "mainmenu":
            return [(_("Setup -") + " " + cur_skin, main, "Menu", 40)]
    return []


def main(session, **kwargs):
    cprint("Opening Menu ...")
    session.open(OpenVision_Config)


def isInteger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class WeatherLocationChoiceList(Screen):
    skin = """
		<screen name="WeatherLocationChoiceList" position="center,center" size="1280,720" title="Location list" >
			<widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" transparent="1" />
			<widget name="choicelist" position="70,115" size="700,480" scrollbarMode="showOnDemand" scrollbarWidth="6" transparent="1" />
			<eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="red" />
			<eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="green" />
			<eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="yellow" />
			<eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="blue" />
			<widget name="key_red" position="70,635" size="260,25" zPosition="1" font="Regular;20" horizontalAlignment="left" foregroundColor="foreground" transparent="1" />
			<widget name="key_green" position="365,635" size="260,25" zPosition="1" font="Regular;20" horizontalAlignment="left" foregroundColor="foreground" transparent="1" />
		</screen>
		"""

    def __init__(self, session, location_list):
        self.session = session
        self.location_list = location_list
        list = []
        Screen.__init__(self, session)
        self.title = _("Location list")
        self["choicelist"] = MenuList(list)
        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("OK"))
        self["myActionMap"] = ActionMap(["SetupActions", "ColorActions"],
        {
                "ok": self.keyOk,
                "green": self.keyOk,
                "cancel": self.keyCancel,
                "red": self.keyCancel,
        }, -1)
        self.createChoiceList()

    def createChoiceList(self):
        list = []
        print(self.location_list)
        for x in self.location_list:
            list.append((str(x[1]), str(x[0])))
        self["choicelist"].l.setList(list)

    def keyOk(self):
        returnValue = self["choicelist"].l.getCurrentSelection()[1]
        if returnValue is not None:
            self.close(returnValue)
        else:
            self.keyCancel()

    def keyCancel(self):
        self.close(None)


class OpenVision_Config(Screen, ConfigListScreen):
    if reswidth == 1920:
        skin = """
			<screen name="OpenVision_Config" backgroundColor="#80000000" flags="wfNoBorder" position="0,0" size="1920,1080" title="OpenVision Setup">
  				<eLabel text="Choose yout style" position="18,18" size="1300,50" font="Regular;40" verticalAlignment="center" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1"/>
  				<eLabel text="Preview" position="1266,550" size="610,70" font="Regular;40" horizontalAlignment="center" verticalAlignment="center" foregroundColor="#0000ff00" zPosition="2"/>
  				<eLabel text="* OpenVision Skin Tools Mod RAED *" position="585,20" size="860,50" font="Regular;35" verticalAlignment="center" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1" horizontalAlignment="center"/>
  				<widget name="config" position="50,130" size="1120,650" font="Regular;36" itemHeight="50" enableWrapAround="1" backgroundColor="#80000000" transparent="1"/>
  				<eLabel text="/ Save" position="380,1000" size="160,70" font="Regular;35" horizontalAlignment="center" backgroundColor="#80000000" transparent="1" verticalAlignment="center"/>
  				<eLabel text="Yellow button Press to select the skin parts" position="92,900" size="1020,45" font="Regular;36" backgroundColor="#80000000" transparent="1" verticalAlignment="center" foregroundColor="default"/>
  				<widget name="Picture" position="1265,630" size="612,344" alphaTest="on"/>
  				<ePixmap pixmap="~/pic/key_menu.png" position="50,823" size="103,35" zPosition="10" transparent="1"/>
  				<eLabel text="Weather Setup .... Press Menu Button to get to the weather plugin" position="170,820" size="1090,45" font="Regular;36" backgroundColor="#80000000" transparent="1" verticalAlignment="center" foregroundColor="default" zPosition="2"/>
  				<eLabel position="23,1073" size="290,5" zPosition="-10" backgroundColor="#00ff0000"/>
  				<eLabel position="280,1073" size="290,5" zPosition="-10" backgroundColor="#0000ff00"/>
  				<eLabel position="640,1073" size="290,5" zPosition="-10" backgroundColor="#00ffff00"/>
  				<eLabel position="92,948" size="290,5" zPosition="-10" backgroundColor="#00ffff00"/>
  				<widget name="key_red" position="40,1000" size="227,70" zPosition="1" verticalAlignment="center" font="Regular;35" backgroundColor="#80000000" transparent="1" horizontalAlignment="center"/>
  				<widget name="key_green" position="334,1000" size="100,70" zPosition="1" verticalAlignment="center" font="Regular;35" backgroundColor="#80000000" transparent="1"/>
  				<widget name="key_yellow" position="640,1000" size="290,70" zPosition="1" verticalAlignment="center" font="Regular;35" backgroundColor="#80000000" transparent="1" horizontalAlignment="center" borderWidth="-1"/>
  				<widget source="global.CurrentTime" render="Label" position="1322,22" size="585,50" font="Regular;40" horizontalAlignment="right" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1">
   					 <convert type="ClockToText">FullDate</convert>
  				</widget>
  				<eLabel backgroundColor="#0066ccff" position="1223,103" size="674,423" zPosition="-15"/>
  				<eLabel backgroundColor="#0066ccff" position="1225,483" size="670,1" zPosition="6"/>
  				<eLabel backgroundColor="#80000000" position="1225,105" size="671,420" zPosition="-10"/>
  				<widget position="1225,105" size="671,377" source="session.VideoPicture" render="Pig" zPosition="3" backgroundColor="#ff000000"/>
  				<widget position="1225,484" size="670,40" source="session.CurrentService" render="Label" font="Regular;36" foregroundColor="#0066ccff" backgroundColor="#80000000" transparent="1" verticalAlignment="center" horizontalAlignment="center" noWrap="1" zPosition="5">
   					 <convert type="ServiceName">Name</convert>
  				</widget>
			</screen>
		"""
    else:
        skin = """
			<screen name="OpenVision_Config" backgroundColor="#80000000" flags="wfNoBorder" position="0,0" size="1280,720" title="OpenVision Setup">
  				<eLabel text="Choose yout style" position="15,8" size="400,35" font="Regular;25" verticalAlignment="center" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1"/>
  				<eLabel text="Preview" position="813,375" size="446,40" font="Regular;25" horizontalAlignment="center" verticalAlignment="center" foregroundColor="#0000ff00" zPosition="2"/>
  				<eLabel text="* OpenVision Skin Tools Mod RAED *" position="359,8" size="568,35" font="Regular;25" verticalAlignment="center" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1" horizontalAlignment="center"/>
  				<widget name="config" position="25,58" size="775,502" font="Regular;25" itemHeight="50" enableWrapAround="1" backgroundColor="#80000000" transparent="1"/>
  				<eLabel text="/ Save" position="297,680" size="160,35" font="Regular;25" horizontalAlignment="center" backgroundColor="#80000000" transparent="1" verticalAlignment="center"/>
  				<eLabel text="Yellow button Press to select the skin parts" position="17,627" size="668,29" font="Regular;25" backgroundColor="#80000000" transparent="1" verticalAlignment="center" foregroundColor="default"/>
  				<widget name="Picture" position="809,437" size="452,237" alphaTest="on"/>
  				<ePixmap pixmap="~/pic/key_menu.png" position="20,583" size="103,35" zPosition="10" transparent="1"/>
  				<eLabel text="Weather Setup .... Press Menu Button to get to the weather plugin" position="125,587" size="559,25" font="Regular;25" backgroundColor="#80000000" transparent="1" verticalAlignment="center" foregroundColor="default" zPosition="2"/>
  				<eLabel position="2,715" size="230,5" zPosition="-10" backgroundColor="#00ff0000"/>
  				<eLabel position="235,715" size="230,5" zPosition="-10" backgroundColor="#0000ff00"/>
  				<eLabel position="470,715" size="230,5" zPosition="-10" backgroundColor="#00ffff00"/>
  				<eLabel position="16,661" size="151,7" zPosition="-10" backgroundColor="#00ffff00"/>
  				<widget name="key_red" position="25,680" size="188,35" zPosition="1" verticalAlignment="center" font="Regular;25" backgroundColor="#80000000" transparent="1"/>
  				<widget name="key_green" position="289,680" size="100,35" zPosition="1" verticalAlignment="center" font="Regular;25" backgroundColor="#80000000" transparent="1"/>
  				<widget name="key_yellow" position="474,680" size="221,35" zPosition="1" verticalAlignment="center" font="Regular;25" backgroundColor="#80000000" transparent="1"/>
  				<widget source="global.CurrentTime" render="Label" position="941,8" size="326,35" font="Regular;25" horizontalAlignment="right" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1">
   					 <convert type="ClockToText">FullDate</convert>
  				</widget>
  				<eLabel backgroundColor="#0066ccff" position="813,58" size="446,246" zPosition="-15"/>
  				<eLabel backgroundColor="#0066ccff" position="813,308" size="446,1" zPosition="6"/>
  				<eLabel backgroundColor="background" position="813,58" size="446,246" zPosition="-10"/>
  				<widget position="815,80" size="441,199" source="session.VideoPicture" render="Pig" zPosition="3" backgroundColor="#ff000000"/>
  				<widget position="813,309" size="446,35" source="session.CurrentService" render="Label" font="Regular;25" foregroundColor="#0066ccff" backgroundColor="#80000000" transparent="1" verticalAlignment="center" horizontalAlignment="center" noWrap="1" zPosition="5">
   					 <convert type="ServiceName">Name</convert>
  				</widget>
			</screen>
		"""

    def __init__(self, session, args=0):
        self.session = session
        self.skin_lines = []
        self.changed_screens = False
        Screen.__init__(self, session)
        self.skin_path = resolveFilename(SCOPE_PLUGINS, "Extensions/OpenVisonSkinTools")

        self.start_skin = config.skin.primary_skin.value

        if self.start_skin != "skin.xml":
            self.getInitConfig()

        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)

        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("OK"))
        self["key_yellow"] = Label()
        self["key_blue"] = Label(_("About"))
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                {
                        "green": self.keyGreen,
                        "red": self.cancel,
                        "yellow": self.keyYellow,
                        #"blue": self.about,
                        "cancel": self.cancel,
                        "ok": self.keyOk,
                        "menu": self.setWeather,
                }, -2)

        self["Picture"] = Pixmap()

        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        self.createConfigList()
        if self.start_skin == "skin.xml":
            self.onLayoutFinish.append(self.openSkinSelectorDelayed)
        else:
            self.createConfigList()

    def setWeather(self):
        try:
            from Plugins.Extensions.WeatherPlugin2.setup import MSNWeatherPluginEntriesListConfigScreen
            self.session.open(MSNWeatherPluginEntriesListConfigScreen)
        except:
            self.session.open(MessageBox, _("'weatherplugin' is not installed!"), MessageBox.TYPE_INFO)

    def getInitConfig(self):

        global cur_skin

        self.title = _("%s Setup" % cur_skin)
        self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
        cprint("self.skin_base_dir=%s, skin=%s, currentSkin=%s" % (self.skin_base_dir, config.skin.primary_skin.value, cur_skin))

        self.default_font_file = "fonts_Original.xml"
        self.default_color_file = "colors_Original.xml"
        self.default_sb_file = "sb_Original.xml"

        self.default_clock_file = "clock_Original.xml"
        self.default_infobar_file = "infobar_Original.xml"
        self.default_background_file = "background_Original.xml"
        self.default_sib_file = "sib_Original.xml"
        self.default_ch_se_file = "ch_se_Original.xml"
        self.default_ev_file = "ev_Original.xml"
        self.default_emcsel_file = "emcsel_Original.xml"
        self.default_movsel_file = "movsel_Original.xml"
        self.default_ul_file = "ul_Original.xml"

        self.font_file = "skin_user_fonts.xml"
        self.color_file = "skin_user_colors.xml"
        self.sb_file = "skin_user_sb.xml"
        self.clock_file = "skin_user_clock.xml"
        self.infobar_file = "skin_user_infobar.xml"
        self.background_file = "skin_user_background.xml"
        self.sib_file = "skin_user_sib.xml"
        self.ch_se_file = "skin_user_ch_se.xml"
        self.ev_file = "skin_user_ev.xml"
        self.emcsel_file = "skin_user_emcsel.xml"
        self.movsel_file = "skin_user_movsel.xml"
        self.ul_file = "skin_user_ul.xml"

        # font
        current, choices = self.getSettings(self.default_font_file, self.font_file)
        self.OpenVision_font = NoSave(ConfigSelection(default=current, choices=choices))
        # color
        current, choices = self.getSettings(self.default_color_file, self.color_file)
        self.OpenVision_color = NoSave(ConfigSelection(default=current, choices=choices))
        # sb
        current, choices = self.getSettings(self.default_sb_file, self.sb_file)
        self.OpenVision_sb = NoSave(ConfigSelection(default=current, choices=choices))
        # clock
        current, choices = self.getSettings(self.default_clock_file, self.clock_file)
        self.OpenVision_clock = NoSave(ConfigSelection(default=current, choices=choices))
        # infobar
        current, choices = self.getSettings(self.default_infobar_file, self.infobar_file)
        self.OpenVision_infobar = NoSave(ConfigSelection(default=current, choices=choices))
        # background
        current, choices = self.getSettings(self.default_background_file, self.background_file)
        self.OpenVision_background = NoSave(ConfigSelection(default=current, choices=choices))
        # sib
        current, choices = self.getSettings(self.default_sib_file, self.sib_file)
        self.OpenVision_sib = NoSave(ConfigSelection(default=current, choices=choices))
        # ch_se
        current, choices = self.getSettings(self.default_ch_se_file, self.ch_se_file)
        self.OpenVision_ch_se = NoSave(ConfigSelection(default=current, choices=choices))
        # ev
        current, choices = self.getSettings(self.default_ev_file, self.ev_file)
        self.OpenVision_ev = NoSave(ConfigSelection(default=current, choices=choices))
        # emcsel
        current, choices = self.getSettings(self.default_emcsel_file, self.emcsel_file)
        self.OpenVision_emcsel = NoSave(ConfigSelection(default=current, choices=choices))
        # movsel
        current, choices = self.getSettings(self.default_movsel_file, self.movsel_file)
        self.OpenVision_movsel = NoSave(ConfigSelection(default=current, choices=choices))
        # ul
        current, choices = self.getSettings(self.default_ul_file, self.ul_file)
        self.OpenVision_ul = NoSave(ConfigSelection(default=current, choices=choices))
        # myatile
        myatile_active = self.getmyAtileState()
        self.OpenVision_active = NoSave(ConfigYesNo(default=myatile_active))
        self.OpenVision_fake_entry = NoSave(ConfigNothing())

    def getSettings(self, default_file, user_file):
        default = ("default", _("Default"))
        styp = default_file.replace('_Original.xml', '')
        search_str = '%s_' % styp

        # possible setting
        choices = []
        files = listdir(self.skin_base_dir)
        if path.exists(self.skin_base_dir + 'allScreens/%s/' % styp):
            files += listdir(self.skin_base_dir + 'allScreens/%s/' % styp)
        for f in sorted(files, key=str.lower):
            if f.endswith('.xml') and f.startswith(search_str):
                friendly_name = f.replace(search_str, "").replace(".xml", "").replace("_", " ")
                if path.exists(self.skin_base_dir + 'allScreens/%s/%s' % (styp, f)):
                    choices.append((self.skin_base_dir + 'allScreens/%s/%s' % (styp, f), friendly_name))
                else:
                    choices.append((self.skin_base_dir + f, friendly_name))
        choices.append(default)

        # current setting
        myfile = self.skin_base_dir + user_file
        current = ''
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + default_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink(default_file, user_file)
            elif path.exists(self.skin_base_dir + 'allScreens/%s/%s' % (styp, default_file)):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink(self.skin_base_dir + 'allScreens/%s/%s' % (styp, default_file), user_file)
            else:
                current = None
        if current is None:
            current = default
        else:
            filename = path.realpath(myfile)
            friendly_name = path.basename(filename).replace(search_str, "").replace(".xml", "").replace("_", " ")
            current = (filename, friendly_name)

        return current[0], choices

        #SELECTED Skins folder - We use different folder name (more meaningfull) for selections
        if path.exists(self.skin_base_dir + "mySkin_off"):
            if not path.exists(self.skin_base_dir + "OpenVision_Selections"):
                chdir(self.skin_base_dir)
                try:
                    rename("mySkin_off", "OpenVision_Selections")
                except:
                    pass

    def createConfigList(self):
        self.set_font = getConfigListEntry(_("Fonts:"), self.OpenVision_font)
        self.set_color = getConfigListEntry(_("Style:"), self.OpenVision_color)
        self.set_sb = getConfigListEntry(_("ColorSelectedBackground:"), self.OpenVision_sb)
        self.set_clock = getConfigListEntry(_("Clock:"), self.OpenVision_clock)
        self.set_infobar = getConfigListEntry(_("Infobar:"), self.OpenVision_infobar)
        self.set_background = getConfigListEntry(_("Background:"), self.OpenVision_background)
        self.set_sib = getConfigListEntry(_("Secondinfobar:"), self.OpenVision_sib)
        self.set_ch_se = getConfigListEntry(_("Channelselection:"), self.OpenVision_ch_se)
        self.set_ev = getConfigListEntry(_("Eventview:"), self.OpenVision_ev)
        self.set_emcsel = getConfigListEntry(_("EMC_Selection:"), self.OpenVision_emcsel)
        self.set_movsel = getConfigListEntry(_("Movie_Selection:"), self.OpenVision_movsel)
        self.set_ul = getConfigListEntry(_("Userlogo:"), self.OpenVision_ul)
        self.set_myatile = getConfigListEntry(_("Enable %s pro:") % cur_skin, self.OpenVision_active)
        self.set_new_skin = getConfigListEntry(_("Change skin"), ConfigNothing())
        self.find_woeid = getConfigListEntry(_("Search weather location ID"), ConfigNothing())
        self.LackOfFile = ''
        self.list = []
        self.list.append(self.set_myatile)
        if len(self.OpenVision_font.choices) > 1:
            self.list.append(self.set_font)
        if len(self.OpenVision_color.choices) > 1:
            self.list.append(self.set_color)
        if len(self.OpenVision_sb.choices) > 1:
            self.list.append(self.set_sb)
        if len(self.OpenVision_clock.choices) > 1:
            self.list.append(self.set_clock)
        if len(self.OpenVision_infobar.choices) > 1:
            self.list.append(self.set_infobar)
        if len(self.OpenVision_background.choices) > 1:
            self.list.append(self.set_background)
        if len(self.OpenVision_sib.choices) > 1:
            self.list.append(self.set_sib)
        if len(self.OpenVision_ch_se.choices) > 1:
            self.list.append(self.set_ch_se)
        if len(self.OpenVision_ev.choices) > 1:
            self.list.append(self.set_ev)
        if len(self.OpenVision_emcsel.choices) > 1:
            self.list.append(self.set_emcsel)
        if len(self.OpenVision_movsel.choices) > 1:
            self.list.append(self.set_movsel)
        if len(self.OpenVision_ul.choices) > 1:
            self.list.append(self.set_ul)
        self.list.append(self.set_new_skin)
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if self.OpenVision_active.value:
            self["key_yellow"].setText("%s pro" % cur_skin)
        else:
            self["key_yellow"].setText("")

    def changedEntry(self):
        if self["config"].getCurrent() == self.set_font:
            self.setPicture(self.OpenVision_font.value)
        elif self["config"].getCurrent() == self.set_color:
            self.setPicture(self.OpenVision_color.value)
        elif self["config"].getCurrent() == self.set_sb:
            self.setPicture(self.OpenVision_sb.value)
        elif self["config"].getCurrent() == self.set_clock:
            self.setPicture(self.OpenVision_clock.value)
        elif self["config"].getCurrent() == self.set_infobar:
            self.setPicture(self.OpenVision_infobar.value)
        elif self["config"].getCurrent() == self.set_background:
            self.setPicture(self.OpenVision_background.value)
        elif self["config"].getCurrent() == self.set_sib:
            self.setPicture(self.OpenVision_sib.value)
        elif self["config"].getCurrent() == self.set_ch_se:
            self.setPicture(self.OpenVision_ch_se.value)
        elif self["config"].getCurrent() == self.set_ev:
            self.setPicture(self.OpenVision_ev.value)
        elif self["config"].getCurrent() == self.set_emcsel:
            self.setPicture(self.OpenVision_emcsel.value)
        elif self["config"].getCurrent() == self.set_movsel:
            self.setPicture(self.OpenVision_movsel.value)
        elif self["config"].getCurrent() == self.set_ul:
            self.setPicture(self.OpenVision_ul.value)
        elif self["config"].getCurrent() == self.set_myatile:
            if self.OpenVision_active.value:
                self["key_yellow"].setText("%s pro" % cur_skin)
            else:
                self["key_yellow"].setText("")

    def selectionChanged(self):
        if self["config"].getCurrent() == self.set_font:
            self.setPicture(self.OpenVision_font.value)
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.OpenVision_color.value)
        elif self["config"].getCurrent() == self.set_sb:
            self.setPicture(self.OpenVision_sb.value)
        elif self["config"].getCurrent() == self.set_clock:
            self.setPicture(self.OpenVision_clock.value)
        elif self["config"].getCurrent() == self.set_infobar:
            self.setPicture(self.OpenVision_infobar.value)
        elif self["config"].getCurrent() == self.set_background:
            self.setPicture(self.OpenVision_background.value)
        elif self["config"].getCurrent() == self.set_sib:
            self.setPicture(self.OpenVision_sib.value)
        elif self["config"].getCurrent() == self.set_ch_se:
            self.setPicture(self.OpenVision_ch_se.value)
        elif self["config"].getCurrent() == self.set_ev:
            self.setPicture(self.OpenVision_ev.value)
        elif self["config"].getCurrent() == self.set_emcsel:
            self.setPicture(self.OpenVision_emcsel.value)
        elif self["config"].getCurrent() == self.set_movsel:
            self.setPicture(self.OpenVision_movsel.value)
        elif self["config"].getCurrent() == self.set_ul:
            self.setPicture(self.OpenVision_ul.value)
        else:
            self["Picture"].hide()

    def cancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"), MessageBox.TYPE_YESNO, default=False)
        else:
            for x in self["config"].list:
                x[1].cancel()
            if self.changed_screens:
                self.restartGUI()
            else:
                self.close()

    def cancelConfirm(self, result):
        if result is None or result is False:
            cprint("[%s]: Cancel confirmed." % cur_skin)
        else:
            cprint("[%s]: Cancel confirmed. Config changes will be lost." % cur_skin)
            for x in self["config"].list:
                x[1].cancel()
            self.close()

    def getmyAtileState(self):
        chdir(self.skin_base_dir)
        if path.exists("mySkin"):
            return True
        else:
            return False

    def setPicture(self, f):
        pic = f.split('/')[-1].replace(".xml", ".png")
        preview = self.skin_base_dir + "preview/preview_" + pic
        if path.exists(preview):
            self["Picture"].instance.setPixmapFromFile(preview)
            self["Picture"].show()
        else:
            self["Picture"].hide()

    def keyYellow(self):
        if self.OpenVision_active.value:
            self.session.openWithCallback(self.OpenVisionScreenCB, OpenVisionScreens)
        else:
            self["config"].setCurrentIndex(0)

    def keyOk(self):
        sel = self["config"].getCurrent()
        if sel is not None and sel == self.set_new_skin:
            self.openSkinSelector()
        elif sel is not None and sel == self.find_woeid:
            self.session.openWithCallback(self.search_weather_id_callback, InputBox, title=_("Please enter search string for your location"), text="")
        else:
            self.keyGreen()

    def openSkinSelector(self):
        self.session.openWithCallback(self.skinChanged, SkinSelector)

    def openSkinSelectorDelayed(self):
        self.delaytimer = eTimer()
        self.delaytimer.callback.append(self.openSkinSelector)
        self.delaytimer.start(200, True)

    def search_weather_id_callback(self, res):
        if res:
            id_dic = get_woeid_from_yahoo(res)
            if 'error' in id_dic:
                error_txt = id_dic['error']
                self.session.open(MessageBox, _("Sorry, there was a problem:") + "\n%s" % error_txt, MessageBox.TYPE_ERROR)
            elif 'count' in id_dic:
                result_no = int(id_dic['count'])
                location_list = []
                for i in range(0, result_no):
                    location_list.append(id_dic[i])
                self.session.openWithCallback(self.select_weather_id_callback, WeatherLocationChoiceList, location_list)

    def select_weather_id_callback(self, res):
        if res and isInteger(res):
            print(res)
            config.plugins.OpenVision.woeid.value = int(res)

    def skinChanged(self, ret=None):
        global cur_skin
        cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')
        if cur_skin == "skin.xml":
            self.restartGUI()
        else:
            self.getInitConfig()
            self.createConfigList()

    def keyGreen(self):
        if self["config"].isChanged():
            for x in self["config"].list:
                x[1].save()
            chdir(self.skin_base_dir)

            # font
            self.makeSettings(self.OpenVision_font, self.font_file)
            # color
            self.makeSettings(self.OpenVision_color, self.color_file)
            # sb
            self.makeSettings(self.OpenVision_sb, self.sb_file)
            # clock
            self.makeSettings(self.OpenVision_clock, self.clock_file)
            # infobar
            self.makeSettings(self.OpenVision_infobar, self.infobar_file)
            # background
            self.makeSettings(self.OpenVision_background, self.background_file)
            # sib
            self.makeSettings(self.OpenVision_sib, self.sib_file)
            # ch_se
            self.makeSettings(self.OpenVision_ch_se, self.ch_se_file)
            # ev
            self.makeSettings(self.OpenVision_ev, self.ev_file)
            # emcsel
            self.makeSettings(self.OpenVision_emcsel, self.emcsel_file)
            # movsel
            self.makeSettings(self.OpenVision_movsel, self.movsel_file)
            # ul
            self.makeSettings(self.OpenVision_ul, self.ul_file)
            #Pro SCREENS
            if not path.exists("mySkin_off"):
                mkdir("mySkin_off")
                cprint("makedir mySkin_off")
            if self.OpenVision_active.value:
                if not path.exists("mySkin") and path.exists("mySkin_off"):
                    symlink("mySkin_off", "mySkin")
            else:
                if path.exists("mySkin"):
                    if path.exists("mySkin_off"):
                        if path.islink("mySkin"):
                            remove("mySkin")
                        else:
                            shutil.rmtree("mySkin")
                    else:
                        rename("mySkin", "mySkin_off")
            self.update_user_skin()
            self.restartGUI()
        elif config.skin.primary_skin.value != self.start_skin:
            self.update_user_skin()
            self.restartGUI()
        else:
            if self.changed_screens:
                self.update_user_skin()
                self.restartGUI()
            else:
                self.close()

    def makeSettings(self, config_entry, user_file):
        if path.exists(user_file):
            remove(user_file)
        if path.islink(user_file):
            remove(user_file)
        if config_entry.value != 'default':
            symlink(config_entry.value, user_file)

    def OpenVisionScreenCB(self):
        self.changed_screens = True
        self["config"].setCurrentIndex(0)

    def restartGUI(self):
        myMessage = ''
        if self.LackOfFile != '':
            cprint("missing components: %s" % self.LackOfFile)
            myMessage += _("Missing components found: %s\n\n") % self.LackOfFile
            myMessage += _("Skin will NOT work properly!!!\n\n")
        restartbox = self.session.openWithCallback(self.restartGUIcb, MessageBox, _("Restart necessary, restart GUI now?"), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_("Message"))

    def about(self):
        self.session.open(OpenVision_About)

    def restartGUIcb(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def update_user_skin(self):
        global cur_skin
        user_skin_file = resolveFilename(SCOPE_CONFIG, 'skin_user_' + cur_skin + '.xml')
        if path.exists(user_skin_file):
            remove(user_skin_file)
        cprint("update_user_skin.self.OpenVision_active.value")
        user_skin = ""
        if path.exists(self.skin_base_dir + self.font_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.font_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.color_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.color_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.sb_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.sb_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.clock_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.clock_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.infobar_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.infobar_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.background_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.background_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.sib_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.sib_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.ch_se_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.ch_se_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.ev_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.ev_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.emcsel_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.emcsel_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + self.ul_file):
            user_skin = user_skin + self.readXMLfile(self.skin_base_dir + self.ul_file, 'ALLSECTIONS')
        if path.exists(self.skin_base_dir + 'mySkin'):
            for f in listdir(self.skin_base_dir + "mySkin/"):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + "mySkin/" + f, 'screen')
        if user_skin != '':
            user_skin = "<skin>\n" + user_skin
            user_skin = user_skin + "</skin>\n"
            with open(user_skin_file, "w") as myFile:
                cprint("update_user_skin.self.OpenVision_active.value write myFile")
                myFile.write(user_skin)
                myFile.flush()
                myFile.close()
        #checking if all renderers converters are in system
        self.checkComponent(user_skin, 'render', resolveFilename(SCOPE_PLUGINS, '../Components/Renderer/'))
        self.checkComponent(user_skin, 'Convert', resolveFilename(SCOPE_PLUGINS, '../Components/Converter/'))
        self.checkComponent(user_skin, 'pixmap', resolveFilename(SCOPE_SKINS, ''))

    def checkComponent(self, myContent, look4Component, myPath): #look4Component=render|
        def updateLackOfFile(name, mySeparator=', '):
            cprint("Missing component found:%s\n" % name)
            if self.LackOfFile == '':
                self.LackOfFile = name
            else:
                self.LackOfFile += mySeparator + name

        r = re.findall(r' %s="([a-zA-Z0-9_/\.]+)" ' % look4Component, myContent)
        r = list(set(r)) #remove duplicates, no need to check for the same component several times

        cprint("Found %s:\n" % (look4Component))
        print(r)
        if r:
            for myComponent in set(r):
                if look4Component == 'pixmap':
                    if myComponent.startswith('/'):
                        if not path.exists(myComponent):
                            updateLackOfFile(myComponent, '\n')
                    else:
                        if not path.exists(myPath + myComponent):
                            updateLackOfFile(myComponent)
                else:
                    if not path.exists(myPath + myComponent + ".pyo") and not path.exists(myPath + myComponent + ".py"):
                        updateLackOfFile(myComponent)
        return

    def readXMLfile(self, XMLfilename, XMLsection): #sections:ALLSECTIONS|fonts|
        myPath = path.realpath(XMLfilename)
        if not path.exists(myPath):
            remove(XMLfilename)
            return ''
        filecontent = ''
        if XMLsection == 'ALLSECTIONS':
            sectionmarker = True
        else:
            sectionmarker = False
        with open(XMLfilename, "r") as myFile:
            for line in myFile:
                if line.find('<skin>') >= 0 or line.find('</skin>') >= 0:
                    continue
                if line.find('<%s' % XMLsection) >= 0 and sectionmarker == False:
                    sectionmarker = True
                elif line.find('</%s>' % XMLsection) >= 0 and sectionmarker == True:
                    sectionmarker = False
                    filecontent = filecontent + line
                if sectionmarker == True:
                    filecontent = filecontent + line
            myFile.close()
        return filecontent


class OpenVision_About(Screen):

    def __init__(self, session, args=0):
        self.session = session
        Screen.__init__(self, session)
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
                {
                        "cancel": self.cancel,
                        "ok": self.keyOk,
                }, -2)

    def keyOk(self):
        self.close()

    def cancel(self):
        self.close()


class OpenVisionScreens(Screen):
    if reswidth == 1920:
        skin = """
			<screen name="OpenVisionScreens" backgroundColor="#80000000" flags="wfNoBorder" position="0,0" size="1920,1080" title="OpenVision Setup">
  				<eLabel text="Configure Skin" position="180,20" size="1300,50" font="Regular;40" verticalAlignment="center" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1"/>
  				<widget source="menu" render="Listbox" position="10,100" size="1180,880" scrollbarMode="showOnDemand" scrollbarWidth="9" enableWrapAround="1" transparent="1">
					<convert type="TemplatedMultiContent">
						{"template":
							[
							MultiContentEntryPixmapAlphaTest(pos = (15, 13), size = (40, 40), png = 2),
							MultiContentEntryText(pos = (70, 0), size = (1050, 50), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
							],
							"fonts": [gFont("Regular", 40),gFont("Regular", 32)],
							"itemHeight": 50
						}
					</convert>
  				</widget>
  				<eLabel text="Preview" position="1266,550" size="610,70" font="Regular;40" horizontalAlignment="center" verticalAlignment="center" zPosition="2"/>
  				<eLabel text="/ Choose" position="488,1000" size="220,70" font="Regular;33" backgroundColor="#80000000" transparent="1" verticalAlignment="center" foregroundColor="white"/>
  				<widget name="Picture" position="1265,625" size="612,344" alphaTest="on"/>
  				<eLabel position="23,1073" size="290,5" zPosition="-10" backgroundColor="#00ff0000"/>
  				<eLabel position="370,1073" size="290,5" zPosition="-10" backgroundColor="#0000ff00"/>
  				<widget source="key_red" render="Label" position="43,1005" size="250,70" zPosition="1" verticalAlignment="center" font="Regular;33" backgroundColor="#80000000" transparent="1" horizontalAlignment="center"/>
  				<widget source="key_green" render="Label" position="427,1000" size="80,70" zPosition="1" verticalAlignment="center" font="Regular;33" backgroundColor="#80000000" transparent="1" />
  				<widget source="global.CurrentTime" render="Label" position="1192,22" size="585,50" font="Regular;40" horizontalAlignment="right" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1">
    					<convert type="ClockToText">FullDate</convert>
  				</widget>
  				<eLabel backgroundColor="#0066ccff" position="1223,103" size="674,423" zPosition="-15"/>
  				<eLabel backgroundColor="#0066ccff" position="1225,483" size="670,1" zPosition="6"/>
  				<eLabel backgroundColor="background" position="1225,105" size="671,420" zPosition="-10"/>
  				<widget position="1225,105" size="671,377" source="session.VideoPicture" render="Pig" zPosition="3" backgroundColor="#ff000000"/>
  				<widget position="1225,484" size="670,40" source="session.CurrentService" render="Label" font="Regular;36" foregroundColor="#0066ccff" backgroundColor="#80000000" transparent="1" verticalAlignment="center" horizontalAlignment="center" noWrap="1" zPosition="5">
    					<convert type="ServiceName">Name</convert>
  				</widget>
			</screen>
		"""
    else:
        skin = """
			<screen name="OpenVisionScreens" backgroundColor="#80000000" flags="wfNoBorder" position="0,0" size="1280,720" title="OpenVision Setup">
  				<eLabel text="Configure Skin" position="40,5" size="507,35" font="Regular;25" verticalAlignment="center" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1"/>
  				<widget source="menu" render="Listbox" position="25,58" size="775,594" scrollbarMode="showOnDemand" scrollbarWidth="9" enableWrapAround="1" transparent="1">
      					<convert type="TemplatedMultiContent">
						{"template":
							[
							MultiContentEntryPixmapAlphaTest(pos = (15, 13), size = (40, 40), png = 2),
							MultiContentEntryText(pos = (70, 0), size = (1050, 50), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),
							],
							"fonts": [gFont("Regular", 26),gFont("Regular", 22)],
							"itemHeight": 50
						}
					</convert>
  				</widget>
  				<eLabel text="Preview" position="813,350" size="446,40" font="Regular;25" horizontalAlignment="center" verticalAlignment="center" foregroundColor="#0000ff00" zPosition="2"/>
  				<eLabel text="/ Choose" position="337,680" size="204,35" font="Regular;25" backgroundColor="#80000000" transparent="1" verticalAlignment="center" foregroundColor="white"/>
  				<widget name="Picture" position="809,437" size="452,237" alphaTest="on"/>
  				<eLabel position="2,715" size="290,5" zPosition="-10" backgroundColor="#00ff0000"/>
  				<eLabel position="230,715" size="290,5" zPosition="-10" backgroundColor="#0000ff00"/>
  				<widget source="key_red" render="Label" position="25,680" size="188,35" zPosition="1" verticalAlignment="center" font="Regular;25" backgroundColor="#80000000" transparent="1" horizontalAlignment="center"/>
  				<widget source="key_green" render="Label" position="284,680" size="80,35" zPosition="1" verticalAlignment="center" font="Regular;25" backgroundColor="#80000000" transparent="1"/>
  				<widget source="global.CurrentTime" render="Label" position="687,7" size="585,35" font="Regular;25" horizontalAlignment="right" foregroundColor="white" backgroundColor="#80000000" borderColor="#00065c9e" borderWidth="3" transparent="1" zPosition="1">
    					<convert type="ClockToText">FullDate</convert>
  				</widget>
  				<eLabel backgroundColor="#0066ccff" position="813,58" size="446,246" zPosition="-15"/>
  				<eLabel backgroundColor="#0066ccff" position="813,308" size="446,1" zPosition="6"/>
  				<eLabel backgroundColor="background" position="813,58" size="446,246" zPosition="-10"/>
  				<widget position="815,80" size="441,199" source="session.VideoPicture" render="Pig" zPosition="3" backgroundColor="#ff000000"/>
  				<widget position="813,309" size="446,35" source="session.CurrentService" render="Label" font="Regular;25" foregroundColor="#0066ccff" backgroundColor="#80000000" transparent="1" verticalAlignment="center" horizontalAlignment="center" noWrap="1" zPosition="5">
    					<convert type="ServiceName">Name</convert>
  				</widget>
			</screen>
		"""

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session

        global cur_skin

        self.title = _("%s additional screens") % cur_skin
        try:
            self["title"] = StaticText(self.title)
        except:
            cprint("self['title'] was not found in skin")

        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText(_("on"))

        self["Picture"] = Pixmap()

        menu_list = []
        self["menu"] = List(menu_list)

        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
        {
                "ok": self.runMenuEntry,
                "cancel": self.keyCancel,
                "red": self.keyCancel,
                "green": self.runMenuEntry,
        }, -2)

        self.skin_base_dir = "/usr/share/enigma2/%s/" % cur_skin
        self.screen_dir = "allScreens"
        self.skinparts_dir = "skinparts"
        self.file_dir = "mySkin_off"
        my_path = resolveFilename(SCOPE_SKINS, "%s/icons/lock_on.png" % cur_skin)
        if not path.exists(my_path):
            my_path = resolveFilename(SCOPE_SKINS, "skin_default/icons/lock_on.png")
        self.enabled_pic = LoadPixmap(cached=True, path=my_path)
        my_path = resolveFilename(SCOPE_SKINS, "%s/icons/lock_off.png" % cur_skin)
        if not path.exists(my_path):
            my_path = resolveFilename(SCOPE_SKINS, "skin_default/icons/lock_off.png")
        self.disabled_pic = LoadPixmap(cached=True, path=my_path)

        if not self.selectionChanged in self["menu"].onSelectionChanged:
            self["menu"].onSelectionChanged.append(self.selectionChanged)

        self.onLayoutFinish.append(self.createMenuList)

    def selectionChanged(self):
        sel = self["menu"].getCurrent()
        if sel is not None:
            self.setPicture(sel[0])
            if sel[2] == self.enabled_pic:
                self["key_green"].setText(_("off"))
            elif sel[2] == self.disabled_pic:
                self["key_green"].setText(_("on"))

    def createMenuList(self):
        chdir(self.skin_base_dir)
        f_list = []
        dir_path = self.skin_base_dir + self.screen_dir
        if not path.exists(dir_path):
            makedirs(dir_path)
        dir_skinparts_path = self.skin_base_dir + self.skinparts_dir
        if not path.exists(dir_skinparts_path):
            makedirs(dir_skinparts_path)
        file_dir_path = self.skin_base_dir + self.file_dir
        if not path.exists(file_dir_path):
            makedirs(file_dir_path)
        dir_global_skinparts = resolveFilename(SCOPE_SKINS, "skinparts")
        if path.exists(dir_global_skinparts):
            for pack in listdir(dir_global_skinparts):
                if path.isdir(dir_global_skinparts + "/" + pack):
                    for f in listdir(dir_global_skinparts + "/" + pack):
                        if path.exists(dir_global_skinparts + "/" + pack + "/" + f + "/" + f + "_Atile.xml"):
                            if not path.exists(dir_path + "/skin_" + f + ".xml"):
                                symlink(dir_global_skinparts + "/" + pack + "/" + f + "/" + f + "_Atile.xml", dir_path + "/skin_" + f + ".xml")
                            if not path.exists(dir_skinparts_path + "/" + f):
                                symlink(dir_global_skinparts + "/" + pack + "/" + f, dir_skinparts_path + "/" + f)
        list_dir = sorted(listdir(dir_path), key=str.lower)
        for f in list_dir:
            if f.endswith('.xml') and f.startswith('skin_'):
                if (not path.islink(dir_path + "/" + f)) or os.path.exists(os.readlink(dir_path + "/" + f)):
                    friendly_name = f.replace("skin_", "")
                    friendly_name = friendly_name.replace(".xml", "")
                    friendly_name = friendly_name.replace("_", " ")
                    linked_file = file_dir_path + "/" + f
                    if path.exists(linked_file):
                        if path.islink(linked_file):
                            pic = self.enabled_pic
                        else:
                            remove(linked_file)
                            symlink(dir_path + "/" + f, file_dir_path + "/" + f)
                            pic = self.enabled_pic
                    else:
                        pic = self.disabled_pic
                    f_list.append((f, friendly_name, pic))
                else:
                    if path.islink(dir_path + "/" + f):
                        remove(dir_path + "/" + f)
        menu_list = []
        for entry in f_list:
            menu_list.append((entry[0], entry[1], entry[2]))
        self["menu"].updateList(menu_list)
        self.selectionChanged()

    def setPicture(self, f):
        pic = f.replace(".xml", ".png")
        preview = self.skin_base_dir + "preview/preview_" + pic
        if path.exists(preview):
            self["Picture"].instance.setPixmapFromFile(preview)
            self["Picture"].show()
        else:
            self["Picture"].hide()

    def keyCancel(self):
        self.close()

    def runMenuEntry(self):
        sel = self["menu"].getCurrent()
        if sel is not None:
            if sel[2] == self.enabled_pic:
                remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
            elif sel[2] == self.disabled_pic:
                symlink(self.skin_base_dir + self.screen_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
            self.createMenuList()
