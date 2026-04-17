from wsireg.wsireg2d import WsiReg2D
from wsireg.parameter_maps.preprocessing import ImagePreproParams
import os
import glob
import csv
import argparse
from pathlib import Path

# testiaja vielä!
# result_folders palauttaa aina NONE !!!

def result_folders(samplenumbers, project_folder, rotation_csv_path, group, input_base_path):    

    pair_name = group.name
    folder_for_image_group = os.path.join(input_base_path, pair_name)
    os.makedirs(folder_for_image_group, exist_ok=True)
    
    with open(rotation_csv_path, mode ='r') as file:
        data = csv.reader(file)
        he = None
        for row in data:
            mihc = row[0]
            for key, value in samplenumbers.items():
                if value == mihc:
                    # H&E-mIHC pair found
                    he = key
                    break
    
            if he == pair_name and len(row)==6: # check these
                print("Processing:",he, mihc)

                try:
                    rotation=int(row[5]) # wsireg rotation parameter
                except ValueError:
                    print("Value error: int(wsireg_rotation) row", row)
                    rotation = None
                    continue # next row in the file

                print(pair_name, row[0], rotation)

                print(glob.glob(f"{folder_for_image_group}"))
                try:
                    he_filename = glob.glob(f"{folder_for_image_group}/*_HE*")[0]
                    he_name = "_".join((he_filename.split("/")[-1]).split("_")[:2])
                    print(he_name)
                except IndexError:
                    print("No HE files found.")
                    return

                try:
                    mihc_filename_af555 = glob.glob(f"{folder_for_image_group}/*AF555*")[0]
                    mihc_name_af555 = "_".join((mihc_filename_af555.split("/")[-1]).split("_")[:8])
                    print(mihc_name_af555)
                except IndexError:
                    print("No mIHC AF555 files found.")
                    return

                try:
                    mihc_filename_dapi = glob.glob(f"{folder_for_image_group}/*DAPI*")[0]
                    mihc_name_dapi = "_".join((mihc_filename_dapi.split("/")[-1]).split("_")[:8])
                    print(mihc_name_dapi)
                except IndexError:
                    print("No mIHC DAPI files found.")
                    return

                results_sub_folder = project_folder / f"{he_name}_{mihc_name_af555}"
                if os.path.exists(results_sub_folder):
                    print("folder already exists", results_sub_folder, "skipping it...")
                    return
                else:
                    os.makedirs(results_sub_folder)

                return he_name, mihc_name_af555, he_filename, mihc_filename_dapi, mihc_filename_af555, results_sub_folder, rotation



def image_registration(he_name, mihc_name_af555, he_filename, mihc_filename_dapi, mihc_filename_af555, image_res_he, image_res_mihc, results_sub_folder, rotation):
    
    name = "wsireg_output_"+he_name+"_"+mihc_name_af555
    reg_graph = WsiReg2D(name, results_sub_folder)

    preprocessing_params_ihc = ImagePreproParams(
        image_type="FL",
        rot_cc=rotation,
    )

    preprocessing_params_he = ImagePreproParams(
        image_type="BF", 
    )

    # add modality 1 (mIHC = DAPI)
    reg_graph.add_modality(
        modality_name="modality_dapi",
        image_fp=mihc_filename_dapi,
        image_res=image_res_mihc,
        preprocessing=preprocessing_params_ihc,
    )

    # add modality 2 (H&E)
    reg_graph.add_modality(
        modality_name="modality_he",
        image_fp=he_filename,
        image_res=image_res_he,
        preprocessing=preprocessing_params_he,
    )

    # add additional mIHC images
    reg_graph.add_attachment_images(
        modality_name= "modality_af555",
        attachment_modality = "modality_dapi",
        image_fp = mihc_filename_af555,
        image_res=image_res_mihc
    )

    reg_graph.add_reg_path(
        "modality_dapi",
        "modality_he",
        thru_modality = None,
        reg_params=["rigid", "nl"],
    )

    print("registering...", name)
    reg_graph.register_images()
    print("saving...", name)
    reg_graph.save_transformations()
    print("transforming...",name)
    reg_graph.transform_images(file_writer="ome.tiff")
    print("done!", name)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("output_path", help="project results base path (there should be image_groups folder in this path)")
    parser.add_argument("samplenumbers_csv_path", help="path to the csv with samplenames of the images to be registered")
    parser.add_argument("he_res", type=float, help="micrometers/pixel (H&E), for example 0.1214")
    parser.add_argument("mIHC_res", type=float, help="micrometers/pixel (mIHC), for example 0.3249")
    parser.add_argument("rotation_csv", help="csv with mIHC (coordinate) and rotation info")
    args = parser.parse_args()
    project_folder = args.output_path
    samplenames_csv_path = args.samplenumbers_csv_path
    image_res_he = args.he_res
    image_res_mihc = args.mIHC_res
    rotation_csv_path = args.rotation_csv

    os.makedirs(project_folder, exist_ok=True)

    # corresponding H&E and mIHC samplenames
    samplenumbers = {}
    with open(samplenames_csv_path, mode ='r') as file:
        data = csv.reader(file, delimiter=";")
        for row in data:
            if not row:
                continue
            he, mihc = row[0], row[1].split(",")[0]
            samplenumbers[he] = mihc

    print(samplenumbers)

    input_base_path = Path(project_folder) / "image_groups"
    group_folders = [p for p in input_base_path.rglob("*") if p.is_dir()]

    output_results_path = Path(project_folder) / "image_registration_results"
    os.makedirs(output_results_path, exist_ok=True)

    for group in group_folders:
        print("Image group:", group)
        return_values = result_folders(samplenumbers, output_results_path, rotation_csv_path, group, input_base_path)
        if return_values is None:
            continue
        he_name, mihc_name_af555, he_filename, mihc_filename_dapi, mihc_filename_af555, results_sub_folder, rotation = return_values
        image_registration(he_name, mihc_name_af555, he_filename, mihc_filename_dapi, mihc_filename_af555, image_res_he, image_res_mihc, results_sub_folder, rotation)


main()