"""Simple firework particle simulation."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class Particle:
    """A particle emitted by a firework explosion."""

    x: float
    y: float
    vx: float
    vy: float
    color: str


def _random_color(rng: random.Random) -> str:
    palette = ("red", "gold", "blue", "green", "purple", "white")
    return rng.choice(palette)


def explode(
    center: Tuple[float, float],
    count: int = 30,
    speed: float = 5.0,
    seed: int | None = None,
) -> List[Particle]:
    """Create a burst of particles originating from ``center``."""

    rng = random.Random(seed)
    cx, cy = center
    particles = []
    for _ in range(count):
        angle = rng.uniform(0.0, 2.0 * math.pi)
        magnitude = rng.uniform(0.4, 1.0) * speed
        particles.append(
            Particle(
                x=cx,
                y=cy,
                vx=math.cos(angle) * magnitude,
                vy=math.sin(angle) * magnitude,
                color=_random_color(rng),
            )
        )
    return particles


def step(
    particles: Iterable[Particle],
    dt: float = 0.1,
    gravity: float = -9.81,
) -> List[Particle]:
    """Advance particles by ``dt`` seconds with a constant gravity term."""

    updated: List[Particle] = []
    for particle in particles:
        vx = particle.vx
        vy = particle.vy + gravity * dt
        updated.append(
            Particle(
                x=particle.x + vx * dt,
                y=particle.y + vy * dt,
                vx=vx,
                vy=vy,
                color=particle.color,
            )
        )
    return updated


def simulate_firework(
    origin: Tuple[float, float] = (0.0, 0.0),
    steps: int = 10,
    count: int = 30,
    speed: float = 5.0,
    seed: int | None = None,
) -> List[List[Particle]]:
    """Run a small firework simulation and return particle positions per step."""

    frames: List[List[Particle]] = []
    particles = explode(origin, count=count, speed=speed, seed=seed)
    frames.append(particles)
    for _ in range(steps - 1):
        particles = step(particles)
        frames.append(particles)
    return frames


if __name__ == "__main__":
    demo = simulate_firework(seed=7)
    last = demo[-1]
    for particle in last[:5]:
        print(
            f"{particle.color} particle at ({particle.x:.2f}, {particle.y:.2f})"
        )
