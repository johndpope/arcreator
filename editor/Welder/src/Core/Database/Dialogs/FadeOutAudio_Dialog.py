"""Subclass of FadeOutAudio_Dialog, which is generated by wxFormBuilder."""

import wx
from Boot import WelderImport

Kernel = WelderImport('Kernel')
Core = WelderImport('Core')

Templates = Core.Database.Welder_Templates

# Implementing FadeOutAudio_Dialog
class FadeOutAudio_Dialog( Templates.FadeOutAudio_Dialog ):
	def __init__( self, parent ):
		Templates.FadeOutAudio_Dialog.__init__( self, parent )
	
	# Handlers for FadeOutAudio_Dialog events.
	def buttonOK_Clicked( self, event ):
		# TODO: Implement buttonOK_Clicked
		pass
	
	def buttonCancel_Clicked( self, event ):
		# TODO: Implement buttonCancel_Clicked
		pass
	
	