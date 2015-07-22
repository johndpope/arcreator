"""Subclass of Animations_Panel, which is generated by wxFormBuilder."""
from PyitectConsumes import ChangeMaximum_Dialog
from PyitectConsumes import ChooseGraphic_Dialog
from PyitectConsumes import AnimationTiming_Dialog
from PyitectConsumes import AnimationTweening_Dialog
from PyitectConsumes import AnimationCellBatch_Dialog
from PyitectConsumes import AnimationCellProperties_Dialog
from PyitectConsumes import AnimationEntireSlide_Dialog

# import AnimationFrames_Dialog  # TODO: Forgot to implement these
# import CopyFrames_Dialog
# import ClearFrames_Dialog
from PyitectConsumes import PanelBase, Animations_Panel_Template
from PyitectConsumes import DatabaseManager as DM


# Implementing Animations_Panel
class Animations_Panel(Animations_Panel_Template, PanelBase):

    _arc_panel_info = {
        "Name": "Animations Panel",
        "Caption": "Animations Panel",
        "CaptionV": True,
        "Center": None,
        "CloseB": True,
        "DestroyOC": True,
        "Floatable": True,
        "IconARCM": 'animations',
        "MaximizeB": True,
        "MinimizeB": True,
        "MinimizeM": ["POS_SMART", "CAPT_SMART"],
        "Movable": True,
        "NotebookD": True,
        "Resizable": True,
        "Snappable": True,
        "Layer": 1
    }

    def __init__(self, parent):
        Animations_Panel_Template.__init__(self, parent)

        DM.DrawHeaderBitmap(self.bitmapAnimations, 'Animations')

        # Bind the panel tot he Panel Manager
        self.bindPanelManager()

    # Handlers for Animations_Panel events.
    def listBoxAnimations_SelectionChanged(self, event):
        # TODO: Implement listBoxAnimations_SelectionChanged
        pass

    def buttonMaximum_Clicked(self, event):
        # TODO: Implement buttonMaximum_Clicked
        pass

    def textCtrlName_ValueChanged(self, event):
        # TODO: Implement textCtrlName_ValueChanged
        pass

    def comboBoxGraphic_Clicked(self, event):
        # TODO: Implement comboBoxGraphic_Clicked
        pass

    def comboBoxPosition_SelectionChanged(self, event):
        # TODO: Implement comboBoxPosition_SelectionChanged
        pass

    def comboBoxFrames_Clicked(self, event):
        # TODO: Implement comboBoxFrames_Clicked
        pass

    def listControlTiming_DoubleClicked(self, event):
        # TODO: Implement listControlTiming_DoubleClicked
        pass

    def buttonBack_Clicked(self, event):
        # TODO: Implement buttonBack_Clicked
        pass

    def listBoxFrames_SelectionChanged(self, event):
        # TODO: Implement listBoxFrames_SelectionChanged
        pass

    def buttonNext_Clicked(self, event):
        # TODO: Implement buttonNext_Clicked
        pass

    def buttonBattler_Clicked(self, event):
        # TODO: Implement buttonBattler_Clicked
        pass

    def buttonPaste_Clicked(self, event):
        # TODO: Implement buttonPaste_Clicked
        pass

    def buttonCopy_Clicked(self, event):
        # TODO: Implement buttonCopy_Clicked
        pass

    def buttonClear_Clicked(self, event):
        # TODO: Implement buttonClear_Clicked
        pass

    def buttonTweening_Clicked(self, event):
        # TODO: Implement buttonTweening_Clicked
        pass

    def buttonCellBatch_Clicked(self, event):
        # TODO: Implement buttonCellBatch_Clicked
        pass

    def buttonEntireSlide_Clicked(self, event):
        # TODO: Implement buttonEntireSlide_Clicked
        pass

    def buttonPlayHit_Clicked(self, event):
        # TODO: Implement buttonPlayHit_Clicked
        pass

    def buttonPlayMiss_Clicked(self, event):
        # TODO: Implement buttonPlayMiss_Clicked
        pass

    def bitmapAnimationFrames_Clicked(self, event):
        # TODO: Implement bitmapAnimationFrames_Clicked
        pass
