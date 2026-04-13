import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import json
import os

BASE_DIR        = os.path.dirname(__file__)
MODEL_PATH      = os.path.join(BASE_DIR, "efficientnet_food.pth")
CLASS_PATH      = os.path.join(BASE_DIR, "class_names.json")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225]),
])

_model       = None
_class_names = None


def _load_model():
    global _model, _class_names
    if _model is not None:
        return

    with open(CLASS_PATH, "r", encoding="utf-8") as f:
        _class_names = json.load(f)

    _model = models.efficientnet_b0(weights=None)
    _model.classifier[1] = torch.nn.Linear(
        _model.classifier[1].in_features, len(_class_names)
    )
    _model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    _model.eval()


def predict(image: Image.Image) -> dict:
    """
    PIL 이미지를 받아 음식명과 신뢰도를 반환합니다.
    모델 파일이 없을 경우 더미 결과를 반환합니다.
    """
    if not os.path.exists(MODEL_PATH):
        return {"food_name": "비빔밥", "confidence": 0.91, "is_dummy": True}

    _load_model()
    tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = _model(tensor)
        probs   = torch.softmax(outputs, dim=1)
        conf, idx = probs.max(dim=1)

    return {
        "food_name":  _class_names[idx.item()],
        "confidence": round(conf.item(), 4),
        "is_dummy":   False,
    }
