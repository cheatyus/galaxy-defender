import os
import math
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
    seed = Image.open(get_asset_path("asset/Enemy2.png")).convert("RGBA")
    boss_hull = seed.resize((140, 70), Image.Resampling.NEAREST)
    bw, bh = boss_hull.size

    fw, fh = 160, 90
    num_frames = 4
    sheet = Image.new("RGBA", (fw * num_frames, fh), (0, 0, 0, 0))

    ship_x = 8
    ship_y = (fh - bh) // 2

    engine_y_positions = [ship_y + 12, ship_y + bh // 2, ship_y + bh - 12]
    exhaust_x = ship_x + bw - 4

    flame_lengths = [10, 18, 25, 15]

    for i in range(num_frames):
        frame = Image.new("RGBA", (fw, fh), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)

        flen = flame_lengths[i]
        for ey in engine_y_positions:
            draw.polygon(
                [(exhaust_x, ey - 5), (exhaust_x + flen, ey), (exhaust_x, ey + 5)],
                fill=(155, 89, 182, 240),
            )
            draw.polygon(
                [(exhaust_x, ey - 2), (exhaust_x + int(flen * 0.6), ey), (exhaust_x, ey + 2)],
                fill=(241, 196, 15, 255),
            )

        frame.paste(boss_hull, (ship_x, ship_y), boss_hull)

        shield_alpha = int(90 + 60 * math.sin(i * math.pi / 2))
        draw.ellipse([ship_x - 6, ship_y - 6, ship_x + bw + 6, ship_y + bh + 6], outline=(142, 68, 173, shield_alpha), width=2)

        core_x = ship_x + bw // 2
        core_y = ship_y + bh // 2
        core_radius = 5 + int(2 * math.sin(i * math.pi / 2))
        draw.ellipse(
            [core_x - core_radius, core_y - core_radius, core_x + core_radius, core_y + core_radius],
            fill=(231, 76, 60, 255),
        )

        sheet.paste(frame, (i * fw, 0))

    sheet.save(get_asset_path("asset/boss_sheet.png"))
    print("Salvo: asset/boss_sheet.png")


if __name__ == "__main__":
    create_player_spritesheet()
    create_scout_spritesheet()
    create_cruiser_spritesheet()
    create_explosion_spritesheet()
    create_boss_spritesheet()
    print("Todos os spritesheets foram gerados com sucesso!")
