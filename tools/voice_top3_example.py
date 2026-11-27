import torchaudio as ta, sys
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
m=ChatterboxMultilingualTTS.from_pretrained(device="cpu")
lines=[
"Salut, c'est Amine de The Punchline Lab. Voici le top trois des punchlines de la semaine. Accroche-toi.",
"Numéro trois. Le Comte de Bouderbala, sur Pôle emploi : un stage non rémunéré... mais payant. En Roumanie.",
"Numéro deux. Redouane Bougheraba découvre le salaire d'une conductrice de tram : huit mille euros ? J'arrête l'humour, je fais tram !",
"Et numéro un. Sarah Lélé à un Italien qui lui dit Wakanda forever : tu as un pilote en Formule un ? Mario Kart !",
"Laquelle tu préfères ? Dis-le en commentaire, et abonne-toi pour le top de la semaine prochaine.",
]
out=sys.argv[1]
for i,t in enumerate(lines):
    w=m.generate(t,language_id="fr",audio_prompt_path="ref.wav",exaggeration=0.6,cfg_weight=0.5)
    ta.save(f"{out}/l{i}.wav",w,m.sr)
