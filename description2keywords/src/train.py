import pandas as pd
import torch
import torch.nn as nn
from tqdm import tqdm
from rich.progress import track
from torch import optim
import random
import os
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
import datetime
import time
import ast

from utils import config
from datasets import DES2KEYDataset
from models import Model


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


def seed_everything(seed: int):
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True


def train(model, train_loader, criterion, optimizer):
    model.train()
    running_loss, total, correct = 0, 0, 0
    bar = tqdm(train_loader, total=len(train_loader))
    for sample in bar:
        input_ids, labels = sample[0], sample[1]
        input_ids, labels = input_ids.to(device), labels.to(device)  # on GPU
        # zero the parameter gradients
        optimizer.zero_grad()
        # forward + backward + optimize
        outputs = model(input_ids)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        # print statistics
        running_loss += loss.item()
        bar.set_postfix(loss=loss.item())

    loss_score = running_loss/len(train_loader)
    return loss_score


def eval(model, val_loader, criterion):
    model.eval()
    batch_loss, total, correct = 0, 0, 0
    bar = tqdm(val_loader, total=len(val_loader))
    with torch.no_grad():
        for sample in bar:
            input_ids, labels = sample[0], sample[1]
            input_ids, labels = input_ids.to(
                device), labels.to(device)  # on GPU
            outputs = model(input_ids)
            loss = criterion(outputs, labels)
            batch_loss += loss.item()
            bar.set_postfix(loss=loss.item())

    loss_score = batch_loss/len(val_loader)
    return loss_score


def main():
    print('\n======== START TRAINING: {} ========\n'.format(
        datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S")))
    start_time = time.time()

    seed_everything(42)

    if config["run_first_time"]:
        print("Preprocessing data first time training...")
        df = pd.read_csv(config["path_df"]).sample(
            frac=config["sample_frac"])

        from sklearn.preprocessing import MultiLabelBinarizer
        mlb = MultiLabelBinarizer()
        keywords = []
        for i, r in df.iterrows():
            keywords.append(set(ast.literal_eval(r["keywords"])))
        mlb.fit(keywords)
        joblib.dump(mlb, config["encoder_label"])
        test_df = df[-300:]
        df = df[:-300]
        train_df, val_df = train_test_split(
            df, test_size=config["train_val_split_rate"], random_state=42)
        train_df = train_df.reset_index(drop=True)
        val_df = val_df.reset_index(drop=True)
        test_df = test_df.reset_index(drop=True)

        train_df.to_csv(config["train_df_path"], index=False)
        val_df.to_csv(config["val_df_path"], index=False)
        test_df.to_csv(config["test_df_path"], index=False)
    else:
        train_df = pd.read_csv(config["train_df_path"])
        val_df = pd.read_csv(config["val_df_path"])
        test_df = pd.read_csv(config["test_df_path"])
        mlb = joblib.load(config["encoder_label"])

    print("Train:", train_df.shape)
    print("Valid:", val_df.shape)
    print("Test:", test_df.shape)
    print(f"len mlb label: {len(mlb.classes_)}")

    train_dataset = DES2KEYDataset(df=train_df, mlb=mlb)
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config["batch_size"],
        shuffle=True
    )

    val_dataset = DES2KEYDataset(df=val_df, mlb=mlb)
    val_loader = torch.utils.data.DataLoader(
        val_dataset,
        batch_size=config["batch_size"]
    )

    model = Model(num_classes=len(mlb.classes_))
    if os.path.exists(config["model_path"]):
        model.load_state_dict(torch.load(config["model_path"]))
    model.to(device)
    # criterion = nn.CrossEntropyLoss()
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=config["learning_rate"])

    best_loss = np.Inf

    for epoch in range(1, config["n_epochs"]+1):
        print("\nEpoch = [{}]/[{}]\n".format(epoch, config["n_epochs"]))
        t_loss = train(model, train_loader, criterion, optimizer)
        print(f"\ntrain loss: {t_loss:.4f}")

        v_loss = eval(model, val_loader, criterion)
        print(f"validation loss: {v_loss:.4f}")

        # Saving the best weight
        if v_loss < best_loss:
            best_loss = v_loss
            torch.save(model.state_dict(), config["model_path"])
            print("Detected network improvement, saving current model")
            print("Best loss is {}".format(best_loss))
        from inference import inference_test_data
        inference_test_data(model, mlb)
    end_time = time.time()
    print('\n======== END TRAINING: {} ========\n'.format(
        datetime.datetime.now().strftime("%d-%m-%y_%H:%M:%S")))

    print("Time traning model is {} (minutes). Best loss is {}".format(
        round((end_time-start_time)/60, 2), best_loss))


if __name__ == "__main__":
    main()
