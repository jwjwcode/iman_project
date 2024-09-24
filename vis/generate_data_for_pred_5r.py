import rasterio as rio
import numpy as np
import os
import cv2
import copy
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io as sio
import pandas as pd

B1 = 20 # use band B1 to remove label
B2 = 231#use band B2 to remove other background

count = 0


#input hsi raw data, output foreground coordinates and spectral signiture

def data_extract(hsi_file):
		hsi_src = rio.open(hsi_file)
		hsi_array = hsi_src.read()
		hsi_array = hsi_array.astype(np.float64)
		print(hsi_array.shape)
		print(np.amin(hsi_array))
		print(np.amax(hsi_array))
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
		print(sample_start_row)
		#remove edges
		sum_s2_row = np.sum(band_s2, axis=0)

		sum_s2_row = sum_s2_row > 90
		sum_s2_row = np.ediff1d(sum_s2_row.astype(np.float64))

		sample_start_end_col = np.nonzero(sum_s2_row)[0]
		sample_start_col = np.amin(np.abs(sample_start_end_col - 330)) + 330
		if np.abs(sample_start_col - 330) > 50:
			sample_start_col = 310

		sample_end_col = np.amin(np.abs(sample_start_end_col - 1220)) + 1220
		if np.abs(sample_end_col - 1220) > 20:
			sample_end_col = np.minimum(1200, sample_start_col+890)


		sum_s2_col = np.sum(band_s2, axis=1)

		sum_s2_col = sum_s2_col > 75
		sum_s2_col = np.ediff1d(sum_s2_col.astype(np.float64))
		sample_end_row = np.nonzero(sum_s2_col)[0]
		sample_end_row = np.amin(np.abs(sample_end_row - 1300)) + 1300
		if np.abs(sample_end_row - 1300) > 20:
			sample_end_row = np.maximum(1300, sample_start_row+1060)
		mask[sample_end_row:,:] = 0
		mask[:,:sample_start_col] = 0
		mask[:,sample_end_col:] = 0
		#remove background inside sample area
		hsi_reduce = np.sqrt(np.mean(hsi_array*hsi_array, axis=0))
		hsi_reduce = hsi_reduce*mask
		hsi_reduce = (hsi_reduce - np.amin(hsi_reduce)) / (np.amax(hsi_reduce) - np.amin(hsi_reduce))	
		
		mask2 = hsi_reduce > 0.19
		#mask2 = mask_process(mask2)
		output_mask_file = '~/' + hsi_file[:-4]+'.png'
		cv2.imwrite(output_mask_file, mask2*256)
		
		#apply mask on hsi and get mean
		hsi_data = hsi_data*mask2
		#print(np.amax(hsi_data))

            
		lnonzero = np.nonzero(mask2)
		print(lnonzero)
		x_nonzero = lnonzero[0]
		y_nonzero = lnonzero[1]
		print(x_nonzero)
		print(y_nonzero)
		coord = []
		pixel_spec = []
            
		for i in range(x_nonzero.shape[0]):
			    coord.append((x_nonzero[i], y_nonzero[i]))
			    pixel_spec.append(hsi_data[:, x_nonzero[i], y_nonzero[i]])
			    #print(x_nonzero[i], y_nonzero[i])
			    #print(i)
                
            
            
		num_fg = np.sum(mask2)
		avg_spec = np.sum(hsi_data, axis=(1,2)) / num_fg
		print('fg', num_fg)
		return coord, pixel_spec

































if __name__ == '__main__':
    hsi_file = '/media/jing/GRDC-A/5-g Samples/Resonon Corrected one by one/050233.bil'
    coord, data_fg = data_extract(hsi_file)
    data_fg_coord_dict = {coord[i] : data_fg[i] for i in range(len(data_fg))}
    #sio.savemat('datafgcoord.mat', data_fg_coord_dict)
    df = pd.DataFrame(data_fg_coord_dict).T
    df.to_csv('datafgcoordsample_5r_233.csv')
    
    
