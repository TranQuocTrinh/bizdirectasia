from transformers import BertModel, BertConfig
import torch
import torch.nn as nn
import torch.nn.functional as F

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# Model
class Model(nn.Module):

    def __init__(self, num_classes=1000):
        super(Model, self).__init__()
        confbert = BertConfig()
        self.bert = BertModel(confbert)
        self.classifier = nn.Linear(768, num_classes)
        self.sigmoid = nn.Sigmoid()

    def forward(self, input_ids):
        bert_output = self.bert(
            input_ids, attention_mask=input_ids != 0)
        bert_output = bert_output.last_hidden_state[:, 0, :]
        logit = self.sigmoid(self.classifier(bert_output))
        return logit