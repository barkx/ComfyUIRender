# -*- coding: utf-8 -*-
"""workflow.py - Builds ComfyUI workflow JSON. Injects base64 image, prompt, seed."""

import json
import random

_TEMPLATE = {
    "9": {"inputs": {"filename_prefix": "Flux2-Klein", "images": ["75:65", 0]}, "class_type": "SaveImage", "_meta": {"title": "Save Image"}},
    "132": {"inputs": {"base64_data": "", "image_output": "Preview", "save_prefix": "ComfyUI"}, "class_type": "easy loadImageBase64", "_meta": {"title": "Load Image (Base64)"}},
    "141": {"inputs": {"side_length": 2048, "side": "Height", "upscale_method": "nearest-exact", "crop": "center", "image": ["132", 0]}, "class_type": "DF_Image_scale_to_side", "_meta": {"title": "Image scale to side"}},
    "143": {"inputs": {"width": 2048, "height": 2048, "position": "center", "x_offset": 0, "y_offset": 0, "image": ["141", 0]}, "class_type": "ImageCrop+", "_meta": {"title": "Image Crop"}},
    "75:61": {"inputs": {"sampler_name": "euler"}, "class_type": "KSamplerSelect", "_meta": {"title": "KSamplerSelect"}},
    "75:73": {"inputs": {"noise_seed": 0}, "class_type": "RandomNoise", "_meta": {"title": "RandomNoise"}},
    "75:70": {"inputs": {"unet_name": "flux-2-klein-4b-fp8.safetensors", "weight_dtype": "default"}, "class_type": "UNETLoader", "_meta": {"title": "Load Diffusion Model"}},
    "75:71": {"inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "flux2", "device": "default"}, "class_type": "CLIPLoader", "_meta": {"title": "Load CLIP"}},
    "75:72": {"inputs": {"vae_name": "flux2-vae.safetensors"}, "class_type": "VAELoader", "_meta": {"title": "Load VAE"}},
    "75:74": {"inputs": {"text": "", "clip": ["75:71", 0]}, "class_type": "CLIPTextEncode", "_meta": {"title": "CLIP Text Encode (Positive Prompt)"}},
    "75:82": {"inputs": {"conditioning": ["75:74", 0]}, "class_type": "ConditioningZeroOut", "_meta": {"title": "ConditioningZeroOut"}},
    "75:80": {"inputs": {"upscale_method": "nearest-exact", "megapixels": 1, "resolution_steps": 1, "image": ["143", 0]}, "class_type": "ImageScaleToTotalPixels", "_meta": {"title": "ImageScaleToTotalPixels"}},
    "75:81": {"inputs": {"image": ["75:80", 0]}, "class_type": "GetImageSize", "_meta": {"title": "Get Image Size"}},
    "75:79:78": {"inputs": {"pixels": ["75:80", 0], "vae": ["75:72", 0]}, "class_type": "VAEEncode", "_meta": {"title": "VAE Encode"}},
    "75:62": {"inputs": {"steps": 8, "width": ["75:81", 0], "height": ["75:81", 1]}, "class_type": "Flux2Scheduler", "_meta": {"title": "Flux2Scheduler"}},
    "75:66": {"inputs": {"width": ["75:81", 0], "height": ["75:81", 1], "batch_size": 1}, "class_type": "EmptyFlux2LatentImage", "_meta": {"title": "Empty Flux 2 Latent"}},
    "75:79:76": {"inputs": {"conditioning": ["75:82", 0], "latent": ["75:79:78", 0]}, "class_type": "ReferenceLatent", "_meta": {"title": "ReferenceLatent"}},
    "75:79:77": {"inputs": {"conditioning": ["75:74", 0], "latent": ["75:79:78", 0]}, "class_type": "ReferenceLatent", "_meta": {"title": "ReferenceLatent"}},
    "75:63": {"inputs": {"cfg": 1, "model": ["75:70", 0], "positive": ["75:79:77", 0], "negative": ["75:79:76", 0]}, "class_type": "CFGGuider", "_meta": {"title": "CFGGuider"}},
    "75:64": {"inputs": {"noise": ["75:73", 0], "guider": ["75:63", 0], "sampler": ["75:61", 0], "sigmas": ["75:62", 0], "latent_image": ["75:66", 0]}, "class_type": "SamplerCustomAdvanced", "_meta": {"title": "SamplerCustomAdvanced"}},
    "75:65": {"inputs": {"samples": ["75:64", 0], "vae": ["75:72", 0]}, "class_type": "VAEDecode", "_meta": {"title": "VAE Decode"}}
}


def build(base64_image, prompt, seed=None):
    if seed is None or seed < 0:
        seed = random.randint(0, 2147483647)
    wf = json.loads(json.dumps(_TEMPLATE))
    wf["132"]["inputs"]["base64_data"]  = base64_image
    wf["75:74"]["inputs"]["text"]       = prompt
    wf["75:73"]["inputs"]["noise_seed"] = seed
    return wf
