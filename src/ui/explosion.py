import random
import pygame
from src.infrastructure.utils import load_spritesheet


class AnimatedExplosion(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int):
        super().__init__()
        self.frames = load_spritesheet("asset/explosion_sheet.png", 64, 64)
        self.current_frame = 0
        self.image = self.frames[0] if self.frames else pygame.Surface((64, 64), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.animation_timer = pygame.time.get_ticks()
        self.frame_delay = 45

    def update(self) -> None:
        now = pygame.time.get_ticks()
        if now - self.animation_timer >= self.frame_delay:
            self.animation_timer = now
            self.current_frame += 1
            if self.current_frame < len(self.frames):
                self.image = self.frames[self.current_frame]
            else:
                self.kill()


class Particle:

    def __init__(self, x: float, y: float, color: tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4.0, 4.0)
        self.vy = random.uniform(-4.0, 4.0)
        self.radius = random.uniform(2.0, 5.0)
        self.life = random.randint(15, 30)
        self.color = color

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.radius = max(0.5, self.radius * 0.93)
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius))


class ParticleSystem:

    def __init__(self):
        self.particles: list[Particle] = []

    def create_explosion(self, x: float, y: float, count: int = 18, color_palette: list[tuple[int, int, int]] | None = None) -> None:
        if color_palette is None:
            color_palette = [
                (255, 100, 20),
                (255, 200, 40),
                (255, 60, 20),
                (255, 255, 255),
            ]

        for _ in range(count):
            color = random.choice(color_palette)
            self.particles.append(Particle(x, y, color))

    def update(self) -> None:
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            p.draw(surface)

    def clear(self) -> None:
        self.particles.clear()
