# -*- coding: utf-8 -*-
"""VOICEVOXで読み上げ音声を作る。1モーラあたりの長さを指定できる（既定200ミリ秒）。"""
import json, subprocess, sys, os, urllib.request, urllib.parse

HOST = 'http://127.0.0.1:50021'
SPEAKER = 30          # No.7 アナウンス
MORA_SEC = 0.200      # 1モーラあたりの長さ
OUT = 'sounds'

def post(path, params, body=None):
    url = HOST + path + '?' + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else b''
    req = urllib.request.Request(url, data=data, method='POST',
                                 headers={'Content-Type': 'application/json'})
    return urllib.request.urlopen(req).read()

def mora_stats(q):
    """モーラ数と、標準の速さでの発話の長さを数える"""
    n = 0; length = 0.0
    for ap in q['accent_phrases']:
        for m in ap['moras']:
            n += 1
            length += (m.get('consonant_length') or 0.0) + (m.get('vowel_length') or 0.0)
        if ap.get('pause_mora'):
            pm = ap['pause_mora']
            length += (pm.get('consonant_length') or 0.0) + (pm.get('vowel_length') or 0.0)
    return n, length

def synth(text, path):
    q = json.loads(post('/audio_query', {'text': text, 'speaker': SPEAKER}))
    n, length = mora_stats(q)
    target = n * MORA_SEC
    q['speedScale'] = max(0.5, min(2.0, length / target)) if target > 0 else 1.0
    q['prePhonemeLength'] = 0.1
    q['postPhonemeLength'] = 0.3
    wav = post('/synthesis', {'speaker': SPEAKER}, q)
    tmp = path + '.wav'
    open(tmp, 'wb').write(wav)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-b:a', '96k', path], check=True)
    os.remove(tmp)
    dur = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
        '-of','csv=p=0', path], capture_output=True, text=True).stdout.strip())
    return n, dur

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    yomi = json.load(open('yomi.json', encoding='utf-8'))
    tot_n = tot_d = 0
    for pid, (kami, shimo) in yomi.items():
        for part, text in (('A', kami), ('B', shimo)):
            path = f'{OUT}/I-{int(pid):03d}{part}.mp3'
            n, dur = synth(text, path)
            tot_n += n; tot_d += dur
            print(f'{path}  {n}モーラ  {dur:.2f}秒  {dur/n*1000:.0f}ミリ秒/モーラ')
    print(f'\n全体 {tot_n}モーラ {tot_d:.1f}秒　平均 {tot_d/tot_n*1000:.0f}ミリ秒/モーラ（前後の無音を含む）')
