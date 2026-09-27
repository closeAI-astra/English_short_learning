"""Compile the hand-authored bilingual expansion; no network or generated filler.

Run: python materials/_build_expansion.py
Source rows: header, four or five EN<TAB>JA slides, vocabulary, question,
Japanese answer explanation. The correct option is authored first and rotated.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def sense_groups(text):
    """Keep authored boundaries; break long groups at clause/preposition boundaries."""
    result = []
    starts = {'because', 'while', 'when', 'if', 'unless', 'although', 'rather', 'before',
              'after', 'without', 'instead', 'so', 'and', 'but', 'or', 'whether',
              'that', 'which', 'who', 'where', 'with', 'from', 'for', 'in', 'on', 'to', 'as'}
    for group in text.split(' / '):
        words = group.split()
        while len(words) > 6:
            candidates = [i for i in range(2, min(6, len(words) - 2) + 1)
                          if words[i].lower() in starts or words[i-1].endswith((',', '.', ':'))]
            cut = min(candidates, key=lambda i: abs(i-4)) if candidates else min(6, len(words)-2)
            result.append(' '.join(words[:cut]))
            words = words[cut:]
        result.append(' '.join(words))
    return ' / '.join(result)

def compile_shorts(filename, prefix, series):
    lessons = []
    for number, block in enumerate((HERE / filename).read_text(encoding='utf-8').strip().split('\n\n'), 1):
        lines = block.splitlines()
        genre, title, scene = lines[0].split('|', 2)
        slides = [[scene, sense_groups(line.split('\t')[0]), line.split('\t')[1]] for line in lines[1:-3]]
        vocab = [item.split('=') for item in lines[-3].split('|')]
        question, *options = lines[-2].split('|')
        position = (number - 1) % 4
        options = options[-position:] + options[:-position] if position else options
        lessons.append(dict(id=f'{prefix}-{number:02}', g=genre, t=title, sl=slides,
                            w=vocab, q=[question, options, position],
                            series=series, explanation=lines[-1]))
    (HERE / f'shorts_{prefix}.json').write_text(json.dumps(lessons, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'{prefix}: {len(lessons)} shorts')

def compile_stories():
    lessons = []
    for block in (HERE / '_bridge_readings.txt').read_text(encoding='utf-8').strip().split('\n\n'):
        lines = block.splitlines()
        key, genre, title, scene = lines[0].split('|', 3)
        questions, explanations = [], []
        for i, line in enumerate(lines[7:]):
            question, correct, wrong1, wrong2, explanation = line.split('|')
            options = [correct, wrong1, wrong2]
            position = i % 3
            options = options[-position:] + options[:-position] if position else options
            questions.append([question, options, position])
            explanations.append(explanation)
        lessons.append(dict(key=key, g=genre, title=title, scene=scene, level='B1–B2',
                            paras=[line.split('\t') for line in lines[1:7]], qs=questions,
                            explanations=explanations, series='600→850 読み聞き実践'))
    (HERE / 'stories_bridge850.json').write_text(json.dumps(lessons, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'bridge850: {len(lessons)} stories')

if __name__ == '__main__':
    compile_shorts('_native.txt', 'native', 'Native or Weird?')
    compile_shorts('_curiosity.txt', 'curiosity', '日常のしくみ')
    compile_shorts('_bridge850.txt', 'bridge850', '600→850 スキル別')
    compile_stories()
