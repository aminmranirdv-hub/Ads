# M'RANI FAMILY Ep.2 "The Case of the Missing Cookie" - dialogue (key, speaker, text with eleven_v4 tags)
# speakers AZI ABD AMI HIC; "ALL" lines are recorded by every speaker and blended
VOICE = {"AZI": 499, "ABD": 1417, "AMI": 521, "HIC": 303}
LINES = [
 ("c1", "AZI", "[proud, dreamy] My prize cookie. Saved all week."),
 ("c2", "AZI", "[screaming] WHO. ATE. MY. COOKIE?!"),
 ("s1a", "AZI", "[commanding] Nobody leaves this house until we find the thief!"),
 ("s1b", "AMI", "[smug] I already know who did it. I predicted it yesterday."),
 ("s1c", "AZI", "[suspicious] Who?"),
 ("s1d", "AMI", "[dramatic, pointing] HIM!"),
 ("s1e", "ABD", "[mouth full, chewing] Mmf... I'm eating CHIPS. Totally different snack family."),
 ("s1f", "HIC", "[deadpan, not looking up] Statistically, the person with crumbs on his shirt is guilty eighty-seven percent of the time."),
 ("s1g", "ABD", "[panicked] Those are chip crumbs! I'm innocent!"),
 ("s1h", "AZI", "[writing, then confused] Suspect number one... wait, what was his name again?"),
 ("s1i", "ALL", "[shouting together] ABDEL-HAMID!"),
 ("s2a", "AZI", "[focused, whispering] A crumb trail... very suspicious."),
 ("s2b", "AMI", "[excited] Re-enactment! The thief came in fast, dodged left, and... BOOM!"),
 ("s2c", "ABD", "[lazy, thoughtful] Interesting. The thief had... very small hands."),
 ("s2d", "HIC", "[calm] Accessing the old baby camera. Beep-boop."),
 ("s2e", "HIC", "[calm] Got it. The thief is on camera."),
 ("s2f", "AZI", "[urgent] Play it!"),
 ("s2g", "AMI", "[scared] It's a GHOST!"),
 ("s2h", "ABD", "[slow realization] ...That's not a ghost."),
 ("s3a", "ABD", "[guilty, sheepish] I built a robot to bring me snacks, so I'd never have to get up. I told it to find... the best snack in the house."),
 ("s3b", "AZI", "[hands on hips, annoyed] And it found MY cookie."),
 ("s3c", "AMI", "[triumphant] So technically... I was right! It WAS him!"),
 ("s3d", "HIC", "[deadpan] Technically, it was his robot. Fifty percent right."),
 ("s4a", "AMI", "[proud] Tactical precision!"),
 ("s4b", "AZI", "[reading slowly] Step three... wait..."),
 ("s4c", "AZI", "[relieved, smiling] ...thank you, Hicham."),
 ("s4d", "ABD", "[sincere] I'm sorry, Aziza. I should have just asked, instead of taking a shortcut."),
 ("s4e", "AZI", "[warm, smiling] And I'm sorry too. I blamed you without any proof."),
 ("s5a", "HIC", "[deadpan, to camera] Case closed."),
 ("s5b", "ALL", "[shouting together, shocked] SNACK-O-BOT!"),
]
def takes():
    out = {}
    for spk in VOICE:
        ks = [(k, t) for k, s, t in LINES if s == spk or s == "ALL"]
        out[spk] = ks
    return out
