import os
import json
from PIL import Image

BASE_DIR   = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "efficientnet_food.pth")
CLASS_PATH = os.path.join(BASE_DIR, "class_names.json")

_model       = None
_class_names = None


def _load_model():
    global _model, _class_names
    if _model is not None:
        return
    try:
        import torch
        import torchvision.transforms as transforms
        from torchvision import models

        with open(CLASS_PATH, "r", encoding="utf-8") as f:
            _class_names = json.load(f)

        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = torch.nn.Linear(
            model.classifier[1].in_features, len(_class_names)
        )
        model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
        model.eval()
        _model = model
    except Exception as e:
        print(f"모델 로드 실패: {e}")


def predict(image: Image.Image) -> dict:
    if not os.path.exists(MODEL_PATH):
        return {"food_name": "비빔밥", "confidence": 0.91, "is_dummy": True}

    _load_model()

    if _model is None:
        return {"food_name": "비빔밥", "confidence": 0.91, "is_dummy": True}

    try:
        import torch
        import torchvision.transforms as transforms

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225]),
        ])
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
    except Exception as e:
        print(f"추론 실패: {e}")
        return {"food_name": "비빔밥", "confidence": 0.91, "is_dummy": True}
