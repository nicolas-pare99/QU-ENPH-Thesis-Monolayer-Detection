# -*- coding: ascii -*-
#from zaber_motion.ascii.all_axes import AllAxes as allaxes
from zaber_motion.ascii import Axis, AxisSettings, Connection, Device
from zaber_motion import Units, Library, CommandFailedExceptionData, Library, LogOutputMode
#from zaber_motion.ascii import AxisSettings as axis_settings


### Written for Zaber firmware version 7.37.15516
#this moidule was used for both gui version 1.0 and 2.0 stage control
#some functions may be legacy and not used anymore

Library.enable_device_db_store()
try:
	#pass
	import os
	Library.set_log_output(LogOutputMode.FILE, os.path.join("C:\\", "Users", "Queen's University","Desktop", "SCOPE", "microscope code [warning! raw code!]", "SCOPE","motion_library_log.txt"))
except:
	print("Log file could not be created/opened. Thhis sometimes happens if the stage is not connected with the USB. Check this")
class StageObject():
	def __init__(self):
		self.x = 0
		self.y = 0
		self.lcd_x = 0
		self.lcd_y = 0
		self.max_accel = 450.0 #800.0 #native units --- Its easier just t owork in these # 0 for maximum # I think 820 may be the max (or 880)
		self.max_vel = 20.0 #5.0# Units.VELOCITY_MILLIMETRES_PER_SECOND ##### equal to 209715 #native units
		self.rel_lcd_x = 0
		self.rel_lcd_y = 0
		self.raster_units = Units.LENGTH_MICROMETRES
		self.current_units = Units.LENGTH_CENTIMETRES
		self.drive_units=Units.LENGTH_CENTIMETRES
		self.drive_mode = 'POSITION'
		self.drive_mag = 0.0
		self.rel_reference = False
		self.is_homed = False
		self.is_parked = False
		self.step_size = None
		self.step_units=None
		self.zero_x = 0
		self.zero_y = 0
		self.rel_x =0
		self.rel_y =0
		self.busy = False
		self.device = None	
		self.device_id = None
		self.port_id = None
		self.prev_x_motion = None
		self.prev_y_motion = None
		self.x_backlash = 1.2 #in microns ### If a better value can be found, go for it. 
		self.y_backlash = 2.2 #in microns

		self.connection = None
		self.axis1 = None
		self.axis2 = None
		self.curr_msg = None
		###DANGERZONE
		self.y_max_limit_cm = 3.25 #DANGERZONE!!!!!  we need to adjust the maximum range of the stage so it does not hit the microscope condensor or body tube. Adjusting this value can severely screw up the microscope stage. 
		#self.x_max_limit = DANGERZONE  ---- setting this can seriously screw up the device. Only adjust this value to proper device parameters. ie - if the device has a maximum of 5cm, it is possible to set it to 50cm, and do serious damage. 
		self._x_position_prior_home = 0
		self._y_position_prior_home = 0
	def get_curr_msg(self):
		return self.curr_msg

	def set_curr_msg(self, txt):
		self.curr_msg = txt
		
		
	def set_device(self):
		try: 
			#print(self.get_connection().detect_devices())
			device_list = self.get_connection().detect_devices()
			print("Found {} devices".format(len(device_list)))
			#self.set_curr_msg("Found {} devices".format(len(device_list)))
			device = device_list[0]
			self.device = device
			
			#Library.set_log_output(LogOutputMode.FILE, o.path.join(os.getcwd(),"motion_library_log.txt"))
			
			self.axis1 = device.get_axis(2)
			#print(self.axis1.get_position())

			self.axis2 = device.get_axis(1)
			print(self.get_axis2())
			print(self.get_axis1())
			
			
			###DANGERZONE
			###
			###This line of code will arbitrarily set the maximum distance the stage can travel along a particular axis. 
			#Be very wary of what you are about to do
			#This can damage the stage
			#According to the documentation, the default limit.max variable for this stage is 320000 Units.NATIVE
			#This value is actually just below 5cm, so please don't try to change it to 5cm b/c the stage is labelled 5cm x 5cm .... its essentially 4.998cm 
			#Setting larger than this amount makes the motor think this is possible ---- bad idea
			#The y - axis four our stage must be limited to 3.65cm ---- so, perform a unit conversion when setting this value.
			#
			#DANGERZONE
			#self.axis1.settings.set('limit.max', 320000, Units.NATIVE) #warning --- needs different step value if changing microsteps.
			self.axis2.settings.set('limit.max', self.y_max_limit_cm, Units.LENGTH_CENTIMETRES)
			#----- untested self.axis1.settings.set('resolution', 128, Units.NATIVE)
			#------ untested  self.device.settings.set('resolution', 128, Units.NATIVE)
			#------ untested self.axis2.settings.set('resolution', 128, Units.NATIVE)
			msg = "\tPosition limits set.\n"
			
		except:
			print('No valid device has been set.')
			self.device = None
			self.axis1 = None
			self.axis2 = None
			self.set_curr_msg('Device has been set: '+ str(device))
			msg = "\tError applying position limit settings.\n"
		try:

			self.axis1.settings.set('maxspeed', self.max_vel, Units.VELOCITY_MILLIMETRES_PER_SECOND)
			self.axis2.settings.set('maxspeed', self.max_vel, Units.VELOCITY_MILLIMETRES_PER_SECOND)
			self.axis1.settings.set('accel', self.max_accel, Units.NATIVE)
			self.axis2.settings.set('accel', self.max_accel, Units.NATIVE)
			print("Max accleration: ", self.axis1.settings.get('accel', Units.NATIVE))
			print("Max speed: ", self.axis2.settings.get('maxspeed', Units.VELOCITY_MILLIMETRES_PER_SECOND))

			
			msg2 =	"\tMax speed: {:.2f} mm/s \n\tMax acceleration: {:.2f} in native step units\n\n".format(
					round(
						self.axis2.settings.get(
						'maxspeed', Units.VELOCITY_MILLIMETRES_PER_SECOND
						) 
						), 
						self.axis1.settings.get(
							'accel', Units.NATIVE
							) 
							)
							
			#print(device)
		except Exception as e:
			print(e)
			msg2 = "\tError applying settings. \n\n"
		finally:
			self.set_curr_msg('Device has been set: '+ str(device) +"\n\n" + msg + msg2)

	def get_device(self):
		return self.device
	def get_device_id(self):
		return self.device_id

	def get_axis1(self):
		return self.axis1

	def get_axis2(self):
		return self.axis2
		
	def set_port_id(self, port):
		if isinstance(port, str) and port[0:3] == 'COM':
			self.port_id = port
			print(f"Port ID set to {port}")
		else:
			print("Invalid port ID. It should start with 'COM'.")
	
	def get_port_id(self):
		if self.port_id is not None:
			return self.port_id
		else:
			print("Port ID is not set.")
			return None
	

	def set_connection(self, port):
		if isinstance(port, str) and port[0:3] == 'COM':
			self.connection = Connection.open_serial_port(port)
			self.set_port_id(port)
			print(f"Connection established on port {port}")
			print(self.get_connection())
		else:
			self.connection = None
	def get_connection(self):
		return self.connection


	def close_connection(self):
		try:
			self.set_is_parked(True)
		except Exception as e:
			print(f"Error setting parked state: {e}")
		current_connection = self.get_connection()
		if current_connection is not None:
			try:
				#print(f"Closing connection object: {type(current_connection)}")
				current_connection.close()
				print("Serial port close() called.")
			except Exception as e:
				print(f"Error closing serial port: {e}")
		else:
			print("No connection object to close.")
		self.set_connection(None)
		self.device = None
		self.device_id = None
		self.axis1 = None
		self.axis2 = None
		print('Successfully disconnected.')
		print('There are no devices or axes set up.')


	def set_x(self, val ):#= axis1.get_position()):
		self.x = val
	def get_x(self):
		return self.x
	def set_y(self, val ):#= axis2.get_position()):
		self.y = val
	def get_y(self):
		return self.y

	def update_lcd_x(self):#= axis1.get_position()):
		val = self.axis1.settings.convert_from_native_units('pos', self.axis1.get_position(), self.get_current_units())
		#print(val)
		self.lcd_x = val
	def get_lcd_x(self):
		return self.lcd_x
	def update_lcd_y(self):#= axis2.get_position()):
		val = self.axis2.settings.convert_from_native_units('pos', self.axis2.get_position(), self.get_current_units())
		#print(val)
		self.lcd_y = val
	def get_lcd_y(self):
		return self.lcd_y

	def update_rel_lcd_x(self):#= axis1.get_position()):
		#print(self.get_zero_x())
		#print('x-zero: ', self.get_zero_x())
		val = self.axis1.settings.convert_from_native_units('pos', self.axis1.get_position(), self.get_current_units()) - self.axis1.settings.convert_from_native_units('pos', self.get_zero_x(), self.get_current_units())
		#print('lcd_x_rel: ',val)
		
		self.rel_lcd_x = val
	def get_rel_lcd_x(self):
		return self.rel_lcd_x
	def update_rel_lcd_y(self):#= axis2.get_position()):
		val = self.axis2.settings.convert_from_native_units('pos', self.axis2.get_position(), self.get_current_units()) - self.axis2.settings.convert_from_native_units('pos', self.get_zero_y(), self.get_current_units())
		#print('lcd_y_val: ',val)
		self.rel_lcd_y = val
	def get_rel_lcd_y(self):
		return self.rel_lcd_y



	def get_pos(self):
		x_z = self.axis1.get_position()
		y_z = self.axis2.get_position()

		x_z = self.axis1.settings.convert_from_native_units('pos', x_z, self.get_current_units())
		y_z = self.axis2.settings.convert_from_native_units('pos', y_z, self.get_current_units())
		#u = self.get_current_units()
		self.set_curr_msg('Exported ({},{}) to OUTPUT.txt'.format(x_z,y_z))
		return x_z, y_z

	def get_pos_raster(self):
		x_pos = self.axis1.get_position()
		x_val = self.get_axis1().settings.convert_from_native_units('pos', x_pos, self.raster_units)
		y_pos = self.axis2.get_position()
		y_val = self.get_axis2().settings.convert_from_native_units('pos', y_pos, self.raster_units)

		#u = self.get_current_units()
		#self.set_curr_msg('Exported ({},{}) to OUTPUT.txt'.format(x_z,y_z))
		return x_val, y_val


	def set_current_units(self, units):
		self.current_units = units
	def get_current_units(self):
		return self.current_units

	def set_drive_units(self, units):
		self.drive_units = units
	def get_drive_units(self):
		return self.drive_units

	def set_drive_mode(self, dmode):
		self.drive_mode = dmode
	def get_drive_mode(self):
		return self.drive_mode

	def set_drive_mag(self, val):
		self.drive_mag = val
	def get_drive_mag(self):
		return self.drive_mag

	def set_rel_reference(self, bool):
		self.rel_reference = bool
	def get_rel_reference(self):
		return self.rel_reference


	def set_is_homed(self, bool):
		self.is_homed = bool
	def get_is_homed(self):
		return self.is_homed
	def set_step_size(self, val):
		self.step_size = val
	def get_step_size(self):
		return self.step_size
	def set_step_size_units(self, val):
		self.step_size_units = val
	def get_step_size_units(self):
		return self.step_size_units


	def set_is_parked(self, bool):
		if not self.get_is_parked():
			self.axis1.park()
			self.axis2.park()
		else:
			self.axis1.unpark()
			self.axis2.unpark()
		self.is_parked = bool
		print('Successfully changed Park status')	
	def get_is_parked(self):
		return self.is_parked
	def set_zero_x(self, val):
		self.zero_x = val
	def get_zero_x(self):
		return self.zero_x
	def set_zero_y(self, val):
		self.zero_y = val
	def get_zero_y(self):
		return self.zero_y


	def set_rel_x(self):
		val = self.get_x()-self.get_zero_x()
		self.rel_x = val
	def get_rel_x(self):
		return self.rel_x
	def set_rel_y(self):
		val = self.get_y()-self.get_zero_y()
		self.rel_y = val
	def get_rel_y(self):
		return self.rel_y
	def set_busy(self, bool):
		self.busy = bool	
	def get_busy(self):
		return self.busy


	#########################
	#########################
	def set_zero(self):
		#x_z = self.set_x(self.axis1.settings.convert_from_native_units('pos', self.axis1.get_position(), self.get_current_units()))
		x_z = self.axis1.get_position()
		#print(x_z)
		self.set_zero_x(x_z)
		
		y_z = self.axis2.get_position()
		self.set_zero_y(y_z)
		#print(y_z)
		print('Set Zero Point to: ({},{})'.format(x_z, y_z))

		x_z = self.axis1.settings.convert_from_native_units('pos', x_z, self.get_current_units())
		y_z = self.axis2.settings.convert_from_native_units('pos', y_z, self.get_current_units())
		#print(x_z)
		#print(y_z)
		msg = str('({},{})'.format(x_z,y_z))
		#print(msg)
		self.set_curr_msg(msg)
	
	def go_home(self, progress_callback=None):
		self.set_is_parked(False)
		print('Park Status: ',self.get_is_parked()  )
		x_z = self.axis1.get_position()
		y_z = self.axis2.get_position()
		self._x_position_prior_home = x_z
		self._y_position_prior_home = y_z
		print("Position prior to homing is ({:},{:})".format(x_z,y_z))

		self.axis1.home(wait_until_idle = True)
		self.axis2.home(wait_until_idle = True)
		self.set_is_homed(True)
		#print('Homing operation completed.')
		#self.unpark()
		self.set_zero()
		self.prev_x_motion = "RIGHT" #"LEFT"
		self.prev_y_motion = "DOWN" #"UP"
		#print('x = ',self.axis1.get_position())
		#print('y = ',self.axis2.get_position())
		#print('Successfully reset zero position')
		
	def park(self):
		if self.get_is_parked():
			print('Already Parked')
			self.set_curr_msg("Hey! I'm already parked!")
		else:
			print('Parking Stage ... ')
			self.set_curr_msg('Parking Stage ...')
			self.axis1.park()
			self.axis2.park()
			self.set_is_parked(True)
	def unpark(self):
		if self.get_is_parked():
			print('Unparking Stage....')
			self.set_curr_msg("Unparking Stage...")
			self.set_is_parked(False)
			self.axis1.unpark()
			self.axis2.unpark()
		else:
			print('Stage Not Parked')
			self.set_curr_msg('Hey! I am not currently parked!')
			
							

	def goto_x(self, step, units = None):
		try:
			if self.get_is_parked():
				self.unpark()
			if units is None:
				units = self.get_current_units()
			#print(str(units))
			self.x_correct(-step)
			if self.get_rel_reference():
				#print('Moving Relative')
				self.axis1.move_relative(step, units, wait_until_idle = False, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
				#self.set_rel_x()		
				
			else:
				self.axis1.move_absolute(step, units, wait_until_idle = False, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
				#self.set_x()
			x_pos = self.axis1.get_position()
			x_val = self.get_axis1().settings.convert_from_native_units('pos', x_pos, units)
			#print(x_val)
			self.set_x(x_val)
			#print(self.get_x())
		except:
			print('Operation Failed. Please see motor log.')
			print("Perhaps you told the stage to drive beyond its physical limits?")

	def goto_y(self, step, units):
		try:
			if self.get_is_parked():
				self.unpark()
			if units is None:
				units = self.get_current_units()
			self.y_correct(-step)
			if self.get_rel_reference():
				#self.y_correct(-step)
				#print('Moving Relative')
				
				self.axis2.move_relative(step,  units, wait_until_idle = False, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
				#self.set_rel_y()		
				
			else:
				self.axis2.move_absolute(step, units, wait_until_idle = False, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
				#self.set_y()
			
			y_pos = self.axis2.get_position()
			y_val = self.get_axis2().settings.convert_from_native_units('pos', y_pos, units)
			#print(y_val)
			self.set_y(y_val)
			#print(self.axis2.get_position())
			#print(self.get_y())
		except:
			print('Operation Failed. Please see motor log.')
			print("Perhaps you told the stage to drive beyond its physical limits?")
	
	
	def stop(self):
		self.axis1.stop(wait_until_idle=False)
		self.axis2.stop(wait_until_idle=False)
		self.set_curr_msg('Stage is now stopped.')
	

	def raster_x(self, step):
		#print("moving x=", step )
		self.x_correct(-step)
		self.axis1.move_relative(-step, Units.LENGTH_MICROMETRES, wait_until_idle = True, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
		x_pos = self.axis1.get_position()
		x_val = self.get_axis1().settings.convert_from_native_units('pos', x_pos, self.get_current_units())
		
		self.set_x(x_val)
		#print(self.get_x())

	def raster_y(self, step): 
		#print("moving y =", step)
		self.y_correct(-step)
		self.axis2.move_relative(-step, Units.LENGTH_MICROMETRES, wait_until_idle = True, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
		y_pos = self.axis2.get_position()
		y_val = self.get_axis2().settings.convert_from_native_units('pos', y_pos, self.get_current_units())
		
		self.set_y(y_val)
		#print(self.get_y())

	def y_correct(self, curr):
		prev = self.prev_y_motion
		if curr > 0:
			self.prev_y_motion = "UP"
		elif curr < 0:
			self.prev_y_motion = "DOWN"
		
		if prev is not self.prev_y_motion:
			neg = {"UP": -1, "DOWN": 1}
			#print("Correcting for backlash in Y")
			#try:
			self.axis2.move_relative(-1*neg[prev]*self.y_backlash, Units.LENGTH_MICROMETRES, wait_until_idle = True, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
			#except Exception:
			#	print("Stage unable to comply. Perhaps it is at a ")
			return 

	def x_correct(self, curr):
		prev = self.prev_x_motion
		if curr < 0:
			self.prev_x_motion = "RIGHT"
		elif curr > 0:
			self.prev_x_motion = "LEFT"
		
		if prev is not self.prev_x_motion:
			neg = {"RIGHT": -1, "LEFT": 1}
			#print("Correcting for backlash in X")
			self.axis1.move_relative(-1.0*neg[prev]*self.x_backlash, Units.LENGTH_MICROMETRES, wait_until_idle = True, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
			return 



	def move_x(self, step, curr_unit):
		try:
			if self.get_is_parked():
				self.unpark()
			#units = self.get_current_units()
			#print(str(self.get_drive_units()))
			if self.get_drive_mode() == 'SPEED':
				self.x_correct(-step)
				self.axis1.move_velocity(-step, curr_unit, acceleration = 0, acceleration_unit = Units.NATIVE)
				'''
				x_pos = self.axis1.get_position()
				x_val = self.get_axis1().settings.convert_from_native_units('pos', x_pos, self.get_current_units())
				print(x_val)
				self.set_x(x_val)
				print(self.get_x())
				#self.set_rel_x()
				# '''		
				
			else:
				#print('Moving Relative')
				self.x_correct(-step)
				self.axis1.move_relative(-step, curr_unit, wait_until_idle = False, velocity = 0 , velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
				#self.set_x()
			x_pos = self.axis1.get_position()
			x_val = self.get_axis1().settings.convert_from_native_units('pos', x_pos, self.get_current_units())
			#print(x_val)
			self.set_x(x_val)
			#print(self.get_x())
		except:
			print('Operation Failed. Please see motor log.')
			print("Perhaps you told the stage to drive beyond its physical limits?")			

	def move_y(self, step, curr_unit):
		try:
			if self.get_is_parked():
				self.unpark()
			#units = self.get_current_units()
			#print(str(self.get_drive_units()))
			if self.get_drive_mode() == 'SPEED':
				self.y_correct(-step)
				self.axis2.move_velocity(step, curr_unit, acceleration = 0, acceleration_unit = Units.NATIVE)
				'''
				y_pos = self.axis2.get_position()
				y_val = self.get_axis2().settings.convert_from_native_units('pos', y_pos, self.get_current_units())
				print(y_val)
				self.set_y(y_val)
				print(self.get_y())
				#self.set_rel_y()
				'''		
				
			else:
				#print('Moving Relative')
				self.y_correct(-step)
				self.axis2.move_relative(step, curr_unit, wait_until_idle = False, velocity = 0, velocity_unit = Units.NATIVE, acceleration = 0, acceleration_unit = Units.NATIVE)
				#self.set_x()
			y_pos = self.axis2.get_position()
			y_val = self.get_axis2().settings.convert_from_native_units('pos', y_pos, self.get_current_units())
			#print(y_val)
			self.set_y(y_val)
			#print(self.get_y())
		except:
			print('Operation Failed. Please see motor log.')
			print("Perhaps you told the stage to drive beyond its physical limits?")


if '__main__' == __name__:
	import pyautogui
	import time
	import datetime
	import calendar
	import os
	port = 'COM4'
	stage = StageObject()
	stage.set_connection(port)
	stage.set_device()
	stage.go_home()
	time.sleep(2)
	notdone = True
	
	while notdone:
		# MOVING THE MICROSCOPE
		uin = input("Enter command: ")
		if uin == 'home':
			stage.go_home()	
		elif uin == 'w':
			stage.move_y(0.5, Units.LENGTH_CENTIMETRES)
		elif uin == 's':
			stage.move_y(-0.5, Units.LENGTH_CENTIMETRES)
		elif uin == 'a':
			stage.move_x(-0.5, Units.LENGTH_CENTIMETRES)
		elif uin == 'd':
			stage.move_x(0.5, Units.LENGTH_CENTIMETRES)
		elif uin == 'c':
			folder = "C:\Users\Queen's University\Desktop\Detector\img_folder"

			today_str = datetime.today().strftime("%Y-%m-%d")
			new_folder = f"{folder}_{today_str}"

			os.makedirs(new_folder, exist_ok=True)

			MOVE_STEP = 20

			time.sleep(2)

			#mouse coordinates to open nikon software
			x = 750
			y = 1180

			#ideally, this should be replaced by a command that opens the right window, so it doesn't need to auto-click, or just click it yourself
			pyautogui.moveTo(x, y, duration=0.2)
			pyautogui.click()
			pyautogui.press('f4')
			time.sleep(10)

			#minimizing nikon software
			x = 1800
			y = 15

			pyautogui.moveTo(x, y, duration=0.2)
			pyautogui.click()


		elif uin == 'done':
			notdone = False

		# Defining a function that appends a timestamp to a file name
		def append_timestamp(filename):
			timestamp = calendar.timegm(time.gmtime())
			human_readable = datetime.datetime.fromtimestamp(timestamp).isoformat()
			filename_with_timestamp = filename + "_" + str(human_readable)
			return filename_with_timestamp
		
		# This line actually renames your file with a timestamp. Change to whatever path is actually being used
		os.rename(f"{new_folder}\test_image.tif", append_timestamp("{new_folder}\test_image.tif"))

	
	stage.goto_x(5*0.5, Units.LENGTH_CENTIMETRES)
	time.sleep(3)
	stage.goto_y(2.5, Units.LENGTH_CENTIMETRES)
	time.sleep(3)
	#for i in range(5):
	#	for j in range(5):
	#		stage.move_x(0.1, Units.LENGTH_CENTIMETRES)
	#		time.sleep(1)
	#	stage.move_x(-5*0.1, Units.LENGTH_CENTIMETRES)
	#	time.sleep(1)
	#	stage.move_y(0.1, Units.LENGTH_CENTIMETRES)
			
	stage.go_home()
	stage.close_connection()
