# PREPARE FOR COLMAP SPATIAL MATCHING
# 1. write gps information into EXIF from a text file
# 2. rename the images for separating different lens from each other 
# 
# text file format(split by '\t'):
# image_name    LONGITUDE   LATITUDE    HEIGHT
#
# tips:
# 1. You are supposed to install exiftool first through https://exiftool.org/install.html
# 2. You can choose which line to start reading in the gps information file
# 3. Please make sure that each line is corresponding to the images. For example, the first readline should be the gps information of the first picture in the image folder


import os
import subprocess
import argparse


def rename_images(folder_path, folder_name):
    old_names = os.listdir(folder_path)
    for old_name in old_names:
        new_name = folder_name + '-' + old_name
        os.rename(os.path.join(folder_path, old_name), os.path.join(folder_path, new_name))    


def read_coordinates_from_file(file_name, num):
    coordinates = []
    with open(file_name, 'r') as file:
        lines = file.readlines()
        lines = lines[num-1:]  # 如从第2行开始读，即需要剔除lines的编号为0的元素，即从编号为1的开始保留啦啦啦
        for line in lines:
            values = line.strip().split('\t')
            try:
                longitude = float(values[1])
                latitude = float(values[2])
                elevation = float(values[3])
                coordinates.append((longitude, latitude, elevation))
            except (ValueError, IndexError):
                continue
    file.close()
    return coordinates


def get_sorted_image_files(folder_path):
    image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)) and f.endswith(".JPG")]
    return sorted(image_files)


def exiftool_in_one_folder(folder_path):
    image_files = get_sorted_image_files(folder_path)

    for i, image_file in enumerate(image_files):
        if i >= len(coordinates):
            break
        longitude, latitude, elevation = coordinates[i]
        command = f"exiftool -GPSLongitude={longitude} -GPSLatitude={latitude} -GPSAltitude={elevation} {os.path.join(folder_path, image_file)}"
        subprocess.run(command, shell=True)
    # delete original jpg
    for file in os.listdir(folder_path):
        if file.split('.')[1] == 'JPG_original':
            os.remove(os.path.join(folder_path, file))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--text_file', required=True, type=str, help="path of the text file that contains the gps information")
    parser.add_argument('-i', '--image_folder', required=True, type=str, help="path of the aerial images folder")
    parser.add_argument('-n', '--read_start_number', type=int, default=1, help="the number of the line to start reading")
    parser.add_argument('--several_lens', action='store_true', help="whether the image_folder contain several folders that stand for different camera models")
    parser.add_argument('--rename_images', action='store_true', help="whether the images that belong to differnt camera models should be renamed")
    args = parser.parse_args()

    coordinates = read_coordinates_from_file(args.text_file, args.read_start_number)

    if args.several_lens:
        folders = os.listdir(args.image_folder)
        for folder in folders:
            exiftool_in_one_folder(os.path.join(args.image_folder, folder))
            if args.rename_images:
                rename_images(os.path.join(args.image_folder, folder), folder)
    else:
        exiftool_in_one_folder(args.image_folder)

    print("finished")
    
