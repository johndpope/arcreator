﻿#region Using Directives

using System;

#endregion


namespace ARCed.Scintilla
{
    public class FileDropEventArgs : EventArgs
    {
        #region Fields

        private readonly string[] _fileNames;

        #endregion Fields


        #region Properties

        public string[] FileNames
        {
            get
            {
                return _fileNames;
            }
        }

        #endregion Properties


        #region Constructors

        /// <summary>
        ///     Initializes a new instance of the FileDropEventArgs class.
        /// </summary>
        public FileDropEventArgs(string[] fileNames)
        {
            _fileNames = fileNames;
        }

        #endregion Constructors
    }
}