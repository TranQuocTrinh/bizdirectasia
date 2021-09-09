config = dict(
    run_first_time=False,
    batch_size=122,
    n_epochs=50,
    learning_rate=1e-5,  # 1e-6,
    # "albert-base-v2",  # "roberta-base",  # "bert-base-uncased"
    model_base="bert-base-uncased",
    path_df="../data/japan/baseconnect_trans.csv",
    train_df_path="../data/train.csv",
    val_df_path="../data/val.csv",
    test_df_path="../data/test.csv",
    sample_frac=1,
    train_val_split_rate=0.035,
    model_path="./output_models/model_BERT2ML_classification_name-add-des_300k.pt",
    encoder_label="./output_models/mlb_encoder_label_300k.joblib",
)
