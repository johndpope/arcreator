"""Subclass of Wait_Dialog, which is generated by wxFormBuilder."""

import wx


import Kernel


# Implementing Wait_Dialog
from PyitectConsumes import Wait_Dialog_Template


class Wait_Dialog(Wait_Dialog_Template):

    def __init__(self, parent):
        Wait_Dialog_Template.__init__(self, parent)

    # Handlers for Wait_Dialog events.
    def buttonOK_Clicked(self, event):
        # TODO: Implement buttonOK_Clicked
        pass

    def buttonCancel_Clicked(self, event):
        # TODO: Implement buttonCancel_Clicked
        pass