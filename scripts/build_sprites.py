import os
import math
from collections import deque
from PIL import Image, ImageDraw


def get_asset_path(filename: str) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    target = os.path.join(project_root, filename)
    if os.path.exists(os.path.dirname(target)):
        return target
    return filename


def create_player_spritesheet():
    seed = Image.open(get_asset_path("asset/Player1.png")).convert("RGBA")
    sw, sh = seed.size

    fw, fh = 80, 40
    num_frames = 4
    sheet = Image.new("RGBA", (fw * num_frames, fh), (0, 0, 0, 0))

    ship_x = 18
    ship_y = (fh - sh) // 2

    exhaust_x = ship_x + 1
    exhaust_y = ship_y + sh // 2

    flame_lengths = [6, 12, 17, 11]
    flame_colors_core = [(255, 255, 255, 255), (200, 240, 255, 255), (255, 255, 255, 255), (180, 230, 255, 255)]
    flame_colors_outer = [(46, 204, 113, 220), (52, 152, 219, 240), (41, 128, 185, 250), (26, 188, 156, 230)]

    for i in range(num_frames):
        frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        flen = flame_lengths[i]
        outer_col = flame_colors_outer[i]
        core_col = flame_colors_core[i]

        flame_poly_outer = [
            (exhaust_x, exhaust_y - 4),
            (exhaust_x - flen, exhaust_y),
            (exhaust_x, exhaust_y + 4),
        ]
        draw.polygon(flame_poly_outer, fill=outer_col)

        flame_poly_core = [
            (exhaust_x, exhaust_y - 2),
            (exhaust_x - int(flen * 0.6), exhaust_y),
            (exhaust_x, exhaust_y + 2),
        ]
        draw.polygon(flame_poly_core, fill=core_col)

        frame.paste(seed, (ship_x, ship_y), seed)
        sheet.paste(frame, (i * fw, 0))

    sheet.save(get_asset_path("asset/player_sheet.png"))
    print("Salvo: asset/player_sheet.png")


def create_scout_spritesheet():
    seed = Image.open(get_asset_path("asset/Enemy1.png")).convert("RGBA")
    sw, sh = seed.size

    fw, fh = 100, 48
    num_frames = 4
    sheet = Image.new("RGBA", (fw * num_frames, fh), (0, 0, 0, 0))

    ship_x = 4
    ship_y = (fh - sh) // 2
    exhaust_x = ship_x + sw - 2
    exhaust_y = ship_y + sh // 2

    flame_lengths = [5, 11, 15, 9]

    for i in range(num_frames):
        frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        flen = flame_lengths[i]
        outer_poly = [
            (exhaust_x, exhaust_y - 4),
            (exhaust_x + flen, exhaust_y),
            (exhaust_x, exhaust_y + 4),
        ]
        draw.polygon(outer_poly, fill=(231, 76, 60, 230))

        core_poly = [
            (exhaust_x, exhaust_y - 2),
            (exhaust_x + int(flen * 0.5), exhaust_y),
            (exhaust_x, exhaust_y + 2),
        ]
        draw.polygon(core_poly, fill=(255, 230, 100, 255))

        frame.paste(seed, (ship_x, ship_y), seed)
        sheet.paste(frame, (i * fw, 0))

    sheet.save(get_asset_path("asset/scout_sheet.png"))
    print("Salvo: asset/scout_sheet.png")


def create_cruiser_spritesheet():
    seed = Image.open(get_asset_path("asset/Enemy2.png")).convert("RGBA")
    sw, sh = seed.size

    fw, fh = 112, 54
    num_frames = 4
    sheet = Image.new("RGBA", (fw * num_frames, fh), (0, 0, 0, 0))

    ship_x = 4
    ship_y = (fh - sh) // 2

    exhaust_x = ship_x + sw - 2
    exhaust_y1 = ship_y + sh // 3
    exhaust_y2 = ship_y + (2 * sh) // 3

    flame_lengths = [6, 12, 16, 10]

    for i in range(num_frames):
        frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        flen = flame_lengths[i]
        for ey in [exhaust_y1, exhaust_y2]:
            draw.polygon([(exhaust_x, ey - 3), (exhaust_x + flen, ey), (exhaust_x, ey + 3)], fill=(243, 156, 18, 240))
            draw.polygon([(exhaust_x, ey - 1), (exhaust_x + int(flen * 0.6), ey), (exhaust_x, ey + 1)], fill=(255, 255, 200, 255))

        frame.paste(seed, (ship_x, ship_y), seed)

        alpha = int(140 + 100 * math.sin(i * math.pi / 2))
        core_x = ship_x + sw // 2
        core_y = ship_y + sh // 2
        draw.ellipse([core_x - 3, core_y - 3, core_x + 3, core_y + 3], fill=(230, 50, 50, alpha))

        sheet.paste(frame, (i * fw, 0))

    sheet.save(get_asset_path("asset/cruiser_sheet.png"))
    print("Salvo: asset/cruiser_sheet.png")


def create_explosion_spritesheet():
    fw, fh = 64, 64
    num_frames = 6
    sheet = Image.new("RGBA", (fw * num_frames, fh), (0, 0, 0, 0))

    cx, cy = fw // 2, fh // 2

    radii = [6, 14, 22, 27, 24, 18]
    colors_core = [
        (255, 255, 255, 255),
        (255, 240, 150, 255),
        (255, 180, 50, 240),
        (240, 80, 20, 210),
        (180, 40, 20, 160),
        (80, 20, 20, 90),
    ]

    for i in range(num_frames):
        frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        r = radii[i]
        col = colors_core[i]

        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

        if i >= 1:
            r_in = max(1, r - 5)
            draw.ellipse([cx - r_in, cy - r_in, cx + r_in, cy + r_in], fill=(255, 255, 200, col[3]))

        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg + i * 15)
            spark_dist = r + (i * 3)
            sx = cx + int(spark_dist * math.cos(rad))
            sy = cy + int(spark_dist * math.sin(rad))
            if 0 <= sx < fw and 0 <= sy < fh:
                draw.rectangle([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 200, 50, max(0, 255 - i * 40)))

        sheet.paste(frame, (i * fw, 0))

    sheet.save(get_asset_path("asset/explosion_sheet.png"))
    print("Salvo: asset/explosion_sheet.png")


def create_boss_spritesheet():
    raw_path = get_asset_path("asset/boss_raw.jpg")
    if not os.path.exists(raw_path):
        raw_path = r"C:\Users\dev\.gemini\antigravity\brain\ed0b5764-64ee-41f2-9bae-495ec637bbe1\boss_sprite_sheet_1791819113294.jpg"

    if os.path.exists(raw_path):
        raw = Image.open(raw_path).convert("RGB")
        w_total, h_total = raw.size
        half_w, half_h = w_total // 2, h_total // 2

        quadrants = [
            raw.crop((0, 0, half_w, half_h)),
            raw.crop((half_w, 0, w_total, half_h)),
            raw.crop((0, half_h, half_w, h_total)),
            raw.crop((half_w, half_h, w_total, h_total)),
        ]

        def remove_checkerboard(img):
            rgba = img.convert("RGBA")
            w, h = rgba.size
            pix = rgba.load()
            visited = set()
            queue = deque()

            for x in range(w):
                queue.append((x, 0))
                queue.append((x, h - 1))
            for y in range(h):
                queue.append((0, y))
                queue.append((w - 1, y))

            def is_checkerboard(r, g, b):
                return abs(r - g) <= 10 and abs(g - b) <= 10 and abs(r - b) <= 10 and r >= 140

            while queue:
                cx, cy = queue.popleft()
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))

                r, g, b, a = pix[cx, cy]
                if is_checkerboard(r, g, b):
                    pix[cx, cy] = (0, 0, 0, 0)
                    for nx, ny in [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]:
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                            queue.append((nx, ny))

            return rgba

        cleaned_frames = [remove_checkerboard(q) for q in quadrants]

        frame_w = 170
        frame_h = 92
        num_frames = 4

        anchor_bbox = cleaned_frames[0].getbbox()
        anchor_w = anchor_bbox[2] - anchor_bbox[0] if anchor_bbox else 500
        global_scale = 135.0 / float(anchor_w)

        sheet = Image.new("RGBA", (frame_w * num_frames, frame_h), (0, 0, 0, 0))

        for i, frame in enumerate(cleaned_frames):
            new_w = int(frame.width * global_scale)
            new_h = int(frame.height * global_scale)
            scaled_frame = frame.resize((new_w, new_h), Image.Resampling.LANCZOS)
            scaled_frame = scaled_frame.transpose(Image.FLIP_LEFT_RIGHT)

            out_frame = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
            crop_box = scaled_frame.getbbox()
            if crop_box:
                cropped = scaled_frame.crop(crop_box)
                paste_x = (frame_w - cropped.width) // 2
                paste_y = (frame_h - cropped.height) // 2
                out_frame.paste(cropped, (paste_x, paste_y), cropped)
            else:
                out_frame.paste(scaled_frame, (0, 0), scaled_frame)

            sheet.paste(out_frame, (i * frame_w, 0), out_frame)

        sheet.save(get_asset_path("asset/boss_sheet.png"))
        print("Salvo: asset/boss_sheet.png")


if __name__ == "__main__":
    create_player_spritesheet()
    create_scout_spritesheet()
    create_cruiser_spritesheet()
    create_explosion_spritesheet()
    create_boss_spritesheet()
    print("Todos os spritesheets foram gerados com sucesso!")
