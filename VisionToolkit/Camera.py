# -*- coding:utf-8 -*- 


#
# Module to display live images from a camera
#


#
# External dependencies
#
import ctypes as ct
import sys
import threading
import numpy as np
import cv2
from PySide import QtCore
from PySide import QtGui
import Vimba


#
# Qt Widget to display the images from an Allied Vision camera (through Vimba)
#
class VmbCameraWidget( QtGui.QLabel ) :

	#
	# Signal sent by the image callback function called by Vimba
	#
	image_received = QtCore.Signal( np.ndarray )

	#
	# Initialization
	#
	def __init__( self, camera_id, parent = None ) :

		# Initialize QLabel
		super( VmbCameraWidget, self ).__init__( parent )

		# Change the window title
		self.setWindowTitle( 'Allied Vision Camera' )
		
		# Fix the widget size
		self.setFixedSize( 2452*0.3, 2056*0.3 )
		self.setScaledContents( True )
		
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		
		# Connect the signal to update the image
		self.image_received.connect( self.UpdateImage )
		
		# Create an indexed color table (grayscale)
		self.colortable = [ QtGui.qRgb( i, i, i ) for i in range( 256 ) ]
		
		# Initialize the Vimba driver
		Vimba.VmbStartup()

		# Initialize the camera
		self.camera = Vimba.VmbCamera( camera_id )
		
		# Connect the camera
		self.camera.Open()

		# Configure the sync out signal
		Vimba.vimba.VmbFeatureEnumSet( self.camera.handle, 'SyncOutSource', 'Exposing' )

		# Configure fixed rate trigger
		Vimba.vimba.VmbFeatureEnumSet( self.camera.handle, 'TriggerSource', 'FixedRate' )
		Vimba.vimba.VmbFeatureFloatSet( self.camera.handle, 'AcquisitionFrameRateAbs', ct.c_double( 7.4 ) )
	
		# Start image acquisition
		self.camera.StartCapture( self.FrameCallback )

	#
	# Receive the image sent by the camera
	#
	def FrameCallback( self, frame ) :
		
		# Send the image to the widget through a signal
		self.image_received.emit( frame.image )
		
	#
	# Display the image from the camera
	#
	def UpdateImage( self, image ) :
		
		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_Indexed8 )
		
		# Add an indexed color table (grayscale)
		qimage.setColorTable( self.colortable )
			
		# Set the image to the Qt widget
		self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )
			
		# Update the widget
		self.update()
		
	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :
		
		# Stop image acquisition
		self.camera.StopCapture()
		
		# Restore camera default parameters
		Vimba.vimba.VmbFeatureEnumSet( self.camera.handle, 'UserSetSelector', 'Default' )
		Vimba.vimba.VmbFeatureCommandRun( self.camera.handle, 'UserSetLoad' )
		
		# Disconnect the camera
		self.camera.Close()

		# Shutdown Vimba
		Vimba.VmbShutdown()
		
		# Accept the Qt close event
		event.accept()


		
#
# Thread to read images from a USB camera
#
class UsbCamera( threading.Thread ) :
	
	#
	# Initialisation
	#
	def __init__( self, callback ) :

		# Initialize the thread
		super( UsbCamera, self ).__init__()
		
		# Callback function on image received
		self.callback = callback

		# Initialize the camera
		self.camera = cv2.VideoCapture( 0 )

		# Set camera resolution
	#	self.camera.set( cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640 )
	#	self.camera.set( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480 )
		
		# Set camera frame rate
		self.camera.set( cv2.cv.CV_CAP_PROP_FPS, 5 )
		
		self.image = None

	#
	# Start the software trigger thread
	#
	def Start( self ) :

		self.running = True
		self.start()
	
	#
	# Stop the software trigger thread
	#
	def Stop( self ) :

		self.running = False
		self.join()
		
	#
	# Thread main loop
	#
	def run( self ) :

		# Thread running
		while self.running :

			# Capture image
			ok, self.image = self.camera.read()
			
	#		print ok, self.image.shape

			# Convert color coding
			self.image = cv2.cvtColor( self.image, cv2.COLOR_BGR2RGB )
			
			# Callback
			self.callback()
		
		# Release the camera
		self.camera.release()

#
# Qt Widget to display the images from an USB camera
#
class UsbCameraWidget( QtGui.QLabel ) :

	#
	# Signal sent by the image callback function called by Vimba
	#
	image_received = QtCore.Signal()

	#
	# Initialization
	#
	def __init__( self, parent = None ) :

		# Initialize QLabel
		super( UsbCameraWidget, self ).__init__( parent )

		# Change the window title
		self.setWindowTitle( 'USB Camera' )
		
		# Fix the widget size
		self.setFixedSize( 640, 480 )
		self.setScaledContents( True )
		
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		
		# Connect the signal to update the image
		self.image_received.connect( self.UpdateImage )

		# Initialize the stereo cameras
		self.camera = UsbCamera( self.image_received.emit )
		self.camera.Start()

	#
	# Display the image from the camera
	#
	def UpdateImage( self ) :
		
		# Create a Qt image
		qimage = QtGui.QImage( self.camera.image, self.camera.image.shape[1], self.camera.image.shape[0], QtGui.QImage.Format_RGB888 )
		
		# Set the image to the Qt widget
		self.setPixmap( QtGui.QPixmap.fromImage( qimage ) )
			
		# Update the widget
		self.update()
		
	#
	# Close the camera viewer
	#
	def closeEvent( self, event ) :
		
		# Stop image acquisition
		self.camera.Stop()
		
		# Accept the Qt close event
		event.accept()


#
# Main application
#
if __name__ == '__main__' :

	application = QtGui.QApplication( sys.argv )
#	widget = VmbCameraWidget( '50-0503326223' )
	widget = UsbCameraWidget()
	widget.show()
	sys.exit( application.exec_() )
