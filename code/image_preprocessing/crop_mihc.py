import pyvips
import os
import csv
import argparse

def to_int(value):
    if value == "" or value is None or value=='None':
        return None
    return int(value)

def read_csv(samplenumber, coordinates):
    x=None
    y=None
    w=None
    h=None
    with open(coordinates, mode ='r') as file:
        data = csv.reader(file)
        for row in data:
            if row[0] == samplenumber and len(row)==6:
                x=to_int(row[1]) # x (upper left corner x)
                y=to_int(row[2]) # y (upper left corner y)
                w=to_int(row[3]) # width
                h=to_int(row[4]) # height
                break
    return x,y,w,h

def crop(mihc_images_path, round_number, output_folder, output_path_thumbnails, coordinates, markers):
    for dirpath, folders, filenames in os.walk(mihc_images_path):
        skip_folders = {"regs", "thumbs"} #exclude those
        folders[:] = [f for f in folders if f not in skip_folders]
        
        for filename in filenames:
            if filename.endswith(".tif") and round_number in filename:
                samplenumber = filename.split(".")[0]
                samplenumber_parts = samplenumber.split("_")

                if len(samplenumber_parts) == 9: # TM_xx_xx_xx_TMEpanel_roundx_marker_ORG
                    s_index = int(samplenumber_parts[6][1]) #s1, s2 or s3 -> 1st, 2nd or 3rd sample
                    sampleid = samplenumber_parts[s_index] # only one samplenumber
                    marker_code = samplenumber.split("_")[7] # marker code (DAPI/AF555/...)
                elif len(samplenumber_parts) == 6: # if TM_49_TMEpanel_round1_AF488_ORG
                    sampleid = samplenumber_parts[1] # samplenumber
                    marker_code = samplenumber.split("_")[4] # marker code

                if marker_code not in markers:
                    continue

                ret = read_csv(sampleid, coordinates)
                if not any(ret):
                    # not found from coordinates file, skip
                    continue
                x,y,w,h = ret

                print("Processing:", filename, "...")
                print("x:",x,"y:",y,"w:",w,"h:",h)

                img_path = os.path.join(dirpath, filename)
                output_folder_img = output_folder+"/"+marker_code
                output_folder_thumbnail = output_path_thumbnails+"/"+marker_code
                os.makedirs(output_folder_thumbnail, exist_ok=True)
                os.makedirs(output_folder_img, exist_ok=True)

                output_path_cropped = f"{output_folder_img}/{samplenumber}_cropped.tif"
                output_path_thumbnail = f"{output_folder_thumbnail}/{samplenumber}_cropped.png"
                
                if os.path.exists(output_path_cropped) and os.path.exists(output_path_thumbnail):
                    print("File", output_path_cropped, "exists. Skipping...")
                    continue

    
                image = pyvips.Image.new_from_file(img_path, access='sequential')
                if image.height > image.width:
                    scaling_factor=image.height/1024
                elif image.height < image.width:
                    scaling_factor=image.width/1024

                #CROP:
                x = x*scaling_factor
                y = y*scaling_factor
                w = w*scaling_factor
                h = h*scaling_factor

                image = image.crop(x, y, w, h)

                # scaling factor for thumbnail
                scale_factor = 0.1
                scaled = image.resize(scale_factor)
                # save thumbnail
                scaled.write_to_file(output_path_thumbnail)
                print("Thumbnail saved", output_path_thumbnail)

                image.write_to_file(output_path_cropped,
                                    compression="lzw",
                                    tile=True, 
                                    tile_width=256, 
                                    tile_height=256, 
                                    pyramid=True)
                
                print("Image cropped:", samplenumber)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("mihc_input_path", help="path to your original mIHC images (.tif)")
    parser.add_argument("output_path", help="path to the cropped mIHC images (output)")
    parser.add_argument("coordinates_path", help="path to the csv with mIHC coordinates")
    parser.add_argument("round_number", help="mIHC staining round (for example 1, 2, 3 or 4)")
    parser.add_argument("markers", nargs='+', help="mIHC staining markers (for example: DAPI AF555)")
    args = parser.parse_args()

    mihc_images_path =  args.mihc_input_path
    output_folder =  os.path.join(args.output_path, "cropped_mihc_images")
    output_path_thumbnails = os.path.join(args.output_path, "cropped_mihc_thumbnails")
    coordinates = args.coordinates_path
    round_number = "round"+args.round_number
    markers = args.markers

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(output_path_thumbnails, exist_ok=True)

    crop(mihc_images_path, round_number, output_folder, output_path_thumbnails, coordinates, markers)

main()