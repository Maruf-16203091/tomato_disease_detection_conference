from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

from model import load_model
from utils import (
    predict_with_rejection,
    generate_reasoning_only,   # ✅ updated
    disease_info,              # ✅ updated
    val_transforms,
    class_names,
    device
)

# ===============================
# FASTAPI APP
# ===============================
app = FastAPI(title="Tomato Disease API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# LOAD CNN MODEL
# ===============================
model_path = "tomato_disease_detection_vlm.pth"
model = load_model(
    model_path=model_path,
    num_classes=len(class_names),
    device=device
)

# ===============================
# ROOT
# ===============================
@app.get("/")
def root():
    return {"status": "API running"}

# ===============================
# PREDICTION ENDPOINT
# ===============================
@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid image file"
            }
        )

    # Image → Tensor
    image_tensor = val_transforms(img)

    # CNN prediction with rejection
    pred_class, confidence = predict_with_rejection(model, image_tensor)

    if pred_class is None:
        return {
            "status": "rejected",
            "message": "Low confidence or unclear tomato disease image"
        }

    # ✅ Hardcoded advice (safe)
    advice = disease_info.get(
        pred_class,
        "Follow standard tomato disease management practices."
    )

    # ✅ FLAN-T5 explanation only
    reasoning = generate_reasoning_only(pred_class)

    return {
        "status": "success",
        "disease": pred_class,
        "confidence": round(confidence * 100, 2),
        "recommended_action": advice,
        "explanation": reasoning
    }
