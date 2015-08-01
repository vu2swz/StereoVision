#! /usr/bin/env python
# -*- coding:utf-8 -*- 


#
# Application to capture, and calibrate stereo cameras
#


#
# External dependencies
#
import argparse
import glob
import os
import pickle
import Calibration
import Viewer


#
# Command line argument parser
#
parser = argparse.ArgumentParser( description='Camera calibration toolkit.' )
parser.add_argument( '-live', action='store_true', help='Stereo camera live display' )
parser.add_argument( '-rows', action='store', default=15, help='Number of rows in the chessboard pattern' )
parser.add_argument( '-cols', action='store', default=10, help='Number of columns in the chessboard pattern' )
parser.add_argument( '-debug', action='store_true', help='Display the chessboard on each image' )
parser.add_argument( '-mono', action='store', help='Image files for mono camera calibration' )
parser.add_argument( '-stereo', action='store_true', help='Stereo camera calibration' )
parser.add_argument( '-output', action='store_true', help='Save camera calibration results' )
parser.add_argument( '-left', action='store_true', help='Save left camera calibration results' )
parser.add_argument( '-right', action='store_true', help='Save right camera calibration results' )
parser.add_argument( '-undistort', action='store_true', help='Image undistortion' )
parser.add_argument( '-undistort_stereo', action='store_true', help='Stereo image undistortion' )
args = parser.parse_args()


#
# Calibration pattern setup
#
pattern_size = ( int(args.rows), int(args.cols) )

#
# Stereo camera live capture
#
if args.live :

	Viewer.VmbStereoViewer( pattern_size )

#
# Mono camera calibration
#
elif args.mono :

	# Calibrate the camera
	calibration = Calibration.CameraCalibration( sorted( glob.glob( args.mono ) ), pattern_size, args.debug )
	
	# Save calibration results
	if args.output :
		with open( 'camera-calibration.pkl' , 'wb') as output_file :
			pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )
	elif args.left :
		with open( 'camera-calibration-left.pkl', 'wb') as output_file :
			pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )
	elif args.right :
		with open( 'camera-calibration-right.pkl', 'wb') as output_file :
			pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )

#
# Stereo camera calibration
#
elif args.stereo :
	
	# Read camera calibration files
	with open( 'camera-calibration-left.pkl' , 'rb') as input_file :
		cam1 = pickle.load( input_file )
	with open( 'camera-calibration-right.pkl' , 'rb') as input_file :
		cam2 = pickle.load( input_file )
		
	# Calibrate the stereo cameras
	calibration = Calibration.StereoCameraCalibration( cam1, cam2, args.debug )
	
	# Write results with pickle
	if args.output :
		with open( 'stereo-calibration.pkl' , 'wb') as output_file :
			pickle.dump( calibration, output_file, pickle.HIGHEST_PROTOCOL )

#
# Image undistortion
#
elif args.undistort :
	
	# Read camera calibration file
	with open( 'camera-calibration.pkl' , 'rb') as input_file :
		calibration = pickle.load( input_file )
		
	# Undistort calibration files
	Calibration.UndistortImages( calibration )

#
# Stereo image undistortion
#
elif args.undistort_stereo :
	
	# Read camera calibration files
	with open( 'camera-calibration-left.pkl' , 'rb') as input_file :
		cam1 = pickle.load( input_file )
	with open( 'camera-calibration-right.pkl' , 'rb') as input_file :
		cam2 = pickle.load( input_file )
	with open( 'stereo-calibration.pkl' , 'rb') as input_file :
		calibration = pickle.load( input_file )
		
	# Undistort calibration files
	Calibration.StereoUndistortImages( cam1, cam2, calibration )

