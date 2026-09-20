# -*- coding: utf-8 -*-
"""様式のファイルと cards.tsv から、画像生成用のプロンプト一覧を作る。
   使い方:  python3 build_prompts.py [出力ファイル] [--style 様式.md] [作る札の名前...]
   札の名前を省略すると全部を出す。様式を省略すると style.md を使う。"""
import sys, os, re
here = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
stylefile = 'style.md'
if '--style' in args:
    i = args.index('--style'); stylefile = args[i+1]; del args[i:i+2]
style = open(os.path.join(here, stylefile), encoding='utf-8').read()
# 「---」より後ろだけをプロンプトに使う。前は人が読むための説明である
style = style.split('---', 1)[1] if '---' in style else style
style = '\n'.join(l for l in style.split('\n') if l.strip())
style = ' '.join(style.split())

cards = []
for line in open(os.path.join(here,'cards.tsv'), encoding='utf-8'):
    line = line.rstrip('\n')
    if not line.strip() or line.startswith('#'): continue
    parts = line.split('\t')
    if len(parts) < 4: continue
    cards.append(parts[:4])

colors = {}
for line in open(os.path.join(here,'colors.tsv'), encoding='utf-8'):
    line=line.rstrip('\n')
    if not line.strip() or line.startswith('#'): continue
    c=line.split('\t')
    if len(c)>=3: colors[c[0]]=c[2]

out = args[0] if args else os.path.join(here,'prompts.txt')
only = set(args[1:])
n = 0
with open(out,'w',encoding='utf-8') as f:
    for slug, name, subject, fam in cards:
        if only and slug not in only and name not in only: continue
        st = style.replace('{色}', colors.get(fam, '朱色'))
        f.write(f'{slug}.png|{st} 題材は「{name}」。{subject}。\n')
        n += 1
print(f'{n} 枚ぶんのプロンプトを {out} に書いた')
