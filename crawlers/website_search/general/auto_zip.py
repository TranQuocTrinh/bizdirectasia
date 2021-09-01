import os
import sys
import time
from zipfile import ZipFile
from tqdm import tqdm

folder = sys.argv[1]

time_sleep = 3600
while True:
    fnames = os.listdir(folder)
    # create a ZipFile object
    zipObj = ZipFile('taiwan.zip', 'w')

    for fname in tqdm(fnames, desc="Zip file taiwan.zip ..."):
        # Add multiple files to the zip
        zipObj.write(os.path.join(folder, fname))
    # close the Zip File
    zipObj.close()
    time.sleep(time_sleep)

