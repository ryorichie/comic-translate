import os
import cv2
import numpy as np
import torch


from ..utils.inpainting import (
    norm_img,
    get_cache_path_by_url,
    load_jit_model,
    download_model,
)
from .base import InpaintModel
from .schema import Config


# LAMA_MODEL_URL = os.environ.get(
#     "LAMA_MODEL_URL",
#     "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt",
# )
# LAMA_MODEL_MD5 = os.environ.get("LAMA_MODEL_MD5", "e3aa4aaa15225a33ec84f9f4bc47e500")

LAMA_MODEL_URL = os.environ.get(
    "LAMA_MODEL_URL",
    "https://github.com/Sanster/models/releases/download/AnimeMangaInpainting/anime-manga-big-lama.pt",
)
LAMA_MODEL_MD5 = os.environ.get("LAMA_MODEL_MD5", "29f284f36a0a510bcacf39ecf4c4d54f")

current_file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_file_dir, "..", ".."))
model_path = os.path.join(project_root, "models/inpainting/lama_large_512px.ckpt")


class LaMa(InpaintModel):
    name = "lama"
    pad_mod = 8

    def init_model(self, device, **kwargs):
        self.model = load_jit_model(LAMA_MODEL_URL, device, LAMA_MODEL_MD5).eval()

    @staticmethod
    def download():
        download_model(LAMA_MODEL_URL, LAMA_MODEL_MD5)

    @staticmethod
    def is_downloaded() -> bool:
        return os.path.exists(get_cache_path_by_url(LAMA_MODEL_URL))

    def forward(self, image, mask, config: Config):
        """Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W]
        return: BGR IMAGE
        """
        image = norm_img(image)
        mask = norm_img(mask)

        mask = (mask > 0) * 1
        image = torch.from_numpy(image).unsqueeze(0).to(self.device)
        mask = torch.from_numpy(mask).unsqueeze(0).to(self.device)

        inpainted_image = self.model(image, mask)

        cur_res = inpainted_image[0].permute(1, 2, 0).detach().cpu().numpy()
        cur_res = np.clip(cur_res * 255, 0, 255).astype("uint8")
        cur_res = cv2.cvtColor(cur_res, cv2.COLOR_RGB2BGR)
        return cur_res
