# coding: utf-8
"""
Code to find temperature and density of the narrow line region of an 
AGN given its lines ratio of the ions O[III] or N[II] with the ions 
O[II] or S[II].

Usage:

  If the program runs from the main program (this code), the user will
  be asked first of all for the pair of ions from (O[III] or N[II]) and
  (S[II] or O[II]). Then, will be asked for the value of the lines 
  ratio for the selected two ions.

  Output:
    Related to the narrow lines region:
      Temperature in [K] and Density in [particles cm^-3]
  
  Otherwise, if the program is called as a library, then the proccedure 
  calling is like

  >>> import fivel_class as f
  >>> values = f.agn(J1=J1, J2=J2, ion1=ion1, ion2=ion2)
  >>> Temperature, Density = values.fivel()
  
  where J1 stands for the lines ratio of the ion1 (either O[III] or 
  N[II]) and J2 for the lines ratio of the ion2 (S[II] or O[II])


Authors:  Angel Daniel Martinez Cifuentes
          Julián Hernández
          Juan Camilo Torres Rojas
		
Date:     11 march, 2019

"""



# Calling libraries

from __future__ import print_function
from __future__ import division


import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import os
from lmfit import Model
from scipy.integrate import trapz, simps



# Start of class

class agn:
	
	
	"""
	  Definition of AGN class. The objects generated by this class are going
	  to have a "agn" class. This class returns a tuple when the fivel() 
	  definition inside the class is called.
	"""
	
	
	# Definition of __init__ variables inside the function (Python)
	
	def __init__(self, J1=122.72, J2=1.36, ion1="OIII",ion2="SII",show=True):
		self.J1 = J1
		self.J2 = J2
		self.ion1 = ion1
		self.ion2 = ion2
		self.show = show

		
		
	# Define physical constants in MKS
	
	h = 6.62607004e-34  # Planck constant
	c = 2.99792458e8    # Light speed
	k = 1.38064852e-23  # Boltzmann constant
	T = 1000            # Arbitrary temperature value
	
	

	# Dictionary of the constants for the ions (taken from [Astrophysics of gaseous
	# nebulae and Active Galactic Nuclei, Osterbrock, 2006])
	
	values = {'OIII':{'Ods':0.58, 'Lds':4363,'Ads':1.6, 'g':3.00,
					  'Ops':0.29, 'Lps':2321, 'Aps':2.3e-1,
					  'Odp1':2.29, 'Ldp1':4959, 'Adp1':6.8e-3,
					  'Odp2':2.29, 'Ldp2':5007, 'Adp2':2.0e-2},
			  'NII' :{'Ods':0.83, 'Lds':5755,'Ads':1.0, 'g':3.86,
					  'Ops':0.29, 'Lps':3063, 'Aps':3.3e-2,
					  'Odp1':2.64, 'Ldp1':6548, 'Adp1':9.8e-4,
					  'Odp2':2.64, 'Ldp2':6583, 'Adp2':3.0e-3},
			  'SII' :{'Oab':2.76, 'Oag':4.14, 'Obg':7.47,
					  'Aab':8.8e-4, 'Aag':2.6e-4, 'Lab':6731,
					  'Lag':6716},
			  'OII' :{'Oab':0.536, 'Oag':0.804, 'Obg':1.17,
					  'Aab':1.6e-4, 'Aag':3.6e-5, 'Lab':3726,
					  'Lag':3729}}

	
	# Define Exponential function
	
	def E(self,val,T):
		
		h = 6.62607004e-34  # Planck constant
		c = 2.99792458e8    # Light speed
		k = 1.38064852e-23  # Boltzmann constant
		y = np.exp(-h*c*10**10/(k*T*val))
		
		return y

	
	
	# Define lines ratio function

	def ratio(self,J, Ne=10, T=1000, ion='OIII'):
		

		"""
		  ### Lines ratio function
	
		  Function containing the lines ratio for a selected ion
		  (O[III] or N[II] and S[II] or O[II]).
		  
		  If the selected ion is either O[III] or N[II], then the function
		  returns (given an initial density), the temperature via calculating
		  a sign change (name pending). For computational speed, the temperature
		  value goes between 100 and 1e5 Kelvin. This range can be changed.
		  
		  Otherwise, if the selected ion is N[II] or O[II], then the 
		  function returns the density given a preliminar temperature
		"""
		
		
		# Constants values forthe available ions
		
		gd, gs = 5, 1    # Statistical Weigths
		gb, gg = 4, 6    # Statistical Weigths
		V = 8.6e-6    
		dic = self.values[ion]
		
		
		# Conditional selecting the avaliable ions
		
		###########################################################
		
		
		# Conditional with OIII and NII ions
		
		if ion=='OIII' or ion=='NII':
			
			g = dic['g']
			Ods,  Lds,  Ads  = dic['Ods'], dic['Lds'], dic['Ads']
			Ops,  Lps,  Aps  = dic['Ops'], dic['Lps'], dic['Aps']
			Opd1, Lpd1, Adp1 = dic['Odp1'], dic['Ldp1'], dic['Adp1']
			Opd2, Lpd2, Adp2 = dic['Odp2'], dic['Ldp2'], dic['Adp2']
			
			f1 = gd*Adp2*Lds/(gs*Ads*Lpd2)
			f2 = gs*(Ads+Aps)/(g*V*Ops)
			f3 = gs*Ads/(g*V*Opd2)
			f4 = gd*Adp2/(g*V*Opd2)
			
			sol = []

			def funct(T,J):
				fac = f1*self.E(-Lds,T)
				y1 = fac*(Ne/(T**0.5) + f2*(1+(f3/f2)*self.E(Lds,T)))# +\
					#Ne/(g*T**0.5)*(Ods/Opd2)*self.E(Lds,T))
				y2 = J*(Ne/(T**0.5)+f4)# + \
				#Ne*Ods/(g*Opd2)*self.E(Lds,T)*self.E(Lpd2,T)*self.E(-Lps,T))
				
				return y1, y2
			
			# Numpy function to return the value of intesection between the 
			# functions y1 and y2 returned in function func(self)
			
			Te = np.arange(100,1e5,0.1)
			AA = funct(Te,J)[0]
			BB = funct(Te,J)[1]
			idx = np.argwhere(np.diff(np.sign(AA - BB))).flatten()
			
			sol = Te[idx]
			
			return sol[0]
		
		###########################################################
		
		
		# Conditional with the SII and OII ions
		
		elif ion=='SII' or ion=='OII':
			
			val = self.values[ion]
			C = V/(T**0.5)
			Oab, Oag, Obg = val['Oab'], val['Oag'], val['Obg']
			Aab, Aag = val['Aab'], val['Aag']
			Lab, Lag = val['Lab'], val['Lag']

			ff1 = 1+(Obg/Oab)+(Obg/Oag)
			ff2 = gb/Oab
			ff3 = gg/Oag
			ff3/ff1
			
			up = (ff3/ff1)*Aag*Aab*(gg-J*gb)
			down = C*(J*gb*Aab - gb*Aag)
			
			sol = up/down
			
			# Return of the Density
			
			return sol
	
	
	
	
	# Fivel function to iterate
	
	#def fivel(J1,J2,ion1='OIII',ion2='SII',show=True):
	def fivel(self):
		
		
		"""
		  ### Iteration Function
		
		  Function to iterate and find both the temperature and density from
		  the above function ratio().
		  
		  This can be done in two ways. The first one is selecting the ion1 as
		  either OIII or NII, and the second one selecting SII or NII for the 
		  ion1. 
		  
		  If the first method is selected, the input density (to find
		  temperature for 2p3-like ions) is 1x10ˆ4 particles per cm3 which is
		  totally arbitrary and do not interfer with the result. If the slected 
		  density is a few magnitude orders above the resulting one, then the 
		  iteration will converge in one more step, while if the value of the
		  density is similar to the calculated, the iteration will converge in
		  fewer steps.
		  
		  If the second method is selected, then a similar proccess to the one
		  described above is done, just for this case the input parameter is
		  a temperature of 10000 kelvin. 
		  
		  The number of iteration, independent of the initial values for Density
		  and Temperature, will be less than 4 iterations.
		  
		  The final return of this function is the temperature and density as 
		  a python tuple in Kelvin and particles per cm3 respectively.
		"""
		
		
		###########################################################
		
		if self.ion1=='OIII' or self.ion1=='NII': #2p2
			X = 1e4 #value of density
			T = self.ratio(J=self.J1,Ne=X,ion=self.ion1)
			
			print("\n Begin of iteration\n")
			
			#Begin of "iteration"
			for i in range(0,4):
				RES = T
				Ne = self.ratio(J=self.J2,T=RES,ion=self.ion2)
				T = self.ratio(J=self.J1,Ne=Ne,ion=self.ion1)
				if self.show:
					print("  Iteration {}\n Ne  {}  [part/cm3]\n T   {}  [K]\n".format(i+1,Ne,RES))
			print(" Done!\n")
			
		###########################################################
		
		elif self.ion1=='SII' or self.ion1=='OII': #2p3
			X = 1e4 #value of Temperature
			Ne = self.ratio(J=self.J2,T=X,ion=self.ion2)
			print("\n Begion of iteration\n")
			
			#Begin of "iteration"
			for i in range(0,4):
				RES = Ne
				T = self.ratio(J=self.J2,Ne=RES,ion=self.ion2)
				Ne = ratio(J=J1,T=T,ion=ion1)
				if self.show:
					print("  Iteration {}\n Ne  {}  [part/cm3]\n T   {}  [K]\n".format(i+1,RES,T))
			print(" Done!\n")
			
		#Return Temperature and Density 
		return T, Ne





	
	



# Beginning of spectrum class


class spectrum:
	
	"""
	 Calculation of the area under the spectral flux function
	 for an AGN spectrum.
	"""
	
	
	def __init__(self,data,header=False,z=None):
		
		self.data = data
		self.header = header
		self.z = z
	
	
	def read(self,data,header,z=None):
		
		if isinstance(data,str):
			if z is None:
				print('Provide a Redshift')
				print('Exit')
				exit()
			else:
				array = fits.getdata(self.data,0)
				x, y = [], []  #Wavelength and flux
				for i in range(len(array)):
					y.append(array[i][0])
					x.append(10**array[i][1])
				x = np.array(x)
				y = np.array(y)
				xnew = x/(z+1)
				if header == True:
					header = fits.getheader(data,0)
					return xnew, y, header
				else:
					return xnew, y
		else:
			print('Not valid dataset ... Abort')
			exit()


	def plot(self):
		
		if self.header == True:
			x_axis, y_axis, head = self.read(self.data,self.header)
		else:
			x_axis, y_axis = self.read(self.data,self.header)
		
		plt.figure(figsize=(8,5))
		plt.plot(x_axis,y_axis)
		plt.grid()
		plt.ylabel(r'Flux $[10^{17}$ erg cm$^{-2}$ s$^{-1}$ $\AA^{-1}$]')
		plt.xlabel(r'Wavelength [$\AA$]')
		plt.show()


	def limits(self,statistics=False,plot=True,ax=None,
		savefig=False,show_model=False):
		
		
		
		if self.header == True:
			x_axis, y_axis, head = self.read(self.data,self.header,self.z)
		else:
			x_axis, y_axis = self.read(self.data,self.header,self.z)
		
		
		def gaussian(x, amp, cen, wid):
			return (amp/(np.sqrt(2*np.pi)*wid))*np.exp(-(x-cen)**2/(2*wid**2))


		def eqw(lambda1,lambda2,topflux,bottomflux):
			a = topflux-bottomflux
			sigma = (lambda1-lambda2)/2.35
			A = a*sigma*np.sqrt(2*np.pi)/topflux
			return A
		

		def plot_fit(ax,fit,x_range,y_range,X,Y,mini=0,area=0.0,ind=0):
			if ax is None:
				ax = plt.gca()
			ax.plot(x_range,y_range+mini,'o-',color='b')
			ax.plot(X,Y+mini,'-',label='Gaussian function',color='red')
			ax.plot(x_range,fit+mini,'o--',label='Gaussian Fit',color='y')
			plt.title('Area: {0:.3f}'.format(area))
			plt.ylabel(r'Flux $[10^{17}$ erg cm$^{-2}$ s$^{-1}$ $\AA^{-1}$]')
			plt.xlabel(r'Wavelength [$\AA$]')
			plt.legend(loc=2)
			#plt.grid()
			if savefig == True:
				v = ind+1
				plt.savefig(str(v)+'gaussian.png')
			else:
				plt.savefig("temp.png")
				os.system("rm -rf temp.png")

			plt.pause(1) # <-------
			#input("<Hit Enter To Close>")
			plt.waitforbuttonpress(0)
			plt.close()

			plt.show()


		def statistics_fit(y_axis,x_range,y_range,x1,x2,x01,x02,X,Y):
			maxy = max(y_axis[x1-1:x2+1])
			miny = min(y_axis[x1-1:x2+1])
			equi = eqw(x01,x02,maxy,miny)
			print('\nStatistics\n')
			print(' Min Value:  {0:.3f}  Flux'.format(miny))
			print(' Max Value:  {0:.3f}  Flux'.format(maxy))
			print(' Lambda1:    {0:.3f}  Å'.format(x_range[0]))
			print(' Lambda2:    {0:.3f}  Å\n'.format(x_range[-1]))
			print(" Equivalent Width:  {}\n".format(equi))
			print(" Area:")
			print("   Trapezoid:   {}\n   Simpson:     {}".format(trapz(Y,X), simps(Y,X)))
			
		
		def windows(x_axis,y_axis,wavelength1=6734,wavelength2=6760, legend='6716$\AA$',line=4382.4):
			
			xx1 = np.where(abs(x_axis-wavelength1+1) <= 1)[0][0]
			xx2 = np.where(abs(x_axis-wavelength2-2) <= 1)[0][0]
			#maxvaly = max(y_axis[xx1:xx2])
			#maxvalx = np.where(y_axis == maxvaly)[0][0]
			#print(maxvalx)
			plt.plot(x_axis[xx1:xx2],y_axis[xx1:xx2],'o-',color='b',label=legend)
			#plt.axvline(x=maxvalx,linewidth=3,alpha=0.7)
			plt.ylabel(r'Flux $[10^{17}$ erg cm$^{-2}$ s$^{-1}$ $\AA^{-1}$]')
			plt.xlabel(r'Wavelength [$\AA$]')
			plt.grid()
			plt.legend(loc=2)
			print("Please select two regions of the graph ")
			x = plt.ginput(2,show_clicks=True)
			x01 = x[0][0]
			x02 = x[1][0]
			return x01,x02
		
		
		def lines(num=4):
			
			# Set the limit to show the plot for the selected ions
			waves = [[6706,6732,'S[II]: 6716$\AA$',6718],[6723,6742,'S[II]: 6731$\AA$',6732],
			[4354,4372,'O[III]: 4363$\AA$',4365],[4954,4970,'O[III]: 4959$\AA$',4982.0],
			[5002,5013,'O[III]: 5007$\AA$',5030.3]]
			
			x01, x02 = windows(x_axis=x_axis,y_axis=y_axis,wavelength1=waves[num][0],
			wavelength2=waves[num][1],legend=waves[num][2],line=waves[num][3])
			
			x1 = np.where(abs(x_axis-x01+1) <= 1)[0][0]
			x2 = np.where(abs(x_axis-x02-2) <= 1)[0][0]
			
			if y_axis[x1] <= y_axis[x2]:
				mini = y_axis[x1]
			else:
				mini = y_axis[x2]

			x_range = x_axis[x1:x2]
			y_range = y_axis[x1:x2]-mini

			gmodel = Model(gaussian)
			result = gmodel.fit(y_range,x=x_range,amp=1000,cen=x_range[0],wid=1.5)
			
			amp = result.best_values['amp']
			cen = result.best_values['cen']
			wid = result.best_values['wid']
			X = np.linspace(x_range[0],x_range[-1],1000)
			Y = gaussian(X, amp=amp, cen=cen, wid=wid)
			
			
			if show_model == True:
				print(gmodel.param_names)
				print(result.fit_report(show_correl=False))
				result.plot()
				print(result.best_values)
			else:
				pass
				
				
			AREA = trapz(Y,X)
			
			if plot == True:
				plot_fit(ax,result.best_fit,x_range,y_range,X,Y,mini,area=AREA,ind=num)
			else:
				#pass
				plt.show()
			
			
			if statistics == True:
				statistics_fit(y_axis,x_range,y_range,x1,x2,x01,x02,X,Y)
			else:
				pass
			
			if self.header == True:
				return AREA,result.best_fit,x_axis,y_axis,X,Y,head
			else:
				return AREA,result.best_fit,x_axis,y_axis,X,Y
		
		area = []
		for i in range(0,5):
			area.append(lines(i)[0])
		
		return area




####################


def calculation(name=None, ion1=None, ion2=None, statistics=False, header=False, plot=True, savefig=False, ax=None, show_model=False, iteration=True, plot_spectrum=False,z = 0.00420765,**kwargs):
	
	
	if not name:
		print('Please provide a .fits file from SDSS. ')
		print('Exiting...')
		exit()

	def message():
		print('-------------------------------------------------------')
		print(' Code to calculate the Temperature and Density of a set of given lines\n')
		print('  The user have to select two points of the graphic')
		print('  corresponding to the value of two wavelengths over')
		print('  which will be performed a gaussian fit\n')
		print('  The user will be asked for the lines to work with:')
		print('   Avaliable ions: ')
		print('     O[III] or N[II]\n     S[II]  or O[II]')
		print('  \n  After selecting the two points, press enter to pass the next flux\n')
		input('  < Press enter to continue > ')
		print(' ')

	message()
	
	if not ion1:
		i1 = float(input("  Type the number of the ion1\n    1:   O[III]\n    2:   N[II]\n"))
		if i1 == 1:
			ion1 = 'OIII'
		elif i1 == 2:
			ion1 = 'NII'
		else: 
			print("Number not defined")
			print("Exiting")
			exit()
	
	if not ion2:
		i2 = float(input("  Type the number of the ion2\n    1:   S[II]\n    2:   O[II]\n"))
		if i2 == 1:
			ion2 = 'SII'
		elif i2 == 2:
			ion2 = 'OII'
		else: 
			print("Number not defined")
			print("Exiting")
			exit()
	
	data = spectrum(data=name,header=header,z=z)
	
	if plot_spectrum is True:
		data.plot()
	
	A = data.limits(statistics=statistics,plot=plot,savefig=savefig,ax=ax,show_model=show_model)

	F6716, F6731 = A[0], A[1]
	F4363, F4959, F5007 = A[2], A[3], A[4]

	F2 = F6716/F6731
	F1 = (F5007 + F4959)/F4363


	A = agn(J1=F1,J2=F2,ion1=ion1,ion2=ion2,show=iteration)
	T, Ne = A.fivel()
	
	return T, Ne
	
	
if __name__=='__main__':
	
	
	def fluxes():
		data = 'data/spec-1070-52591-0072.fits'
		
		def message():
			print('-------------------------------------------------------')
			print(' Code to calculate the fluxes of a set of given lines\n')
			print('  The user have to select two points of the graphic')
			print('  corresponding to the value of two wavelengths over')
			print('  which will be performed a gaussian fit\n')
			input('  < Press enter to continue > ')
			print(' ')
		
		message()
		
		data = spectrum(data,header=False,z = 0.00420765)
		#data.plot()
		A=data.limits(statistics=False,plot=True,savefig=False)
		print('\n Area\n  6716:   {0:.3f}\n  6731:   {1:.3f}\
		\n  4363:   {2:.3f}\n  4959:   {3:.3f}\
		\n  5007:   {4:.3f}'.format(A[0],A[1],A[2],A[3],A[4]))
		
		
	
	
	def fivel():
		print("---------------------------------\n")
		print(" PROGRAM FIVEL - PYTHON-TEST\n")
		i1 = float(input("  Type the number of the ion1\n    1:   O[III]\n    2:   N[II]\n"))
		if i1 == 1:
			ion1 = 'OIII'
		elif i1 == 2:
			ion1 = 'NII'
		else: 
			print("Number not defined")
			print("Exiting")
			exit()

		i2 = float(input("  Type the number of the ion2\n    1:   S[II]\n    2:   O[II]\n"))
		if i2 == 1:
			ion2 = 'SII'
		elif i2 == 2:
			ion2 = 'OII'
		else: 
			print("Number not defined")
			print("Exiting")
			exit()
		
		print("  Input the lines ratio for the {} ion:  ".format(ion1))
		J1 = float(input())
		print("  Input the lines ratio for the {} ion:  ".format(ion2))
		J2 = float(input())
		
		A = agn(J1=J1,J2=J2,ion1=ion1,ion2=ion2,show=True)
		T, Ne = A.fivel()
		print("  Temperature  {}\n  Density      {}".format(T,Ne))
	
	
	name = 'data/spec-1070-52591-0072.fits'
	name = 'data/spec-1369-53089-0157.fits'
	name = 'data/spec-1995-53415-0214.fits'
	#name = 'data/spec-2128-53800-0577.fits'
	z = 0.00420765
	z = 0.00267364 #1369
	z = 0.022513 #1995
	#z = 0.0165055 #2128
	#name = 'data/spec-1369-53089-0157.fits'
	
	T, Ne = calculation(name,z=z)
	
	
	
	exit()
	
	# Some values for other AGN
	
	### NGC 3227
	A = agn(J1=122.72,J2=1.36,ion1='OIII',ion2='SII')
	T, Ne = A.fivel()
	print("Temperature {}\nDensity     {}".format(T,Ne))


	### NGC 1068
	
	A = agn(J1=15.628,J2=1.228,ion1='OIII',ion2='SII')
	T, Ne = A.fivel()
	print("Temperature {}\nDensity     {}".format(T,Ne))
	
	### NGC 5548
	A = agn(J1=65.865,J2=1.523,ion1='OIII',ion2='SII')
	T, Ne = A.fivel()
	print("Temperature {}\nDensity     {}".format(T,Ne))
