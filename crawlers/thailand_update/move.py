import os
import sys
from tqdm import tqdm


source = sys.argv[1]
dsc = sys.argv[2]

names = os.listdir(source)

for name in tqdm(names):
    if not os.path.exists(dsc+name):
        os.rename(source+name, dsc+name)

