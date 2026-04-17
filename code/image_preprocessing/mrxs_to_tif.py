import pyvips
import os
import csv
import argparse

def read_samplenumbers(samples_path):
    # samples
    samplenumbers = []
    with open(samples_path, mode ='r') as file:
        data = csv.reader(file)
        for row in data:
                samplenum = row[0].split(";")[0]
                if row:
                    samplenumbers.append(samplenum)
        return samplenumbers
    

def save_tif_and_thumbnail(tif_path, thumbnail_path, samplenumber, dirpath, filename):

    tif_file = os.path.join(tif_path, f"{samplenumber}_tif_img.tif")
    thumb_file = os.path.join(thumbnail_path, f"{samplenumber}_tif_img.png")
    
    if os.path.exists(tif_file) and os.path.exists(thumb_file):
        print("File", tif_file, "exists. Skipping...")
        return # next image

    img_path = os.path.join(dirpath, filename)
    print("Processing:", img_path)

    # mrxs to tif
    image = pyvips.Image.new_from_file(img_path, access="sequential")                
    image.tiffsave(
        tif_file,
        tile=True,
        pyramid=True,
        compression="jpeg",
        Q=75,
        tile_width = 256,
        tile_height = 256,
        bigtiff = True
    )
                
    print("Tiff file saved for:", samplenumber)
    
    # save thumbnail
    thumb = pyvips.Image.thumbnail(tif_file, 300)
    thumb.write_to_file(thumb_file)
    print("Thumbnail saved for:", samplenumber)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("mrxs_input_path", help="path to your MIRAX images")
    parser.add_argument("output_path", help="path to the TIFF images")
    parser.add_argument("samplenames_path", help="path to your samplename csv file")
    args = parser.parse_args()

    mrxs_images_path = args.mrxs_input_path
    tif_path = os.path.join(args.output_path, "tif_images")
    thumbnail_path = os.path.join(args.output_path, "tif_thumbnails")
    samples_path = args.samplenames_path

    os.makedirs(tif_path, exist_ok=True)
    os.makedirs(thumbnail_path, exist_ok=True)

    samplenumbers = read_samplenumbers(samples_path)

    for dirpath, folders, filenames in os.walk(mrxs_images_path):
        for filename in filenames:
            samplenumber = filename.split(".")[0]
            if samplenumber in samplenumbers and filename.endswith((".mrxs")):
                save_tif_and_thumbnail(tif_path, thumbnail_path, samplenumber, dirpath, filename)

main()
        
                