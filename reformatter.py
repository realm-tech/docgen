import os
import shutil
from glob import glob
from tqdm import tqdm
from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument('--input_path', default='./dataset')
parser.add_argument('--output_path', default='./reformatted_dataset')

args = parser.parse_args()

os.makedirs(args.output_path, exist_ok=True)

output_imgs_path = os.path.join(args.output_path, 'train_imgs')
output_text_path = os.path.join(args.output_path, 'train_gts')
os.makedirs(output_imgs_path, exist_ok=True)
os.makedirs(output_text_path, exist_ok=True)

train_list_file = open(os.path.join(args.output_path, 'train_list.txt'), 'w')

imgs_glob = args.input_path + '/**/*warped*.png'
print(imgs_glob)

for img in tqdm(glob(imgs_glob, recursive=True), desc="Iterating over images and texts ... "):
    orig_text_path = img + '.txt'
    
    img_name = ""
    for part in img.split('/'):
        if part not in ['.']:
            img_name += '_' + part
    img_name = img_name[1:]

    txt_name = img_name + '.txt'

    train_list_file.write(img_name + '\n')

    dst_img = os.path.join(output_imgs_path, img_name)
    dst_text = os.path.join(output_text_path, txt_name)
    shutil.copy(img, dst_img)
    shutil.copy(orig_text_path, dst_text)


train_list_file.close()
