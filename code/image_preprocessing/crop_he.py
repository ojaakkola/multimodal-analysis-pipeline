import pyvips
import os
import csv
import argparse


def to_int(value):
    if value == "" or value is None or value=='None':
        return None
    return int(value)

def read_coordinates(samplenumber, coordinates_path):
    x=None
    y=None
    w=None
    h=None
    with open(coordinates_path, mode ='r') as file:
        data = csv.reader(file)
        for row in data:
            if row[0] == samplenumber and len(row)==5:
                x=to_int(row[1])
                y=to_int(row[2])
                w=to_int(row[3])
                h=to_int(row[4])
                break
    print("Coordinates read for:", samplenumber, ": x:", x, "y;", y, "w:", w, "h:", h)

    return x,y,w,h,

def crop_he(scaling_factor, samplenumber, output_folder, output_folder_thumbnails, input_path, x, y, w, h):
    if (x != None and y != None and w != None and h != None):
        x=scaling_factor*x
        y=scaling_factor*y
        w=scaling_factor*w
        h=scaling_factor*h
        print("Processing:", samplenumber, "...")
        output_path_cropped = f"{output_folder}/{samplenumber}_cropped.tif"
        thumbnail_path = f"{output_folder_thumbnails}/{samplenumber}_cropped.png"

        if os.path.exists(output_path_cropped):
            print("File", output_path_cropped, "exists. Skipping...")
        else:
            image = pyvips.Image.new_from_file(input_path, access='sequential')
            cropped = image.crop(x, y, w, h)
            cropped.write_to_file(output_path_cropped, 
                compression="jpeg",
                Q=90,
                tile=True,
                tile_width=256,
                tile_height=256,
                pyramid=True,
                bigtiff=False)
            print("Cropping done:", samplenumber)

        if os.path.exists(thumbnail_path):
            print("File", thumbnail_path, "exists. Skipping...")
        else:
            thumb = pyvips.Image.thumbnail(output_path_cropped, 300)
            thumb.write_to_file(thumbnail_path)
            print("Thumbnail saved:", samplenumber)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("he_input_path", help="path to your H&E images (.tif)")
    parser.add_argument("output_path", help="path for the cropped H&E images (output)")
    parser.add_argument("coordinates_path", help="csv with H&E coordinates")
    parser.add_argument("scaling_factor", help="gimp -> whole slide tif (for example 1442.963)")
    args = parser.parse_args()

    coordinates_path = args.coordinates_path
    scaling_factor = float(args.scaling_factor)
    he_images_path = args.he_input_path 
    output_folder = os.path.join(args.output_path, "cropped_he_images")
    output_folder_thumbnails = os.path.join(args.output_path, "cropped_he_thumbnails")
    
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_folder_thumbnails, exist_ok=True)


    for filename in os.listdir(he_images_path):
        if filename.endswith(".tif"):
            input_path = os.path.join(he_images_path, filename)
            samplenumber = str(filename.split("_tif")[0])
            
            x,y,w,h=read_coordinates(samplenumber, coordinates_path)
            crop_he(scaling_factor, samplenumber, output_folder, output_folder_thumbnails, input_path, x, y, w, h)

main()