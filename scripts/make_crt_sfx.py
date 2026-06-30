"""Synthesize warm, understated CRT television SFX for the Spooky Inquisitor
old-TV intro. Outputs 16-bit mono WAVs into assets/audio/ with a tv_ prefix.

Goal: tasteful and analog, NOT harsh — soft thumps, a faint mains hum, gentle
band-limited snow, and a classic descending power-off zip. Levels kept low.
"""
import os
import wave

import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
rng = np.random.default_rng(7)


def save(name, x):
    x = np.asarray(x, dtype=np.float64)
    # soft limit + normalize headroom, then 16-bit
    peak = np.max(np.abs(x)) or 1.0
    x = np.tanh(x / max(peak, 1e-9) * 0.98) * 0.92
    pcm = (x * 32767).astype("<i2")
    with wave.open(os.path.join(OUT, name), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", name, f"{len(x)/SR:.2f}s")


def t(dur):
    return np.linspace(0, dur, int(SR * dur), endpoint=False)


def lp(x, fc):
    b, a = butter(2, fc / (SR / 2), btype="low")
    return lfilter(b, a, x)


def bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], btype="band")
    return lfilter(b, a, x)


def fade(x, fin=0.005, fout=0.02):
    n = len(x)
    ai = int(SR * fin)
    ao = int(SR * fout)
    e = np.ones(n)
    if ai:
        e[:ai] = np.linspace(0, 1, ai)
    if ao:
        e[-ao:] = np.linspace(1, 0, ao)
    return x * e


# --- tv_on: soft electromagnetic thunk + degauss wobble + whine onset -------
def tv_on():
    d = 0.55
    tt = t(d)
    # low "bwomp" of the degauss coil energizing (70 Hz, fast decay)
    thump = np.sin(2 * np.pi * 68 * tt) * np.exp(-tt * 9) * 0.9
    thump += np.sin(2 * np.pi * 136 * tt) * np.exp(-tt * 12) * 0.3
    # degauss wobble: 50/60 Hz hum swelling then settling in first 0.25 s
    swell = np.exp(-((tt - 0.12) ** 2) / (2 * 0.05 ** 2))
    hum = (np.sin(2 * np.pi * 60 * tt) + 0.4 * np.sin(2 * np.pi * 120 * tt)) * swell * 0.22
    # tiny relay click at the very start
    click = np.zeros_like(tt)
    click[: int(SR * 0.004)] = rng.standard_normal(int(SR * 0.004)) * 0.5
    click = lp(click, 4000)
    # faint high CRT whine fading in (kept gentle ~9 kHz, low level)
    whine = np.sin(2 * np.pi * 9000 * tt) * np.clip((tt - 0.1) / 0.4, 0, 1) * 0.04
    x = fade(thump + hum + click + whine, fin=0.001, fout=0.05)
    save("tv_on.wav", x)


# --- tv_hum: quiet loopable CRT bed (mains hum + faint whine + noise floor) --
def tv_hum():
    d = 8.0
    tt = t(d)
    hum = (np.sin(2 * np.pi * 60 * tt) + 0.5 * np.sin(2 * np.pi * 120 * tt)
           + 0.2 * np.sin(2 * np.pi * 180 * tt)) * 0.5
    whine = np.sin(2 * np.pi * 9400 * tt) * 0.07
    floor = lp(rng.standard_normal(len(tt)), 2000) * 0.05
    x = (hum + whine + floor) * 0.18
    # equalize endpoints so it loops without a click
    x = x - np.linspace(x[0], x[-1], len(x)) * 0.0
    save("tv_hum.wav", x)


# --- tv_static: gentle band-limited snow burst ------------------------------
def tv_static():
    d = 0.8
    tt = t(d)
    n = rng.standard_normal(len(tt))
    snow = bp(n, 1200, 7000) * 1.2
    # quick attack, gentle decay so it doesn't stab
    env = np.minimum(tt / 0.02, 1.0) * (0.5 + 0.5 * np.exp(-tt * 1.5))
    x = fade(snow * env * 0.5, fin=0.003, fout=0.08)
    save("tv_static.wav", x)


# --- tv_snap: short soft electrostatic crackle (title letters locking in) ---
def tv_snap():
    d = 0.13
    tt = t(d)
    crackle = bp(rng.standard_normal(len(tt)), 800, 5000)
    env = np.exp(-tt * 28)
    blip = np.sin(2 * np.pi * 1200 * tt) * np.exp(-tt * 40) * 0.25
    x = fade(crackle * env * 0.6 + blip, fin=0.001, fout=0.03)
    save("tv_snap.wav", x)


# --- tv_off: classic descending whine zip + low thud + dot collapse ---------
def tv_off():
    d = 0.6
    tt = t(d)
    # descending whine 2.2 kHz -> 180 Hz over 0.22 s
    sweepdur = 0.22
    k = np.clip(tt / sweepdur, 0, 1)
    f = 2200 * (180 / 2200) ** k
    phase = 2 * np.pi * np.cumsum(f) / SR
    zip_ = np.sin(phase) * np.exp(-tt * 6) * 0.5
    # low thud as the picture collapses
    thud = np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 14) * 0.7
    # final tiny high "ptew" of the dot vanishing
    blip = np.zeros_like(tt)
    s = int(SR * 0.24)
    bt = tt[: len(tt) - s]
    fb = 1600 * (300 / 1600) ** np.clip(bt / 0.05, 0, 1)
    ph = 2 * np.pi * np.cumsum(fb) / SR
    blip[s:] = (np.sin(ph) * np.exp(-bt * 30) * 0.4)[: len(tt) - s]
    x = fade(zip_ + thud + blip, fin=0.001, fout=0.05)
    save("tv_off.wav", x)


if __name__ == "__main__":
    tv_on()
    tv_hum()
    tv_static()
    tv_snap()
    tv_off()
