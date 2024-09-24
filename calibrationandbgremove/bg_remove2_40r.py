import rasterio as rio
import numpy as np
import os
import cv2
import copy
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io as sio


INPUT_FOLDER = '/media/jing/GRDC-A/40-g Samples/Resonon Corrected ony by one'
OUTPUT_FOLDER = '/media/jing/GRDC-A/40-g Samples/Resonon_bgremove'
FILEEXTENSION = '.bil'
B1 = 20 # use band B1 to remove label
B2 = 231#use band B2 to remove other background

count = 0
all_avg_spec = []
all_file_name = []
for file_name in os.listdir(INPUT_FOLDER):
	if file_name.endswith(FILEEXTENSION):
		print(file_name)
		hsi_src = rio.open(os.path.join(INPUT_FOLDER, file_name))
		hsi_array = hsi_src.read()
		hsi_array = hsi_array.astype(np.float64)
		hsi_data = copy.deepcopy(hsi_array)
		mask = np.ones((hsi_array.shape[1], hsi_array.shape[2]))
		hsi_array = (hsi_array - np.amin(hsi_array)) / (np.amax(hsi_array) - np.amin(hsi_array))

		band_s1 = hsi_array[B1,:,:]
		band_s2 = hsi_array[B2,:,:]
		#remove label
		sum_s1_col = np.sum(band_s1, axis=1)
		sum_s1_col = sum_s1_col > 180
		sum_s1_col = np.ediff1d(sum_s1_col.astype(np.float64)) # finding changing band
		sample_start_row = np.nonzero(sum_s1_col)[0] + 15 # 15 gap for shadow
		sample_start_row = np.amin(np.abs(sample_start_row - 240)) + 240
		if np.abs(sample_start_row - 240) > 50:
			sample_start_row = 260
		
		mask[:sample_start_row,:] = 0
		#remove edges
		sum_s2_row = np.sum(band_s2, axis=0)
		sum_s2_row = sum_s2_row > 150
		sum_s2_row = np.ediff1d(sum_s2_row.astype(np.float64))

		sample_start_end_col = np.nonzero(sum_s2_row)[0]
		sample_start_col = np.amin(np.abs(sample_start_end_col - 330)) + 330
		if np.abs(sample_start_col - 330) > 50:
			sample_start_col = 310
		sample_end_col = np.amin(np.abs(sample_start_end_col - 1220)) + 1220
		if np.abs(sample_end_col - 1220) > 20:
			sample_end_col = np.minimum(1200, sample_start_col+890)

		sum_s2_col = np.sum(band_s2, axis=1)
		sum_s2_col = sum_s2_col > 150
		sum_s2_col = np.ediff1d(sum_s2_col.astype(np.float64))
		sample_end_row = np.nonzero(sum_s2_col)[0]
		sample_end_row = np.amin(np.abs(sample_end_row - 1300)) + 1300
		if np.abs(sample_end_row - 1300) > 20:
			sample_end_row = np.maximum(1300, sample_start_row+1060)
		mask[sample_end_row:,:] = 0
		mask[:,:sample_start_col] = 0
		mask[:,sample_end_col:] = 0
		print('col start {}, col end {}, row start {}, row end {}'.format(sample_start_col,sample_end_col,sample_start_row, sample_end_row ))
		#remove background inside sample area
		hsi_reduce = np.sqrt(np.mean(hsi_array*hsi_array, axis=0))
		hsi_reduce = hsi_reduce*mask
		hsi_reduce = (hsi_reduce - np.amin(hsi_reduce)) / (np.amax(hsi_reduce) - np.amin(hsi_reduce))	
		
		mask2 = hsi_reduce > 0.2
		output_mask_file = os.path.join(OUTPUT_FOLDER, file_name[:-4]+'.png')
		cv2.imwrite(output_mask_file, mask2*256)
		#apply mask on hsi and get mean
		
		hsi_data = hsi_data*mask2
		#print(np.amax(hsi_data))
		num_fg = np.sum(mask2)
		#print(num_fg)
		avg_spec = np.sum(hsi_data, axis=(1,2)) / num_fg
		all_avg_spec.append(avg_spec)
		all_file_name.append(file_name[:-4])
		count += 1
		print(count)


# write to excel
res_dict = {all_file_name[i]:all_avg_spec[i] for i in range(len(all_file_name))}
sio.savemat('40r.mat', res_dict)
df = pd.DataFrame(res_dict).T
df.to_csv('40r.csv')
























			
			
