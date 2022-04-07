import os
import pandas as pd
from tqdm import tqdm
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

# content = "11 at Crescent is proudly bought to you by Silver Edge Limited. Established in 2017, Silver Edge is an investment firm which do REIT management and direct property fund management. Sliver main focus is in the real estate development for residential and commercial. Being an all rounded real estate company, it for sustainable urbanization, medical, equity asset management, urban development. Over the, the company produced stellar track of both investment - grade commercial and private residential. Their past include 52 Road 37 Road. The 6 bespoke freehold semi - detached will be their latest development in prime district 26 at Crescent. Right at the heart of estate, 11 is near to upcoming Upper station which is only 500m and surrounded by such as, Sheng Supermarket, Plaza and food. 11 is in nature where both Park and Park are the for nature. Prestigious like Ai Tong School, Catholic High School and St are in the vicinity of the 6 landed. Future of 11 can explore more surrounding with the 11 location map. For appointment booking, please book through this or simply call 65 6100 8187 prior to making your way down to view 11 Showroom to avoid disappointment. Due to private or maintenance work, The will be closed on certain days. Therefore it is strongly encourage to secure an appointment before heading down to the. For whom had registered an appointment, you will be assured of enjoying our Direct Developer Price with NO COMMISSION payable by you. All balance available for sale at 11 are based on a first - come - first serve basis. For the booking of unit, it is only valid for a duration of not more than 2 and is subject to approval. 11 is in a prestige landed enclave of at District 20. It six bespoke exclusive freehold landed. The development is surrounded with lush greenery and is perfect for nature. Luxurious finishing and of the quality is for all six of Semi Detached. It comes with built in elevator, 9 to 10m private pool and 2 to 7 car park. in prime landed estate, 11 is close to many. Top like Ai Tong Primary, Junior College and Catholic High are in very close proximity to the development. It is only 6 walk to upcoming Upper Station and 8 min walk to Plaza. Orchard Road is only 15 drive away. Book An view 11 get ( Limited Time ), Direct Developer Price, E - Brochure. with Best Price Possible. Fill up the form on the right and get a copy of 11 Price, E - Brochure, and Latest!"
def call_gpt3(content):
    prompt = """content: Tesla was founded in 2003 by a group of engineers who wanted to prove that people didnt need to compromise to drive electric  that electric vehicles can be better, quicker and more fun to drive than gasoline cars. Today, Tesla builds not only all-electric vehicles but also infinitely scalable clean energy generation and storage products. Tesla believes the faster the world stops relying on fossil fuels and moves towards a zero-emission future, the better.\n\nLaunched in 2008, the Roadster unveiled Teslas cutting-edge battery technology and electric powertrain. From there, Tesla designed the worlds first ever premium all-electric sedan from the ground up  Model S  which has become the best car in its class in every category. Combining safety, performance, and efficiency, Model S has reset the worlds expectations for the car of the 21st century with the longest range of any electric vehicle, over-the-air software updates that make it better over time, and a record 0-60 mph acceleration time of 2.28 seconds as measured by Motor Trend. In 2015, Tesla expanded its product line with Model X, the safest, quickest and most capable sport utility vehicle in history that holds 5-star safety ratings across every category from the National Highway Traffic Safety Administration. Completing CEO Elon Musks Secret Master Plan, in 2016, Tesla introduced Model 3, a low-priced, high-volume electric vehicle that began production in 2017. Soon after, Tesla unveiled the safest, most comfortable truck ever  Tesla Semi  which is designed to save owners at least $200,000 over a million miles based on fuel costs alone. In 2019, Tesla unveiled Model Y, a mid-size SUV, with seating for up to seven, and Cybertruck, which will have better utility than a traditional truck and more performance than a sports car.\n\nTesla vehicles are produced at its factory in Fremont, California, and Gigafactory Shanghai. To achieve our goal of having the safest factories in the world, Tesla is taking a proactive approach to safety, requiring production employees to participate in a multi-day training program before ever setting foot on the factory floor. From there, Tesla continues to provide on-the-job training and track performance daily so that improvements can be made quickly. The result is that Teslas safety rate continues to improve while production ramps.\n\nTo create an entire sustainable energy ecosystem, Tesla also manufactures a unique set of energy solutions, Powerwall, Powerpack and Solar Roof, enabling homeowners, businesses, and utilities to manage renewable energy generation, storage, and consumption. Supporting Teslas automotive and energy products is Gigafactory 1  a facility designed to significantly reduce battery cell costs. By bringing cell production in-house, Tesla manufactures batteries at the volumes required to meet production goals, while creating thousands of jobs.\n\nAnd this is just the beginning. With Tesla building its most affordable car yet, Tesla continues to make products accessible and affordable to more and more people, ultimately accelerating the advent of clean transport and clean energy production. Electric cars, batteries, and renewable energy generation and storage already exist independently, but when combined, they become even more powerful  thats the future we want.\n\nsumarize: Tesla is accelerating the world's transition to sustainable energy with electric cars, solar and integrated renewable energy solutions for homes and businesses. Our mission is to accelerate the world's transition to sustainable energy. With global temperatures rising, the faster we free ourselves from fossil fuel reliance and achieve a zero-emission future, the better. In pursuit of this mission, we make electric vehicles that are not just great EVs, but the best cars, period. We also produce and install infinitely scalable clean energy generation and storage products that help our customers further decrease their environmental impact. When it comes to achieving our goals, we pride ourselves in accomplishing what others deem impossible. We are opening new factories and increasing our output everyday  join us in building a sustainable future.\n\ncontent: """+content+"\n\nsumarize:"
    # remove non-ascii characters in prompt
    prompt = prompt.encode('ascii', 'ignore').decode('ascii')
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response["choices"][0]["text"]

from extract_keywords_from_website import analyze_text_syntax, get_noun_phrases
def main():
    df = pd.read_csv("1000_urls_singapore_extract_keyword.csv")
    df = df[df["summary_or_not"]=="summary"].sample(n=20).reset_index(drop=True)
    print(df.shape)
    print(df.columns)
    analyze, noun_phrase_list, summary_list = [], [], []
    for i,row in tqdm(df.iterrows(), total=df.shape[0]):
        summ = call_gpt3(row["content"])
        res, _ = analyze_text_syntax(summ)
        ana, noun_ph = get_noun_phrases(res)
        
        summary_list.append(summ)
        analyze.append(ana)
        noun_phrase_list.append(noun_ph)

    df["summary_gpt3"] = summary_list
    df["analyze_gpt3"] = analyze
    df["noun_phrase_list_gpt3"] = noun_phrase_list

    df.to_csv("10_urls_singapore_extract_keyword_sum_by_gpt3.csv", index=False)

if __name__ == "__main__":
    main()