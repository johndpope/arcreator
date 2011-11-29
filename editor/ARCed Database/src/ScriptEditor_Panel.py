import wx
from wxPython import stc	

# For now, this works. The finished product can load the fonts, etc. from the cfg file.

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Consolas',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 10,
              'size2': 8,
            }
else:
    faces = { 'times': 'Times',
              'mono' : 'Courier',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 10,
              'size2': 8,
            }

# Tabs/Indents
TAB_WIDTH = 2
INDENT_GUIDES = True
AUTO_INDENT = True

# Line Highlighting
SHOW_CARET = True
CARET_FORE = wx.Color(40, 40, 40)
CARET_BACK = wx.Color(0, 0, 0)
CARET_ALPHA = 40

# Keywords
RUBY_KEYWORDS = "BEGIN END __ENCODING__ __END__ __FILE__ __LINE__ alias and begin break case class def defined? do else elsif end ensure false for if in module next nil not or redo rescue retry return self super then true undef unless until when while yield"

# Styles unrelated to syntax
GLOBAL_STYLES = {
					stc.wxSTC_STYLE_DEFAULT     : "face:%(mono)s,size:%(size)d" % faces,
					stc.wxSTC_STYLE_DEFAULT     : "face:%(mono)s,size:%(size)d" % faces,
					stc.wxSTC_STYLE_LINENUMBER  : "back:#C0C0C0,face:%(helv)s,size:8" % faces,
					stc.wxSTC_STYLE_CONTROLCHAR : "face:%(other)s" % faces,
					stc.wxSTC_STYLE_BRACELIGHT  : "fore:#FFFFFF,back:#0000FF,bold",
					stc.wxSTC_STYLE_BRACEBAD    : "fore:#000000,back:#FF0000,bold"
				}

# Syntax highlighting
RUBY_STYLES = {
				# Default
				stc.wxSTC_RB_DEFAULT      : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Comment
				stc.wxSTC_RB_COMMENTLINE  : "fore:#008000,face:%(other)s,size:%(size)d" % faces,
				# Numbers
				stc.wxSTC_RB_NUMBER       : "fore:#800000,face:%(mono)s,size:%(size)d" % faces,
				# Double-Quoted Strings
				stc.wxSTC_RB_STRING       : "fore:#800080,italic,face:%(times)s,size:%(size)d" % faces,
				# Single-Quoted Strings
				stc.wxSTC_RB_CHARACTER    : "fore:#C80080,italic,face:%(times)s,size:%(size)d" % faces,
				# Keywords
				stc.wxSTC_RB_WORD         : "fore:#0000FF,bold,size:%(size)d" % faces,
				# Class Name
				stc.wxSTC_RB_CLASSNAME    : "fore:#000000,bold,size:%(size)d" % faces,
				# Module Name
				stc.wxSTC_RB_MODULE_NAME  : "fore:#000000,bold,size:%(size)d" % faces,
				# Method/Function Name
				stc.wxSTC_RB_DEFNAME      : "fore:#000000,bold,size:%(size)d" % faces,
				# Operators
				stc.wxSTC_RB_OPERATOR     : "fore:##2B91AF,bold,size:%(size)d" % faces,
				# Normal Text/Local Variables
				stc.wxSTC_RB_IDENTIFIER   : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Global Variable
				stc.wxSTC_RB_GLOBAL       : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Instance Variable
				stc.wxSTC_RB_INSTANCE_VAR : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Class Variable
				stc.wxSTC_RB_CLASS_VAR    : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Regular Expressions
				stc.wxSTC_RB_REGEX        : "fore:#9370DB,face:%(mono)s,size:%(size)d" % faces,
				# Symbol
				stc.wxSTC_RB_SYMBOL       : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Backticks
				stc.wxSTC_RB_BACKTICKS    : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Data Section
				stc.wxSTC_RB_DATASECTION  : "fore:#000000,face:%(mono)s,size:%(size)d" % faces,
				# Error
				stc.wxSTC_RB_ERROR        : "fore:#FF0000,face:%(mono)s,bold,size:%(size)d" % faces,
			  }

#--------------------------------------------------------------------------------------
# ScriptTextCtrl
#--------------------------------------------------------------------------------------

class ScriptTextCtrl(stc.wxStyledTextCtrl):

	def __init__(self, parent):
		super(ScriptTextCtrl, self).__init__(parent, 
			style=stc.wxSTC_STYLE_LINENUMBER|stc.wxSTC_STYLE_INDENTGUIDE)
		self.ApplyDefaults()
		self.BindHotKeys()
		self.Bind(wx.EVT_KEY_DOWN, self.KeyPressed)
		

	def KeyPressed( self, event ):
		"""Preprocess keystrokes before they are added to the Scintilla control"""
		ch = event.GetKeyCode()
		if ch == wx.WXK_RETURN:
			# Process auto-indentation if the return key was pressed
			thisLine = self.GetCurrentLine()
			nextLine = thisLine + 1
			text = self.GetCurLine()[0]
			indent = self.GetLineIndentation(thisLine)
			indent += self.DetermineIndentChange(text, thisLine, indent)
			self.CmdKeyExecute(stc.wxSTC_CMD_NEWLINE)
			self.SetLineIndentation(nextLine, indent)
			self.GotoPos(self.GetLineEndPosition(nextLine))
		else:
			event.Skip()
		
	def DetermineIndentChange( self, text, previousLine, previousIndent ):
		"""Calculates the value to change the indent level by, if at all"""
		tabWidth = self.GetTabWidth()
		currentWords = text.strip().split()
		if len(currentWords) == 0: 
			return 0
		first, last = currentWords[0], currentWords[-1]
		if last == 'end' or last == 'else' or first in ['elsif', 'rescue', 'ensure']:
			prePreviousIndent = self.GetLineIndentation(previousLine - 1)
			if previousIndent + tabWidth != prePreviousIndent:
				indent = previousIndent - tabWidth
				self.SetLineIndentation(previousLine, indent)
			elif self.GetLineIndentation(previousLine + 1) == previousIndent + tabWidth:
				return tabWidth
			if last == 'end' : return -tabWidth
			return 0
		if first in ['class', 'module', 'if', 'elsif', 'else', 'begin', 'rescue', 
			'ensure','unless', 'while', 'until', 'def', 'for', 'case', 'when']:
			return tabWidth
		return 0
		
	def BindHotKeys( self ):
		self.CmdKeyAssign(ord('Z'), stc.wxSTC_SCMOD_ALT, stc.wxSTC_CMD_ZOOMIN)
		self.CmdKeyAssign(ord('X'), stc.wxSTC_SCMOD_ALT, stc.wxSTC_CMD_ZOOMOUT)

		#self.CmdKeyAssign(ord('Q'), stc.wxSTC_SCMOD_CTRL, stc.w


		

	def ApplyDefaults( self ):
		self.SetLexer(stc.wxSTC_LEX_RUBY)
		self.SetKeyWords(0, RUBY_KEYWORDS)
		for key, value in GLOBAL_STYLES.iteritems():
			self.StyleSetSpec(key, value)
		for key, value in RUBY_STYLES.iteritems():
			self.StyleSetSpec(key, value)
		self.SetTabWidth(TAB_WIDTH)
		self.SetCaretLineVisible(SHOW_CARET)
		self.SetCaretLineBack(CARET_BACK)
		self.SetCaretForeground(CARET_FORE)
		self.SetCaretLineBackAlpha(CARET_ALPHA)
		self.SetIndentationGuides(INDENT_GUIDES)




	def ApplyAutoIndentation( self, event ):
		print 'Char Added'
		ch = chr(event.KeyCode)

		if event.ControlDown():
			print 'CTRL'

		if event.AltDown():
			print 'ALT'
		print event.KeyCode, ch

#--------------------------------------------------------------------------------------
# ScriptEditor_Panel
#--------------------------------------------------------------------------------------

class ScriptEditor_Panel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 696,485 ), style = wx.TAB_TRAVERSAL )
		MainSizer = wx.BoxSizer( wx.VERTICAL )
		bSizer643 = wx.BoxSizer( wx.HORIZONTAL )
		sizerScriptList = wx.BoxSizer( wx.VERTICAL )
		self.bitmapScripts = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 150,26 ), wx.CLIP_CHILDREN|wx.FULL_REPAINT_ON_RESIZE )
		self.bitmapScripts.SetMinSize( wx.Size( 150,26 ) )
		self.bitmapScripts.SetMaxSize( wx.Size( 150,26 ) )
		sizerScriptList.Add( self.bitmapScripts, 0, wx.ALL|wx.EXPAND, 5 )
		listBoxScriptsChoices = []
		self.listBoxScripts = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 184,-1 ), listBoxScriptsChoices, wx.LB_SINGLE|wx.CLIP_CHILDREN )
		sizerScriptList.Add( self.listBoxScripts, 1, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )
		self.m_textCtrl60 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerScriptList.Add( self.m_textCtrl60, 0, wx.ALL|wx.EXPAND, 5 )
		bSizer643.Add( sizerScriptList, 0, wx.EXPAND, 5 )
		sizerScriptControl = wx.BoxSizer( wx.VERTICAL )
		self.scriptControl = ScriptTextCtrl(self)
		sizerScriptControl.Add( self.scriptControl, 1, wx.ALL|wx.EXPAND, 5 )
		bSizer643.Add( sizerScriptControl, 1, wx.EXPAND, 5 )
		MainSizer.Add( bSizer643, 1, wx.EXPAND, 5 )
		sizerButtons = wx.BoxSizer( wx.HORIZONTAL )
		self.buttonHelp = wx.Button( self, wx.ID_ANY, u"Help", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerButtons.Add( self.buttonHelp, 0, wx.ALL, 5 )
		self.buttonOK = wx.Button( self, wx.ID_ANY, u"OK", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonOK.SetDefault() 
		sizerButtons.Add( self.buttonOK, 0, wx.TOP|wx.BOTTOM|wx.LEFT, 5 )
		self.buttonCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerButtons.Add( self.buttonCancel, 0, wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )
		MainSizer.Add( sizerButtons, 0, wx.ALIGN_RIGHT, 5 )
		self.SetSizer( MainSizer )
		self.Layout()

#--------------------------------------------------------------------------------------
# TEST
#--------------------------------------------------------------------------------------

app = wx.PySimpleApp( 0 )
frame = wx.Frame( None, wx.ID_ANY, 'ARCed Script Editor', size=(800,600) )
panel = ScriptEditor_Panel( frame )

try:
	# I was testing in Ubuntu, and didn't want to copy the all the source files...
	from DatabaseManager import DatabaseManager as DM
	DM.DrawHeaderBitmap(panel.bitmapScripts, 'Scripts')
except:
	pass

frame.Centre( wx.BOTH )
frame.Show()
app.MainLoop()