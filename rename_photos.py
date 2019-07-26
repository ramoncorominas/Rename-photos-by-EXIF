#!/usr/bin/env python

import os
import datetime as dt
import logging
# import asyncio
# import pandas as pd

from PIL import Image
from PIL.ExifTags import TAGS

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

class FileOpenError(Exception):
    """Raise if a file cannot be opened or is invalid"""
    pass

class ExifDateError(Exception):
    """Raise if an image does not contain any EXIF Date tags"""
    logging.warning('QUÉ PACHA')
    return 'aaaa-mm-dd_hh-mm-ss'
    pass

def get_exif_data(img_filename):
    """Get EXIF data from an image file"""
    try:
        image = Image.open(img_filename)
        exif_raw = image.getexif()
        exif_data = {
            TAGS[key]: val
            for key, val in exif_raw.items()
            if key in TAGS
        }
        return exif_data
    except IOError as err:
        logging.warning(f'Error opening {img_filename}')
        raise FileOpenError from err


## exif = get_exif_data('./img/foto.jpg')


def get_filenames(directory, extensions=('.jpg', '.jpeg', '.png', '.gif')):
    """Get a list of filenames that match any extension in the list, recurring subdirs"""
    logging.info(f'Reading directory: {directory}')
    if isinstance(extensions, str):
        extensions = (extensions.lower(),)
    elif isinstance(extensions, list):
        extensions = tuple([ext.lower() for ext in extensions])
    filenames = []
    for path, dirs, files in os.walk(directory):
        filenames += [
            path + os.sep + filename
            for filename in files
            if filename.lower().endswith(extensions)
        ]
    logging.info(f'{len(filenames)} files matching the extension filter')
    # df_filenames = pd.DataFrame({'filename': filenames})
    # return df_filenames
    return filenames


def date_from_exif(img_filename):
    """Get a datetime from EXIF tags"""
    exif_datetags = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
    exif_data = get_exif_data(img_filename)
    for datetag in exif_datetags:
        if datetag in exif_data:
            return exif_data[datetag]
    
    logging.warning(f'No EXIF Date tags found in {img_filename}')
    # ** raise ExifDateError('No EXIF Date tags found')
    return None


def format_exif_date(exif_date, format='%Y-%m-%d_%H-%M-%S'):
    """Converts an EXIF Date to the specified format"""
    # ** TBD: use the format instead of just replacing ':'
    if isinstance(exif_date, str):
        return exif_date.replace(':', '-').replace(' ', '_')
    else:
        return exif_date

def create_renaming_dict(img_filenames):
    renaming_dict = {}
    for img_filename in img_filenames:
        img_exif_date = date_from_exif(img_filename)
        img_date_fmt = format_exif_date(img_exif_date)
        logging.debug(f'{img_filename}\t{img_date_fmt}')
        renaming_dict[img_filename] = img_date_fmt
    return renaming_dict
    

## ** TBD: There can be duplicate dates, so renaming will fail
def number_of_duplicates(renaming_dict):
    """Check if there are any repeated dates in the same directory"""
    repeated_dates = []
    existing_dates = []
    all_dates = [dt for dt in renaming_dict.values() if dt is not None]
    for date_val in all_dates:
        if date_val in existing_dates:
            repeated_dates.append(date_val)
        else:
            existing_dates.append(date_val)
    return len(repeated_dates)


    

    return renaming_dict

## ** Just rename those images that can be renamed, log all
def rename_images(renaming_dict):
    for old_fname, new_fname in renaming_dict.items():
        try:
            os.rename(old_fname, new_fname)
            logging.info(f'{old_fname} -> {new_fname}')
        except IOError as err:
            logging.warning(f'{old_fname} coul not be renamed')
        


def main():
    img_dir = './fotos'
    img_ext = ['.gif', '.png', '.jpg', '.jpeg']
    
    images = get_filenames(img_dir, img_ext)
    logging.info('Creating renaming dictionary...')
    renaming_dict = create_renaming_dict(images)
    num_good = len({k:v for k,v in renaming_dict.items() if v is not None})
    num_bad  = len(renaming_dict) - num_good
    num_dupl = number_of_duplicates(renaming_dict)
    logging.info(f'{num_good} files have a valid EXIF datetime')
    logging.info(f'{num_bad} files have no valud EXIF datetime')
    logging.info(f'{num_dupl} repeated date & time')
    
    
    # rename_images(renaming_dict)

if __name__ == '__main__':
    main()
