#!/usr/bin/env python


## -----
## WARNING: WORK IN PROGRESS
## DUPLICATE DATES MAY CAUSE DELETED FILES
## -----

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
    pass

def get_exif_data(img_fullpath):
    """Get EXIF data from an image file"""
    try:
        image = Image.open(img_fullpath)
        exif_raw = image.getexif()
        exif_data = {
            TAGS[key]: val
            for key, val in exif_raw.items()
            if key in TAGS
        }
        return exif_data
    except IOError as err:
        logging.warning(f'Error opening "{img_fullpath}"')
        raise FileOpenError from err


## exif = get_exif_data('./img/foto.jpg')


def get_files_dict(directory, extensions=('.jpg', '.jpeg', '.png', '.gif')):
    """Get a dictionary with components of filenames that match any extension in the list, recurring subdirs"""
    logging.info(f'Reading directory: {directory}')
    if isinstance(extensions, str):
        extensions = (extensions.lower(),)
    elif isinstance(extensions, list):
        extensions = tuple([ext.lower() for ext in extensions])
    files_dict = {}
    for path, dirs, files in os.walk(directory):
        for fname in files:
            if fname.lower().endswith(extensions):
                fullpath = path + os.sep + fname
                file_ext = os.path.splitext(fname)[1]
                files_dict[fullpath] = {'path': path, 'fname': fname, 'ext': file_ext}
    
    logging.info(f'{len(files_dict)} files matching the extension filter')
    # df_filenames = pd.DataFrame({'filename': files_dict})
    # return df_filenames
    return files_dict


def date_from_exif(img_fullpath):
    """Get a datetime from EXIF tags"""
    exif_datetags = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
    exif_data = get_exif_data(img_fullpath)
    for datetag in exif_datetags:
        if datetag in exif_data:
            return exif_data[datetag]
    
    logging.warning(f'No EXIF Date tags found in "{img_fullpath}"')
    # ** raise ExifDateError('No EXIF Date tags found')
    return None


def format_exif_date(exif_date, format='%Y-%m-%d_%H-%M-%S'):
    """Converts an EXIF Date to the specified format"""
    # ** TBD: use the format instead of just replacing ':'
    if isinstance(exif_date, str):
        return exif_date.replace(':', '-').replace(' ', '_')
    else:
        return exif_date

def create_renaming_dict(img_dict):
    logging.info('Creating renaming dictionary...')
    renaming_dict = {}
    for img_fullpath, img_parts in img_dict.items():
        img_exif_date = date_from_exif(img_fullpath)
        img_date_fmt = format_exif_date(img_exif_date)
        logging.debug(f'{img_fullpath}\t{img_date_fmt}')
        if img_date_fmt is None:
            renaming_dict[img_fullpath] = None
        else:
            new_name = img_parts['path']+os.sep+img_date_fmt+img_parts['ext']
            renaming_dict[img_fullpath] = new_name
    
    num_good = len({k:v for k,v in renaming_dict.items() if v is not None})
    num_bad  = len(renaming_dict) - num_good
    logging.info(f'{num_good} files have a valid EXIF datetime')
    logging.info(f'{num_bad} files have no valud EXIF datetime')
    
    num_dupl = number_of_duplicates(renaming_dict)
    logging.info(f'{num_dupl} repeated date & time')
    
    return renaming_dict
    

## ** TBD: There can be duplicate dates, so renaming will fail
def number_of_duplicates(renaming_dict):
    """Check if there are any repeated destination names in the same directory"""
    repeated_fnames = []
    existing_fnames = []
    all_fnames = [fn for fn in renaming_dict.values() if fn is not None]
    for fn in all_fnames:
        if fn in existing_fnames:
            repeated_fnames.append(fn)
        else:
            existing_fnames.append(fn)
    return len(repeated_fnames)

## ** Just rename those images that can be renamed, log all
def rename_images(renaming_dict):
    for old_fname, new_fname in renaming_dict.items():
        if new_fname is not None:
            try:
                os.rename(old_fname, new_fname)
                logging.info(f'{old_fname} -> {new_fname}')
            except IOError as err:
                logging.warning(f'{old_fname} coul not be renamed')

def main():
    img_dir = './fotos1'
    img_ext = ['.gif', '.png', '.jpg', '.jpeg']
    
    images = get_files_dict(img_dir, img_ext)
    renaming_dict = create_renaming_dict(images)
    rename_images(renaming_dict)

if __name__ == '__main__':
    main()
