# -*- coding: utf-8 -*-
"""できた札の絵をキーワードごとに並べた一覧を作る。小さくしたときの見分けも確かめられる。
   使い方: python3 images/一覧を作る.py [出力.png] [--small]"""
from PIL import Image, ImageDraw, ImageFont
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
small = '--small' in sys.argv
args = [a for a in sys.argv[1:] if not a.startswith('--')]
out = args[0] if args else os.path.join(here, '一覧.png')

colors, cards = {}, []
for line in open(os.path.join(here,'prompts','colors.tsv'), encoding='utf-8'):
    if line.startswith('#') or not line.strip(): continue
    c = line.rstrip('\n').split('\t'); colors[c[0]] = (c[1], c[3] if len(c)>3 else '#333')
for line in open(os.path.join(here,'prompts','cards.tsv'), encoding='utf-8'):
    if line.startswith('#') or not line.strip(): continue
    p = line.rstrip('\n').split('\t')
    if len(p) >= 4: cards.append(p)

order = ['ki','si','kn','ay','tk','ik','cm']
byfam = {f: [c for c in cards if c[3]==f] for f in order}
S = 84 if small else 190
pad, lab, gap = 10, 26, 22
cols = max(len(v) for v in byfam.values())
W = 120 + cols*(S+pad) + pad
H = pad + sum((S+lab+gap) for f in order if byfam[f])
im = Image.new('RGB', (W,H), (240,236,226)); d = ImageDraw.Draw(im)
JP = '/System/Library/Fonts/Hiragino Sans GB.ttc'
font  = ImageFont.truetype(JP, 15) if os.path.exists(JP) else ImageFont.load_default()
font2 = ImageFont.truetype(JP, 17) if os.path.exists(JP) else font
y = pad
for f in order:
    if not byfam[f]: continue
    name, hexcol = colors.get(f, ('?','#333'))
    d.rectangle([pad, y, pad+96, y+S], fill=hexcol)
    for i,(slug,jp,subj,_) in enumerate(byfam[f]):
        x = 120 + i*(S+pad)
        p = os.path.join(here,'fuda',slug+'.png')
        if os.path.exists(p):
            im.paste(Image.open(p).convert('RGB').resize((S,S), Image.LANCZOS), (x,y))
        else:
            d.rectangle([x,y,x+S,y+S], fill=(255,255,255), outline=(200,200,200))
        d.text((x+3, y+S+6), jp, fill=(40,40,40), font=font)
    y += S+lab+gap
im.save(out); print(out, im.size, f'（{sum(1 for c in cards if os.path.exists(os.path.join(here,"fuda",c[0]+".png")))}/{len(cards)} 枚）')
