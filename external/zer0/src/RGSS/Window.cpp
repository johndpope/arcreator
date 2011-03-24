#include <ruby.h>

#include <hltypes/util.h>

#include "RGSS/Window.h"
#include "RGSS/Bitmap.h"
#include "RGSS/Rect.h"
#include "RGSS/Viewport.h"
#include "CodeSnippets.h"

namespace zer0
{
	namespace RGSS
	{
		void Window::createRubyInterface()
		{
			rb_cWindow = rb_define_class("Window", rb_cObject);
			rb_define_attr(rb_cWindow, "active", 1, 1);
			rb_define_attr(rb_cWindow, "back_opacity", 1, 0);
			rb_define_attr(rb_cWindow, "contents", 1, 0);
			rb_define_attr(rb_cWindow, "contents_opacity", 1, 0);
			rb_define_attr(rb_cWindow, "cursor_rect", 1, 1);
			rb_define_attr(rb_cWindow, "height", 1, 1);
			rb_define_attr(rb_cWindow, "opacity", 1, 0);
			rb_define_attr(rb_cWindow, "ox", 1, 1);
			rb_define_attr(rb_cWindow, "oy", 1, 1);
			rb_define_attr(rb_cWindow, "pause", 1, 1);
			rb_define_attr(rb_cWindow, "stretch", 1, 1);
			rb_define_attr(rb_cWindow, "viewport", 1, 0);
			rb_define_attr(rb_cWindow, "visible", 1, 1);
			rb_define_attr(rb_cWindow, "width", 1, 1);
			rb_define_attr(rb_cWindow, "windowskin", 1, 0);
			rb_define_attr(rb_cWindow, "x", 1, 1);
			rb_define_attr(rb_cWindow, "y", 1, 1);
			rb_define_attr(rb_cWindow, "z", 1, 1);
			rb_define_method(rb_cWindow, "back_opacity=", RUBY_METHOD_FUNC(&Window::setBackOpacity), 1);
			rb_define_method(rb_cWindow, "contents=", RUBY_METHOD_FUNC(&Window::setContents), 1);
			rb_define_method(rb_cWindow, "contents_opacity=", RUBY_METHOD_FUNC(&Window::setContentsOpacity), 1);
			rb_define_method(rb_cWindow, "initialize", RUBY_METHOD_FUNC(&Window::rb_initialize), -1);
			rb_define_method(rb_cWindow, "opacity=", RUBY_METHOD_FUNC(&Window::setOpacity), 1);
			rb_define_method(rb_cWindow, "windowskin=", RUBY_METHOD_FUNC(&Window::setWindowskin), 1);
			rb_define_method(rb_cWindow, "dispose", RUBY_METHOD_FUNC(&Window::dispose), 0);
			rb_define_method(rb_cWindow, "disposed?", RUBY_METHOD_FUNC(&Window::isDisposed), 0);
		}
	
		VALUE Window::wrap()
		{
			Window* window = this;
			return Data_Wrap_Struct(rb_cWindow, NULL, NULL, window);
		}
		/// @todo add RGSS Error calls
		/// @todo set values for changing alpha on C++ side

		VALUE Window::rb_initialize(int argc, VALUE *argv, VALUE self)
		{
			if (argc > 1)
				;// rb_raise(ArgumentError);
			else if (argc == 1)
				rb_iv_set(rb_cWindow, "@viewport", argv[0]);
			return self;
		}

		VALUE Window::dispose(VALUE self)
		{
			/// @todo Implement dispose method
			return self;
		}

		VALUE Window::isDisposed(VALUE self)
		{
			/// @todo Implement disposed? method 
			return self;
		}

		VALUE Window::setBackOpacity(VALUE self, VALUE value)
		{
			value = rb_float_new(hclamp(NUM2DBL(value), 0.0, 255.0));
			rb_iv_set(self, "@back_opacity", value);
			return value;
		}

		VALUE Window::setContents(VALUE self, VALUE* value)
		{
			rb_iv_set(self, "@bitmap", *value);
			return *value;
		}

		VALUE Window::setContentsOpacity(VALUE self, VALUE value)
		{
			value = rb_float_new(hclamp(NUM2DBL(value), 0.0, 255.0));
			rb_iv_set(self, "@opacity", value);
			return value;
		}

		VALUE Window::setOpacity(VALUE self, VALUE value)
		{
			value = rb_float_new(hclamp(NUM2DBL(value), 0.0, 255.0));
			rb_iv_set(self, "@opacity", value);
			return value;
		}

		VALUE Window::setWindowskin(VALUE self, VALUE* value)
		{
			rb_iv_set(self, "@windowskin", *value);
			return *value;
		}

		VALUE Window::update(VALUE self)
		{

			return self;
		}
	}
}
