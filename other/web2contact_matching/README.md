### Kill ray:
```shell
ray stop && ps aux | grep ray::IDLE | grep -v grep | awk '{print $2}' | xargs kill -9
```
```shell

echo "--------- STEP 1: GET CONTENT OF WEBSITE ---------" \
&& time python get_content.py --task query_text --cache_dir cache_text/ --num_thread 8 --domain_path domain/newzealand.txt \
& python get_content.py --task report --domain_path domain/newzealand.txt \
&& echo "--------- STEP 2: EXTRACT COMPANY NAME FROM WEBSITE ---------" \
&& time python extract_company-name_address_country.py --cache_text_dir cache_text/ --cache_extract_dir cache_extract/ --output_csv_path enrich_newzealand.csv \
&& echo "--------- STEP 3: MATCHING TO FIND WEBSITE FOR BIZDIRECT DATA ---------" \
&& time python matching.py --csv_biz_path "" \
& wait
```