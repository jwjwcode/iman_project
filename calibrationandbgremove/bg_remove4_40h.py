import rasterio as rio
import numpy as np
import os
import cv2
import copy
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io as sio


INPUT_FOLDER = '/media/jing/GRDC-A/40-g Samples/Hyspex Corrected'
OUTPUT_FOLDER = '/media/jing/GRDC-A/40-g Samples/Hyspex_bgremove'
FILEEXTENSION = '.raw'

row_start = 133
row_end = 600
col_start = 7
col_end = 378

B1 = 287 #use band 287 to remove label
all_avg_spec = []
all_file_name = []
count = 0
for folder_name in os.listdir(INPUT_FOLDER):
	for file_name in os.listdir(os.path.join(INPUT_FOLDER,folder_name)):
	
		if file_name.endswith(FILEEXTENSION):
			print(os.path.join(INPUT_FOLDER, folder_name, file_name))

			hsi_src = rio.open(os.path.join(INPUT_FOLDER, folder_name, file_name))
			hsi_array = hsi_src.read()
			hsi_array = hsi_array.astype(np.float64)
			#print(hsi_array.shape)
			print(np.amax(hsi_array))

			hsi_data = copy.deepcopy(hsi_array)
			mask = np.ones((hsi_array.shape[1], hsi_array.shape[2]))
			hsi_array = (hsi_array - np.amin(hsi_array)) / (np.amax(hsi_array) - np.amin(hsi_array))
			
			band_s1 = hsi_array[B1,:,:]
					#remove label
			sum_s1_col = np.sum(band_s1, axis=1)

			sum_s1_col = sum_s1_col > 50
			sum_s1_col = np.ediff1d(sum_s1_col.astype(np.float64)) # finding changing band
			sample_start_row = np.nonzero(sum_s1_col)[0] # 1 gap for shadow
			sample_start_row = np.amin(np.abs(sample_start_row - 133)) + 133
			if np.abs(sample_start_row - 133) > 10:
				sample_start_row = 133
			print(sample_start_row)
		
			mask[:sample_start_row,:] = 0
			mask[row_end:,:] = 0
			mask[:,:col_start] = 0
			mask[:,col_end:] = 0
			#remove background inside sample area
			hsi_reduce = np.sqrt(np.mean(hsi_array*hsi_array, axis=0))
			output_reduce_file = os.path.join(OUTPUT_FOLDER, file_name[:-4]+'a.png')
			cv2.imwrite(output_reduce_file, hsi_reduce*256)
			#cv2.imwrite('5g2.png', hsi_reduce*256)
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
			


		
				
		
			#hsi_reduce = np.sqrt(np.mean(hsi_array*hsi_array, axis=0))
			#hsi_reduce = (hsi_reduce - np.amin(hsi_reduce)) / (np.amax(hsi_reduce) - np.amin(hsi_reduce))
			#hsi_reduce_crop = hsi_reduce[row_start:row_end, col_start:col_end]
			#mask = hsi_reduce_crop > 0.15
			#cv2.imwrite('5g1.png', hsi_reduce*256)
			#cv2.imwrite('5g2.png', hsi_reduce_crop*256)
			#cv2.imwrite('5g3.png', mask2*256)
# write to excel
res_dict = {all_file_name[i]:all_avg_spec[i] for i in range(len(all_file_name))}
sio.savemat('40h.mat', res_dict)
df = pd.DataFrame(res_dict).T
df.to_csv('40h.csv')



