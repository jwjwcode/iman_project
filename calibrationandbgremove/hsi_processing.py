import rasterio as rio
import numpy as np
import os

def white_dark_process(f):
	"""process dark and white, average on x direction. input shape (band_number, x, line_length)"""
	src = rio.open(f)
	src_array = src.read()
	array_avg = np.mean(src_array, axis=1)
	array_avg = np.expand_dims(array_avg, 1)
	return array_avg
	
def hdr_generate(ORI_HDRFILE):
	"""generate hdrfile for output"""
	h_file = open(os.path.join(INPUT_FOLDER, ORI_HDRFILE))
	hdr_ori = h_file.read()
	hdr_correction = hdr_ori.replace('data type = 12', 'data type = 4')
	COR_HDRFILE = os.path.join(OUTPUT_FOLDER, ORI_HDRFILE[:-4] + '_correction.hdr')
	with open(COR_HDRFILE, 'w') as f:
		f.write(hdr_correction)
	h_file.close()
	
def calibrate(ORI_HSIFILE, dark_avg, white_avg, FACTOR):
	""" perform calibration"""
	#read hsi file
	hsi_src = rio.open(os.path.join(INPUT_FOLDER, ORI_HSIFILE))
	hsi_array = hsi_src.read()	
	#hsi correction
	hsi_correction = ((hsi_array - dark_avg) / (white_avg - dark_avg)) * FACTOR
	hsi_correction = np.swapaxes(hsi_correction,0,1) # bil requirement order is [lines, bands, samples], numpy array default is row major
	hsi_correction = hsi_correction.astype('float32') # float32 cooresponds to data type=4 in hdr file
	hsi_correction.tofile(os.path.join(OUTPUT_FOLDER, ORI_HSIFILE[:-4] +'_correction.raw'))

FACTOR = 1  # if full white, FACTOR=1, if 50% white, FACTOR=0.5
FILEEXTENSION = '.bil' # can be .bil or .raw
ROOT = os.getcwd()
INPUT_FOLDER = os.path.join(ROOT, 'hsi')# this is the folder for the hsi data, change the content in '' to your folder name
OUTPUT_FOLDER = os.path.join(ROOT, 'corrected') # this is the folder for corrected data
	
#loop through all files in folder
for file_name in os.listdir(INPUT_FOLDER):
	if file_name.endswith(FILEEXTENSION):
		ORI_HSIFILE = file_name
		if os.path.exists(os.path.join(INPUT_FOLDER, file_name.replace(FILEEXTENSION,'.hdr'))):
			ORI_HDRFILE = file_name.replace(FILEEXTENSION,'.hdr')
			hdr_generate(ORI_HDRFILE)
			#read and process dark and white file
			if os.path.exists(os.path.join(ROOT, 'ref', 'darkref_' + file_name)) and os.path.exists(os.path.join(ROOT, 'ref', 'whiteref_' + file_name)):
				DARKFILE = os.path.join(ROOT, 'ref', 'darkref_' + file_name
				WHITEFILE = os.path.exists(os.path.join(ROOT, 'ref', 'whiteref_' + file_name))
				dark_avg = white_dark_process(DARKFILE)
				white_avg = white_dark_process(WHITEFILE)
				#calibrate
				calibrate(ORI_HSIFILE, dark_avg, white_avg, FACTOR)
			else: 
				print('no reference file: ', ORI_HSIFILE)
		else:
			print('hdr file not exit for bil/raw file: ', ORI_HSIFILE)

	
	
	












