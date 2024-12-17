from typing import Dict, List, Optional
import logging
import torch
import numpy as np
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from transformers import Emu2Processor, Emu2ForVisionText2Text
from transformers import IdeficsProcessor, IdeficsForVisionText2Text
from transformers import Fuyu8BConfig, Fuyu8BForCausalLM
from nomic import embed
from ...config import settings
from ...database.cache import RedisCache

logger = logging.getLogger(__name__)

class VisionManager:
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.models = {
            "clip": {
                "model": self._load_clip_model(),
                "processor": CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            },
            "emu2": {
                "model": self._load_emu2_model(),
                "processor": Emu2Processor.from_pretrained("adept/emu2-base")
            },
            "idefics": {
                "model": self._load_idefics_model(),
                "processor": IdeficsProcessor.from_pretrained("HuggingFaceM4/idefics-9b")
            },
            "fuyu": {
                "model": self._load_fuyu_model(),
                "processor": None  # Fuyu uses direct image input
            },
            "nomic": {
                "model": None,  # Nomic uses API calls
                "processor": None
            }
        }
        self.default_model = "clip"
        self.fallback_order = ["clip", "emu2", "idefics", "fuyu", "nomic"]
        self.retry_attempts = 2
        self.confidence_threshold = 0.75

    async def analyze_image(
        self,
        image_path: str,
        model_key: str = None,
        context: Dict = None,
        max_retries: int = None
    ) -> Dict:
        """Analyze image with fallback and retry logic"""
        retries = max_retries or self.retry_attempts
        errors = []
        
        # Try cache first
        cache_key = f"vision_analysis:{hash(image_path)}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            return cached_result

        # Try primary model
        model_key = model_key or self.default_model
        try:
            result = await self._process_image(model_key, image_path, context)
            if result["confidence"] >= self.confidence_threshold:
                await self.cache.set(cache_key, result, expire=3600)  # Cache for 1 hour
                return result
        except Exception as e:
            errors.append(f"{model_key}: {str(e)}")
            logger.warning(f"Primary model {model_key} failed: {str(e)}")

        # Try fallback models
        for fallback_model in self.fallback_order:
            if fallback_model == model_key:
                continue
                
            try:
                result = await self._process_image(fallback_model, image_path, context)
                if result["confidence"] >= self.confidence_threshold:
                    await self.cache.set(cache_key, result, expire=3600)
                    return result
            except Exception as e:
                errors.append(f"{fallback_model}: {str(e)}")
                logger.warning(f"Fallback model {fallback_model} failed: {str(e)}")

        raise RuntimeError(f"All models failed: {'; '.join(errors)}")

    def _load_clip_model(self) -> CLIPModel:
        """Load CLIP model"""
        try:
            return CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        except Exception as e:
            logger.error(f"Error loading CLIP model: {str(e)}")
            raise

    def _load_emu2_model(self) -> Emu2ForVisionText2Text:
        """Load Emu2 model"""
        try:
            return Emu2ForVisionText2Text.from_pretrained("adept/emu2-base")
        except Exception as e:
            logger.error(f"Error loading Emu2 model: {str(e)}")
            raise

    def _load_idefics_model(self) -> IdeficsForVisionText2Text:
        """Load IDEFICS model"""
        try:
            return IdeficsForVisionText2Text.from_pretrained("HuggingFaceM4/idefics-9b")
        except Exception as e:
            logger.error(f"Error loading IDEFICS model: {str(e)}")
            raise

    def _load_fuyu_model(self) -> Fuyu8BForCausalLM:
        """Load Fuyu-8B model"""
        try:
            config = Fuyu8BConfig()
            return Fuyu8BForCausalLM(config)
        except Exception as e:
            logger.error(f"Error loading Fuyu model: {str(e)}")
            raise

    async def _process_image(
        self,
        model_key: str,
        image_path: str,
        context: Dict = None
    ) -> Dict:
        """Process image with specific model"""
        try:
            image = Image.open(image_path).convert('RGB')
            
            if model_key == "clip":
                return await self._process_with_clip(image, context)
            elif model_key == "emu2":
                return await self._process_with_emu2(image, context)
            elif model_key == "idefics":
                return await self._process_with_idefics(image, context)
            elif model_key == "fuyu":
                return await self._process_with_fuyu(image, context)
            elif model_key == "nomic":
                return await self._process_with_nomic(image, context)
            else:
                raise ValueError(f"Unknown model: {model_key}")
                
        except Exception as e:
            logger.error(f"Error processing with {model_key}: {str(e)}")
            raise

    async def _process_with_clip(self, image: Image, context: Dict = None) -> Dict:
        """Process image with CLIP"""
        try:
            model_config = self.models["clip"]
            inputs = model_config["processor"](
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            outputs = model_config["model"].get_image_features(**inputs)
            
            # Get similarity scores with food categories
            food_categories = context.get("food_categories", ["meal", "snack", "drink"])
            text_inputs = model_config["processor"](
                text=food_categories,
                return_tensors="pt",
                padding=True
            )
            
            text_outputs = model_config["model"].get_text_features(**text_inputs)
            similarity = torch.nn.functional.cosine_similarity(
                outputs, text_outputs
            )
            
            best_match_idx = similarity.argmax().item()
            confidence = similarity[best_match_idx].item()
            
            return {
                "model": "clip",
                "category": food_categories[best_match_idx],
                "confidence": confidence,
                "embeddings": outputs.detach().numpy().tolist()
            }
            
        except Exception as e:
            logger.error(f"Error processing with CLIP: {str(e)}")
            raise

    async def _process_with_emu2(self, image: Image, context: Dict = None) -> Dict:
        """Process image with Emu2"""
        try:
            model_config = self.models["emu2"]
            prompt = context.get("prompt", "Describe the food in this image.")
            
            inputs = model_config["processor"](
                images=image,
                text=prompt,
                return_tensors="pt"
            )
            
            outputs = model_config["model"].generate(**inputs)
            description = model_config["processor"].decode(outputs[0])
            
            return {
                "model": "emu2",
                "description": description,
                "confidence": self._calculate_confidence(outputs),
                "raw_outputs": outputs.detach().numpy().tolist()
            }
            
        except Exception as e:
            logger.error(f"Error processing with Emu2: {str(e)}")
            raise

    async def _process_with_idefics(self, image: Image, context: Dict = None) -> Dict:
        """Process image with IDEFICS"""
        try:
            model_config = self.models["idefics"]
            prompt = context.get("prompt", "What food items are in this image?")
            
            inputs = model_config["processor"](
                images=image,
                text=prompt,
                return_tensors="pt"
            )
            
            outputs = model_config["model"].generate(**inputs)
            description = model_config["processor"].decode(outputs[0])
            
            return {
                "model": "idefics",
                "description": description,
                "confidence": self._calculate_confidence(outputs),
                "raw_outputs": outputs.detach().numpy().tolist()
            }
            
        except Exception as e:
            logger.error(f"Error processing with IDEFICS: {str(e)}")
            raise

    async def _process_with_fuyu(self, image: Image, context: Dict = None) -> Dict:
        """Process image with Fuyu-8B"""
        try:
            model_config = self.models["fuyu"]
            image_tensor = self._preprocess_image_for_fuyu(image)
            
            outputs = model_config["model"].generate(
                pixel_values=image_tensor,
                max_length=50
            )
            
            description = outputs[0].detach().numpy().tolist()
            
            return {
                "model": "fuyu",
                "description": description,
                "confidence": self._calculate_confidence(outputs),
                "raw_outputs": outputs.detach().numpy().tolist()
            }
            
        except Exception as e:
            logger.error(f"Error processing with Fuyu: {str(e)}")
            raise

    async def _process_with_nomic(self, image: Image, context: Dict = None) -> Dict:
        """Process image with Nomic Embed Vision"""
        try:
            # Convert image to bytes
            image_bytes = self._image_to_bytes(image)
            
            # Get embeddings from Nomic API
            embeddings = embed.embed(
                images=[image_bytes],
                model="nomic-embed-vision",
                task_type="visual_classification"
            )
            
            return {
                "model": "nomic",
                "embeddings": embeddings.tolist(),
                "confidence": self._calculate_nomic_confidence(embeddings),
                "raw_outputs": embeddings.tolist()
            }
            
        except Exception as e:
            logger.error(f"Error processing with Nomic: {str(e)}")
            raise

    def _calculate_confidence(self, outputs) -> float:
        """Calculate confidence score from model outputs"""
        try:
            # Convert outputs to probabilities
            probs = torch.nn.functional.softmax(outputs, dim=-1)
            
            # Get maximum probability as confidence
            confidence = probs.max().item()
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0

    def _calculate_nomic_confidence(self, embeddings) -> float:
        """Calculate confidence score for Nomic embeddings"""
        try:
            # Calculate L2 norm of embeddings
            norm = np.linalg.norm(embeddings)
            
            # Normalize to [0, 1] range
            confidence = min(norm / 10.0, 1.0)
            
            return float(confidence)
            
        except Exception as e:
            logger.error(f"Error calculating Nomic confidence: {str(e)}")
            return 0.0

    def _preprocess_image_for_fuyu(self, image: Image) -> torch.Tensor:
        """Preprocess image for Fuyu model"""
        try:
            # Resize image
            image = image.resize((224, 224))
            
            # Convert to tensor
            image_array = np.array(image)
            image_tensor = torch.from_numpy(image_array).float()
            
            # Normalize
            image_tensor = image_tensor / 255.0
            image_tensor = image_tensor.permute(2, 0, 1)
            image_tensor = image_tensor.unsqueeze(0)
            
            return image_tensor
            
        except Exception as e:
            logger.error(f"Error preprocessing image for Fuyu: {str(e)}")
            raise

    def _image_to_bytes(self, image: Image) -> bytes:
        """Convert PIL Image to bytes"""
        try:
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting image to bytes: {str(e)}")
            raise 