import pyvips
import os
from PIL import Image
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("registration_results_path", help="path to the folder with image registration results")
    args = parser.parse_args()
    base_path = args.registration_results_path

    dapi_filename = "-modality_af555_to_modality_he_registered" # change this if needed
    he_filename = "-modality_he_registered" # change this if needed
    af555_filename = "-modality_af555_to_modality_he_registered" # change this if needed

    sample_dirs = os.listdir(base_path)

    for sample_dir in sample_dirs:
        sample_dir_path = os.path.join(base_path, sample_dir)

        if not os.path.isdir(sample_dir_path):
            continue

        dapi_path_thumb = None
        af555_path_thumb = None
        he_path_thumb = None

        for filename in os.listdir(sample_dir_path):
            print(filename)

        try:
            #DAPI
            for filename in os.listdir(sample_dir_path):
                if dapi_filename in filename: # "-modality_dapi_to_modality_he_registered.ome.tiff" in filename:
                    print("processing:",filename, "...")
                    filename_mihc=filename
                    mihc_path = os.path.join(sample_dir_path, filename_mihc)
                    dapi_path_thumb = sample_dir_path + "/wsireg_results_thumb_" + sample_dir + "_dapi.png"
                    if os.path.exists(dapi_path_thumb):
                            print("file already exists", dapi_path_thumb, "skipping it...")
                            break

                    image_mihc = pyvips.Image.new_from_file(mihc_path, access="sequential")
                    thumbnail = image_mihc.resize(0.01)
                    if thumbnail.bands > 1:
                        thumbnail = thumbnail[0]
                    low = thumbnail.percent(1)
                    high = thumbnail.percent(99)
                    if high > low:
                        thumbnail = thumbnail.linear(
                            255.0 / (high - low),
                            -low * 255.0 / (high - low)
                        )
                    thumbnail = thumbnail.cast("uchar")
                    thumbnail = 255 - thumbnail
                    binary = thumbnail > 128
                    binary = binary.cast("uchar") * 255
                    binary.write_to_file(dapi_path_thumb)        
            
            
            #AF555
            for filename in os.listdir(sample_dir_path):
                if af555_filename in filename:
                    print("processing:",filename, "...")
                    filename_mihc=filename
                    mihc_path = os.path.join(sample_dir_path, filename_mihc)
                    af555_path_thumb = sample_dir_path + "/wsireg_results_thumb_" + sample_dir + "_af555.png"
                    if os.path.exists(af555_path_thumb):
                            print("file already exists", af555_path_thumb, "skipping it...")
                            break
                
                    image_mihc = pyvips.Image.new_from_file(mihc_path, access="sequential")
                    thumbnail = image_mihc.resize(0.01)
                    if thumbnail.bands > 1:
                        thumbnail = thumbnail[0]
                    low = thumbnail.percent(1)
                    high = thumbnail.percent(99)
                    if high > low:
                        thumbnail = thumbnail.linear(
                            255.0 / (high - low),
                            -low * 255.0 / (high - low)
                        )
                    thumbnail = 255 - thumbnail
                    thumbnail = thumbnail.cast("uchar")
                    binary = thumbnail > 128
                    binary = binary.cast("uchar") * 255
                    binary.write_to_file(af555_path_thumb)
            

            #HE
            for filename in os.listdir(sample_dir_path):
                if he_filename in filename: # "-modality_he_registered.ome.tiff" in filename:
                    print("processing:",filename, "...")
                    filename_he = filename
                    he_path = os.path.join(sample_dir_path, filename_he)
                    he_path_thumb = sample_dir_path+"/wsireg_results_thumb_"+sample_dir+"_he.png"
                    if os.path.exists(he_path_thumb):
                            print("file already exists", he_path_thumb, "skipping it...")
                            break

                    image = pyvips.Image.new_from_file(he_path, access="sequential")
                    thumbnail = image.resize(0.01)
                    grayscale = thumbnail.colourspace("b-w") < 240
                    mask = grayscale.cast("uchar") * 255
                    inverted = 255 - mask
                    inverted.write_to_file(he_path_thumb)
                    break
            
            if dapi_path_thumb is None  or he_path_thumb is None or af555_path_thumb is None:
                print("missing one or more modalities, skipping", sample_dir)
                print("dapi:", dapi_path_thumb)
                print("af555:", af555_path_thumb)
                print("he", he_path_thumb)
                continue

        except pyvips.error.Error as e:
            print("Error in reading ome.tiff")
            continue
            
        
        #overlap images:
        print("overlapping 3 images...")

        overlap_path = sample_dir_path + "/overlap_3_modalities_" + sample_dir + ".png"

        img_dapi = Image.open(dapi_path_thumb).convert("L")
        img_af555 = Image.open(af555_path_thumb).convert("L")
        img_he = Image.open(he_path_thumb).convert("L")

        background = Image.new("RGBA", img_dapi.size, (255, 255, 255, 255))

        color_dapi =  (0, 84, 148) # blue
        color_af555 =  (185, 0, 255) # purple
        color_he    = (255, 140, 0) # orange 
        alpha = 140 # transparency

        col_mihc = Image.new("RGBA", img_dapi.size, (*color_dapi, alpha))
        col_fluo2 = Image.new("RGBA", img_af555.size, (*color_af555, alpha))
        col_he = Image.new("RGBA", img_he.size, (*color_he, alpha))

        mask_mihc = img_dapi.point(lambda p: 255 - p)
        mask_fluo2 = img_af555.point(lambda p: 255 - p)
        mask_he = img_he.point(lambda p: 255 - p)

        layer_mihc = Image.new("RGBA", img_dapi.size)
        layer_fluo2 = Image.new("RGBA", img_af555.size)
        layer_he = Image.new("RGBA", img_he.size)

        layer_mihc.paste(col_mihc, (0, 0), mask_mihc)
        layer_fluo2.paste(col_fluo2, (0, 0), mask_fluo2)
        layer_he.paste(col_he, (0, 0), mask_he)

        combined = Image.alpha_composite(background, layer_mihc)
        combined = Image.alpha_composite(combined, layer_fluo2)
        combined = Image.alpha_composite(combined, layer_he)

        combined.save(overlap_path)

        print("OK!")

main()