"""White and dark calibration
1- Input can be both bil or raw
2- output is ".raw" but can be changed
3- Images should be organised in 3 different folders including (1) References, (2) Raw_HSI, (3) Corrected_HSI.
4- The Corrected_HSI folder is for the model to save the output data
5- Dark calibration file should name "Dark.bil" and white shoudl name "White.bil"
6- Define the factor: if used 99% or 100% white board, factor should be 0.99... 
....or 1 respectively, or if used 50%, factor should be 0.5. 
7- In the "#loop through all files in folder", check for the bil file extensions. If the actual hdr files are .bi.hdr, keep it this way bil.hdr,... 
...and if they are .raw, keep it raw.
8- Keep the code file in the same folder (main folder) as the data"""
