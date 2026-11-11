# M'RANI FAMILY: Series Bible
*An original animated family comedy for YouTube.*

## Logline
**Four siblings, four completely different kinds of genius, and zero ability to agree.** Big sister Aziza tries to lead lazy inventor Abdel-Hamid, daredevil playmaker Amir and screen-hacker toddler Hicham. Every episode, a problem only gets solved when they finally combine their talents.

## Format
- **Platform:** YouTube (main channel) plus Shorts cut from every episode.
- **Episode length:** 5–8 minutes (16:9, 1080p, 24 fps).
- **Audience:** families, kids 4–10 plus their parents. Marked **"Made for kids"** on YouTube.
- **Release rhythm:** 1 episode per week, same day and time, plus 2–3 Shorts per week from the episode.
- **Look:** 3D animated feature-film style (warm light, big expressive eyes), built from the approved character model sheets.
- **Language:** English first; Arabic/French dubs later (easy to add with AI voices).

## The family
| | Age | Genius | Funny weakness | Catchphrase | Color |
|---|---|---|---|---|---|
| **Aziza** | 12 | Hard-working scholar and natural leader | Forgets everything mid-sentence | *"Listen to me, I'm in charge! …wait, what was I doing?"* | Purple |
| **Abdel-Hamid** | ~10 | Inventor: math, science, code | Too lazy to move, always snacking | *"Why walk when I can invent?"* | Yellow |
| **Amir** | ~6 | Reads and predicts everything; football star | Overconfident; hates being treated like a kid | *"Don't talk to me like a kid. I already know how this ends."* | Orange |
| **Hicham** | 4 | Tech hacker who fixes any device | Glued to the screen; sneaky shortcuts | *"I watched a video about this."* | Blue |

Full character bibles live in `characters/<name>/character-sheet.md` with model sheets and hero images.

## The engine of every episode (the formula)
1. **Cold open (0:00–0:20):** a funny hook showing someone's weakness (Abdel-Hamid's robot fetching snacks, Aziza's sticky note on her forehead).
2. **The problem:** something goes wrong at home, school or in the neighborhood.
3. **Solo attempts fail:** each sibling tries alone with their own genius, and their weakness ruins it.
4. **"TEAM, HUDDLE UP!"** Aziza calls the huddle (signature moment, same music sting every episode).
5. **Combined plan:** Abdel-Hamid thinks, Amir moves, Hicham hacks, Aziza leads (and someone reminds her what the plan was).
6. **Twist:** the plan works, but with one funny surprise.
7. **Heart moment plus lesson:** one line about teamwork, kindness or family.
8. **Button gag and end card:** "See you next time, M'Rani Family!"

**Signature visuals:** Abdel-Hamid's floating equations, Amir's glowing prediction arrows, Hicham's floating app icons, and Aziza's "loading circle" when she forgets.

## Season 1: episode ideas (10 episodes)
1. **"The Snack Robot"**: Abdel-Hamid invents a robot to bring him snacks so he never has to stand up. It goes haywire and steals every snack in the house. *Lesson: shortcuts can make bigger problems.*
2. **"Babysitter Aziza"**: Mom and Dad go out and Aziza is in charge. She forgets where she put the house keys, Hicham's tablet and the dinner plan. *Lesson: even leaders need help.*
3. **"The Big Match"**: Amir's overconfidence almost loses the youth football final, until he learns to pass. *Lesson: a team is stronger than a star.*
4. **"The Wi-Fi Is Down!"**: movie night is ruined and only the 4-year-old can save it. *Lesson: everyone has something to give, even the smallest.*
5. **"Sticky Note Storm"**: wind blows Aziza's reminder notes across the neighborhood; the brothers chase them. *Lesson: helping family is a big deal.*
6. **"Science Fair"**: Abdel-Hamid's genius project needs him to actually move. *Lesson: trying something hard is brave.*
7. **"Screen-Free Saturday"**: Hicham without his tablet for a whole day; the siblings show him real-world adventure. *Lesson: the best fun is together.*
8. **"I Predicted That"**: all of Amir's predictions come true, until the one time they don't. *Lesson: it's okay to be wrong.*
9. **"Grandma's Visit"**: the house must be perfect in one hour. Total chaos, then teamwork. *Lesson: family first.*
10. **"The Mystery of the Missing Cookies"**: a detective episode where each sibling suspects another. *Lesson: don't judge too fast.*

## Channel branding (in `channel-art/`): official style "C"
- **Look:** sky-blue sunburst, confetti in the siblings' colors, chunky **Lilita One** letters (SIL Open Font License, free for commercial use) with a navy outline and a white **FAMILY** pill.
- `logo.png`: official logo (transparent).
- `youtube-profile-800.jpg`: the four siblings' faces in an arc with the logo below; readable even at comment size.
- `youtube-banner-2560x1440.jpg`: logo plus team picture inside YouTube's safe area.
- `title-card-1920x1080.jpg`: opening title for every episode.
- Earlier options are archived as `*-A.*` (dark purple) and `*-B.*` (sunny yellow); `profile-variants-compare.jpg` shows all three.
- Rebuild with `python3 channel-art/make_variants.py && python3 channel-art/finalize_c.py`.

## Copyright and safety notes
- Characters, names, stories, music and voices are original or licensed for the channel.
- Avoid real brand logos and real football clubs. The Pikachu-style cap ears were already replaced with an original gear badge.
- The characters are based on real children: keep their real names only with the family's consent, and never share personal details (school, location) in videos or descriptions.
- YouTube "Made for kids" means comments are off and there are no personalized ads (YouTube requires this under COPPA).
