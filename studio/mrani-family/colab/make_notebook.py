import json, sys
md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s}
code = lambda s: {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s}
cells = [
md("""# 🎬 M'RANI FAMILY: free Wan2.2 animator (Google Colab)
Turns the approved M'Rani Family scene pictures into **moving cartoon shots** with the free, open-source **Wan2.2** model. **0 credits.**

**How to use (once per episode):**
1. Menu **Runtime → Change runtime type → T4 GPU → Save**.
2. Menu **Runtime → Run all**. Allow Google Drive access when asked.
3. Leave the tab open. Each finished shot is saved to `My Drive/MRaniFamily/ep01_clips/`.
4. If Colab disconnects (the free tier does that), just **Run all** again: finished shots are skipped and it continues where it stopped.
5. When all shots are done, tell Claude **"clips are ready"**. Claude downloads them from your Drive and assembles the episode in 1080p with the voices, music and sound effects.

⏱️ The first cell prints how long one shot takes on your GPU. The model download (about 20 GB) happens once per session.
"""),
code("""#@title 1 · Settings + GPU check + Google Drive
EPISODE   = "ep01"
QUALITY   = "720p"   #@param ["720p", "480p"]
STEPS     = 30       #@param {type:"integer"}
TEST_ONLY = False    #@param {type:"boolean"}
import subprocess, os
print(subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv"], capture_output=True, text=True).stdout)
assert os.path.exists("/dev/nvidia0") or subprocess.run(["nvidia-smi"]).returncode == 0, "No GPU! Runtime > Change runtime type > T4 GPU"
from google.colab import drive
drive.mount("/content/drive")
ROOT = "/content/drive/MyDrive/MRaniFamily"
PACK = f"{ROOT}/mrani_{EPISODE}_pack"   # one zip or several *_partN.zip files
OUT  = f"{ROOT}/{EPISODE}_clips"
os.makedirs(OUT, exist_ok=True)
import glob
ZIPS = sorted(glob.glob(PACK + "*.zip"))
assert ZIPS, f"Put mrani_{EPISODE}_pack*.zip in My Drive/MRaniFamily/ (Claude uploads it for you)"
W, H = (1280, 704) if QUALITY == "720p" else (832, 480)
print("OK ->", OUT, W, H)
"""),
code("""#@title 2 · Install (about 2 minutes)
!pip -q install -U "git+https://github.com/huggingface/diffusers" transformers accelerate ftfy sentencepiece imageio imageio-ffmpeg
!rm -rf /content/pack && mkdir -p /content/pack
for z in ZIPS: get_ipython().system(f'unzip -q -o "{z}" -d /content/pack')
import json
SHOTS = json.load(open("/content/pack/shots.json"))
todo = [s for s in SHOTS["shots"] if not os.path.exists(f"{OUT}/{s['id']}.mp4")]
if TEST_ONLY: todo = todo[:1]
print(len(SHOTS["shots"]), "shots in episode,", len(todo), "still to animate")
"""),
code("""#@title 3 · Read the shot descriptions (text encoder, then freed from memory)
import torch, gc, re, html, ftfy
from transformers import AutoTokenizer, UMT5EncoderModel
REPO = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
NEG = ("色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，"
       "多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走, "
       "text, watermark, logo, flicker, morphing face, extra limbs, different character, realistic photo")
def clean(t): t = ftfy.fix_text(t); t = html.unescape(html.unescape(t)); return re.sub(r"\\s+", " ", t).strip()
EMB = "/content/embeds.pt"
if not os.path.exists(EMB):
    tok = AutoTokenizer.from_pretrained(REPO, subfolder="tokenizer")
    te = UMT5EncoderModel.from_pretrained(REPO, subfolder="text_encoder", torch_dtype=torch.bfloat16, device_map="cuda")
    @torch.no_grad()
    def enc(p):
        x = tok([clean(p)], padding="max_length", max_length=512, truncation=True, add_special_tokens=True, return_attention_mask=True, return_tensors="pt")
        n = int(x.attention_mask.sum()); e = te(x.input_ids.cuda(), x.attention_mask.cuda()).last_hidden_state[0, :n]
        return torch.cat([e, e.new_zeros(512 - n, e.shape[1])])[None].to(torch.float16).cpu()
    E = {s["id"]: enc(s["prompt"] + ". " + SHOTS["style"]) for s in SHOTS["shots"]}; E["__neg__"] = enc(NEG)
    torch.save(E, EMB); del te; gc.collect(); torch.cuda.empty_cache()
E = torch.load(EMB); print("encoded", len(E) - 1, "shots")
"""),
code("""#@title 4 · Load Wan2.2 animation model (5B, free and open source)
from diffusers import WanImageToVideoPipeline, AutoencoderKLWan, WanTransformer3DModel
from diffusers.utils import export_to_video
# loaded straight onto the GPU so Colab's 12 GB of system RAM is never exceeded
vae = AutoencoderKLWan.from_pretrained(REPO, subfolder="vae", torch_dtype=torch.float32).to("cuda")
tr  = WanTransformer3DModel.from_pretrained(REPO, subfolder="transformer", torch_dtype=torch.float16, device_map="cuda")
pipe = WanImageToVideoPipeline.from_pretrained(REPO, text_encoder=None, transformer=tr, vae=vae, torch_dtype=torch.float16)
try: pipe.vae.enable_tiling()
except Exception as e: print("tiling not available:", e)
print("GPU memory used: %.1f GB" % (torch.cuda.memory_allocated() / 1e9))
"""),
code("""#@title 5 · Animate every shot (saved to Drive one by one; resume-safe)
import time
from PIL import Image
for i, s in enumerate(todo):
    path = f"{OUT}/{s['id']}.mp4"
    if os.path.exists(path): continue
    img = Image.open(f"/content/pack/images/{s['image']}.jpg").convert("RGB").resize((W, H), Image.LANCZOS)
    n = 49 if TEST_ONLY else s.get("frames", 81)
    t0 = time.time()
    with torch.inference_mode():
        out = pipe(image=img, prompt_embeds=E[s["id"]].cuda(), negative_prompt_embeds=E["__neg__"].cuda(),
                   height=H, width=W, num_frames=n, num_inference_steps=STEPS, guidance_scale=5.0,
                   generator=torch.Generator("cuda").manual_seed(1000 + i)).frames[0]
    export_to_video(out, path + ".tmp.mp4", fps=24); os.replace(path + ".tmp.mp4", path)
    gc.collect(); torch.cuda.empty_cache()
    print(f"✅ {i+1}/{len(todo)} {s['id']}  ({n} frames) in {(time.time()-t0)/60:.1f} min")
print("🎉 All done! Tell Claude: clips are ready." if not TEST_ONLY else "Test finished: untick TEST_ONLY and Run all.")
"""),
code("""#@title 6 · Preview the last finished shot
from IPython.display import HTML; from base64 import b64encode; import glob
f = sorted(glob.glob(f"{OUT}/*.mp4"), key=os.path.getmtime)[-1]
HTML(f'<p>{os.path.basename(f)}</p><video width=640 controls autoplay loop src="data:video/mp4;base64,{b64encode(open(f,"rb").read()).decode()}">')
"""),
md("""### Troubleshooting
- **"CUDA out of memory"**: set QUALITY to **480p** in cell 1 and **Run all** again.
- **Out of GPU time for today**: free Colab gives limited GPU hours per day. Come back tomorrow and **Run all**; finished shots are kept.
- **A shot looks wrong**: delete that one `.mp4` from `My Drive/MRaniFamily/ep01_clips/` and run again (you'll get a new take).
"""),
]
nb = {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4"},
      "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open(sys.argv[1], "w"), indent=1, ensure_ascii=False)
