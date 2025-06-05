import os
import re
import json
import srt
import MeCab

from flask import Flask, render_template, request
from collections import defaultdict, Counter

app = Flask(__name__)

# ——————————————————————————
# MeCab initialization (Homebrew paths on macOS)
# ——————————————————————————
prefix = os.popen("brew --prefix").read().strip()
MECABRC_PATH = os.path.join(prefix, "etc/mecabrc")
MECAB_DIC_PATH = os.path.join(prefix, "lib/mecab/dic/ipadic")

# —————————
# Helper classes
# —————————
class TextLine:
    """
    Holds either a .txt sentence or .srt subtitle,
    including filename and optional timestamps.
    """
    def __init__(self, filename, content, start=None, end=None):
        self.filename = filename
        self.content = content
        self.start = start
        self.end = end

# ————————————————————————————
# Split full Japanese text into sentences ending in “。”
# ————————————————————————————
def extract_jp_sentences(full_text):
    parts = full_text.split("。")
    sentences = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        sentences.append(part + "。")
    return sentences

# ——————————————————————————
# Regex to detect Japanese/word characters and ASCII tokens
# ——————————————————————————
WORD_RE = re.compile(r"[\\w\u3040-\u30ff\u4e00-\u9fff]")
ASCII_RE = re.compile(r"^[A-Za-z0-9]+$")

def is_word(token: str) -> bool:
    return bool(WORD_RE.search(token))

# ————————————————————————————————
# Routes
# ————————————————————————————————
@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        ignore_paren    = 'ignore_paren' in request.form
        filter_nonwords = 'filter_nonwords' in request.form
        filter_num_romaji = 'filter_num_romaji' in request.form

        # 1) Load known words from optional JSON
        known_words = set()
        json_file = request.files.get('json_file')
        if json_file and json_file.filename.lower().endswith('.json'):
            try:
                data = json.load(json_file)
                for entry in data:
                    if isinstance(entry, list) and entry:
                        word = entry[0].split('◴')[0]
                        known_words.add(word)
            except Exception:
                pass

        # 2) Collect .srt and .txt files into TextLine items
        sub_files = request.files.getlist('sub_files')
        items = []

        for uploaded in sub_files:
            fname = uploaded.filename
            lower = fname.lower()

            if lower.endswith('.srt'):
                raw = uploaded.read().decode('utf-8', errors='ignore')
                if ignore_paren:
                    raw = re.sub(r"\([^)]*\)", "", raw)
                try:
                    for sub in srt.parse(raw):
                        content = sub.content.strip()
                        if not content:
                            continue
                        items.append(TextLine(
                            filename=fname,
                            content=content,
                            start=sub.start,
                            end=sub.end
                        ))
                except Exception:
                    pass

            elif lower.endswith('.txt'):
                raw = uploaded.read().decode('utf-8', errors='ignore')
                if ignore_paren:
                    raw = re.sub(r"\([^)]*\)", "", raw)
                for sentence in extract_jp_sentences(raw):
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    items.append(TextLine(
                        filename=fname,
                        content=sentence,
                        start=None,
                        end=None
                    ))

            # *** No longer handling .epub or .pdf ***

        # 3) Initialize MeCab for morphological parsing
        tagger = MeCab.Tagger(f"-r {MECABRC_PATH} -d {MECAB_DIC_PATH}")

        # 4) Tokenize each TextLine, use lemma (base form) for matching
        word_occurrences = defaultdict(list)

        for item in items:
            node = tagger.parseToNode(item.content)
            while node:
                surface  = node.surface
                features = node.feature.split(',')
                lemma = features[6] if len(features) > 6 and features[6] != '*' else surface

                if filter_nonwords and not is_word(surface):
                    node = node.next
                    continue

                if filter_num_romaji and ASCII_RE.fullmatch(surface):
                    node = node.next
                    continue

                if known_words and lemma in known_words:
                    node = node.next
                    continue

                word_occurrences[lemma].append(item)
                node = node.next

        # 5) Compute frequencies (by lemma)
        freq = Counter({w: len(occ) for w, occ in word_occurrences.items()})
        vocabulary = sorted(freq.items(), key=lambda x: x[1], reverse=True)

        app.config['WORD_OCCURRENCES'] = word_occurrences

        return render_template(
            'vocabulary.html',
            vocabulary=vocabulary,
            ignore_paren=ignore_paren,
            filter_nonwords=filter_nonwords,
            filter_num_romaji=filter_num_romaji,
            known_count=len(known_words),
            new_count=len(vocabulary)
        )

    return render_template('upload.html')


@app.route('/word/<word>')
def show_occurrences(word):
    raw_list = app.config.get('WORD_OCCURRENCES', {}).get(word, [])

    # Group by filename and remove exact duplicates
    by_file = defaultdict(list)
    seen = set()
    for item in raw_list:
        key = (item.filename, item.start, item.end, item.content.strip())
        if key in seen:
            continue
        seen.add(key)
        by_file[item.filename].append(item)

    return render_template(
        'occurrences.html',
        word=word,
        occurrences=by_file
    )


if __name__ == '__main__':
    app.run(debug=True, port=5000)
