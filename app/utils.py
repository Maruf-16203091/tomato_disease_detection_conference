import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ===============================
# DEVICE
# ===============================
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

# ===============================
# CLASS NAMES
# ===============================
class_names = [
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

# ===============================
# DISEASE HINTS (ONLY CONTEXT)
# ===============================
DISEASE_HINTS = {
    "Tomato___Bacterial_spot": "small dark water-soaked bacterial spots",
    "Tomato___Early_blight": "concentric brown rings and yellowing leaves",
    "Tomato___Late_blight": "rapidly spreading dark lesions under humid conditions",
    "Tomato___Leaf_Mold": "yellow patches with mold growth on the underside of leaves",
    "Tomato___Septoria_leaf_spot": "small circular spots with gray centers and dark margins",
    "Tomato___Spider_mites Two-spotted_spider_mite": "stippling damage and webbing",
    "Tomato___Target_Spot": "brown target-like lesions",
    "Tomato___Tomato_mosaic_virus": "mosaic patterns and leaf distortion",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "leaf curling and yellowing"
}

# ===============================
# HARDCODED DISEASE ADVICE
# ===============================
disease_info = {
    "Tomato___Bacterial_spot": "Apply copper fungicide and remove infected leaves.",
    "Tomato___Early_blight": "Reduce irrigation and apply chlorothalonil fungicide.",
    "Tomato___Late_blight": "Apply systemic fungicide immediately.",
    "Tomato___Leaf_Mold": "Improve ventilation and apply fungicide.",
    "Tomato___Septoria_leaf_spot": "Remove infected leaves and apply mancozeb.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Increase humidity and use miticide.",
    "Tomato___Target_Spot": "Avoid leaf wetness and apply fungicide.",
    "Tomato___Tomato_mosaic_virus": "Remove infected plants and disinfect tools.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Control whiteflies and remove infected plants.",
    "Tomato___healthy": "Plant is healthy. Continue standard care."
}


# ===============================
# THRESHOLDS
# ===============================
TEMPERATURE = 2.0
CONFIDENCE_THRESHOLD = 0.35
ENTROPY_THRESHOLD = 2.0

# ===============================
# IMAGE TRANSFORMS
# ===============================
val_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# ===============================
# LOAD FLAN-T5-LARGE
# ===============================
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-large")
t5_model = AutoModelForSeq2SeqLM.from_pretrained(
    "google/flan-t5-large"
).to(device)
t5_model.eval()

print("✅ FLAN-T5-LARGE loaded")

# ===============================
# PREDICTION WITH REJECTION
# ===============================
def predict_with_rejection(model, image_tensor):
    image_tensor = image_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(image_tensor)
        probs = F.softmax(logits / TEMPERATURE, dim=1)

        confidence, idx = probs.max(dim=1)
        entropy = -(probs * torch.log(probs + 1e-8)).sum(dim=1)

    print(f"[DEBUG] confidence={confidence.item():.3f}, entropy={entropy.item():.3f}")

    if confidence.item() < CONFIDENCE_THRESHOLD or entropy.item() > ENTROPY_THRESHOLD:
        return None, confidence.item()

    return class_names[idx.item()], confidence.item()

# ===============================
# FLAN-T5 REASONING ONLY (CONTROLLED)
# ===============================
def generate_reasoning_only(disease_name):
    if disease_name == "Tomato___healthy":
        return (
            "The tomato plant shows normal leaf color and structure with no visible "
            "signs of disease or pest damage. Proper irrigation, nutrition, and "
            "regular monitoring help maintain healthy growth and yield."
        )

    hint = DISEASE_HINTS.get(disease_name, "tomato leaf disease symptoms")

    prompt = f"""
You are a tomato plant disease expert.

Predicted disease: {disease_name}
Observed symptoms: {hint}

Write a concise paragraph (3–4 sentences) explaining:
- The biological cause of the disease
- How it affects tomato plant growth and yield
- Why timely management is important

Do not repeat the symptoms verbatim.
Do not mention other diseases.
Write clearly for farmers and agricultural students.
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    outputs = t5_model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.25,
        top_p=0.9,
        do_sample=True,
        repetition_penalty=1.2,
        no_repeat_ngram_size=3
    )

    reasoning = tokenizer.decode(outputs[0], skip_special_tokens=True)
    reasoning = " ".join(reasoning.split())

    return reasoning
