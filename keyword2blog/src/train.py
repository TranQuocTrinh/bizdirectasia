from dataset import CustomDataset
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
from torch.utils.data import DataLoader

# Importing the T5 modules from huggingface/transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def convert_seconds(seconds):
    sec = timedelta(seconds=seconds)
    d = datetime.datetime(1, 1, 1) + sec
    str_format = "%d days, %d hours, %d minutes, %d seconds" % (
        d.day-1, d.hour, d.minute, d.second)
    return str_format


def train(tokenizer, model, device, loader, optimizer):
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
        TRAIN_EPOCHS = 100
        LEARNING_RATE = 5e-4
        SEED = 42
        MAX_LEN = 20
        SUMMARY_LEN = 350
        OUTPUT_DIR = "./output/"
        # "google/roberta2roberta_L-24_discofuse"  # "t5-base"
        MODEL_BASE = "t5-base"  # "google/pegasus-xsum"
        MODEL_PATH = f"{OUTPUT_DIR}model_key2blog.pt"
        PATH_DF = "/home/ubuntu/tqtrinh/keyword2blog/wiki_data/version2/data_training_key2blog.csv"
        OTHER_KEYWORD = "/home/ubuntu/tqtrinh/keyword2blog/wiki_data/version2/keyword.csv"
        FRAC_SAMPLE = 1
        NUM_TEST_CASE = 300
        OUTPUT_TEST_PATH = f"{OUTPUT_DIR}pred_samples.csv"

    if not os.path.exists(config.OUTPUT_DIR):
        os.mkdir(config.OUTPUT_DIR)
    # Set random seeds and deterministic pytorch for reproducibility
    torch.manual_seed(config.SEED)  # pytorch random seed
    np.random.seed(config.SEED)  # numpy random seed
    torch.backends.cudnn.deterministic = True

    # tokenzier for encoding the text
    if config.MODEL_BASE == "t5-base":
        tokenizer = T5Tokenizer.from_pretrained(config.MODEL_BASE)
    else:
        tokenizer = PegasusTokenizer.from_pretrained(config.MODEL_BASE)

    df = pd.read_csv(config.PATH_DF, encoding="utf-8")
    df = df.sample(frac=config.FRAC_SAMPLE).reset_index(drop=True)
    set_keyword = set(df.keyword)

    df["wiki"] = "wiki: " + df.wiki
    df.keyword = "keyword: " + df.keyword
    # df = df[["wiki", "keyword"]]

    print(df.head())

    test_dataset = df.sample(n=config.NUM_TEST_CASE, random_state=config.SEED)
    train_dataset = df  # .drop(test_dataset.index).reset_index(drop=True)

    test2_lst_keyword = [k.strip() for k in pd.read_csv(
        config.OTHER_KEYWORD).keyword.values if k.strip() not in set_keyword]
    print(f"Number of keyword not in df: {len(test2_lst_keyword)}")
    test2_df = pd.DataFrame({
        "keyword": test2_lst_keyword,
        "wiki": ["wiki: "]*len(test2_lst_keyword)
    })
    test2_df = test2_df.sample(
        n=config.NUM_TEST_CASE, random_state=config.SEED)
    test_dataset = pd.concat([test_dataset, test2_df]).reset_index(drop=True)

    print("FULL Dataset: {} \t Columns: {}".format(df.shape, df.columns))
    print("TRAIN Dataset: {} \t Columns: {}".format(
        train_dataset.shape, train_dataset.columns))
    print("TEST Dataset: {} \t Columns: {}".format(
        test_dataset.shape, test_dataset.columns))

    from utils import clean_text
    test_dataset["wiki_clean"] = test_dataset.wiki.apply(clean_text)

    test_dataset.to_csv("test.csv", index=False)

    # Creating the Training and Testing dataset for further creation of Dataloader
    training_set = CustomDataset(
        dataframe=train_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN,
        phase="train"
    )
    test_set = CustomDataset(
        dataframe=test_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN,
        phase="train"
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
    if os.path.exists(config.MODEL_PATH):
        print("============ LOAD MODEL AND CONTINUE TO TRAINING ============")
        model.load_state_dict(torch.load(
            config.MODEL_PATH, map_location=device))

    model = nn.DataParallel(model)
    model = model.to(device)

    optimizer = torch.optim.Adam(
        params=model.parameters(),
        lr=config.LEARNING_RATE
    )
    # Training loop
    print('\n======== START TRAINING: {} ========\n'.format(
        datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S")))
    start_time = time.time()

    best_loss = np.Inf
    for epoch in range(1, 1+config.TRAIN_EPOCHS):
        print(
            f"========================= START EPOCHS {epoch} ==================")
        t_loss = train(tokenizer, model, device,
                       training_loader, optimizer)
        print(f"Epoch: {epoch}, Loss:  {t_loss}")
        if t_loss < best_loss:
            print(f"---> Best loss training model is {t_loss}\n")
            best_loss = t_loss
            # Save model
            # torch.save(model.state_dict(), config.MODEL_PATH)

            # torch.save(model.module.state_dict(), config.MODEL_PATH)
            torch.save(model.module.state_dict(), config.MODEL_PATH)
            # INFERENCE
            # Validation loop and saving the resulting file with predictions and acutals in a dataframe.
            print(
                "Run inference for 600 data with best model, and save result as dataframe")
            predictions, actuals = validate(
                tokenizer, model, device, test_loader)
            test_dataset["generated_wiki"] = predictions
            # test_dataset["actual_wiki"] = actuals
            # test_dataset["keyword"] = [
            #     ' '.join(keyword.split()[1:]) for keyword in test_dataset.keyword.values]
            sort_cols = ["keyword", "wiki", "wiki_clean", "generated_wiki"]
            test_dataset = test_dataset[sort_cols]
            test_dataset.to_csv(config.OUTPUT_TEST_PATH, index=False)
            print("Output Files generated for review")
            if epoch % 50 == 0:
                torch.save(model.module.state_dict(),
                           f"epoch_{epoch}_model_key2blog.pt")
                test_dataset.to_csv(
                    f"epoch_{epoch}_pred_samples.csv", index=False)

        end_time = time.time()
        print('=============== END TRAINING EPOCHS {}: {} ==============='.format(
            epoch, datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S")))
        print("Time traning model is {}".format(
            convert_seconds(end_time-start_time)))
        print("Best loss is {}".format(best_loss))
        print("====================================================================\n\n\n")


if __name__ == "__main__":
    main()
