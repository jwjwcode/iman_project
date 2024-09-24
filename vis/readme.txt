This folder contain files for visualization. generate_data_for_pred_5h.py is used to read one raw hsi data, filter out all forground pixels and output a csv file with the spectral signiture and its coordinate.

Then the csv file is sent to a MATLAB model for prediction and get a excel of predictions and coordinates as the  Pixels_S166_Y_Predicted.xlsx

vis_use_pred_excel.py use the predicted excel file to generate an image with different colors representing different level of DONs. It can ouput two versions: 1. a color per pixel. 2. a color per grain using average.

To be improved: different data, 5h, 5r, 40h, 40r use different parameters and slightly different filtering procedures. Can be integrated to one file with different paramters.
