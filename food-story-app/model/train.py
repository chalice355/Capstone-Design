"""
EfficientNet-B0 파인튜닝 스크립트
AI Hub 한국 음식 이미지 데이터셋 기준

데이터 폴더 구조:
  dataset/
    train/
      비빔밥/  img1.jpg  img2.jpg ...
      된장찌개/ ...
    val/
      비빔밥/  ...
      된장찌개/ ...

실행 방법:
  python model/train.py
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
import json
import os

DATA_DIR   = "dataset"
SAVE_DIR   = os.path.dirname(__file__)
SAVE_PATH  = os.path.join(SAVE_DIR, "efficientnet_food.pth")
CLASS_PATH = os.path.join(SAVE_DIR, "class_names.json")

EPOCHS     = 10
BATCH_SIZE = 32
LR         = 1e-4


def train():
    transform_train = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])
    transform_val = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])

    train_ds = datasets.ImageFolder(os.path.join(DATA_DIR, "train"), transform_train)
    val_ds   = datasets.ImageFolder(os.path.join(DATA_DIR, "val"),   transform_val)
    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=4)
    val_dl   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False, num_workers=4)

    with open(CLASS_PATH, "w", encoding="utf-8") as f:
        json.dump(train_ds.classes, f, ensure_ascii=False)
    print(f"클래스 수: {len(train_ds.classes)}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"학습 장치: {device}")

    model = models.efficientnet_b0(weights="IMAGENET1K_V1")
    for param in model.features.parameters():
        param.requires_grad = False
    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features, len(train_ds.classes)
    )
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    best_acc = 0.0
    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_dl:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(inputs), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()

        model.eval()
        correct = total = 0
        with torch.no_grad():
            for inputs, labels in val_dl:
                inputs, labels = inputs.to(device), labels.to(device)
                _, preds = model(inputs).max(1)
                correct += (preds == labels).sum().item()
                total   += labels.size(0)

        acc = correct / total
        print(f"Epoch {epoch+1}/{EPOCHS}  loss: {running_loss/len(train_dl):.4f}  val_acc: {acc:.4f}")

        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"  → 모델 저장 (best acc: {best_acc:.4f})")

        scheduler.step()

    print(f"\n학습 완료. 최고 정확도: {best_acc:.4f}")


if __name__ == "__main__":
    train()
