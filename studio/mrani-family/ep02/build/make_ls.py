# builds lip-sync inputs: base video (ping-pong segment, exact length) + padded line audio
import subprocess, sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
PRE, POST = 0.20, 0.30
PLAN = {  # line key: (clip, seg start, seg end)
 "s1a": ("T_aziza_det", 0.0, 5.0), "s1c": ("T_aziza_det", 3.9, 5.0), "s1h": ("T_aziza_det", 0.8, 5.0),
 "s1b": ("T_amir_point", 0.0, 5.0), "s1d": ("T_amir_point", 0.9, 2.4),
 "s1e": ("T_abd_bean", 0.0, 5.0), "s1g": ("T_abd_bean", 2.4, 5.0),
 "s1f": ("T_hic_couch", 0.0, 5.0), "s2e": ("A_hack", 3.0, 5.0),
 "s3a": ("T_abd_bed", 2.2, 5.0), "s3b": ("T_aziza_bed", 0.0, 5.0),
 "s3c": ("T_amir_bed", 0.0, 2.7), "s3d": ("T_hic_bed", 0.0, 5.0),
 "s4a": ("A_egg", 3.0, 5.0), "s4d": ("A_stir", 2.4, 5.0),
 "s4b": ("T_aziza_recipe", 0.0, 5.0), "s4c": ("T_aziza_recipe", 2.5, 5.0), "s4e": ("T_aziza_recipe", 0.5, 5.0),
 "s5a": ("T_hic_closed", 0.0, 5.0),
}
SPK = {"s1a":"AZI","s1c":"AZI","s1h":"AZI","s1b":"AMI","s1d":"AMI","s1e":"ABD","s1g":"ABD","s1f":"HIC","s2e":"HIC",
       "s3a":"ABD","s3b":"AZI","s3c":"AMI","s3d":"HIC","s4a":"AMI","s4d":"ABD","s4b":"AZI","s4c":"AZI","s4e":"AZI","s5a":"HIC"}
CROP = {"s4b","s4c","s4e"}  # Aziza-only crop (Hicham also in frame); pasted back at x=0 in the edit
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",p]))
def run(*a): subprocess.run(["ffmpeg","-y","-loglevel","error",*a], check=True)
for k in (sys.argv[1:] or PLAN):
    clip, a, b = PLAN[k]; src = f"{HERE}/clips/{clip}.mp4"
    if not os.path.exists(src): print("skip", k); continue
    wav = f"{HERE}/vo/{k}_{SPK[k]}.wav"; L = math.ceil((dur(wav) + PRE + POST) / 0.64) * 0.64 + 0.03  # latentsync keeps whole 16-frame blocks only
    out_a = f"{HERE}/ls_in/{k}.wav"
    run("-i", wav, "-af", f"adelay={int(PRE*1000)}:all=1,apad,atrim=0:{L:.3f}", "-ar", "44100", "-ac", "1", out_a)
    seg = b - a; n = int(L // seg) + 2
    parts = "".join(f"[f]" if i % 2 == 0 else f"[r]" for i in range(n))
    FULL = os.environ.get("FULL") == "1"
    crop = ",crop=640:720:0:0" if k in CROP and not FULL else ""
    fc = (f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,scale=1280:720{crop},fps=25,split=2[x][y];[y]reverse[r0];"
          f"[x]split={(n+1)//2}" + "".join(f"[f{i}]" for i in range((n+1)//2)) + ";" +
          f"[r0]split={max(1,n//2)}" + "".join(f"[r{i}x]" for i in range(max(1,n//2))) + ";")
    seq, fi, ri = "", 0, 0
    for i in range(n):
        if i % 2 == 0: seq += f"[f{fi}]"; fi += 1
        else: seq += f"[r{ri}x]"; ri += 1
    if n // 2 == 0: fc += "[r0x]nullsink;"
    fc += f"{seq}concat=n={n}:v=1:a=0,trim=0:{L:.3f},setpts=PTS-STARTPTS[v]"
    run("-i", src, "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", f"{HERE}/ls_in/{k}" + ("_full" if FULL else "") + ".mp4")
    print(k, clip, round(L, 2))
