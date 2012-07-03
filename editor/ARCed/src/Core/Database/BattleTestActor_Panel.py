import wx
from Core.Database import ARCed_Templates as Templates
from Core.Panels import PanelBase
#--------------------------------------------------------------------------------------
# BattleTestActor_Panel
#--------------------------------------------------------------------------------------

# Implementing BattleTestActor_Panel
class BattleTestActor_Panel( Templates.BattleTestActor_Panel, PanelBase ):
    def __init__( self, parent ):
        Templates.BattleTestActor_Panel.__init__( self, parent )

        # Bind the panel tot he Panel Manager
        self.BindPanelManager()
    
    # Handlers for BattleTestActor_Panel events.
    def comboBoxActor_SelectionChanged( self, event ):
        # TODO: Implement comboBoxActor_SelectionChanged
        pass
    
    def spinCtrlLevel_ValueChanged( self, event ):
        # TODO: Implement spinCtrlLevel_ValueChanged
        pass
    
    def buttonInitialize_Clicked( self, event ):
        # TODO: Implement buttonInitialize_Clicked
        pass
    
    
