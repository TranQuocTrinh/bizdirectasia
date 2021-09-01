import json
import os
import abn
from tqdm import tqdm
import sys

thread = int(sys.argv[1])
threads = []
for i in range(9):
    th = ((i+1)*10**10,(i+2)*10**10)
    threads.append(th)

batch = 100000
i = 0
lst_abn = []

for x in tqdm(range(threads[thread][0],threads[thread][1])):
    abn_check = str(x)
    while len(abn_check) != 11:
        abn_check = '0' + abn_check
    check = abn.validate(abn_check)
    if check != False:
        lst_abn.append(check)

    if len(lst_abn) == batch:
        json.dump(lst_abn,open('abn/thread_'+str(thread)+'_file_'+str(i)+'.json','w'))
        lst_abn = []
        i += 1

json.dump(lst_abn,open('abn/thread_'+str(thread)+'_file_'+str(i)+'.json','w'))
i += 1
