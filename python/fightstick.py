#!/usr/bin/python

import gtk
import pygtk
pygtk.require('2.0')
import os, sys, time
import pygame
import inspect
file_name = "~/FightstickDisplay/images/fightstick_paneltemplate.png"
class GUI:

	def __init__(self):


            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.image = gtk.Image()
            self.image.set_from_file(file_name)
            self.window.set_title ("Fightstick Display")
            self.window.add(self.image)
            self.window.show_all()
            self.window.connect_after('destroy', self.destroy)

	def destroy(window, self):
		gtk.main_quit()

def main():
	app = GUI()
	gtk.main()

if __name__ == "__main__":
    sys.exit(main())
