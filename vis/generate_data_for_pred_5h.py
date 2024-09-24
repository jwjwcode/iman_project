import rasterio as rio
import numpy as np
import os
import cv2
import copy
import matplotlib.pyplot as plt
import pandas as pd
import scipy.io as sio
import pandas as pd
from sklearn.preprocessing import StandardScaler

# generate coordinates and spec for vis

row_start = 135
row_end = 600
col_start = 10
col_end = 375
B1 = 287 #use band 287 to remove label


#input hsi raw data, output foreground coordinates and spectral signiture
def data_extract(hsi_file):
			hsi_src = rio.open(hsi_file)
			hsi_array = hsi_src.read()
			hsi_array = hsi_array.astype(np.float64)

			hsi_data = copy.deepcopy(hsi_array)
			print(hsi_data.shape)
			mask = np.ones((hsi_array.shape[1], hsi_array.shape[2]))
			hsi_array = (hsi_array - np.amin(hsi_array)) / (np.amax(hsi_array) - np.amin(hsi_array))
			
			band_s1 = hsi_array[B1,:,:]
					#remove label
			sum_s1_col = np.sum(band_s1, axis=1)

			sum_s1_col = sum_s1_col > 50
			sum_s1_col = np.ediff1d(sum_s1_col.astype(np.float64)) # finding changing band
			sample_start_row = np.nonzero(sum_s1_col)[0] # 1 gap for shadow
			sample_start_row = np.amin(np.abs(sample_start_row - 135)) + 135
			if np.abs(sample_start_row - 135) > 15:
				sample_start_row = 135
			print(sample_start_row)
		
			mask[:sample_start_row,:] = 0
			mask[row_end:,:] = 0
			mask[:,:col_start] = 0
			mask[:,col_end:] = 0
			#remove background inside sample area
			hsi_reduce = np.sqrt(np.mean(hsi_array*hsi_array, axis=0))
			#cv2.imwrite('5g2.png', hsi_reduce*256)
			hsi_reduce = hsi_reduce*mask
			hsi_reduce = (hsi_reduce - np.amin(hsi_reduce)) / (np.amax(hsi_reduce) - np.amin(hsi_reduce))	
		
			mask2 = hsi_reduce > 0.2
			output_mask_file = hsi_file[:-4]+'.png'
			cv2.imwrite(output_mask_file, mask2*256)
			#apply mask on hsi and get mean		
			hsi_data = hsi_data*mask2
            
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
# 			scaler = StandardScaler()
# 			for pix in pixel_spec:
# 			    pix = pix.reshape(pix.shape[1], pix.shape[0])
# 			    pix = scaler.fit_transform(pix)
# 			    pix = pix.reshape(pix.shape[1], pix.shape[0])
# 			    plt.plot(pix, 'g')
# 			avg_spec = avg_spec.reshape(avg_spec.shape[1], avg_spec.shape[0])
# 			avg_spec = scaler.fit_transform(avg_spec)
# 			avg_spec = avg_spec.reshape(avg_spec.shape[1], avg_spec.shape[0])
# 			plt.plot(avg_spec, 'r+')
# 			plt.show()
			return coord, pixel_spec

































if __name__ == '__main__':
    hsi_file = '/media/jing/GRDC-A/5-g Samples/Hyspex Corrected/050161/050161_ref.raw'
    coord, data_fg = data_extract(hsi_file)
    data_fg_coord_dict = {coord[i] : data_fg[i] for i in range(len(data_fg))}
    #sio.savemat('datafgcoord.mat', data_fg_coord_dict)
    df = pd.DataFrame(data_fg_coord_dict).T
    df.to_csv('datafgcoordsample5h161.csv')
    
    
