# Importing stock libraries
from numpy.core.fromnumeric import sort
from datasets import CustomDataset
from tqdm import tqdm
import numpy as np
import ast
import os
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler

# Importing the T5 modules from huggingface/transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


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

            generated_ids = model.generate(
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
        TRAIN_BATCH_SIZE = 10
        VALID_BATCH_SIZE = 10
        TRAIN_EPOCHS = 20
        LEARNING_RATE = 1e-4
        SEED = 42
        MAX_LEN = 128
        SUMMARY_LEN = 320
        MODEL_PATH = "model_keywords2description_t5.pt"
        PATH_DF = "/home/ubuntu/tqtrinh/description2keywords/data/japan/baseconnect_trans.csv"
        FRAC_SAMPLE = 1

    # Set random seeds and deterministic pytorch for reproducibility
    torch.manual_seed(config.SEED)  # pytorch random seed
    np.random.seed(config.SEED)  # numpy random seed
    torch.backends.cudnn.deterministic = True

    # tokenzier for encoding the text
    tokenizer = T5Tokenizer.from_pretrained("t5-base")

    # Importing and Pre-Processing the domain data
    # Selecting the needed columns only.
    # Adding the summarzie text in front of the text. This is to format the dataset similar to how T5 model was trained for summarization task.
    df = pd.read_csv(config.PATH_DF, encoding="utf-8")
    df = df.sample(frac=config.FRAC_SAMPLE).reset_index(drop=True)
    df["keywords"] = [", ".join(ast.literal_eval(keywords))
                      for keywords in df.keywords.values]
    # df = df[["description", "keywords"]]
    df.keywords = "summarize: " + df.keywords
    print(df.head())

    # Creation of Dataset and Dataloader
    # Defining the train size. So 80% of the data will be used for training and the rest will be used for validation.
    # train_size = 0.8  # 1-0.001
    # train_dataset = df.sample(frac=train_size, random_state=config.SEED)
    # val_dataset = df.drop(train_dataset.index).reset_index(drop=True)
    # train_dataset = train_dataset.reset_index(drop=True)

    train_dataset = df[:-300].reset_index(drop=True)
    val_dataset = df[-300:].reset_index(drop=True)

    print("FULL Dataset: {}".format(df.shape))
    print("TRAIN Dataset: {}".format(train_dataset.shape))
    print("TEST Dataset: {}".format(val_dataset.shape))

    # Creating the Training and Validation dataset for further creation of Dataloader
    training_set = CustomDataset(
        dataframe=train_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN
    )
    val_set = CustomDataset(
        dataframe=val_dataset,
        tokenizer=tokenizer,
        source_len=config.MAX_LEN,
        summ_len=config.SUMMARY_LEN
    )

    # Defining the parameters for creation of dataloaders
    # Creation of Dataloaders for testing and validation. This will be used down for training and validation stage for the model.
    training_loader = DataLoader(
        training_set,
        batch_size=config.TRAIN_BATCH_SIZE,
        shuffle=True,
        num_workers=0
    )
    val_loader = DataLoader(
        val_set,
        batch_size=config.VALID_BATCH_SIZE,
        shuffle=False,
        num_workers=0
    )

    # Defining the model. We are using t5-base model and added a Language model layer on top for generation of Summary.
    # Further this model is sent to device (GPU/TPU) for using the hardware.
    model = T5ForConditionalGeneration.from_pretrained("t5-base")
    # Defining the optimizer that will be used to tune the weights of the network in the training session.
    model = model.to(device)
    if os.path.exists(config.MODEL_PATH):
        print("Load model and continue to training...")
        model.load_state_dict(torch.load(
            config.MODEL_PATH, map_location=device))

    optimizer = torch.optim.Adam(
        params=model.parameters(),
        lr=config.LEARNING_RATE
    )
    # Training loop
    print("Initiating Fine-Tuning for the model on our dataset")

    best_loss = np.Inf
    for epoch in range(config.TRAIN_EPOCHS):
        t_loss = train(epoch, tokenizer, model, device,
                       training_loader, optimizer)
        print(f"Epoch: {epoch}, Loss:  {t_loss}")
        if t_loss < best_loss:
            print(f"---> Best loss training model is {t_loss}\n")
            best_loss = t_loss
            # Save model
            torch.save(model.state_dict(), config.MODEL_PATH)

            # INFERENCE
            # Validation loop and saving the resulting file with predictions and acutals in a dataframe.
            print(
                "Run inference for 300 data with best model, and save result as dataframe")
            predictions, actuals = validate(
                tokenizer, model, device, val_loader)
            val_dataset["generated_description"] = predictions
            # val_dataset["actual_description"] = actuals
            sort_cols = ["company_id", "company_name", "keywords",
                         "description", "generated_description"]
            val_dataset = val_dataset[sort_cols]
            val_dataset.to_csv("predictions.csv")
            print("Output Files generated for review")


if __name__ == "__main__":
    main()
