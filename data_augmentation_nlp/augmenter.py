import torch
import nlpaug.augmenter.word as naw
import nlpaug.augmenter.sentence as nas
import random
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import nltk
nltk.download('averaged_perceptron_tagger')

# import nlpaug.flow as naf
# aug = naf.Sequential([
#     contextual_word,
#     back_translate,
# ])

import torch
from transformers import PegasusForConditionalGeneration, PegasusTokenizer



class Augmenter:
    def __init__(self):
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model, self.tokenizer = self.__load_model__()
        
        # Augmenter that apply semantic meaning based to textual input.
        self.synonym = naw.SynonymAug()
        # Augmenter that leverage two translation models for augmentation
        self.back_translate = naw.BackTranslationAug(
            from_model_name="Helsinki-NLP/opus-mt-en-de", 
            to_model_name="Helsinki-NLP/opus-mt-de-en", 
            device=self.device
        )

        # Augmenter that leverage contextual word embeddings to find top n similar word for augmentation.
        self.contextual_word = naw.ContextualWordEmbsAug(
            model_path="roberta-base",
            model_type="roberta",
            action='insert', 
            top_k=20,
            device=self.device
        )
    def __load_model__(self):
        model_name = 'tuner007/pegasus_paraphrase'
        tokenizer = PegasusTokenizer.from_pretrained(model_name)
        model = PegasusForConditionalGeneration.from_pretrained(model_name).to(torch.device(self.device))
        return model, tokenizer
    
    def pegasus_paraphrase(self, input_text, max_length=128, do_sample=False, num_return_sequences=2, num_beams=2):
        batch = self.tokenizer(
            input_text,
            truncation=True,
            return_tensors="pt"
        ).to(torch.device(self.device))
        try:
            translated = self.model.generate(
                **batch, 
                max_length=len(batch["input_ids"])+20, 
                do_sample=do_sample,
                num_beams=num_beams, 
                num_return_sequences=num_return_sequences, 
                temperature=1.5
            )
        except:
            import ipdb; ipdb.set_trace()
        tgt_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        return tgt_text

    def preprocess_sent(self, sent):
        import string
        sent = sent.encode("ascii", "ignore").decode().strip()+"."
        # remove punctuation
        nonre = ".,?!:;@"
        punc = "".join([c for c in string.punctuation if c not in nonre])
        sent = sent.translate(str.maketrans('', '', punc))
        sent = sent.strip()
        return sent

    def augment_lst_sents(self, lst_sents, method, ratio):
        lst_sentences = [sentence.strip()+"." for sentence in lst_sents]
        lst_idx = [random.randint(0, len(lst_sentences)-1) for _ in range(int(len(lst_sentences)*ratio))]
        lst_idx = list(set(lst_idx))
        for idx in lst_idx:
            lst_sentences[idx] = self.augment_sent(lst_sentences[idx], method)
        
        return ".".join(lst_sentences)
    
    def augment(self, doc, method="random", ratio=1.0):
        doc = [d for d in doc.split("\n") if d]

        aug_doc = []
        for paragraph in doc:
            lst_sentences = paragraph.split(".")
            aug_lst_sent = self.augment_lst_sents(lst_sentences, method, ratio)
            aug_paragraph = " ".join(aug_lst_sent.split(".")[:-1])
            aug_doc.append(aug_paragraph)
        
        return "\n".join(aug_doc)

    def augment_sent(self, sentence, method):
        if method == "random":
            methods = ["synonym", "back_translate", "contextual_word", "pegasus_paraphrase"]
            lst_method = random.choices(methods, weights=[2, 2, 1, 5], k=10)
        else:
            lst_method = [method]

        for method in lst_method:
            if method == "synonym":
                lst_augs = self.__check__(sentence, self.synonym.augment(sentence, n=500))
                if len(lst_augs) > 0:
                    return random.choice(lst_augs)

            elif method == "back_translate":
                lst_augs = self.__check__(sentence, self.back_translate.augment(sentence, n=1))
                if len(lst_augs) > 0:
                    return random.choice(lst_augs)

            elif method == "contextual_word":
                lst_augs = self.__check__(sentence, self.contextual_word.augment(sentence, n=10))
                if len(lst_augs) > 0:
                    return random.choice(lst_augs)
                
            elif method == "pegasus_paraphrase":
                lst_augs = self.__check__(
                    sentence, 
                    self.pegasus_paraphrase(
                        self.preprocess_sent(sentence), 
                        max_length=256, 
                        do_sample=False, 
                        num_return_sequences=2,
                        num_beams=2
                    )
                )
                if len(lst_augs) > 0:
                    return random.choice(lst_augs)
        return sentence

    def __check__(self, sentence, lst_sentences):
        def find_all_capital(sentence):
            caps = set()
            for i, word in enumerate(sentence.split()):
                if word[0].isupper():
                    caps.add(word)
            return caps

        rep = []
        for sent2 in lst_sentences:
            if find_all_capital(sentence) == find_all_capital(sent2) and sentence != sent2:
                rep.append(sent2)
        # rep.append(sentence)
        return rep
    

def main():
    sentence = "Visit the Learning Center and Money Museum at the Federal Reserve Bank of Cleveland for interactive exhibits and activities."
    augter = Augmenter()
    print("Original text:", sentence)
    print("Augmented text:", augter.augment(sentence))

if __name__ == "__main__":
    main()
