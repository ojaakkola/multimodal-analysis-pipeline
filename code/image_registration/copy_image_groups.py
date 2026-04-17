import csv
from pathlib import Path
import shutil
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("samplenames_csv_path", help="path to the samplename csv")
    parser.add_argument("input_path_he", help="path to the cropped H&E images")
    parser.add_argument("input_path_dapi", help="path to the cropped DAPI images")
    parser.add_argument("input_path_cd3", help="path to the cropped CD3 images")
    parser.add_argument("output_path", help="path to the image groups")
    args = parser.parse_args()

    os.makedirs(args.output_path, exist_ok=True)

    csv_file = Path(args.samplenames_csv_path)
    source_dir_he = Path(args.input_path_he)
    source_dir_dapi = Path(args.input_path_dapi)
    source_dir_af555 = Path(args.input_path_cd3)
    output_dir = Path(args.output_path)

    with csv_file.open(newline="") as f:
        reader = csv.reader(f, delimiter=";")
        
        for row in reader:
            if not row:
                continue #empty row
            he, mihc = row[0], row[1].split(",")[0] # H&E and mIHC samplenames from the csv file row

            # create a folder for the image group
            group_dir = output_dir / he
            group_dir.mkdir(parents=True, exist_ok=True)

            # copy an H&E image
            for file in source_dir_he.iterdir():
                if not file.is_file():
                    continue
                name = file.name
                if he in name:
                    filename = file.stem  # filename without ".tif"
                    dest_file = group_dir / file.name

                    if dest_file.exists():
                        print(f"File already exists {dest_file}...")
                    else:
                        shutil.copy(file, dest_file)
                        print(f"Copied {file.name} to {group_dir}")
                        
            # copy a DAPI image
            for file in source_dir_dapi.iterdir():
                if not file.is_file():
                    continue
                name = file.name
                if ("TM" in name) and ("DAPI" in name) and ("_"+mihc+"_" in name):
                    filename = file.stem
                    parts = filename.split("_")
                    s_part = next((p for p in parts if p.startswith("s")), None)
                    if not s_part:
                        id = "49"
                    else:
                        s_index = int(s_part[1:])
                        id = filename.split("_")[s_index]
                    if mihc == id:
                        dest_file = group_dir / file.name
                        if dest_file.exists():
                            print(f"File already exists {dest_file}...")
                        else:
                            shutil.copy(file, dest_file)
                            print(f"Copied {file.name} -> {group_dir}")                            

            # copy a CD3 image
            for file in source_dir_af555.iterdir():
                if not file.is_file():
                    continue
                name = file.name
                if ("TM" in name) and ("AF555" in name) and ("_"+mihc+"_" in name):
                    filename = file.stem
                    parts = filename.split("_")
                    s_part = next((p for p in parts if p.startswith("s")), None)
                    if not s_part:
                        id = "49"
                    else:
                        s_index = int(s_part[1:])
                        id = filename.split("_")[s_index]
                    if mihc == id:
                        dest_file = group_dir / file.name
                        if dest_file.exists():
                            print(f"File already exists {dest_file}...")
                        else:
                            shutil.copy(file, dest_file)
                            print(f"Copied {file.name} -> {group_dir}")
                     
main()