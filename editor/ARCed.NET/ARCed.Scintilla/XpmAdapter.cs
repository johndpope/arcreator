#region Using Directives

using System.Collections.Generic;
using System.Drawing;
using System.Text;
using System.Windows.Forms;

#endregion


namespace ARCed.Scintilla
{
	/// <summary>
	///     Converts Bitmap images to XPM data for use with ARCed.Scintilla.
	///     Warning: images with more than (around) 50 colors will generate incorrect XPM
	///     The XpmConverter class was based on code from flashdevelop. 
	/// </summary>
	internal static class XpmConverter
	{
		#region Fields

		/// <summary>
		///     The default transparent Color
		/// </summary>
		public static readonly string DefaultTransparentColor = "#FF00FF";

		#endregion Fields


		#region Methods

		/// <summary>
		///     Converts Bitmap images to XPM data for use with ARCed.Scintilla.
		///     Warning: images with more than (around) 50 colors will generate incorrect XPM.
		///     Uses the DefaultTransparentColor.
		/// </summary>
		/// <param name="bmp">The _srcTexture to transform.</param>
		public static string ConvertToXPM(Bitmap bmp)
		{
			return ConvertToXPM(bmp, DefaultTransparentColor);
		}


		/// <summary>
		///     Converts Bitmap images to XPM data for use with ARCed.Scintilla.
		///     Warning: images with more than (around) 50 colors will generate incorrect XPM
		///     tColor: specified transparent color in format: "#00FF00".
		/// </summary>
		/// <param name="bmp">The _srcTexture to transform.</param>
		/// <param name="transparentColor">The overriding transparent Color</param>
		public static string ConvertToXPM(Bitmap bmp, string transparentColor)
		{
			var sb = new StringBuilder();
			var colors = new List<string>();
			var chars = new List<char>();
			int width = bmp.Width;
			int height = bmp.Height;
			int index;
			sb.Append("/* XPM */static char * xmp_data[] = {\"").Append(width).Append(" ").Append(height).Append(" ? 1\"");
			int colorsIndex = sb.Length;
			string col;
			char c;
			for (int y = 0; y < height; y++)
			{
				sb.Append(",\"");
				for (int x = 0; x < width; x++)
				{
					col = ColorTranslator.ToHtml(bmp.GetPixel(x, y));
					index = colors.IndexOf(col);
					if (index < 0)
					{
						index = colors.Count + 65;
						colors.Add(col);
						if (index > 90) index += 6;
						c = Encoding.ASCII.GetChars(new[] { (byte)(index & 0xff) })[0];
						chars.Add(c);
						sb.Insert(colorsIndex, ",\"" + c + " c " + col + "\"");
						colorsIndex += 14;
					}
					else c = chars[index];
					sb.Append(c);
				}
				sb.Append("\"");
			}
			sb.Append("};");
			string result = sb.ToString();
			int p = result.IndexOf("?");
			string finalColor = result.Substring(0, p) + colors.Count + result.Substring(p + 1).Replace(transparentColor.ToUpper(), "None");

			return finalColor;
		}


		/// <summary>
		///     Cicles an _srcTexture list object to convert contained images into xpm
		///     at the same time we add converted images into an arraylist that lets us to retrieve images later.
		///     Uses the DefaultTransparentColor.
		/// </summary>
		/// <param name="imageList">The _srcTexture list to transform.</param>
		public static List<string> ConvertToXPM(ImageList imageList)
		{
			return ConvertToXPM(imageList, DefaultTransparentColor);
		}


		/// <summary>
		///     Cicles an _srcTexture list object to convert contained images into xpm
		///     at the same time we add converted images into an arraylist that lets us to retrieve images later	
		/// </summary>
		/// <param name="imageList">The _srcTexture list to transform.</param>
		/// <param name="transparentColor">The overriding transparent Color</param>
		public static List<string> ConvertToXPM(ImageList imageList, string transparentColor)
		{
			var xpmImages = new List<string>();
			foreach (Image image in imageList.Images)
			{
				if (image is Bitmap)
				{
					xpmImages.Add(ConvertToXPM(image as Bitmap, transparentColor));
				}
			}
			return xpmImages;
		}

		#endregion Methods
	}
}