import tifftools
import os
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("he_input_path", help="path to your cropped H&E images")
    parser.add_argument("output_path", help="path for the images with metadata (output)")
    parser.add_argument("mpp", help="micrometers per pixel (for example 0.1214)")
    args = parser.parse_args()

    input_dir = args.he_input_path 
    output_path_metadata = args.output_path
    mpp = str(args.mpp)

    for filename in os.listdir(input_dir):
        
        if filename.endswith((".tif")):
            samplenumber = filename.split("_")[0]+"_"+filename.split("_")[1]

            input_img_path = os.path.join(input_dir, f"{samplenumber}_cropped.tif")
            metadata_img_path = os.path.join(output_path_metadata, f"{samplenumber}_cropped_metadata.tif")
            
            if os.path.exists(metadata_img_path):
                print("File", metadata_img_path, "exists. Skipping...")
                continue

            print("Processing:", metadata_img_path)

            #set tags
            setlist = [('ImageDescription', 'Aperio |AppMag=40|MPP='+mpp)]
            tifftools.tiff_set(input_img_path, metadata_img_path, setlist=setlist)
            print("Metadata saved for", samplenumber)

main()