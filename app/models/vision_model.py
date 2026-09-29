import re
import threading

import torch
from PIL import Image
from transformers import (
    AutoModelForImageTextToText,
    AutoProcessor,
    MarianMTModel,
    MarianTokenizer,
)

from app import config


class _Translator:

    def __init__(self, name: str, device: str):
        self.device = device
        self.tokenizer = MarianTokenizer.from_pretrained(name)
        self.model = MarianMTModel.from_pretrained(name).to(device).eval()

    @torch.inference_mode()
    def __call__(self, texts: list[str]) -> list[str]:
        batch = self.tokenizer(
            texts, return_tensors="pt", padding=True, truncation=True, max_length=256
        ).to(self.device)
        output = self.model.generate(**batch, max_new_tokens=256)
        return self.tokenizer.batch_decode(output, skip_special_tokens=True)


class VisionModel:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            self.dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        else:
            self.dtype = torch.float32

        self._lock = threading.Lock()

        self.processor = AutoProcessor.from_pretrained(
            config.MODEL_ID, do_image_splitting=False
        )
        self.model = (
            AutoModelForImageTextToText.from_pretrained(
                config.MODEL_ID, torch_dtype=self.dtype
            )
            .to(self.device)
            .eval()
        )

        self.to_en = _Translator("Helsinki-NLP/opus-mt-es-en", self.device)
        self.to_es = _Translator("Helsinki-NLP/opus-mt-en-es", self.device)

    def describe(self, image: Image.Image) -> str:
        return self._to_es(self._run(image, config.PROMPT_DESCRIBE))

    def ask(self, image: Image.Image, question: str) -> str:
        question_en = self.to_en([question])[0]
        return self._to_es(self._run(image, question_en))

    def info(self) -> dict:
        gpu = torch.cuda.get_device_name(0) if self.device == "cuda" else "CPU"
        return {"model": config.MODEL_ID.split("/")[-1], "device": gpu}

    def _to_es(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)  
        return " ".join(self.to_es(sentences))

    @torch.inference_mode()
    def _run(self, image: Image.Image, prompt: str) -> str:
        image = image.convert("RGB")
        image.thumbnail((config.MAX_IMAGE_SIDE, config.MAX_IMAGE_SIDE))

        messages = [
            {"role": "user", "content": [{"type": "image"}, {"type": "text", "text": prompt}]}
        ]
        text = self.processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = self.processor(text=text, images=[image], return_tensors="pt")
        inputs = inputs.to(self.device, dtype=self.dtype)

        with self._lock:
            output = self.model.generate(
                **inputs, max_new_tokens=config.MAX_NEW_TOKENS, do_sample=False
            )

        generated = output[:, inputs["input_ids"].shape[1]:]
        return self.processor.batch_decode(generated, skip_special_tokens=True)[0].strip()