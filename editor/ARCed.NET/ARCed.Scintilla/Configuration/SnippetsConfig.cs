#region Using Directives



#endregion Using Directives


namespace ARCed.Scintilla.Configuration
{
    public class SnippetsConfig
    {
        #region Fields

        private string _code;
        private char? _delimeter;

        // Really all snippets can be used as SurroundsWith. The only
        // thing this really controls is whether or not the snippet 
        // appears in the Surrounds With List. Really.
        private bool? _isSurroundsWith;
        private string _shortcut;

        #endregion Fields


        #region Properties

        public string Code
        {
            get
            {
                return _code;
            }
            set
            {
                _code = value;
            }
        }


        public char? Delimeter
        {
            get
            {
                return _delimeter;
            }
            set
            {
                _delimeter = value;
            }
        }


        public bool? IsSurroundsWith
        {
            get
            {
                return _isSurroundsWith;
            }
            set
            {
                _isSurroundsWith = value;
            }
        }


        public string Shortcut
        {
            get
            {
                return _shortcut;
            }
            set
            {
                _shortcut = value;
            }
        }

        #endregion Properties
    }
}