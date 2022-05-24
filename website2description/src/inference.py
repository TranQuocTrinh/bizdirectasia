import torch
from transformers import (
    LEDForConditionalGeneration,
    LEDTokenizer,
)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    # Input
    parser.add_argument("--model_path", type=str, default=None, help="Path to model.")
    parser.add_argument("--max_source_length", default=4096, type=int, help="Maximum length of the source sequence")
    parser.add_argument("--max_target_length", default=128, type=int, help="Maximum length of the target sequence")
    parser.add_argument("--device", default="cuda", type=str, help="Device to use")
    args = parser.parse_args()

    # Load model, tokenizer
    tokenizer = LEDTokenizer.from_pretrained(args.model_path)
    model = LEDForConditionalGeneration.from_pretrained(args.model_path)
    model.eval()
    
    devive = torch.device("cuda" if torch.cuda.is_available() and args.device == "cuda" else "cpu")
    print("Model to device:", devive)
    model.to(devive)

    from utils import get_content_company, preprocess_text
    while True:
        website = input(">>>>website (example: https://www.bizdirectasia.com, press q to quit): ")
        if website == "":
            print("Please input website")
            continue
        if website == "q":
            break
        input_text = get_content_company(website)
        if input_text is None:
            print("------ Can't get content!")
            continue
        input_text = preprocess_text(input_text)
        if len(input_text) == 0:
            print("------ Can't get content!")
            continue
        print("------ Content:", input_text)
        
        with torch.no_grad():
            # Tokenize
            inputs = tokenizer(
                input_text, 
                max_length=args.max_source_length, 
                padding="max_length", 
                truncation=True, 
                return_tensors="pt"
            )
            # To device
            inputs = {k: v.to(devive) for k, v in inputs.items()}
            # Inference
            output = model.generate(
                **inputs, 
                max_length=args.max_target_length, 
                temperature=0.8, 
                no_repeat_ngram_size=4,
                do_sample=True,
                early_stopping=True,
                num_return_sequences=1,
                min_length=50,
            )
            # Decode
            desc = tokenizer.decode(output[0], skip_special_tokens=True)
            desc = desc.strip().split("\n")[0]
            desc = ".".join(desc.split(".")[:-1])+"."
        print("------ Description:", desc)


if __name__ == "__main__":
    main()