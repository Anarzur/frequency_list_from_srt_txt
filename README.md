# frequency_list_from_srt_txt

A Flask web app that parses Japanese `.srt` or `.txt` subtitle files (and optionally a JSON word list) to generate a frequency‐sorted vocabulary list. Includes options to:

- Ignore text in parentheses `( … )`
- Filter out non-word tokens (pure punctuation or symbols, including “・”)
- Exclude numbers and romaji
- Skip words you already know (via an uploaded Migaku Export JSON word list)
- Click any word in the resulting list to see every sentence or subtitle line where it appears

---
