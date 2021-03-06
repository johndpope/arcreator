﻿#region Using Directives

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using ARCed.Core;

#endregion

namespace ARCed.Helpers
{
	/// <summary>
	/// Static class for loading graphic resources and caching them to increase performance. This class 
	/// class also performs hue and opacity alterations on graphics.
	/// </summary>
	public static class Cache
	{
		#region Fields
		/// <summary>
		/// The internal dictionary that contains all the cached images
		/// </summary>
		private static readonly Dictionary<string, Image> _cache = new Dictionary<string, Image>();

		/// <summary>
		/// The index to reference for building autotile graphics
		/// </summary>
		private static readonly int[][] _autoindex = new[] { 
			new[] { 27,28,33,34 },   new[] { 5,28,33,34 },   new[] { 27,6,33,34 },  
			new[] { 5,6,33,34 },     new[] { 27,28,33,12 },  new[] { 5,28,33,12 },  
			new[] { 27,6,33,12 },    new[] { 5,6,33,12 },    new[] { 27,28,11,34 },  
			new[] { 5,28,11,34 },    new[] { 27,6,11,34 },   new[] { 5,6,11,34 },
			new[] { 27,28,11,12 },   new[] { 5,28,11,12 },   new[] { 27,6,11,12 },  
			new[] { 5,6,11,12 },     new[] { 25,26,31,32 },  new[] { 25,6,31,32 },  
			new[] { 25,26,31,12 },   new[] { 25,6,31,12 },   new[] { 15,16,21,22 },  
			new[] { 15,16,21,12 },   new[] { 15,16,11,22 },  new[] { 15,16,11,12 },
			new[] { 29,30,35,36 },   new[] { 29,30,11,36 },  new[] { 5,30,35,36 },  
			new[] { 5,30,11,36 },    new[] { 39,40,45,46 },  new[] { 5,40,45,46 },  
			new[] { 39,6,45,46 },    new[] { 5,6,45,46 },    new[] { 25,30,31,36 },  
			new[] { 15,16,45,46 },   new[] { 13,14,19,20 },  new[] { 13,14,19,12 },
			new[] { 17,18,23,24 },   new[] { 17,18,11,24 },  new[] { 41,42,47,48 }, 
			new[] { 5,42,47,48 },    new[] { 37,38,43,44 },  new[] { 37,6,43,44 },  
			new[] { 13,18,19,24 },   new[] { 13,14,43,44 },  new[] { 37,42,43,48 },  
			new[] { 17,18,47,48 },   new[] { 13,18,43,48 },  new[] { 13,18,43,48 }
		};
		#endregion

		/// <summary>
		/// Loads a filename as a Image from the specified folder, or recalls
		/// a cached image, and returns it.
		/// </summary>
		/// <param name="folder">Folder specifying where the image will be searched</param>
		/// <param name="filename">FullPath of the image, omitting extension</param>
		/// <returns>Cached image</returns>
		public static Image LoadBitmap(string folder, string filename)
		{
			var path = ResourceHelper.GetFullPath(folder, filename);
			if (String.IsNullOrEmpty(path))
				return null;
			if (_cache.ContainsKey(path))
				return _cache[path];
			try
			{
				_cache[path] = Image.FromFile(path);
				return _cache[path];
			}
			catch { return null; }
		}

		/// <summary>
		/// Rotates the hue and alters the opacity of an image. Using this
		/// method is more efficient than performing the actions separately.
		/// </summary>
		/// <param name="image">Image to change</param>
		/// <param name="hue">Degree of hue displacement (0..360)</param>
		/// <param name="opacity">Opacity change to apply (0..255)</param>
		/// <remarks>Values out of range will be automatically corrected</remarks>
		public static void ChangeHueOpacity(Image image, int hue, int opacity)
		{
			using (var newImage = new Bitmap(image))
			{
				using (var g = Graphics.FromImage(image))
				{
					var imageAttr = new ImageAttributes();
					var qm = new QColorMatrix();
					qm.RotateHue(hue % 360);
					qm.ScaleOpacity(opacity.Clamp(0, 255) / 255.0f);
					imageAttr.SetColorMatrix(qm.ToColorMatrix());
					var destRect = new Rectangle(new Point(), image.Size);
					g.Clear(Color.Transparent);
					g.DrawImage(newImage, destRect, 0, 0, image.Width, image.Height,
						GraphicsUnit.Pixel, imageAttr);
				}
			}
		}

		/// <summary>
		/// Rotates the hue of an image
		/// </summary>
		/// <param name="image">Image to change</param>
		/// <param name="hue">Degree of hue displacement (0..360)</param>
		/// <remarks>Values out of range will be automatically corrected</remarks>
		public static void RotateHue(Image image, int hue)
		{
			using (var newImage = new Bitmap(image))
			{
				using (var g = Graphics.FromImage(image))
				{
					var imageAttr = new ImageAttributes();
					var qm = new QColorMatrix();
					qm.RotateHue(hue % 360);
					imageAttr.SetColorMatrix(qm.ToColorMatrix());
					var destRect = new Rectangle(new Point(), image.Size);
					g.Clear(Color.Transparent);
					g.DrawImage(newImage, destRect, 0, 0, image.Width, image.Height,
						GraphicsUnit.Pixel, imageAttr);
				}
			}
		}

		/// <summary>
		/// Changes the opacity of an image. 
		/// </summary>
		/// <param name="image">Image to change</param>
		/// <param name="opacity">Opacity change to apply (0..255)</param>
		/// <remarks>Values out of range will be automatically corrected</remarks>
		public static void ChangeOpacity(Image image, int opacity)
		{
			using (var newImage = new Bitmap(image))
			{
				using (var g = Graphics.FromImage(image))
				{
					var imageAttr = new ImageAttributes();
					var qm = new QColorMatrix();
					qm.ScaleOpacity(opacity.Clamp(0, 255) / 255.0f);
					imageAttr.SetColorMatrix(qm.ToColorMatrix());
					var destRect = new Rectangle(new Point(), image.Size);
					g.Clear(Color.Transparent);
					g.DrawImage(newImage, destRect, 0, 0, image.Width, image.Height,
						GraphicsUnit.Pixel, imageAttr);
				}
			}
		}

		/// <summary>
		/// Loads/recalls a cached image autotile file and returns it
		/// </summary>
		/// <param name="filename">Full path of the autotile graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Autotile(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Autotiles", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached image icon file and returns it
		/// </summary>
		/// <param name="filename">Full path of the icon graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Icon(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Icons", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached character file and returns it
		/// </summary>
		/// <param name="filename">Full path of the character graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Character(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Characters", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached tileset file and returns it
		/// </summary>
		/// <param name="filename">Relative path of the tileset graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Tileset(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Tilesets", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached animation file and returns it
		/// </summary>
		/// <param name="filename">Relative path of the animation graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Animation(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Animations", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached fog file and returns it
		/// </summary>
		/// <param name="filename">Full path of the fog graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Fog(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Fogs", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached panorama file and returns it
		/// </summary>
		/// <param name="filename">Full path of the panorama graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Panorama(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Panoramas", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Loads/recalls a cached battleback file and returns it
		/// </summary>
		/// <param name="filename">Full path of the battleback graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned image</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Battleback(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Battlebacks", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Returns a tile of a character graphic using the given pattern and direction
		/// </summary>
		/// <param name="filename">FullPath of the character graphic</param>
		/// <param name="pattern">Pattern of the character tile</param>
		/// <param name="direction">Direction of the character tile</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached _srcTexture with effects applied</returns>
		public static Image CharacterStance(string filename, int pattern, int direction,
			int hue = 0, int opacity = 255)
		{
			var image = Character(filename, hue, opacity);
			var cw = image.Width / 4;
			var ch = image.Height / 4;
			var sx = pattern * cw;
			var sy = (direction - 2) / 2 * ch;
			var tile = new Bitmap(cw, ch);
			using (var g = Graphics.FromImage(tile))
				g.DrawImage(image, new Rectangle(0, 0, cw, ch), sx, sy, cw, ch, GraphicsUnit.Pixel);
			GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
			return tile;
		}

		/// <summary>
		/// Loads/recalls a cached image battler file and returns it
		/// </summary>
		/// <param name="filename">FullPath of the character graphic</param>
		/// <param name="hue">Hue rotation to apply to graphic, with 360 degrees of displacement</param>
		/// <param name="opacity">Opacity of the returned _srcTexture</param>
		/// <returns>Cached <see cref="Image"/> with effects applied</returns>
		public static Image Battler(string filename, int hue = 0, int opacity = 255)
		{
			var bitmap = LoadBitmap(@"Graphics\Battlers", filename);
			if (bitmap == null)
				return null;
			using (Image image = new Bitmap(bitmap))
			{
				if (hue != 0)
					RotateHue(image, hue);
				if (opacity != 255)
					ChangeOpacity(image, opacity);
				GC.Collect(GC.GetGeneration(image), GCCollectionMode.Forced);
				return new Bitmap(image);
			}
		}

		/// <summary>
		/// Disposes all cached images and clears all keys and values of the dictionary
		/// </summary>
		public static void Clear()
		{
			var cacheGeneration = GC.GetGeneration(_cache);
			try
			{
				foreach (var image in _cache.Values.Where(image => image != null))
					image.Dispose();
			}
			finally
			{
				_cache.Clear();
				GC.Collect(cacheGeneration, GCCollectionMode.Forced);
			}
		}
	}
}