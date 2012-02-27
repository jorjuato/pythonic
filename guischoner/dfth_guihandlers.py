

#########################################################################	
#####	CALLBACKS		#################################################
#########################################################################
	
class Handlers:
	
	def __init__(self,application):
		self.app=application
		
######## MAIN WINDOW CALLBACKS
	def on_delete_event(self,event):
		return False
	
	def on_destroy(self):
		gtk.main_quit()

######## BUTTONS CALLBACKS				
	def on_button_simula_clicked(self, widget):
		thread_aloro("dfth001",leer_parametros())
		import scipy.arange
		import ioservices.load_data
		u, du_dt, S , t , x = load_data()
		tran=scipy.arange(5,(len(u[0,:])-1),10)
		xran=scipy.arange(10,len(u[:,0])-1)
		u2=u[:,tran]
		du2=du_dt[:,tran]
		S2=S[:,tran]
		return
			
	def on_button_estadisticas_clicked(self, widget):
		pass
		return
			
	def on_button_reset_clicked(self, widget):
		wacomDraw = drawingarea.WacomDrawWindow()
		return
			
	def on_button_guardarmatriz_clicked(self, widget):
		wacomDraw = drawingarea.WacomDrawWindow()
		return

	def on_button_graficar_clicked(self, widget):
		import ioservices.mesh
		import pylab.ion 

		pylab.ion()
		mesh(u2[xran,:],"u[x,t]","surface")
		mesh(du2[xran,:],"du/dt[x,t]","surface")	
		return

	def on_button_reset_clicked(self, widget):
		wacomDraw = drawingarea.WacomDrawWindow()
		return

######## TOGGLED CALLBACKS
	def on_checkbuttonHV_toggled(self, widget):
		if self.app['frameHV'].get_property("sensitive") == False:
			self.app['frameHV'].set_sensitive(True) 
		else: 
			self.app['frameHV'].set_sensitive(False)
	
	def on_checkbuttonFlash_toggled(self, widget):
		if self.app['frameFlash'].get_property("sensitive") == False:
			self.app['frameFlash'].set_sensitive(True) 
		else: 
			self.app['frameFlash'].set_sensitive(False)

######## FUNCIONES AUXILIARES
def thread_aloro(comand,lista_parametros):
	pass

def leer_parametros(self):
	pass

