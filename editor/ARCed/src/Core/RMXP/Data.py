'''
Created on Dec 21, 2010

'''
import os
import sys
import platform
import subprocess
import threading
import re
import cPickle
import ConfigParser
import shutil
import wx
import RMPY
import Kernel
from Kernel import Manager as KM


def Call_RMXP_Import(path, changed, all=False):
    #set up changed files
    changedfiles = ""
    if all:
        i = 0
        for file in changed:
            i += 1
            changedfiles += file
            if len(changed) > i:
                changedfiles += "|"
    else:
        changedfiles = "all"

    #set up directories
    os.chdir(Kernel.Global.Program_Dir)
    local_path = os.path.normpath(Kernel.Global.Program_Dir + "/import")
    config = Kernel.Global.RMPYconfig

    #start the process
    if platform.system() == "Windows":
        callmode = config.get("RMXP", "win_importer_type")
        importer_command = config.get("RMXP", "win_importer_command")
        importer_file = config.get("RMXP", "win_importer_file")
        if callmode == "static":
            #the mode is static so the command must be a local executable 
            process = subprocess.Popen([importer_command, "import", path,
                                       local_path, changedfiles], shell=True)
        elif callmode == "local":
            #the mode is local so the command refers to the system ruby command
            #thus we pass the file which should be a path (local or absolute)
            #to a import script
            process = subprocess.Popen([importer_command, importer_file,
                                       "import", path, local_path,
                                       changedfiles], shell=True)
        else:
            raise Exception, "RMXP win_importer_type can only be static or local"
    else:
        callmode = config.get("RMXP", "other_importer_type")
        importer_command = config.get("RMXP", "other_importer_command")
        importer_file = config.get("RMXP", "other_importer_file")
        if callmode == "static":
            #the mode is static so the command must be a local executable 
            process = subprocess.Popen([importer_command, "import", path,
                                       local_path, changedfiles])
        elif callmode == "local":
            #the mode is local so the command refers to the system ruby command
            #thus we pass the file which should be a path (local or absolute)
            #to a import script
            process = subprocess.Popen([importer_command, importer_file,
                                       "import", path, local_path,
                                       changedfiles])
        else:
            raise Exception, "RMXP other_importer_type can only be static " \
                             " or local"

    #wait for the process to finish
    process.wait()

    #find out if it worked
    f = open("import.log", 'rb')
    result = f.read()
    f.close()
    match = re.search("success", result)
    if match:
        os.remove("import.log")
    else:
        raise Warning, "success of datafile import can't be verified"

def Call_RMXP_Export(path, topath, changed, all=False):
    #set up changed files
    changedfiles = ""
    if all:
        i = 0
        for file in changed:
            i += 1
            changedfiles += file
            if len(changed) > i:
                changedfiles += "|"
    else:
        changedfiles = "all"

    #set up directories   
    os.chdir(Kernel.Global.Program_Dir)
    config = Kernel.Global.RMPYconfig

    #start the process
    if platform.system() == "Windows":
        callmode = config.get("RMXP", "win_importer_type")
        importer_command = config.get("RMXP", "win_importer_command")
        importer_file = config.get("RMXP", "win_importer_file")
        if callmode == "static":
            #the mode is static so the command must be a local executable 
            process = subprocess.Popen([importer_command, "export", path,
                                       topath, changedfiles], shell=True)
        elif callmode == "local":
            #the mode is local so the command refers to the system ruby command
            #thus we pass the file which should be a path (local or absolute)
            #to a import script
            process = subprocess.Popen([importer_command, importer_file,
                                       "export", path, topath,
                                       changedfiles], shell=True)
        else:
            raise Exception, "RMXP win_importer_type can only be static or local"
    else:
        callmode = config.get("RMXP", "other_importer_type")
        importer_command = config.get("RMXP", "other_importer_command")
        importer_file = config.get("RMXP", "other_importer_file")
        if callmode == "static":
            #the mode is static so the command must be a local executable 
            process = subprocess.Popen([importer_command, "export", path,
                                       topath, changedfiles])
        elif callmode == "local":
            #the mode is local so the command refers to the system ruby command
            #thus we pass the file which should be a path (local or absolute)
            #to a import script
            process = subprocess.Popen([importer_command, importer_file,
                                       "export", path, topath,
                                       changedfiles])
        else:
            raise Exception, "RMXP other_importer_type can only be static " \
                             " or local"
    process.wait()
    f = open("export.log", 'rb')
    result = f.read()
    f.close()
    match = re.search("success", result)
    if match:
        os.remove("export.log")
    else:
        raise Warning, "success of datafile export can't be verified"

def RefreshRMXPProject():
    pass

def ImportRMXPProject(mainwindow):
    dlg = KM.get_component("DialogImportProject", "RMXP").object(mainwindow)
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        list = dlg.GetFilesList()
        location = dlg.GetLocation()
        importer = KM.get_component("ProjectImporter", "RMXP").object()
        importer.Import(location, list, mainwindow)
    dlg.Destroy()

def ExportRMXPProject(mainwindow):
    dlg = KM.get_component("DialogExportProject", "RMXP").object(mainwindow)
    result = dlg.ShowModal()
    if result == wx.ID_OK:
        list = dlg.GetFilesList()
        location = dlg.GetLocation()
        exporter = KM.get_component("ProjectImporter", "RMXP").object()
        exporter.Export(location, list, mainwindow)
    dlg.Destroy()

class RMXPProjectLoader(object):

    DataFiles = ["Actors", "Classes", "Skills", "Items", "Weapons", "Armors",
                 "Enemies", "Troops", "States", "Animations", "Tilesets",
                 "CommonEvents", "System", "MapInfos"
                 ]

    def __init__(self):
        self.project = KM.get_component("RMXPProject", "RMXP").object

    def Load(self, path, mainwindow=None):
        self.mainwindow = mainwindow
        #load
        self.doLoad(path)


        self.project.Location = path
        if platform.system() == "Windows":
            rtppath = "%PROGRAMFILES%/Common Files/Enterbrain/RGSS/Standard"
            self.project.RTP_Location = os.path.normpath(os.path.expandvars(
                                                         rtppath))
        else:
            self.project.RTP_Location = ""
        self.project.Data_actors = (self.load_data(os.path.
                                    join(path, os.path.normpath("Data/Actors.xppy"))))
        self.project.Data_classes = (self.load_data(os.path.
                                     join(path, os.path.normpath("Data/Classes.xppy"))))
        self.project.Data_skills = (self.load_data(os.path.
                                    join(path, os.path.normpath("Data/Skills.xppy"))))
        self.project.Data_items = (self.load_data(os.path.
                                   join(path, os.path.normpath("Data/Items.xppy"))))
        self.project.Data_weapons = (self.load_data(os.path.
                                     join(path, os.path.normpath("Data/Weapons.xppy"))))
        self.project.Data_armors = (self.load_data(os.path.
                                    join(path, os.path.normpath("Data/Armors.xppy"))))
        self.project.Data_enemies = (self.load_data(os.path.
                                     join(path, os.path.normpath("Data/Enemies.xppy"))))
        self.project.Data_troops = (self.load_data(os.path.
                                    join(path, os.path.normpath("Data/Troops.xppy"))))
        self.project.Data_states = (self.load_data(os.path.
                                    join(path, os.path.normpath("Data/States.xppy"))))
        self.project.Data_animations = (self.load_data(os.path.join(path,
                                        os.path.normpath("Data/Animations.xppy"))))
        self.project.Data_tilesets = (self.load_data(os.path.
                                      join(path, os.path.normpath("Data/Tilesets.xppy"))))
        self.project.Data_common_events = (self.load_data(os.path.join(path,
                                           os.path.normpath("Data/CommonEvents.xppy"))))
        self.project.Data_system = (self.load_data(os.path.
                                    join(path, os.path.normpath("Data/System.xppy"))))
        self.project.Map_infos = (self.load_data(os.path.
                                  join(path, os.path.normpath("Data/MapInfos.xppy"))))
        self.project.Maps = {}
        for key in self.project.Map_infos.keys():
            _map = (self.load_data(os.path.
                    join(path, os.path.normpath("Data/Map%03d.xppy" % key))))
            self.project.Maps[key] = _map

        KM.raise_event("EventRefreshProject")

    def load_data(self, filename):
        f = open(filename, 'rb')
        data = cPickle.load(f)
        f.close()
        return data

class RMXPProjectSaver(object):
    def __init__(self):
        self.project = KM.get_component("RMXPProject", "RMXP").object

    def Save(self, path):
        dirpath = os.path.join(path, "Data")
        if not os.path.exists(dirpath) and not os.path.isdir(dirpath):
            os.mkdir(dirpath)
        self.dump_data(self.project.Data_actors, os.path.join(path,
                       os.path.normpath("Data/Actors.xppy")))
        self.dump_data(self.project.Data_classes, os.path.join(path,
                       os.path.normpath("Data/Classes.xppy")))
        self.dump_data(self.project.Data_skills, os.path.join(path,
                       os.path.normpath("Data/Skills.xppy")))
        self.dump_data(self.project.Data_items, os.path.join(path,
                       os.path.normpath("Data/Items.xppy")))
        self.dump_data(self.project.Data_weapons, os.path.join(path,
                       os.path.normpath("Data/Weapons.xppy")))
        self.dump_data(self.project.Data_armors, os.path.join(path,
                       os.path.normpath("Data/Armors.xppy")))
        self.dump_data(self.project.Data_enemies, os.path.join(path,
                       os.path.normpath("Data/Enemies.xppy")))
        self.dump_data(self.project.Data_troops, os.path.join(path,
                       os.path.normpath("Data/Troops.xppy")))
        self.dump_data(self.project.Data_states, os.path.join(path,
                       os.path.normpath("Data/States.xppy")))
        self.dump_data(self.project.Data_animations, os.path.join(path,
                       os.path.normpath("Data/Animations.xppy")))
        self.dump_data(self.project.Data_tilesets, os.path.join(path,
                       os.path.normpath("Data/Tilesets.xppy")))
        self.dump_data(self.project.Data_common_events, os.path.join(path,
                       os.path.normpath("Data/CommonEvents.xppy")))
        self.dump_data(self.project.Data_system, os.path.join(path,
                       os.path.normpath("Data/System.xppy")))
        self.dump_data(self.project.Map_infos, os.path.join(path,
                       os.path.normpath("Data/MapInfos.xppy")))
        for key in self.project.Map_infos.iterkeys():
            self.dump_data(self.project.Maps[key], os.path.join(path,
                           os.path.normpath("Data/Map%03d.xppy" % key)))


    def dump_data(self, data, filename):
        f = open(filename, 'wb')
        cPickle.dump(data, f, protocol= -1)
        f.close()

class RMXPProjectImporter(object):
    def __init__(self, all=False):
        self.project = KM.get_component("RMXPProject", "RMXP").object
        self.all = all
        self.progress = 0
        self.message = ""

    def Import(self, path, changed=[], mainwindow=None):
        self.changed = changed
        if "all" in self.changed:
            self.all = True
        self.dlg = wx.ProgressDialog("Importing Project",
                               "Importing .rxdata files",
                               maximum=16,
                               parent=mainwindow,
                               style=wx.PD_APP_MODAL
                                | wx.PD_AUTO_HIDE
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_ESTIMATED_TIME
                                )
        self.progress = 0
        self.message = "Importing .rxdata files"
        self.dlg.Bind(wx.EVT_UPDATE_UI, self.updatedlg)
        self.thread = threading.Thread(group=None, target=self.doImport,
                                       args=(path,))
        self.thread.start()


    def doImport(self, path):
        Call_RMXP_Import(path, self.changed, self.all)
        if platform.system() == "Windows":
            rtppath = "%PROGRAMFILES%/Common Files/Enterbrain/RGSS/Standard"
            self.project.RTP_Location = os.path.normpath(os.path.expandvars(
                                                         rtppath))
        else:
            self.project.RTP_Location = ""
        print "================================"
        print "Loading data into RPG Maker PY"
        print "================================"
        local_path = os.path.join(Kernel.Global.Program_Dir, "import")
        if self.all or "Actors" in self.changed:
            self.dlgUpdate(1, "Loading Actors")
            self.project.Data_actors = (self.load_data(os.path.
                                        join(local_path, os.path.normpath("Data/Actors.rmpy"))))
        if self.all or "Classes" in self.changed:
            self.dlgUpdate(2, "Loading Classes")
            self.project.Data_classes = (self.load_data(os.path.
                                         join(local_path, os.path.normpath("Data/Classes.rmpy"))))
        if self.all or "Skills" in self.changed:
            self.dlgUpdate(3, "Loading Skills")
            self.project.Data_skills = (self.load_data(os.path.
                                        join(local_path, os.path.normpath("Data/Skills.rmpy"))))
        if self.all or "Items" in self.changed:
            self.dlgUpdate(4, "Loading Items")
            self.project.Data_items = (self.load_data(os.path.
                                       join(local_path, os.path.normpath("Data/Items.rmpy"))))
        if self.all or "Items" in self.changed:
            self.dlgUpdate(5, "Loading Weapons")
            self.project.Data_weapons = (self.load_data(os.path.
                                         join(local_path, os.path.normpath("Data/Weapons.rmpy"))))
        if self.all or "Armors" in self.changed:
            self.dlgUpdate(6, "Loading Armors")
            self.project.Data_armors = (self.load_data(os.path.
                                        join(local_path, os.path.normpath("Data/Armors.rmpy"))))
        if self.all or "Enemies" in self.changed:
            self.dlgUpdate(7, "Loading Enemies")
            self.project.Data_enemies = (self.load_data(os.path.
                                         join(local_path, os.path.normpath("Data/Enemies.rmpy"))))
        if self.all or "Troops" in self.changed:
            self.dlgUpdate(8, "Loading Troops")
            self.project.Data_troops = (self.load_data(os.path.
                                        join(local_path, os.path.normpath("Data/Troops.rmpy"))))
        if self.all or "States" in self.changed:
            self.dlgUpdate(9, "Loading States")
            self.project.Data_states = (self.load_data(os.path.
                                        join(local_path, os.path.normpath("Data/States.rmpy"))))
        if self.all or "Animations" in self.changed:
            self.dlgUpdate(10, "Loading Animations")
            self.project.Data_animations = (self.load_data(os.path.join(local_path,
                                            os.path.normpath("Data/Animations.rmpy"))))
        if self.all or "Tilesets" in self.changed:
            self.dlgUpdate(11, "Loading Tilesets")
            self.project.Data_tilesets = (self.load_data(os.path.
                                          join(local_path, os.path.normpath("Data/Tilesets.rmpy"))))
        if self.all or "CommonEvents" in self.changed:
            self.dlgUpdate(12, "Loading CommonEvents")
            self.project.Data_common_events = (self.load_data(os.path.
                                               join(local_path,
                                               os.path.normpath("Data/CommonEvents.rmpy"))))
        if self.all or "System" in self.changed:
            self.dlgUpdate(13, "Loading System")
            self.project.Data_system = (self.load_data(os.path.
                                        join(local_path, os.path.normpath("Data/System.rmpy"))))
        if self.all or "MapInfos" in self.changed:
            self.dlgUpdate(14, "Loading MapInfos")
            self.project.Map_infos = (self.load_data(os.path.
                                      join(local_path, os.path.normpath("Data/MapInfos.rmpy"))))
        for key in self.project.Map_infos.keys():
            if self.all or ("Map%03d" % key) in self.changed:
                self.dlgUpdate(15, "Loading Map: %d" % key)
                _map = (self.load_data(os.path.
                        join(local_path, os.path.normpath("Data/Map%03d.rmpy" % key))))
                self.project.Maps[key] = _map

        self.dlgUpdate(15, "Removing temp files")
        shutil.rmtree(local_path)
        self.dlgUpdate(16, "Done")
        print "Done"

        #(keepGoing, skip) = dlg.Update(16, "Done")
        self.dlg.Destroy()
        saver = RMXPProjectSaver()
        saver.Save(self.project.Location)
        KM.raise_event("EventRefreshProject")

    def load_data(self, filename):
        print "- rmpy loading %s..." % filename
        f = open(filename, 'rb')
        data = RMPY.load(f)
        f.close()
        return data

    def updatedlg(self, event):
        self.dlg.Update(self.progress, self.message)

    def dlgUpdate(self, progress, message):
        self.progress = progress
        self.message = message

class RMXPProjectExporter(object):

    def __init__(self, all=False):
        self.project = KM.get_component("RMXPProject", "RMXP").object
        self.all = all
        self.progress = 0
        self.message = ""

    def Export(self, path, changed=[], mainwindow=None):
        self.changed = changed
        self.dlg = wx.ProgressDialog("Exporting Project",
                               "Exporting .rxdata files",
                               maximum=16,
                               parent=mainwindow,
                               style=wx.PD_APP_MODAL
                                | wx.PD_AUTO_HIDE
                                | wx.PD_ELAPSED_TIME
                                | wx.PD_ESTIMATED_TIME
                                )
        self.progress = 0
        self.message = "Exporting .rxdata files"
        self.dlg.Bind(wx.EVT_UPDATE_UI, self.updatedlg)
        self.thread = threading.Thread(group=None, target=self.doExport,
                                       args=(path,))
        self.thread.start()

    def doExport(self, path):
        local_path = os.path.join(Kernel.Global.Program_Dir, "export")
        data_path = os.path.join(local_path, "Data")
        if not os.path.exists(data_path) and not os.path.isdir(data_path):
            os.makedirs(data_path)
        print "================================"
        print "Dumping Data to RMPY format"
        print "================================"
        if self.all or "Actors" in self.changed:
            self.dlgUpdate(0, "Dumping Actors")
            self.dump_data(self.project.Data_actors, os.path.join(local_path,
                           os.path.normpath("Data/Actors.rmpy")))
        if self.all or "Classes" in self.changed:
            self.dlgUpdate(1, "Dumping Classes")
            self.dump_data(self.project.Data_classes, os.path.join(local_path,
                           os.path.normpath("Data/Classes.rmpy")))
        if self.all or "Skills" in self.changed:
            self.dlgUpdate(2, "Dumping Skills")
            self.dump_data(self.project.Data_skills, os.path.join(local_path,
                           os.path.normpath("Data/Skills.rmpy")))
        if self.all or "Items" in self.changed:
            self.dlgUpdate(3, "Dumping Items")
            self.dump_data(self.project.Data_items, os.path.join(local_path,
                           os.path.normpath("Data/Items.rmpy")))
        if self.all or "Items" in self.changed:
            self.dlgUpdate(4, "Dumping Weapons")
            self.dump_data(self.project.Data_weapons, os.path.join(local_path,
                           os.path.normpath("Data/Weapons.rmpy")))
        if self.all or "Armors" in self.changed:
            self.dlgUpdate(5, "Dumping Armors")
            self.dump_data(self.project.Data_armors, os.path.join(local_path,
                           os.path.normpath("Data/Armors.rmpy")))
        if self.all or "Enemies" in self.changed:
            self.dlgUpdate(6, "Dumping Enemies")
            self.dump_data(self.project.Data_enemies, os.path.join(local_path,
                           os.path.normpath("Data/Enemies.rmpy")))
        if self.all or "Troops" in self.changed:
            self.dlgUpdate(7, "Dumping Troops")
            self.dump_data(self.project.Data_troops, os.path.join(local_path,
                           os.path.normpath("Data/Troops.rmpy")))
        if self.all or "States" in self.changed:
            self.dlgUpdate(8, "Dumping States")
            self.dump_data(self.project.Data_states, os.path.join(local_path,
                           os.path.normpath("Data/States.rmpy")))
        if self.all or "Animations" in self.changed:
            self.dlgUpdate(9, "Dumping Animations")
            self.dump_data(self.project.Data_animations, os.path.join(
                           local_path, os.path.normpath("Data/Animations.rmpy")))
        if self.all or "Tilesets" in self.changed:
            self.dlgUpdate(10, "Dumping Tilesets")
            self.dump_data(self.project.Data_tilesets, os.path.join(local_path,
                           os.path.normpath("Data/Tilesets.rmpy")))
        if self.all or "CommonEvents" in self.changed:
            self.dlgUpdate(11, "Dumping CommonEvents")
            self.dump_data(self.project.Data_common_events, os.path.join(
                           local_path, os.path.normpath("Data/CommonEvents.rmpy")))
        if self.all or "System" in self.changed:
            self.dlgUpdate(12, "Dumping System")
            self.dump_data(self.project.Data_system, os.path.join(local_path,
                           os.path.normpath("Data/System.rmpy")))
        if self.all or "MapInfos" in self.changed:
            self.dlgUpdate(13, "Dumping MapInfos")
            self.dump_data(self.project.Map_infos, os.path.join(local_path,
                           os.path.normpath("Data/MapInfos.rmpy")))
        for key, map in self.project.Map_infos:
            self.dlgUpdate(14, "Loading Map: %d" % key)
            self.dump_data(map, os.path.join(path,
                           os.path.normpath("Data/Map%03d.rmpy" % key)))

        self.dlgUpdate(15, "Exporting to .rxdata")
        Call_RMXP_Export(local_path, path, self.changed, self.all)

        self.dlgUpdate(15, "Removing temp files")
        shutil.rmtree(local_path)
        self.dlgUpdate(16, "Done")
        print "Done"

    def dump_data(self, data, filename):
        print "- rmpy dumping %s..." % filename
        f = open(filename, 'wb')
        RMPY.dump(data, f)
        f.close()

    def updatedlg(self, event):
        self.dlg.Update(self.progress, self.message)

    def dlgUpdate(self, progress, message):
        self.progress = progress
        self.message = message

class RMXPProjectCreator(object):
    def __init__(self):
        self.project = KM.get_component("RMXPProject", "RMXP").object

    def Create(self, path, title, saveas=False):
        config = ConfigParser.ConfigParser()
        config.add_section("Project")
        config.set("Project", "title", title)
        config.set("Project", "type", "RMXP")
        filename = os.path.join(path, "Project.rmpyproj")
        f = open(filename, 'w')
        config.write(f)
        f.close()
        saver = RMXPProjectSaver()
        saver.Save(path)
        if not saveas:
            KM.raise_event("EventRefreshProject")