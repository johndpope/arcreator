"""Subclass of ChangeStat_Dialog, which is generated by wxFormBuilder."""

import wx
from Boot import WelderImport

Kernel = WelderImport('Kernel')
Core = WelderImport('Core')

Templates = Core.Database.Welder_Templates

# Implementing ChangeStat_Dialog
class ChangeStat_Dialog( Templates.ChangeStat_Dialog ):
	def __init__( self, parent ):
		Templates.ChangeStat_Dialog.__init__( self, parent )
	
	# Handlers for ChangeStat_Dialog events.
	def radioButtonConstant_CheckChanged( self, event ):
		# TODO: Implement radioButtonConstant_CheckChanged
		pass
	
	def radioButtonVariable_CheckChanged( self, event ):
		# TODO: Implement radioButtonVariable_CheckChanged
		pass
	
	def comboBoxVariable_Clicked( self, event ):
		# TODO: Implement comboBoxVariable_Clicked
		pass
	
	def buttonOK_Clicked( self, event ):
		# TODO: Implement buttonOK_Clicked
		pass
	
	def buttonCancel_Clicked( self, event ):
		# TODO: Implement buttonCancel_Clicked
		pass
	
	