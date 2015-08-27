import wx

import welder_kernel as kernel
from PyitectConsumes import DatabaseManager as DM
from PyitectConsumes import RPG_RGSS1 as RPG

from PyitectConsumes import PanelBase, Weapons_Panel_Template
# --------------------------------------------------------------------------------------
# Weapons_Panel
# --------------------------------------------------------------------------------------


class Weapons_Panel(Weapons_Panel_Template, PanelBase):

    _arc_panel_info = {
        "Name": "WeaponsPanel",
        "Caption": "Weapons",
        "CaptionV": True,
        "Center": None,
        "CloseB": True,
        "DestroyOC": True,
        "Floatable": True,
        "IconARCM": 'weapons',
        "MaximizeB": True,
        "MinimizeB": True,
        "MinimizeM": ["POS_SMART", "CAPT_SMART"],
        "Movable": True,
        "NotebookD": True,
        "Resizable": True,
        "Snappable": True
    }

    def __init__(self, parent, weapon_index=0):
        """Basic constructor for the Weapons panel"""
        Weapons_Panel_Template.__init__(self, parent)
        global Config, DataWeapons, DataStates, DataAnimations, DataElements
        
        try:
            proj = kernel.GlobalObjects['PROJECT']
            DataWeapons = proj.getData('Weapons')
            DataAnimations = proj.getData('Animations')
            DataStates = proj.getData('States')
            DataElements = proj.getData('System').elements
        except NameError:
            kernel.Log(
                'Database opened before Project has been initialized', '[Database:WEAPONS]', True)
            self.Destroy()
        font = wx.Font(
            8, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        font.SetFaceName(kernel.Config.getUnified()['Misc']['NoteFont'])
        self.textCtrlNotes.SetFont(font)
        default = ['Price:', 'ATK:', 'PDEF:', 'MDEF:']
        self.ParameterControls = DM.CreateParameterControls(self.panelParameters,
                                                            self.spinCtrlParameter_ValueChanged, '+:', 4, default)
        self.SelectedWeapon = DataWeapons[DM.FixedIndex(weapon_index)]
        self.setRanges()
        self.refreshAll()
        self.listBoxWeapons.SetSelection(weapon_index)
        DM.DrawHeaderBitmap(self.bitmapWeapons, 'Weapons')

        # Bind the panel tot he Panel Manager
        self.bindPanelManager()

    def setRanges(self):
        """Applies the range of values allowed fir the controls on the panel"""
        self.ParameterControls[0].SetRange(
            0, int(kernel.Config.getUnified()['DatabaseLimits']['Gold']))
        max = int(kernel.Config.getUnified()['DatabaseLimits']['ActorParameter'])
        for i in range(1, len(self.ParameterControls)):
            self.ParameterControls[i].SetRange(-max, max)

    def refreshAll(self):
        """Refreshes all the controls on the panel"""
        self.refreshWeaponList()
        self.refreshElements()
        self.refreshStates()
        self.refreshAnimations()
        self.refreshValues()

    def refreshWeaponList(self):
        """Refreshes the list of weapons"""
        digits = len(kernel.Config.getUnified()['GameObjects']['Weapons'])
        DM.FillControl(self.listBoxWeapons, DataWeapons, digits, [])

    def refreshElements(self):
        """Refreshes the list of elements in the wxCheckListBox"""
        self.checkListElements.Clear()
        self.checkListElements.AppendItems(DataElements[DM.FixedIndex(0):])

    def refreshStates(self):
        """Clears and refreshes the list of states in the checklist"""
        self.checkListStates.DeleteAllItems()
        names = [DataStates[i].name for i in range(
            DM.FixedIndex(0), len(DataStates))]
        self.checkListStates.AppendItems(names)

    def refreshAnimations(self):
        """Refreshes the choices in the user and target animation controls"""
        digits = len(kernel.Config.getUnified()['GameObjects']['Animations'])
        DM.FillControl(
            self.comboBoxUserAnimation, DataAnimations, digits, ['(None)'])
        DM.FillControl(
            self.comboBoxTargetAnimation, DataAnimations, digits, ['(None)'])

    def refreshValues(self):
        weapon = self.SelectedWeapon
        self.textCtrlName.ChangeValue(weapon.name)
        self.labelIconName.SetLabel(weapon.icon_name)
        DM.DrawButtonIcon(self.bitmapButtonIcon, weapon.icon_name, False)
        self.textCtrlDescription.ChangeValue(weapon.description)
        self.comboBoxUserAnimation.SetSelection(weapon.animation1_id)
        self.comboBoxTargetAnimation.SetSelection(weapon.animation2_id)
        if DM.ARC_FORMAT:
            # TODO: Implement
            addstates = weapon.plus_state_set
            minusstates = weapon.minus_state_set
            checked = weapon.element_set
        else:
            checked = [i - 1 for i in weapon.element_set]
            addstates = [id - 1 for id in weapon.plus_state_set]
            minusstates = [id - 1 for id in weapon.minus_state_set]
            self.ParameterControls[0].SetValue(weapon.price)
            self.ParameterControls[1].SetValue(weapon.atk)
            self.ParameterControls[2].SetValue(weapon.pdef)
            self.ParameterControls[3].SetValue(weapon.mdef)
            self.ParameterControls[4].SetValue(weapon.str_plus)
            self.ParameterControls[5].SetValue(weapon.dex_plus)
            self.ParameterControls[6].SetValue(weapon.agi_plus)
            self.ParameterControls[7].SetValue(weapon.int_plus)
        self.checkListElements.SetChecked(checked)
        for i in range(self.checkListStates.GetItemCount()):
            if i in addstates:
                self.checkListStates.SetItemImage(i, 1)
            elif i in minusstates:
                self.checkListStates.SetItemImage(i, 2)
            else:
                self.checkListStates.SetItemImage(i, 0)
        if not hasattr(weapon, 'note'):
            setattr(weapon, 'note', '')
        self.textCtrlNotes.ChangeValue(weapon.note)

    def spinCtrlParameter_ValueChanged(self, event):
        index = self.ParameterControls.index(event.GetEventObject())
        weapon = self.SelectedWeapon
        if DM.ARC_FORMAT:
            # TODO: Implement
            pass
        else:
            print(index)
            value = event.GetInt()
            if index == 0:
                weapon.price = value
            elif index == 1:
                weapon.atk = value
            elif index == 2:
                weapon.pdef = value
            elif index == 3:
                weapon.mdef = value
            elif index == 4:
                weapon.str_plus = value
            elif index == 5:
                weapon.dex_plus = value
            elif index == 6:
                weapon.agi_plus = value
            elif index == 7:
                weapon.int_plus = value

    def listBoxWeapons_SelectionChanged(self, event):
        """Changes the selected weapon and update the values on the panel"""
        index = DM.FixedIndex(event.GetSelection())
        if DataWeapons[index] is None:
            DataWeapons[index] = RPG.Weapon()
        self.SelectedWeapon = DataWeapons[index]
        self.refreshValues()

    def buttonMaximum_Clicked(self, event):
        """Starts the Change Maximum dialog"""
        max = int(kernel.Config.getUnified()['GameObjects']['Weapons'])
        DM.ChangeDataCapacity(self, self.listBoxWeapons, DataWeapons, max)

    def textCtrlName_TextChanged(self, event):
        """updates the selected weapon's name"""
        DM.updateObjectName(self.SelectedWeapon, event.GetString(),
                            self.listBoxWeapons, len(kernel.Config.getUnified()['GameObjects']['Weapons']))

    def bitmapButtonIcon_Clicked(self, event):
        """Opens dialog to select an icon for the selected skill"""
        filename = DM.ChooseGraphic(
            self, 'Icons', self.SelectedWeapon.icon_name)
        if filename:
            self.SelectedWeapon.icon_name = filename
        self.refreshValues()

    def textCtrlDescription_TextChange(self, event):
        """Set the selected weapon's description"""
        self.SelectedWeapon.description = event.GetString()

    def comboBoxUserAnimation_SelectionChanged(self, event):
        """Set the selected weapon's user animation"""
        self.SelectedWeapon.animation1_id = event.GetInt()

    def comboBoxTargetAnimation_SelectionChanged(self, event):
        """Set the selected weapon's target animation"""
        self.SelectedWeapon.animation2_id = event.GetInt()

    def textCtrlNotes_TextChanged(self, event):
        """Set the selected weapon's magical defense"""
        self.SelectedWeapon.note = event.GetString()

    def checkListElements_Clicked(self, event):
        """updates the guard elements for the selected weapon"""
        self.checkListElements.ChangeState(event, 1)
        if DM.ARC_FORMAT:
            # TODO: Implement
            pass
        else:
            ids = [DM.FixedIndex(id)
                   for id in self.checkListElements.GetChecked()]
            self.SelectedWeapon.element_set = ids

    def checkListStates_LeftClicked(self, event):
        """updates the plus/minus state set for the selected weapon"""
        data = self.checkListStates.ChangeState(event, 1)
        DM.ChangeSkillStates(self.SelectedWeapon, data[0], data[1])

    def checkListStates_RigthClicked(self, event):
        """updates the plus/minus state set for the selected weapon"""
        data = self.checkListStates.ChangeState(event, -1)
        DM.ChangeSkillStates(self.SelectedWeapon, data[0], data[1])