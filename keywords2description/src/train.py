# Importing stock libraries
from numpy.core.arrayprint import str_format
from numpy.core.fromnumeric import sort
from datasets import CustomDataset
from tqdm import tqdm
import numpy as np
import ast
import datetime
from datetime import timedelta
import time
import os
import pandas as pd
import torch
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel
import torch.nn.functional as F
from torch.utils.data import DataLoader

# Importing the T5 modules from huggingface/transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
from transformers import AutoModel, AutoTokenizer
from transformers import BartForConditionalGeneration, BartTokenizer
from transformers import EncoderDecoderModel

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def convert_seconds(seconds):
    sec = timedelta(seconds=seconds)
    d = datetime.datetime(1, 1, 1) + sec
    str_format = "%d days, %d hours, %d minutes, %d seconds" % (
        d.day-1, d.hour, d.minute, d.second)
    return str_format


def train(epoch, tokenizer, model, device, loader, optimizer):
    model.train()
    training_loss = 0
    bar = tqdm(enumerate(loader, 0), total=len(loader))
    for _, data in bar:
        y = data["target_ids"].to(device, dtype=torch.long)
        y_ids = y[:, :-1].contiguous()
        lm_labels = y[:, 1:].clone().detach()
        lm_labels[y[:, 1:] == tokenizer.pad_token_id] = -100

        ids = data["source_ids"].to(device, dtype=torch.long)
        mask = data["source_mask"].to(device, dtype=torch.long)

        outputs = model(
            input_ids=ids,
            attention_mask=mask,
            decoder_input_ids=y_ids,
            labels=lm_labels
        )
        loss = torch.mean(outputs.loss)
        training_loss += loss.item()
        bar.set_postfix(Training_Loss=loss.item())

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    return training_loss / len(loader)


def validate(tokenizer, model, device, loader):
    model.eval()
    predictions = []
    actuals = []
    with torch.no_grad():
        bar = tqdm(enumerate(loader, 0), total=len(loader))
        for _, data in bar:
            y = data["target_ids"].to(device, dtype=torch.long)
            ids = data["source_ids"].to(device, dtype=torch.long)
            mask = data["source_mask"].to(device, dtype=torch.long)

            generated_ids = model.module.generate(
                input_ids=ids,
                attention_mask=mask,
                max_length=320,
                num_beams=2,
                repetition_penalty=2.5,
                length_penalty=1.0,
                early_stopping=True
            )
            preds = [tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                     for g in generated_ids]
            target = [tokenizer.decode(t, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                      for t in y]

            predictions.extend(preds)
            actuals.extend(target)
    return predictions, actuals


def main():

    class config:
        BATCH_SIZE = 30
        TRAIN_EPOCHS = 50
        LEARNING_RATE = 5e-4
        SEED = 42
        MAX_LEN = 128
        SUMMARY_LEN = 320
        # "google/roberta2roberta_L-24_discofuse"  # "t5-base"
        MODEL_BASE = "t5-base"  # "google/pegasus-xsum"
        MODEL_PATH = f"model_{MODEL_BASE.replace('/','-')}_key2des.pt"
        PATH_DF = "/home/ubuntu/tqtrinh/description2keywords/data/japan/baseconnect_trans_full_filter.csv"
        TEST_DF = "/home/ubuntu/tqtrinh/keywords2description/src_seq2seq_t5_model/final_model/epoch_39_pred_t5-base_300_samples.csv"
        FRAC_SAMPLE = 1
        OUTPUT_TEST_PATH = f"pred_{MODEL_BASE.replace('/','-')}_filter_300_samples.csv"

    # Set random seeds and deterministic pytorch for reproducibility
    torch.manual_seed(config.SEED)  # pytorch random seed
    np.random.seed(config.SEED)  # numpy random seed
    torch.backends.cudnn.deterministic = True

    # tokenzier for encoding the text
    if config.MODEL_BASE == "t5-base":
        tokenizer = T5Tokenizer.from_pretrained(config.MODEL_BASE)
    else:
        tokenizer = PegasusTokenizer.from_pretrained(config.MODEL_BASE)

    # Importing and Pre-Processing the domain data
    # Selecting the needed columns only.
    # Adding the summarzie text in front of the text. This is to format the dataset similar to how T5 model was trained for summarization task.
    df = pd.read_csv(config.PATH_DF, encoding="utf-8")
    df = df.sample(frac=config.FRAC_SAMPLE).reset_index(drop=True)
    df["keywords"] = [", ".join(ast.literal_eval(keywords))
                      for keywords in df.keywords.values]
    df["description"] = "description: " + df.description
    # df = df[["description", "keywords"]]
    df.keywords = "keywords: " + df.keywords
    print(df.head())

    # Creation of Dataset and Dataloader
    # train_size = 0.8  # 1-0.001
    # train_dataset = df.sample(frac=train_size, random_state=config.SEED)
    # test_dataset = df.drop(train_dataset.index).reset_index(drop=True)
    # train_dataset = train_dataset.reset_index(drop=True)

    train_dataset = df[:-300].reset_index(drop=True)
    test_dataset = df[-300:].reset_index(drop=True)

    # df.index = df["company_id"]
    # test_dataset = pd.read_csv(config.TEST_DF, encoding="utf-8")
    # test_dataset = df.loc[test_dataset.company_id, ].reset_index(drop=True)
    # train_dataset = df.drop(test_dataset.index).reset_index(drop=True)

    print("FULL Dataset: {} \t Columns: {}".format(df.shape, df.columns))
    print("TRAIN Dataset: {} \t Columns: {}".format(
        train_dataset.shape, train_dataset.columns))
    print("TEST Dataset: {} \t Columns: {}".format(
        test_dataset.shape, test_dataset.columns))

    # Creating the Training and Testing dataset for further creation of Dataloader
    training_set = CustomDataset(
        dataframe=train_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN
    )
    test_set = CustomDataset(
        dataframe=test_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN
    )

    # Defining the parameters for creation of dataloaders
    training_loader = DataLoader(
        training_set,
        batch_size=config.BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )
    test_loader = DataLoader(
        test_set,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )
    print(f"\nModel base: {config.MODEL_BASE}")
    # Defining the model. We are using t5-base model and added a Language model layer on top for generation of Summary.
    if config.MODEL_BASE == "t5-base":
        model = T5ForConditionalGeneration.from_pretrained(config.MODEL_BASE)
    else:
        model = PegasusForConditionalGeneration.from_pretrained(
            config.MODEL_BASE)

    # Defining the optimizer that will be used to tune the weights of the network in the training session.
    model = model.to(device)
    # if os.path.exists(config.MODEL_PATH):
    #     print("============ LOAD MODEL AND CONTINUE TO TRAINING ============")
    #     model.load_state_dict(torch.load(
    #         config.MODEL_PATH, map_location=device))

    print("============ LOAD MODEL AND CONTINUE TO TRAINING ============")
    print("epoch_49_"+config.MODEL_PATH)
    model.load_state_dict(torch.load(
        "epoch_49_"+config.MODEL_PATH, map_location=device))

    model = nn.DataParallel(model)

    optimizer = torch.optim.Adam(
        params=model.parameters(),
        lr=config.LEARNING_RATE
    )
    # Training loop
    print('\n======== START TRAINING: {} ========\n'.format(
        datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S")))
    start_time = time.time()

    best_loss = np.Inf
    for epoch in range(50, 50+config.TRAIN_EPOCHS):
        print(
            f"========================= START EPOCHS {epoch} ==================")
        t_loss = train(epoch, tokenizer, model, device,
                       training_loader, optimizer)
        print(f"Epoch: {epoch}, Loss:  {t_loss}")
        if t_loss < best_loss:
            print(f"---> Best loss training model is {t_loss}\n")
            best_loss = t_loss
            # Save model
            #torch.save(model.state_dict(), config.MODEL_PATH)

            # torch.save(model.module.state_dict(), config.MODEL_PATH)
            torch.save(model.module.state_dict(),
                       f"epoch_{epoch}_{config.MODEL_PATH}")
            # INFERENCE
            # Validation loop and saving the resulting file with predictions and acutals in a dataframe.
            print(
                "Run inference for 300 data with best model, and save result as dataframe")
            predictions, actuals = validate(
                tokenizer, model, device, test_loader)
            test_dataset["generated_description"] = predictions
            # test_dataset["actual_description"] = actuals
            # test_dataset["keywords"] = [
            #     ' '.join(keywords.split()[1:]) for keywords in test_dataset.keywords.values]
            sort_cols = ["company_id", "company_name", "keywords",
                         "description", "generated_description"]
            test_dataset = test_dataset[sort_cols]
            test_dataset.to_csv(
                f'./output_pred/epoch_{epoch}_'+config.OUTPUT_TEST_PATH, index=False)
            print("Output Files generated for review")

        end_time = time.time()
        print('=============== END TRAINING EPOCHS {}: {} ==============='.format(
            epoch, datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S")))
        print("Time traning model is {}".format(
            convert_seconds(end_time-start_time)))
        print("Best loss is {}".format(best_loss))
        print("====================================================================\n\n\n")


if __name__ == "__main__":
    main()
