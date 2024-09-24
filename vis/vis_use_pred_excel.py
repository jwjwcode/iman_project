import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cv2

def seed_level_vis(mask, image):
    output = cv2.connectedComponentsWithStats(mask)
    (numLabels, labels, stats, centroids) = output
    #plt.imshow(labels*256)
    bbox = []
    print(numLabels)
    componentMasks = []
    # loop over the number of unique connected component labels
    for i in range(0, numLabels):
    	 componentMask = (labels == i).astype("uint8") 
    	 # if this is the first component then we examine the
    	 # *background* (typically we would just ignore this
    	 # component in our loop)
    	 if i == 0:
    	 	text = "examining component {}/{} (background)".format(
    	 		i + 1, numLabels)
    	 # otherwise, we are examining an actual connected component
    	 else:
    	 	text = "examining component {}/{}".format( i + 1, numLabels)
    	 # print a status message update for the current connected
    	 # component
    	 print("[INFO] {}".format(text))
    	 # extract the connected component statistics and centroid for
    	 # the current label
    	 x = stats[i, cv2.CC_STAT_LEFT]
    	 y = stats[i, cv2.CC_STAT_TOP]
    	 w = stats[i, cv2.CC_STAT_WIDTH]
    	 h = stats[i, cv2.CC_STAT_HEIGHT]
    	 area = stats[i, cv2.CC_STAT_AREA]
    	 (cX, cY) = centroids[i]
    	 if area >10:
             bbox.append([x,y,w,h])
             componentMasks.append(componentMask)
    #print(len(bbox))
    display_image = np.zeros_like(image)
    # for x,y,w,h in bbox:
    #     seed_individual = image[y:y+h, x:x+w]
    #     avg_don_seed = np.sum(seed_individual) / np.sum(seed_individual!=0)
    #     #print(avg_don_seed)
    #     seed_individual_mask = seed_individual!=0
    #     seed_individual_final = avg_don_seed*seed_individual_mask
    #     #plt.imshow(seed_individual_final)
    #     display_image[y:y+h, x:x+w] = seed_individual_final
    #plt.imshow(componentMasks[-1])
    componentMasks = componentMasks[1:]
    for c in componentMasks:

        seed_individual = image*c
        print(np.sum(seed_individual!=0))
        avg_don_seed = np.sum(seed_individual) / np.sum(seed_individual!=0)
        display_image = display_image + c*avg_don_seed
        
    #plt.imshow(display_image)

    return display_image
            
    

file_name = 'Pixels_S166_Y_Predicted.xlsx'
df = pd.read_excel(file_name)
print(df.head())

x = df.iloc[:,0]
y = df.iloc[:,1]
don = df.iloc[:,4]

x = x.to_numpy().astype(int)
y = y.to_numpy().astype(int)

don = don.to_numpy().astype(float)
#don = don / (np.amax(don))

print(x)
print(y)
print(don)

fg_mask = cv2.imread('/media/jing/GRDC-A/5-g Samples/Hyspex_bgremove/050161_ref.png')
mask = fg_mask[:,:,0]

image = np.zeros((608,384))

for i in range(x.shape[0]):
    image[x[i], y[i]] = don[i]
    
display_image = seed_level_vis(mask, image)

data = display_image


# # Define a colormap from blue to red
colors = ["green", "red"]
n_bins = 100  # Number of bins for color interpolation
cmap = mcolors.LinearSegmentedColormap.from_list("green_red", colors, N=n_bins)

# Create a custom colormap that includes black for NaN values
cmap_with_nan_black = mcolors.ListedColormap(['black'] + [cmap(i / (n_bins - 1)) for i in range(n_bins)])

# Prepare data: use np.nan for background to show it as black
display_data = np.where(data > 0, data, np.nan)

# Normalize based on non-NaN values
norm = mcolors.Normalize(vmin=np.nanmin(display_data[~np.isnan(display_data)]),
                          vmax=np.nanmax(display_data[~np.isnan(display_data)]))

print(np.nanmin(display_data[~np.isnan(display_data)]))
print(np.nanmax(display_data[~np.isnan(display_data)]))
# Display the image
plt.imshow(data, cmap=cmap_with_nan_black, norm=norm, interpolation='nearest')
plt.colorbar()  # Show the color scale
plt.savefig('vis.png', dpi=300)
plt.title("visualization")
plt.show()
