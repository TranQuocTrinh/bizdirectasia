import os
import numpy as np
import pandas as pd
import logging
import torch
from torch.utils.data import dataset
from datasets import load_dataset, load_metric
from transformers import (
    LEDForConditionalGeneration,
    LEDConfig,
    LEDTokenizer,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    set_seed,
    EarlyStoppingCallback,
    DataCollatorForSeq2Seq
)

logger = logging.getLogger(__name__)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    # Input
    parser.add_argument("--test_file", type=str, default=None, help="Path to test file.")
    parser.add_argument("--model_path", type=str, default=None, help="Path to model.")
    parser.add_argument("--max_source_length", default=4096, type=int, help="Maximum length of the source sequence")
    parser.add_argument("--max_target_length", default=256, type=int, help="Maximum length of the target sequence")
    # Output
    parser.add_argument("--output_path", type=str, default=None, help="Path to output file.")
    args = parser.parse_args()

    # Load model, tokenizer
    tokenizer = LEDTokenizer.from_pretrained(args.model_path)
    model = LEDForConditionalGeneration.from_pretrained(args.model_path)
    model.eval()
    devive = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Model to device:", devive)
    model.to(devive)

    # Load test data
    df = pd.read_csv(args.test_file)
    predictions = []
    bar = tqdm(df.iterrows(), total=len(df))
    with torch.no_grad():
        for i, row in bar:
            # Tokenize
            inputs = tokenizer(
                input_text, max_length=args.max_source_length, padding="max_length", truncation=True, return_tensors="pt"
            )
            # To device
            inputs = {k: v.to(devive) for k, v in inputs.items()}
            # Inference
            output = model.generate(
                **inputs, 
                max_length=args.max_target_length, 
                temperature=1.0, 
                no_repeat_ngram_size=3,
                do_sample=True,
                early_stopping=True,
                num_return_sequences=1
            )
            # Decode
            output = tokenizer.decode(output[0], skip_special_tokens=True)
            precisions.append(output)
        
    # Save results
    df["predictions"] = predictions
    df.to_csv(args.output_path, index=False)


if __name__ == "__main__":
    main()