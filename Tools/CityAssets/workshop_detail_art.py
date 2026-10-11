"""Create original workshop labels and copy attributed existing wood maps."""
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/City/WorkshopDetail/Textures'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wood = OUT / 'Wood'
    wood.mkdir(exist_ok=True)
    for name in ('color', 'normal', 'roughness'):
        shutil.copy2(ROOT / f'Assets/City/InteriorArchitecture/Textures/Oak/{name}.png', wood / f'{name}.png')
    image = Image.new('RGB', (2048, 1024), (207, 199, 172))
    draw = ImageDraw.Draw(image)
    font_path = 'C:/Windows/Fonts/consolab.ttf'
    def text(pos, message, size, fill=(32, 40, 38)):
        draw.text(pos, message, font=ImageFont.truetype(font_path, size), fill=fill)
    draw.rectangle((14, 14, 2033, 239), outline=(46, 59, 57), width=8)
    text((62, 48), 'ANANTA  /  SERVICE TOOLS', 116)
    draw.rectangle((0, 256, 2047, 511), fill=(44, 55, 54))
    text((52, 319), '10  12  13  14  15  17  19  21  22  24', 74, (211, 200, 163))
    draw.rectangle((26, 537, 2020, 997), outline=(37, 45, 40), width=11)
    text((80, 563), 'ANANTA  /  SERVICE DEPOT', 87)
    draw.line((80, 678, 1964, 678), fill=(37, 45, 40), width=7)
    text((80, 700), 'MECHANICAL PARTS', 118)
    text((80, 845), 'LOT 024-C   |   QTY 12   |   KEEP DRY', 64)
    for x in range(1540, 1930, 11):
        draw.rectangle((x, 938, x + (3 if x % 3 else 7), 976), fill=(37, 45, 40))
    title = Image.new('RGB', (2048, 68), (207, 199, 172))
    td = ImageDraw.Draw(title)
    td.rectangle((3, 3, 2044, 64), outline=(46, 59, 57), width=2)
    td.text((72, -3), 'ANANTA / SERVICE TOOLS / METRIC SET 01',
            font=ImageFont.truetype(font_path, 64), fill=(32, 40, 38))
    image.paste(title.resize((2048, 256), Image.Resampling.LANCZOS), (0, 0))
    sizes = Image.new('RGB', (2048, 64), (44, 55, 54))
    sd = ImageDraw.Draw(sizes)
    sd.text((65, -5), '10   12   13   14   15   17   19   21   22   24',
            font=ImageFont.truetype(font_path, 62), fill=(211, 200, 163))
    image.paste(sizes.resize((2048, 256), Image.Resampling.LANCZOS), (0, 256))
    image.save(OUT / 'WorkshopLabels.png')


if __name__ == '__main__':
    main()
