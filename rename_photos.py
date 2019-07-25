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

## ** change extension as a test of renaming files **
def change_extension(fname, ext1, ext2):
    if fname.endswith('.'+ext1):
        new_fname = fname[:-len(ext1)]+ext2
    os.rename(fname, new_fname)


def main():
    img_dir = './fotos'
    img_ext = ['.gif', '.png', '.jpg', '.jpeg']
    
    images = get_filenames(img_dir, img_ext)
    logging.info('Creating renaming dictionary...')
    renaming_dict = create_renaming_dict(images)
    good_files = {k:v for k,v in renaming_dict.items() if v is not None}
    bad_files = {k:v for k,v in renaming_dict.items() if v is None}
    logging.info(f'{len(good_files)} GOOD files in dictionary')
    logging.info(f'{len(bad_files)} BAD files in dictionary')
    # rename_images(renaming_dict)

if __name__ == '__main__':
    main()
