from __future__ import annotations

import math
import random
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RATE = 44_100
DURATION_SECONDS = 6.0


def envelope(time: float, start: float, attack: float, release: float) -> float:
    if time < start:
        return 0.0
    age = time - start
    if age < attack:
        return age / attack
    if age < attack + release:
        return 1.0 - (age - attack) / release
    return 0.0


def main() -> None:
    rng = random.Random(20260609)
    samples: list[int] = []
    total = int(SAMPLE_RATE * DURATION_SECONDS)
    noise_state = 0.0

    for index in range(total):
        time = index / SAMPLE_RATE
        loop_phase = time / DURATION_SECONDS
        hum = 0.18 * math.sin(math.tau * 62 * time)
        hum += 0.08 * math.sin(math.tau * 124 * time + 0.4)
        power_wobble = 0.75 + 0.25 * math.sin(math.tau * 0.17 * time)

        scanner = 0.0
        for start in (1.05, 2.15, 3.15, 4.2):
            scanner += envelope(time, start, 0.08, 0.45) * math.sin(math.tau * (540 + 120 * math.sin(time * 2.0)) * time)

        dome_pulse = envelope(time, 2.0, 0.35, 1.4) + envelope(time, 3.3, 0.25, 1.1)
        dome = dome_pulse * (0.12 * math.sin(math.tau * 280 * time) + 0.07 * math.sin(math.tau * 405 * time))

        noise_state = noise_state * 0.86 + (rng.random() * 2 - 1) * 0.14
        steam = (envelope(time, 3.7, 0.05, 0.9) + envelope(time, 4.7, 0.05, 0.75)) * noise_state * 0.32

        click = 0.0
        for start in (0.6, 1.8, 2.85, 5.15):
            click += envelope(time, start, 0.006, 0.08) * math.sin(math.tau * 1_600 * time)

        fade = min(1.0, time / 0.08, (DURATION_SECONDS - time) / 0.08)
        sample = (hum * power_wobble + scanner * 0.07 + dome + steam + click * 0.08) * fade
        sample = max(-0.92, min(0.92, sample))
        samples.append(int(sample * 32767))

    sound_dir = ROOT / "sound"
    sound_dir.mkdir(parents=True, exist_ok=True)
    wav_path = sound_dir / "interstellar-lab-working.wav"
    with wave.open(str(wav_path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(b"".join(sample.to_bytes(2, "little", signed=True) for sample in samples))

    print(wav_path)


if __name__ == "__main__":
    main()
