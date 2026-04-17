import os
from histoprep import SlideReader
from histoprep.utils import OutlierDetector
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import argparse

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("he_images", help="path to the cropped H&E images with metadata (input)")
    parser.add_argument("output_path", help="output path for the tile images")
    parser.add_argument("masks_path", help="path to the tissue masks (histoQC output)")
    parser.add_argument("width", type=int, help="tile width as pixels (for example: 512)")
    parser.add_argument("overlap", type=float, help="tile overlap (for example: 0)")
    parser.add_argument("max_background", type=float, help="maximum proportion of background in a tile (for example 0.5)")
    args = parser.parse_args()
    directory = args.he_images
    masks_path = args.masks_path
    output_path = args.output_path
    width = args.width
    overlap = args.overlap
    max_background = args.max_background

    for image_name in os.listdir(directory):
        try:
            if image_name.endswith(".tif"):
                samplenumber = image_name.split("_")[0]+"_"+image_name.split("_")[1]
                print("processing:", samplenumber)
                image_path = f"{directory}/{image_name}"
                
                # Read slide image
                reader = SlideReader(image_path, backend="OPENSLIDE")
                print("SlideReader ok for", samplenumber)
                
                #----------
                level = None #Slide pyramid level to use for tissue detection. If None, uses the level_from_max_dimension method. Defaults to None.
                threshold = None #Threshold for tissue detection. If set, will detect tissue by global thresholding. Otherwise Otsu's method is used to find a threshold. Defaults to None.
                multiplier = 1 #Otsu's method finds an optimal threshold by minimizing the weighted within-class variance. This threshold is then multiplied with multiplier. Ignored if threshold is not None. Defaults to 1.0.
                sigma = 0 #Sigma for gaussian blurring. Defaults to 0.0.

                threshold1, tissue_mask = reader.get_tissue_mask(
                    level=level, threshold=threshold, multiplier=multiplier, sigma=sigma
                ) 
                #-----------
                
                mask_path = f"{masks_path}/{samplenumber}_cropped_metadata.tif/{samplenumber}_cropped_metadata.tif_mask_use.png"
                image = Image.open(mask_path)
                tissue_mask2 = np.array(image)
                print("mask opened", samplenumber)
        
                # Extract overlapping tile coordinates with less than x% background.
                tile_coordinates = reader.get_tile_coordinates(
                    tissue_mask2, width=width, overlap=overlap, max_background=max_background, out_of_bounds=False
                )
                print("tile coordinates ok", samplenumber)

                # Save tile images with image metrics for preprocessing.
                tile_metadata = reader.save_regions(
                    f"{output_path}", 
                    tile_coordinates, save_metrics=True, threshold=threshold1
                )

        except Exception as e:
            print("Error",image_name,e)

main()