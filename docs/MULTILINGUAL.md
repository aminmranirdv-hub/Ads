# Multilingual Editions (FR · EN · Darija · Arabic)

## Principles

1. **Translate the joke, not the words.** Keep the mechanism (misdirection, escalation, the twist word) and land the twist word as close to the end of the cue as the target language allows.
2. **Preserve meaning.** An adaptation can swap a reference only if it does the *same comedic job* and doesn't change what the comedian is saying about anyone.
3. **Label adaptations.** When a line is adapted rather than translated, add a short editorial note in the description ("Subtitles adapted for English-speaking audiences"). Never present an adaptation as a verbatim quote.
4. **Keep the timing.** One translated cue per source cue, same timestamps, so the punchline subtitle still appears *on* the punchline.

## Per-language notes

| language | script / `language` value | notes |
|---|---|---|
| French | `fr` | Keep the spaces before `? ! :` (French typography). Uppercase subtitles are fine. |
| English | `en` | Shorter lines; land the twist word last. |
| Moroccan Darija | `darija` (Latin, "3arabizi") or `darija_ar` (Arabic script) | Pick one script per edition. Latin Darija reaches diaspora audiences; Arabic script reaches Morocco. Keep code-switching (FR/AR) as spoken, since it's part of the humour. |
| Arabic (MSA) | `ar` | RTL is handled by libass. Arabic font from `brand.fonts.ar`. No forced uppercase. Use MSA for pan-Arab reach and Darija for Moroccan authenticity. |

Add `"darija_ar": "DejaVu Sans"` (or a better Arabic display font once installed) under `fonts` in `brand/identity.json` if you render Darija in Arabic script.

## Files

```
subs.srt          original language (word for word)
subs.en.srt       English
subs.ar.srt       Arabic
edit.en.json      copy of edit.json with "subtitles": "subs.en.srt", "language": "en",
                  translated editorial_captions and publishing block
```

## Translator checklist

- [ ] The punchline still lands in the same cue
- [ ] Names, places and numbers are correct
- [ ] Adapted references are marked in the description
- [ ] No line attributes something the comedian didn't say
- [ ] A native speaker has reviewed it (especially Darija)
