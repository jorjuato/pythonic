#!/usr/bin/env python

import sys

try:
	import pygtk 
	#tell pyGTK, if possible, that we want GTKv2
	pygtk.require("2.0")
except:
	#Some distributions come with GTK2, but not pyGTK
	pass
try:
	import gtk
	import gtk.glade
	import dfth
	
except:
	print "Tienes que instalar pyGTK or GTKv2 ",
	print "o configurar PYTHONPATH correctamente."
	print "try: export PYTHONPATH=",
	print "/usr/local/lib/python2.2/site-packages/"
	#sys.exit(1)





class Appgui:
	"""
		Esta clase contiene la definicion del interfaz principal de la aplicacion.
	"""
	def __init__(self):
		gladefile="schonergui.glade"
		windowname="main_window"
		self.wTree=gtk.glade.XML (gladefile,windowname)
		from handlers import Handlers
		self.handlers = Handlers(self)
		self.wTree.signal_autoconnect(self.handlers)
		#self.dfth_lineal = dfth.run_lineal
		#self.dfth_nolineal = dfth.run_nolineal
		#self.dfth_kernel_basico = dfth.run_kernel
		#self.dfth_inhibidor = dfth.run_inhibidor
		#self.dfth_inhibidor_ltm = dfth.run_inhibidor_ltm
		return

## Y asi es como iniciamos la aplicacion desde la shell
if __name__ == '__main__':
	app=Appgui()
	gtk.main()
	
