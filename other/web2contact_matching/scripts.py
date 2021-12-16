

dct = {
    # "nz": "New Zealand",
    # "bn": "Brunei",
    # "kh": "Cambodia",
    # "la": "Laos",
    # "th": "Thailand",
    # "hk": "Hong Kong",
    # "ph": "Philippines",
    # "sg": "Singapore",
    # "my": "Malaysia", - Dien
    "tw": "Taiwan",
    # "id": "Indonesia",
    "vn": "Vietnam",
    "kr": "Korea",
    # "jp": "Japan",
    "au": "Australia",
}
# """
# Japan
# Vietnam
# Hong Kong
# Australia
# Singapore
# Laos
# Taiwan
# Indonesia
# Korea
# Thailand
# Philippines
# Malaysia
# """
# all_command = ""
# # & python get_content.py --task report --cache_dir cache_text_{}/ --domain_path domain/networksdb.io-domains_{}.txt \
# for country_code in dct:
#     one_shot = '''echo "--------- STEP 1: GET CONTENT OF WEBSITE {} ---------" \
#     && time python get_content.py --task query_text --cache_dir cache_text_{}/ --num_thread 32 --domain_path domain/networksdb.io-domains_{}.txt \
#     && echo "--------- STEP 2: EXTRACT COMPANY NAME FROM WEBSITE {} ---------" \
#     && time python extract_company-name_address_country.py --cache_text_dir cache_text_{}/ --cache_extract_dir cache_extract_{}/ --output_csv_path enrich_{}.csv \
#     && echo "--------- STEP 3: MATCHING TO FIND WEBSITE FOR BIZDIRECT DATA {} ---------" \
#     && time python matching.py --csv_biz_path "" --csv_enrich_path enrich_{}.csv --country {} --output_final_csv_path result_matching_{}.csv'''.format(dct[country_code], country_code, country_code, dct[country_code], country_code, country_code, dct[country_code].lower().replace(" ","_"), dct[country_code], dct[country_code].lower().replace(" ","_"), dct[country_code], dct[country_code].lower().replace(" ","_"))
#     all_command = all_command + " && " + one_shot

# print(all_command)

country_code = "tw"
one_shot = '''echo "--------- STEP 1: GET CONTENT OF WEBSITE {} ---------" \
    && time python get_content.py --task query_text --cache_dir cache_text_{}/ --num_thread 64 --domain_path domain/networksdb.io-domains_{}.txt \
    & python get_content.py --task report --cache_dir cache_text_{}/ --domain_path domain/networksdb.io-domains_{}.txt \
    && echo "--------- STEP 2: EXTRACT COMPANY NAME FROM WEBSITE {} ---------" \
    && time python extract_company-name_address_country.py --cache_text_dir cache_text_{}/ --cache_extract_dir cache_extract_{}/ --output_csv_path enrich_{}.csv \
    && echo "--------- STEP 3: MATCHING TO FIND WEBSITE FOR BIZDIRECT DATA {} ---------" \
    && time python matching.py --csv_biz_path biz_{}.csv --csv_enrich_path enrich_{}.csv --country {} --output_final_csv_path result_matching_{}.csv'''.format(
        dct[country_code], 
        country_code, country_code,
        country_code, country_code, 
        dct[country_code], 
        country_code, country_code, dct[country_code].lower().replace(" ","_"), 
        dct[country_code], 
        dct[country_code].lower().replace(" ","_"), dct[country_code].lower().replace(" ","_"), dct[country_code], dct[country_code].lower().replace(" ","_")
        )
print(one_shot)
