import os
import sys
import pygame


def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        path_next_to_exe = os.path.join(exe_dir, relative_path)
        if os.path.exists(path_next_to_exe):
            return path_next_to_exe

        parent_dir = os.path.dirname(exe_dir)
        path_in_parent = os.path.join(parent_dir, relative_path)
        if os.path.exists(path_in_parent):
            return path_in_parent

        meipass_dir = getattr(sys, '_MEIPASS', exe_dir)
        path_in_meipass = os.path.join(meipass_dir, relative_path)
        if os.path.exists(path_in_meipass):
            return path_in_meipass

    script_dir = os.path.dirname(os.path.abspath(__file__))
    path_next_to_script = os.path.join(script_dir, relative_path)
    if os.path.exists(path_next_to_script):
        return path_next_to_script

    project_root = os.path.dirname(os.path.dirname(script_dir))
    path_in_project = os.path.join(project_root, relative_path)
    if os.path.exists(path_in_project):
        return path_in_project

    return os.path.join(project_root, relative_path)


def load_image(relative_path: str, scale_size: tuple[int, int] | None = None) -> pygame.Surface:
    full_path = resource_path(relative_path)
    try:
        image = pygame.image.load(full_path).convert_alpha()
        if scale_size is not None:
            image = pygame.transform.scale(image, scale_size)
        return image
    except Exception:
        fallback_size = scale_size if scale_size else (40, 40)
        surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
        surf.fill((255, 0, 255, 200))
        return surf


def play_music(relative_path: str, loop: int = -1, volume: float = 0.6) -> None:
    full_path = resource_path(relative_path)
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loop)
    except Exception:
        pass


def play_sound(relative_path: str, volume: float = 0.5) -> None:
    full_path = resource_path(relative_path)
    try:
        if pygame.mixer.get_init():
            sound = pygame.mixer.Sound(full_path)
            sound.set_volume(volume)
            sound.play()
    except Exception:
        pass


def load_spritesheet(
    relative_path: str,
    frame_width: int,
    frame_height: int,
    scale_size: tuple[int, int] | None = None,
) -> list[pygame.Surface]:
    sheet = load_image(relative_path)
    sheet_w, sheet_h = sheet.get_size()
    num_frames = max(1, sheet_w // frame_width)

    frames: list[pygame.Surface] = []
    for i in range(num_frames):
        rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame_surface.blit(sheet, (0, 0), rect)

        if scale_size is not None:
            frame_surface = pygame.transform.scale(frame_surface, scale_size)

        frames.append(frame_surface)

    return frames
