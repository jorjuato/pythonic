#!/usr/bin/env python
# -*- coding: utf-8 -*-


import scipy as s
import numpy
import tables 
from pylab import *
import os

############################################################################################
#####################	EXPERIMENT CONSTANTS AND ENUMS  ####################################

trial_list 	= ['LL','LR','RL','RR']
cueing_list = ['cued','uncued']
key_list	= ['L','R']

trial_enum	= tables.Enum(trial_list)
cueing_enum	= tables.Enum(cueing_list)
key_enum	= tables.Enum(key_list)


############################################################################################
#####################	MAIN CLASS  ########################################################
class DataAnalysis:

	def __init__(self):
		self.rawdata_path = "./rawdata/"
		self.tables_path  = "./tablas/" 
		self.graphics_path = "./graficas/"
		self.graphics_str  = "continuo_"
		self.rawdata_str = "ior_continuo"
		self.ctoa_beans  = 14
		self.ctd_beans	 = 10
		self.ctoa_min	 = 200
		self.ctoa_max 	 = 1000
		self.ctd_min	 = -280
		self.ctd_max	 = 	280
		self.rt			 = []
		self.ctoa_bean_width = (self.ctoa_max - self.ctoa_min) / self.ctoa_beans
		self.ctd_bean_width  = (self.ctd_max - self.ctd_min) / self.ctd_beans
		self.ctoa_range  = arange(self.ctoa_min,self.ctoa_max,self.ctoa_bean_width)
		self.ctd_range   = arange(self.ctd_min,self.ctd_max,self.ctd_bean_width)
		self.ctoa_size   = len(self.ctoa_range) 
		self.ctd_size    = len(self.ctd_range)
		self.h5filename = self.tables_path + self.rawdata_str + ".h5"
		self.h5file = self.__load_data__()

	############################################################################################
	#####################	DATA FILE PARSER FUNCTIONS  ########################################	
	
	def __load_data__(self):
		"""
			Funcion que lee los datos de salida del programa C  
		"""
		from stats import mean, stdev	
		#Creamos la descripción de la tabla de entrada de datos sin procesar
		class Trial(tables.IsDescription):
			trial_type = tables.EnumCol(trial_enum,'LL', base='uint8')
			key 	= tables.EnumCol(key_enum, 'L', base='uint8')
			cueing  = tables.EnumCol(cueing_enum,'cued', base='uint8')
			ctoa 	= tables.Float32Col()
			ctd 	= tables.Float32Col()
			valid	= tables.UInt8Col()
			rt 		= tables.Float32Col()
			rt_norm = tables.Float32Col()
			rt_corr = tables.Float32Col()
			index 	= tables.UInt16Col()
			order 	= tables.UInt16Col()
			train	= tables.UInt8Col()
			
		#Creamos el archivo h5	
		h5file = tables.openFile(self.h5filename, mode = "w", title = "IOR experiment results")
		
		#Generamos la lista de ficheros de datos en crudo que serán procesado
		rawdata_filelist = [f for f in os.listdir(self.rawdata_path)
									if os.path.isfile(os.path.join(self.rawdata_path, f)) \
									and f.find(self.rawdata_str) == 0 ]

		#Para cada sujeto, generamos un grupo de datos
		
		for rawdata_filename in rawdata_filelist:	
			#Creamos los grupos y tablas necesarios
			datafile = open(os.path.join(self.rawdata_path,rawdata_filename), "r")
			group = h5file.createGroup("/", \
									'Data'+rawdata_filename[len(self.rawdata_str):],\
									'Data from '+rawdata_filename[len(self.rawdata_str):])
			table = h5file.createTable(group, 'rawdata', Trial, "Raw data from IOR continous experiment")
			
			#Los rellenamos por medio del metodo privado __parse_data_file__()
			rt_tmp = self.__parse_data_file__(datafile, table)
			self.rt.extend(rt_tmp)
			datafile.close()
		
		#Aqui creo la tabla de datos raw combinada de todos los sujetos
		groupeto = h5file.createGroup("/", 'DataCombined', "Combined data from all subjects of IOR experiment")
		table = h5file.createTable(groupeto, 'rawdata', Trial, "Raw data from IOR experiment")

		for group in h5file.walkGroups():
			if group._v_name == '/' or group._v_name == 'DataCombined' : continue		
			temp_table = group.rawdata[:]
			table.append(temp_table)
			table.flush()
		#Calculamos la media y stdev del conjunto total de datos, para reescalar
		rt_mean = mean(self.rt)
		rt_stdev= stdev(self.rt)
		for trial in table.iterrows():
			#if trial['valid'] == True:
			trial['rt'] = trial['rt_norm']
			trial.update()
		table.flush()
				#trial['rt'] = trial['rt_norm'] * rt_stdev + rt_mean
				#Chapuzilla para que chute rapido
		#Devuelve el archivo h5 creado 		
		return h5file
					
	def __parse_data_file__(self, datafile, table):
		from stats import mean, stdev
		rt_list = []
		#Parseamos el archivo de datos y rellenamos tablas
		for line in datafile:
			campos = line.split()
	
			if campos.__len__() == 0 :	#Si la linea esta vacia 
				continue
			elif campos[0] == "\n":
				continue	
			elif campos[0] == "#?" : 	#Si es un texto de ayuda
				continue	
			elif campos[0] == "#!":		#Si empezamos el datablock
				continue		
			#Si no es ninguna de las anteriores, es un datablock
			trial = table.row
			trial['order'] 	= int(campos[0])
			trial['trial_type'] = trial_enum[campos[1]]
			trial['ctoa'] 	= float(campos[2])
			trial['ctd'] 	= float(campos[3])
			trial['rt'] 	= int(campos[4])	
			trial['train'] = False
			
			#Codificamos el tipo de trial: cued/uncued		
			if (campos[1] == 'LL' or campos[1] == 'RR'):
				trial['cueing'] = cueing_enum['cued']			
			elif (campos[1] == 'LR' or campos[1] == 'RL'):
				trial['cueing'] = cueing_enum['uncued']	
				
			#Codificamos la tecla pulsada			
			if (int(campos[5]) == 19):
				trial['key'] 	= key_enum['R']
			elif (int(campos[5]) == 20):
				trial['key'] 	= key_enum['L']
				
			#Codificamos la validez del ensayo
			#
			#	Respondiendo a la derecha debe:
			if   trial['key'] 			== key_enum['R'] 	\
			and 250 < trial['rt'] < 550						\
			and (trial['trial_type'] 	== trial_enum['LR'] \
			or   trial['trial_type'] 	== trial_enum['RR'] ):
				trial['valid'] = True
			#
			#	Respondiendo a la izquierda debe:
			elif trial['key'] 			== key_enum['L'] 	\
			and 300 < trial['rt'] < 450						\
			and  (trial['trial_type'] 	== trial_enum['RL'] \
			or    trial['trial_type'] 	== trial_enum['LL'] ):
				trial['valid'] = True
			#
			#	Si no, es inválido							
			else:
				trial['valid'] = False	
			
			#Ahora vamos a generar una lista con los rt válidos
			if	trial['valid'] == True:
				rt_list.append(trial['rt'])
				
			#Añadimos la fila y guardamos	
			trial.append()
			table.flush()
		#Fin del bucle, ahora calculamos los valores normalizados de rt
		rt_mean = mean(rt_list)
		rt_stdev= stdev(rt_list)	
		
		for trial in table.iterrows():
			trial['rt_norm'] = (trial['rt'] - rt_mean) / rt_stdev
			trial.update()		
		#Devuelve la lista de rt válidos para ser usada en promedios posteriores
		table.flush()
		return rt_list
	
	############################################################################################
	#####################	STATISTICAL ANALYSIS FUNCTIONS  ####################################
	def simple_stats(self):
		self.__simple_stats__(self.h5file.root.DataCombined)
		#for group in self.h5file.walkGroups():
		#	if group._v_name == '/'  : continue		
		#	self.__simple_stats__(group)
	
	def __simple_stats__(self, group):
		from stats import mean, stdev, sterr, ttest_ind
	
		#Creamos la descripción de la tabla de analisis estadistico simple
		class DiscreteData(tables.IsDescription):
			ctoa 			= tables.Float32Col()
			ctd 			= tables.Float32Col()
			mean			= tables.Float32Col()
			stdev			= tables.Float32Col()
			frequency		= tables.UInt16Col()
		
		#Creamos la tabla para estadistica y un puntero a la de datos en bruto	
		table_cued = self.h5file.createTable(group, 'discrete_data_cued', DiscreteData, "Discrete organization of cued IOR continous data")
		table_uncued = self.h5file.createTable(group, 'discrete_data_uncued', DiscreteData, "Discrete organization of uncued IOR continous data")
		table_raw = group.rawdata
		
		#Creamos un array para contener los valores y plotearlos con matrixplot3D
		self.cued_array = zeros((self.ctoa_size, self.ctd_size))
		self.uncued_array = zeros((self.ctoa_size, self.ctd_size))
		self.rt_diff = zeros((self.ctoa_size, self.ctd_size))
		
		# Ahora, debería generamos intervalos para las clases en los datos
		# y hacer estadística con esas clases
		ctoa_index= -1
		for ctoa in self.ctoa_range:
			ctoa_index += 1
			ctoa_min = ctoa - self.ctoa_bean_width / 2
			ctoa_max = ctoa + self.ctoa_bean_width / 2
			ctd_index = -1
			for ctd in self.ctd_range:
				ctd_index += 1
				ctd_min = ctd - self.ctd_bean_width / 2
				ctd_max = ctd + self.ctd_bean_width / 2
				cued_lst_tmp = [ trial_raw['rt'] for trial_raw in table_raw.iterrows()
								if  ctoa_min < trial_raw['ctoa'] < ctoa_max		\
								and ctd_min  < trial_raw['ctd']  < ctd_max 		\
								and trial_raw['cueing'] == cueing_enum['cued'] 	\
								and trial_raw['valid'] 	== True 				]
				
				uncued_lst_tmp = [ trial_raw['rt'] for trial_raw in table_raw.iterrows()
								if  ctoa_min < trial_raw['ctoa'] < ctoa_max		\
								and ctd_min  < trial_raw['ctd']  < ctd_max 		\
								and trial_raw['cueing'] == cueing_enum['uncued']\
								and trial_raw['valid'] 	== True 				]
				cued_lst = self.__remove_outliers(cued_lst_tmp)
				uncued_lst = self.__remove_outliers(uncued_lst_tmp)
				
				cued = table_cued.row
				cued['ctoa'] 		= ctoa
				cued['ctd'] 		= ctd
				cued['frequency']	= len(cued_lst) 
				if cued['frequency'] == 0:
					cued['mean'] 	= 0
					cued['stdev'] 	= 0
				elif cued['frequency'] == 1:
					cued['mean'] 	= mean(cued_lst)
					cued['stdev'] 	= 0
				else:
					cued['mean'] 	= mean(cued_lst)
					cued['stdev'] 	= stdev(cued_lst)	
				
				uncued = table_uncued.row
				uncued['ctoa'] 		= ctoa
				uncued['ctd'] 		= ctd
				uncued['frequency']	= len(uncued_lst) 
				if uncued['frequency'] == 0:
					uncued['mean'] 	= 0
					uncued['stdev'] = 0
				elif uncued['frequency'] == 1:
					uncued['mean'] 	= mean(uncued_lst)
					uncued['stdev'] = 0
				else:	
					uncued['mean'] 	= mean(uncued_lst)
					uncued['stdev'] = stdev(uncued_lst)
								 	
				self.cued_array[ctoa_index][ctd_index] 		= cued['mean']
				self.uncued_array[ctoa_index][ctd_index] 	= uncued['mean']
				self.rt_diff[ctoa_index][ctd_index] 		= cued['mean'] - uncued['mean']
				cued.append()
				uncued.append()
				table_cued.flush()
				table_uncued.flush()

				
	def __remove_outliers(self, lista):
		#if len(lista) < 2:
		if True:
			return lista
		else: 	
			from stats import mean, stdev
			#Preparamos listas y limites
			lmean = mean(lista)
			limstdev = 2 * stdev(lista)
			cleaned_list = []
			for item in lista:
				if abs(item - lmean) < limstdev:
					cleaned_list.append(item)
		#return cleaned_list
		return lista
		
	############################################################################################
	#####################	PLOTTING FUNCTIONS  ################################################	
	
	def matrixplot3d(self, mat, title=None, type="wireframe"):
		from numpy import outer,arange,ones 
		from matplotlib import axes3d 
		from pylab import figure,get_current_fig_manager,show,ioff
		fig = figure() 
		ax = axes3d.Axes3D(fig) 
	
		# Construct matrices for r and c values 
		rn,cn = mat.shape 
		c = outer(ones(rn),arange(cn*1.0)) 
		r = outer(arange(rn*1.0),ones(cn)) 
	
		if type=="wireframe": 
			ax.plot_wireframe(r,c,mat) 
		elif type=="surface": 
			# Sometimes fails for no obvious reason 
			ax.plot_surface(r,c,mat) 
		elif type=="contour": 
			# Works but not usually very useful 
			ax.contour3D(r,c,mat) 
			
			#clim(0,1.1)
		else:
			raise ValueError("Unknown plot type "+str(type)) 
		#contourf(mat, 10, cmap=cm.hot)
		ax.set_xlabel('R') 
		ax.set_ylabel('C') 
		ax.set_zlabel('Value') 
	
		if title: 
			try: 
				manager = get_current_fig_manager() 
				manager.window.title(title) 
			except: 
				pass 
		ioff()
		show._needmain=True
		show() 
				
	def plot_matrix(self):
		self.matrixplot3d(self.cued_array,"RT dependency, Cued trials","wireframe")
		self.matrixplot3d(self.uncued_array,"RT dependency, Uncued trials","wireframe")
		self.matrixplot3d((self.rt_diff),"RT dependency, Uncued - Cued","wireframe")
		fig = figure()
		index = 0
		for i in self.ctoa_range:
			plot(self.ctd_range, self.rt_diff[index,:])
			index+=1
		show() 
	
	############################################################################################
	#####################	  DEBUGGING FUNCTIONS     ##########################################
	
	
	############################################################################################
	#####################	FILE MANAGEMENT FUNCTIONS   ########################################
			
	def save_and_close(self):
		self.save()
		self.close()

	def save(self):
		self.h5file.flush()

	def close(self):
		self.h5file.close()	
		

############################################################################################
#####################	MAIN  ##############################################################	

if __name__ == "__main__":

	#import scipy as s 
	
	data_analisis = DataAnalysis()
	data_analisis.simple_stats()
	data_analisis.plot_matrix()
	data_analisis.save_and_close()
    	
    	
    	
    	
    		
    	
