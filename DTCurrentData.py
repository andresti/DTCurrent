import re
import time
import datetime
import numpy as np
from os import walk
import math

# loads CMS DT current log files and returns average currents

class DTCurrentData(object):
	def __init__(self, path=''):
		# initial values filled during loading
		self.loaded = False
		self.path = ""
		self.dates = []
		self.times = []
		self.timestamps = []
		self.luminosity = []
		self.ramses = []
		self.ramsesName=""
		self.fill = ""
		self.currents = None
		self.background = None
		self.PMIL5501 = []
		self.PMIL5502 = []
		self.PMIL5511 = []
		self.PMIL5512 = []
		self.PMIL5513 = []
		self.PMIL5514 = []
		self.PMIL5515 = []
		self.PMIL5521 = []
		self.PMIL5522 = []
		self.PMIL5531 = []
		
		# valid filter options
		self.valid_wheels = np.array([-2,-1,0,1,2])
		self.valid_stations = np.array([1,2,3,4])
		self.valid_sectors = np.array([1,2,3,4,5,6,7,8,9,10,11,12])
		self.valid_superlayers = np.array([1,2,3])
		self.valid_layers = np.array([1,2,3,4])
		self.valid_wires = ["wire0", "wire1", "cathode"]
		
		# autoload data if path is specified
		if path:
			self.load_path(path)
	
	# look for files in dir
	def load_path(self, path):
		self.path = path.rstrip('/')+'/'
		_, _, files = walk(self.path).next()
		files_nr = 0
		#print files
		for file in files:
			if file=="RamsesFile.txt":
				print('FoundRamses')
				self.ramsesName = self.path +"RamsesFile.txt"
        
		for file in files:
            #self.load_fileRamses(self.path + ramsesName)
			m = re.search("^W(M|0|P)([0-2])_MB([1-4])_S([0-9]{2})(L|)\.txt$", file)
			if not m:# filename is not in the correct form: eg WM2_MB1_S07.txt
				continue
			print file
			self.load_file(self.path + file)
			files_nr += 1
		
		print('Loaded {files} files from path {path}'.format(files=files_nr, path=path))
		self.loaded = True
			
		# check which wheels, stations and sectors files have been found
		wheels = []
		for wheel in self.valid_wheels:
			_r = self.get(wheel=wheel)
			if _r is not None and _r.max() > 0:
				wheels.append(wheel)
		self.wheels = np.array(wheels)
				
		stations = []
		for station in self.valid_stations:
			_r = self.get(station=station)
			if _r is not None and _r.max() > 0:
				stations.append(station)
		self.stations = np.array(stations)
				
		sectors = []
		for sector in self.valid_sectors:
			_r = self.get(sector=sector)
			if _r is not None and _r.max() > 0:
				sectors.append(sector)
		self.sectors = np.array(sectors)
			
	# load one txt file
	def load_fileRamses(self, filename):
		print filename
		dates = []
		times = []
		luminosity = []
		timestamps = []
		ramsesData =[]
		ramsesDataPlus =[]
		ramsesDataMinus=[]
		with open(filename) as fp:
			for line_nr, line in enumerate(fp):
                #print line
				if line_nr <2:
					continue
				data = line.split()
				dates.append(data[0])
				times.append(data[1])
                #print data[0]+' '+data[1]
				timestamps.append(datetime.datetime.strptime(data[0]+' '+data[1], "%d-%m-%Y %H:%M:%S"))
				luminosity.append(float(data[3]))
				ramsesData.append([float(i) for i in data[7:]])
		luminosity = np.array(luminosity)
		ramsesData = np.array(ramsesData)
		imax = np.argmax(luminosity)
		ramsesData = ramsesData[imax:]
		luminosity = luminosity[imax:]
    
	def load_file(self, filename):
		dates = []
		times = []
		timestamps = []
		luminosity = []
		currents = []
		ramsesData =[]
		app =[]
		PMIL5501 = []
		PMIL5502 = []
		PMIL5511 = []
		PMIL5512 = []
		PMIL5513 = []
		PMIL5514 = []
		PMIL5515 = []
		PMIL5521 = []
		PMIL5522 = []
		PMIL5531 = [] 

		# read file contents
		with open(filename) as fp:
			for line_nr, line in enumerate(fp):
				if line_nr == 0:
					# file header
					# File for chamber WP2_MB1_S10 for Fill 2984 created at 18-08-2012 09:35:21
					m = re.search("^File for chamber (.+?) for Fill ([0-9]+?) created at ([0-9\-]+?) ([0-9:]{8})", line)
					if not m:
						print("File header is in wrong format")
						return
					chamber, self.fill, _, _ = m.groups()
					
					# parse wheel, station and sector number from chamber name
					chamber_p = re.search("^W(M|0|P)([0-2])_MB([1-4])_S([0-9]{2})(L|)$", chamber)
					if not chamber_p:
						print("Unknown chamber syntax {chamber} in file {file}".format(chamber=chamber, file=filename))
						return
					mp0, wheel_abs, station_str, sector_str, _ = chamber_p.groups()
					wheel = int(wheel_abs) * (1 if mp0 is 'P' else -1)
					station = int(station_str)
					sector = int(sector_str)
				elif line_nr == 1:
					# tabs info
					#          Date     Time      State       Lumi   L1W0    L1W1   L1Cha   L2W0
					continue
				else:
					# data
					#    18-08-2012 09:35:21    STANDBY       0.65  0.000   0.000   0.000  0.000
					data = line.split()
					if not (data[2] == "ON"):# status is RAMPING or STANDBY
						continue
					dates.append(data[0])
					times.append(data[1])
					timestamps.append(datetime.datetime.strptime(data[0]+' '+data[1], "%d-%m-%Y %H:%M:%S"))
					luminosity.append(float(data[3]))
					currents.append([float(i) for i in data[4:]])
		if (self.ramsesName == self.path +"RamsesFile.txt"):
			with open(self.ramsesName) as fp:
				for line_nr, line in enumerate(fp):
					if (line_nr <2):
						continue
					dataRam = line.split()
					if not (dataRam[2] == "ON"):# status is RAMPING or STANDBY
						continue
					PMIL5501.append(float(dataRam[7]))
					PMIL5502.append(float(dataRam[8]))
					PMIL5511.append(float(dataRam[9]))
					PMIL5512.append(float(dataRam[10]))
					PMIL5513.append(float(dataRam[11]))
					PMIL5514.append(float(dataRam[12]))
					PMIL5515.append(float(dataRam[13]))
					PMIL5521.append(float(dataRam[14]))
					PMIL5522.append(float(dataRam[15]))
					PMIL5531.append(float(dataRam[16]))
					
		
		# use numpy arrays (easier to manipulate)
		luminosity = np.array(luminosity)
		currents = np.array(currents)
		PMIL5501 = np.array(PMIL5501) 
		PMIL5502 = np.array(PMIL5502)
		PMIL5511 = np.array(PMIL5511)
		PMIL5512 = np.array(PMIL5512)
		PMIL5513 = np.array(PMIL5513)
		PMIL5514 = np.array(PMIL5514)
		PMIL5515 = np.array(PMIL5515)
		PMIL5521 = np.array(PMIL5521)
		PMIL5522 = np.array(PMIL5522)
		PMIL5531 = np.array(PMIL5531)

		# calculate background current (bg=mean values where state=ON and luminosity<10 at the beginning)
		bgrows = np.argmax(luminosity > 10)
		background = currents[: bgrows].mean(0)
		
		# remove rows with small luminosity from the beginning (during ramping)
		imax = np.argmax(luminosity)
		#final = np.find_nearest( luminosity, 2300 )
		currents = currents[imax:]
		luminosity = luminosity[imax:]
		ramsesData = ramsesData[imax:]
		PMIL5501 = PMIL5501[imax:]
		PMIL5502 = PMIL5502[imax:]
		PMIL5511 = PMIL5511[imax:]
		PMIL5512 = PMIL5512[imax:]
		PMIL5513 = PMIL5513[imax:]
		PMIL5514 = PMIL5514[imax:]
		PMIL5515 = PMIL5515[imax:]
		PMIL5521 = PMIL5521[imax:]
		PMIL5522 = PMIL5522[imax:]
		PMIL5531 =PMIL5531[imax:]
		
	
		
		# number of different options
		wheels = len(self.valid_wheels)
		stations = len(self.valid_stations)
		sectors = len(self.valid_sectors)
		superlayers = len(self.valid_superlayers)
		layers = len(self.valid_layers)
		wires = len(self.valid_wires)
		rows = len(currents)
		
		# create array to hold ALL files data
		if self.currents is None:
			#print PMIL5501
			#print luminosity
			shape = (wheels, stations, sectors, superlayers, layers, wires, rows)
			self.currents = np.ma.array(np.zeros(shape, dtype=np.float), mask=True)
			self.background = np.ma.array(np.zeros(shape, dtype=np.float), mask=True)
			self.luminosity = luminosity
			self.PMIL5501 = PMIL5501
			self.PMIL5502 = PMIL5502
			self.PMIL5511 = PMIL5511
			self.PMIL5512 = PMIL5512 
			self.PMIL5513 = PMIL5513 
			self.PMIL5514 = PMIL5514 
			self.PMIL5515 = PMIL5515
			self.PMIL5521 = PMIL5521
			self.PMIL5522 = PMIL5522 
			self.PMIL5531 = PMIL5531 

			
		# insert this chamber data to global current data
		if station == 4:
			superlayers -= 1
		rows = min(rows, self.currents.shape[6])
		shape = (superlayers, layers, wires, rows)
		self.currents[wheel+2, station-1, sector-1, :superlayers, :, :, :rows] = currents[:rows].T.reshape(shape)
		self.background[wheel+2, station-1, sector-1, :superlayers, :, :, :rows] = np.tile(background, rows).reshape((-1,len(background))).T.reshape(shape)
		
	# get mean values using specified filters
	def get(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires', fit=None, get_slope=None, background=False,get_intercept=None,Usemean = True):
		if not self.loaded:
			print("Data file is not loaded")
			return
		
		# subtract background (default) or use original values
		if background:
			c = self.currents
			csum = self.currents
		else:
			c = self.currents - self.background
			csum = self.currents - self.background
		
		# filter by wheel
		if wheel is None:
			c = c.mean(0)
			csum = csum.sum(0)
		elif wheel in self.valid_wheels:
			c = c[wheel+2]
			csum = csum[wheel+2]
		else:
			print("wheel value should be " + '|'.join(map(str, self.valid_wheels)) + "|None")
			return
			
		# filter by station
		if station is None:
			c = c.mean(0)
			csum = csum.sum(0)
		elif station in self.valid_stations:
			c = c[station-1]
			csum = csum[station-1]
		else:
			print("station value should be " + '|'.join(map(str, self.valid_stations)) + "|None")
			return
			
		# filter by sector
		if sector is None:
			c = c.mean(0)
			csum = csum.sum(0)
		elif sector in self.valid_sectors:
			c = c[sector-1]
			csum = csum[sector-1]
		else:
			print("sector value should be " + '|'.join(map(str, self.valid_sectors)) + "|None")
			return
			
		# filter by superlayer
		if superlayer is None:
			c = c.mean(0)
			csum = csum.sum(0)
		elif superlayer in self.valid_superlayers:
			c = c[superlayer-1]
			csum = csum[superlayer-1]
		else:
			print("superlayer value should be " + '|'.join(map(str, self.valid_superlayers)) + "|None")
			return
			
		# filter by layer
		if layer is None:
			c = c.mean(0)
			csum = csum.sum(0)
		elif layer in self.valid_layers:
			c = c[layer-1]
			csum = csum[layer-1]
		else:
			print("layer value should be " + '|'.join(map(str, self.valid_layers)) + "|None")
			return
			
		# filter by wire
		if wire=="wires":
			c = (c[0] + c[1]) * 0.5
			if csum[0].all() == 0:
				csum[0] = csum[1]
			if csum[1].all() == 0:
				csum[1] = csum[0]
			csum = csum[0] + csum[1]
		elif wire == "wire0":
			c = c[0]
			csum = csum[0]
		elif wire == "wire1":
			c = c[1]
			csum = csum[1]
		elif wire == "cathode":
			c = c[2]
			csum = csum[2]
		else:
			print("wire value should be wire0|wire1|wires|cathode")
			return
		
		# linear regression
		if fit or get_slope or get_intercept:
			# fit only values above 0 (useful in cathode plots, where current vs lumi goes like 0000001234)
			mask1 = c.data > 0
			#print self.luminosity
			#print self.luminosity.data
			#mask1 = self.luminosity >2000  and self.luminosity <2300 and  c.data >0.
			mask1sum = csum.data > 0
			
			# remove points that differs more than 0.02*3 from nearby values mean (outliers)
			mask2 = np.insert((c[1:-1]*2 - c[:-2] - c[2:]) < 0.05 * 3, [0, -1], [True, True])
			mask2sum = np.insert((csum[1:-1]*2 - csum[:-2] - csum[2:]) < 0.05 * 3, [0, -1], [True, True])
			mask = mask1 * mask2 * ~c.mask
			masksum = mask1sum * mask2sum * ~csum.mask
			
			if (not Usemean):
				intercept = 0
				if mask.sum() < 10:# less than 10 points after masking, dont fit
					slope = 0
				else:
					# current = slope * luminosity
					# slope, = np.linalg.lstsq(self.luminosity[:,np.newaxis], retval)[0]
					slope, intercept = np.linalg.lstsq(np.vstack([self.luminosity, np.ones(len(self.luminosity))]).T, c)[0]
					# current = slope * luminosity + intercept
					#slope, intercept = np.linalg.lstsq(np.vstack([self.luminosity[mask], np.ones(len(self.luminosity[mask]))]).T, c[mask])[0]
			
				# return slope or fitted data?
				if get_slope:
					return slope
				
				if get_intercept:
					return intercept
				return slope * self.luminosity + intercept
			
            #return c
				
			else:
				intercept = 0
				if masksum.sum() < 10:# less than 10 points after masking, dont fit
					slope = 0
				else:
					# current = slope * luminosity
					# slope, = np.linalg.lstsq(self.luminosity[:,np.newaxis], retval)[0]
				
					# current = slope * luminosity + intercept
					slope, intercept = np.linalg.lstsq(np.vstack([self.luminosity[masksum], np.ones(len(self.luminosity[masksum]))]).T, csum[masksum])[0]
			
				# return slope or fitted data?
				if get_slope:
					return slope
				
				if get_intercept:
					return intercept
				return slope * self.luminosity + intercept
			
            #return csum
		if (not Usemean):
			print 'Returning c'
			return c
		else:
			return csum
		
	# return slope: d(current)/d(luminosity)
	def slope(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires',Usemean = True):
		return self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire, get_slope=1,Usemean = Usemean)
		
	def intercept(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires',Usemean = True):
		return self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire,background=True,get_intercept=1,Usemean = Usemean)
		
	
	def WireLengh(self,wheel=None, station=None, sector=None, superlayer=None, layer=None):
		if (station ==1):
			NwiresPhi = 196
			L_theta = 202.7
			L_Phi = 236.8
			NwiresTheta = 228
			if (wheel ==1 and sector==4) or (wheel ==-1 and sector==3):
				L_Phi = 197.8
				NwiresTheta = 188
		if (station ==2):
			NwiresPhi = 238
			L_theta = 249
			L_Phi = 236.8
			NwiresTheta = 228
			if (wheel ==1 and sector==4) or (wheel ==-1 and sector==3):
				L_Phi = 197.8
				NwiresTheta = 188
		if (station ==3):
			NwiresPhi = 286
			L_theta = 301.
			L_Phi = 236.8
			NwiresTheta = 228
			if (wheel ==1 and sector==4) or (wheel ==-1 and sector==3):
				L_Phi = 197.8
				NwiresTheta = 188
		if (station ==4) and ((sector >=1 and sector<=3) or (sector >=5 and sector<=7)):
			NwiresPhi = 386
			L_theta = 0
			L_Phi = 236.8
			NwiresTheta = 0
			if (wheel ==-1 and sector==3):
				L_Phi = 197.8
		if (station ==4) and (sector ==8 or sector==12) :
			NwiresPhi = 366
			L_theta = 0
			L_Phi = 236.8
			NwiresTheta = 0
		if (station ==4) and (sector ==9 or sector==11) :
			NwiresPhi = 190
			L_theta = 0
			L_Phi = 236.8
			NwiresTheta = 0
		if (station ==4) and (sector==4):
			NwiresPhi = 572
			L_theta = 0
			L_Phi = 236.8
			NwiresTheta = 0
			if (wheel ==1) :
				L_Phi = 197.8
		if (station ==4) and (sector==10):
			NwiresPhi = 476
			L_theta = 0
			L_Phi = 236.8
			NwiresTheta = 0
			
		if layer in self.valid_layers:
			if (superlayer ==2) and (station <4):
				return L_theta* NwiresTheta/4
			else:
				return L_Phi * NwiresPhi/4
		if (layer is None) and (superlayer in self.valid_superlayers):
			if (superlayer ==2) and (station <4):
				return L_theta*NwiresTheta
			else:
				return L_Phi*NwiresPhi
		if (layer is None) and (superlayer is None):
			return L_theta*NwiresTheta + L_Phi*NwiresPhi*2
		
	def meanCharge(self , wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires',Usemean = 1,time=5.33*math.pow(10,7)):
		slope =self.slope(wheel = wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire='wires',Usemean = 1 )
		inter = self.intercept(wheel = wheel, station=station, sector=sector, superlayer=superlayer,layer=layer, wire='wires',Usemean = 1 )
		current4000= slope *75000 + inter
		currentCm = current4000/self.WireLengh(wheel = wheel, station=station, sector=sector, superlayer=superlayer, layer=layer)
				
		return currentCm * time *math.pow(10,-3)
	
	# return max current
	def maxcurrent(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		return self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire, background=True).max()
		
	# return current for each luminosity
	def current_vs_lumi(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires',Usemean = False):
		xs = self.luminosity
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire,Usemean = Usemean)
		return (xs, ys)
		
	def current_vs_PMIL5501(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5501
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5502(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5502
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5511(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5511
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5512(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5512
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5513(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5513
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5514(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5514
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5515(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5515
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5521(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5521
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5522(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5522
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	def current_vs_PMIL5531(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = self.PMIL5531
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
		return (xs, ys)
		
	# return fitted current for each luminosity
	def current_vs_lumi_fit(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires',Usemean = False):
		xs = self.luminosity
		ys = self.get(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire, fit=1,Usemean=Usemean)
		return (xs, ys)
		
	# return slope for each wheel
	def slope_vs_wheel(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.slope(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for wheel in self.wheels]
		return (self.wheels, np.array(ys))
	
	# return max current for each wheel
	def maxcurrent_vs_wheel(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.maxcurrent(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for wheel in self.wheels]
		return (self.wheels, np.array(ys))
		
	# return slope for each station
	def slope_vs_station(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.slope(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for station in self.stations]
		return (self.stations, np.array(ys))
		
	# return max current for each station
	def maxcurrent_vs_station(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		ys = [self.maxcurrent(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire) for station in self.stations]
		return (self.stations, np.array(ys))
		
	# return slope for each sector
	def slope_vs_sector(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = []
		ys = []
		for sector in self.sectors:
			slope = self.slope(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
			if slope > 0:
				xs.append(sector)
				ys.append(slope)
		return (np.array(xs), np.array(ys))
		
		# return slope for each sector
	def integrated_vs_sector(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = []
		ys = []
		if (station ==4) :
			sec4 ={8,1,3,4,5,7,12}
			for sector in sec4:
				slope = self.meanCharge(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
				if slope > 0:
					xs.append(sector)
					ys.append(slope)
		else:		
			for sector in self.sectors:
				slope = self.meanCharge(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
				if slope > 0:
					xs.append(sector)
					ys.append(slope)
		
		return (np.array(xs), np.array(ys))
		
	# return max current for each sector
	def maxcurrent_vs_sector(self, wheel=None, station=None, sector=None, superlayer=None, layer=None, wire='wires'):
		xs = []
		ys = []
		for sector in self.sectors:
			maxcurrent = self.maxcurrent(wheel=wheel, station=station, sector=sector, superlayer=superlayer, layer=layer, wire=wire)
			if maxcurrent > 0:
				xs.append(sector)
				ys.append(maxcurrent)
		return (np.array(xs), np.array(ys))
