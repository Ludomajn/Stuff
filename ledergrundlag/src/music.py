"""Genererer original, rettighedsfri baggrundsmusik til v4 (lo-fi) og v5 (chiptune).

Brug: python3 src/music.py <ud-mappe>
Musikken følger talens struktur: stop ved "MEN" (50,3 s), fyldigere efter, slutakkord ved "bedste hold".
"""
import sys
import wave
import numpy as np

SR = 44100
TOTAL = 134.5
MEN_STOP, MEN_BACK = 50.3, 52.1
END_CHORD = 128.2

rng = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env(n, a=0.005, tau=1.0):
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    k = max(1, int(a * SR))
    e[:k] *= np.linspace(0, 1, k)
    return e


def add(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    buf[i:i + len(sig)] += sig


def lowpass_fast(x, fc):
    # én-polet lavpas uden scipy
    a = np.exp(-2 * np.pi * fc / SR)
    from itertools import accumulate
    out = np.fromiter(accumulate(x * (1 - a), lambda acc, v: acc * a + v), dtype=np.float64, count=len(x))
    return out


def gate_men(buf, fade=0.08):
    """Stop ved MEN og kom ind igen."""
    t = np.arange(len(buf)) / SR
    g = np.ones_like(buf)
    g[(t >= MEN_STOP) & (t < MEN_BACK)] = 0
    k = int(fade * SR)
    i = int(MEN_STOP * SR)
    g[i - k:i] = np.linspace(1, 0, k)
    j = int(MEN_BACK * SR)
    g[j:j + k // 2] = np.linspace(0, 1, k // 2)
    return buf * g


def master_fade(buf, out=3.5):
    n = int(out * SR)
    buf[-n:] *= np.linspace(1, 0, n) ** 1.5
    k = int(0.6 * SR)
    buf[:k] *= np.linspace(0, 1, k)
    return buf


def write(path, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.89
    s = (x * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(s.tobytes())


# ---------------------------------------------------------------- v4: lo-fi klaver
def lofi():
    N = int(TOTAL * SR)
    keys, bass, drums, bell = (np.zeros(N) for _ in range(4))
    bpm = 84; beat = 60 / bpm; bar = 4 * beat
    # Cmaj9 – Am9 – Fmaj7 – G6/9
    prog = [(48, [64, 67, 71, 74]), (45, [64, 67, 72, 71]), (41, [64, 69, 72, 76]), (43, [62, 67, 69, 71])]

    def ep(freq, dur, vel):
        n = int(dur * SR); t = np.arange(n) / SR
        trem = 1 + 0.06 * np.sin(2 * np.pi * 5 * t)
        s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(2 * np.pi * 2 * freq * t) + 0.08 * np.sin(2 * np.pi * 3 * freq * t)
        return vel * s * trem * env(n, 0.006, 1.3)

    def kick():
        n = int(0.35 * SR); t = np.arange(n) / SR
        f = 45 + 80 * np.exp(-t * 30)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.12)

    def snare():
        n = int(0.25 * SR)
        s = rng.standard_normal(n)
        s = s - lowpass_fast(s, 1200)
        return 0.5 * s * env(n, 0.001, 0.07)

    def hat():
        n = int(0.06 * SR)
        s = rng.standard_normal(n)
        s = s - lowpass_fast(s, 6000)
        return 0.25 * s * env(n, 0.001, 0.015)

    K, Sn, Ht = kick(), snare(), hat()
    t0 = 0.0; b = 0
    while t0 < TOTAL:
        root, chord = prog[b % 4]
        sw = 0.04  # swing
        for hit, vel in ((0, .55), (2.5 * beat, .4)):
            for k, note in enumerate(chord):
                add(keys, t0 + hit + k * 0.012, ep(midi(note), 2.6, vel * (0.9 if k else 1)))
        n = int(bar * SR); tt = np.arange(n) / SR
        bs = np.sin(2 * np.pi * midi(root) * tt) + 0.3 * np.sin(2 * np.pi * 2 * midi(root) * tt)
        add(bass, t0, 0.7 * bs * env(n, 0.01, 1.2))
        add(bass, t0 + 2.5 * beat, 0.45 * (np.sin(2 * np.pi * midi(root + 7) * tt[: n // 2])) * env(n // 2, 0.01, 0.5))
        full = t0 >= MEN_BACK
        for i8 in range(8):
            ht = t0 + i8 * beat / 2 + (sw if i8 % 2 else 0)
            add(drums, ht, Ht * (0.7 if full else 0.45))
        if full or b % 2 == 1:
            add(drums, t0, K * (0.9 if full else 0.5)); add(drums, t0 + 2.5 * beat, K * 0.6 * (1 if full else .6))
        if full:
            add(drums, t0 + beat, Sn); add(drums, t0 + 3 * beat, Sn)
        # klokkemelodi i sidste del
        if t0 >= 104:
            mel = [79, 76, 74, 72] if b % 2 == 0 else [76, 74, 72, 74]
            for i, m in enumerate(mel):
                n2 = int(1.2 * SR); tt2 = np.arange(n2) / SR
                s = np.sin(2 * np.pi * midi(m) * tt2) * env(n2, 0.003, 0.5)
                add(bell, t0 + i * beat, 0.22 * s)
        t0 += bar; b += 1
    mix = 0.55 * lowpass_fast(keys, 2800) + 0.8 * lowpass_fast(bass, 600) + 0.5 * drums + bell
    t = np.arange(N) / SR
    mix[t > END_CHORD - 0.05] = 0  # slutakkorden står alene
    for k, note in enumerate([48, 55, 64, 67, 71, 74]):
        add(mix, END_CHORD + k * 0.03, 0.55 * ep(midi(note), 6.0, 0.6))
    mix += 0.006 * rng.standard_normal(N) * (rng.random(N) < 0.002) * 20  # vinylknas
    mix += 0.002 * lowpass_fast(rng.standard_normal(N), 3000)
    return master_fade(gate_men(mix))


# ---------------------------------------------------------------- v5: chiptune
def chip():
    N = int(TOTAL * SR)
    lead, arp, bass, drums = (np.zeros(N) for _ in range(4))
    bpm = 112; beat = 60 / bpm; bar = 4 * beat
    # G – Em – C – D
    prog = [(43, [67, 71, 74]), (40, [64, 67, 71]), (36, [64, 67, 72]), (38, [66, 69, 74])]

    def pulse(freq, dur, duty=0.25, vol=1.0, tau=0.25):
        n = int(dur * SR); t = np.arange(n) / SR
        ph = (freq * t) % 1.0
        return vol * np.where(ph < duty, 1.0, -1.0) * env(n, 0.002, tau)

    def tri(freq, dur, vol=1.0):
        n = int(dur * SR); t = np.arange(n) / SR
        ph = (freq * t) % 1.0
        return vol * (4 * np.abs(ph - 0.5) - 1) * env(n, 0.002, 0.6)

    def noise(dur, tau, vol, step=1):
        n = int(dur * SR)
        s = rng.choice([-1.0, 1.0], size=n // step + 1).repeat(step)[:n]
        return vol * s * env(n, 0.001, tau)

    kick = tri(55, 0.15, 1.0) * np.linspace(1, 0, int(0.15 * SR))
    snare = noise(0.18, 0.06, 0.6, 2)
    hat = noise(0.04, 0.01, 0.25, 1)
    melody = [74, 76, 79, 76, 74, 71, 74, None, 71, 72, 74, 72, 71, 69, 67, None]
    t0 = 0.0; b = 0
    while t0 < TOTAL:
        root, ch = prog[b % 4]
        full = t0 >= MEN_BACK
        for i16 in range(16):
            n = ch[i16 % 3] + (12 if (i16 // 3) % 2 else 0)
            add(arp, t0 + i16 * beat / 4, pulse(midi(n), beat / 4 * 0.9, 0.125, 0.35, 0.08))
        for i8 in range(8):
            add(bass, t0 + i8 * beat / 2, tri(midi(root + (12 if i8 % 2 else 0)), beat / 2 * 0.95, 0.9))
        for i8 in range(8):
            add(drums, t0 + i8 * beat / 2, hat * (1 if full else .6))
        if full or b % 2:
            add(drums, t0, kick); add(drums, t0 + 2 * beat, kick)
        if full:
            add(drums, t0 + beat, snare); add(drums, t0 + 3 * beat, snare)
            # melodi (2 takter pr. frase)
            ph = (b % 2) * 8
            for i in range(8):
                m = melody[ph + i]
                if m:
                    add(lead, t0 + i * beat / 2, pulse(midi(m), beat / 2 * 0.9, 0.5, 0.5, 0.35))
        t0 += bar; b += 1
    mix = 0.5 * arp + 0.7 * bass + 0.55 * drums + 0.45 * lead
    t = np.arange(N) / SR
    mix[t > END_CHORD - 0.05] = 0
    # sejrsfanfare + slutakkord
    for i, (m, d) in enumerate([(67, .18), (71, .18), (74, .18), (79, .5)]):
        add(mix, END_CHORD + i * 0.18, pulse(midi(m), d + .3, 0.5, 0.55, 0.4))
    for m in (55, 67, 71, 74, 79):
        add(mix, END_CHORD + 0.75, pulse(midi(m), 4.0, 0.25, 0.3, 1.4))
    return master_fade(gate_men(mix))


if __name__ == '__main__':
    out = sys.argv[1]
    write(f'{out}/music-v4.wav', lofi())
    write(f'{out}/music-v5.wav', chip())
    print('ok')
