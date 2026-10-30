# Те же синие обои в стиле PS5, что и на планшете, но под экран компьютера (размер берётся из config).
# Квадратный SVG из make_ps.py растягивается на весь экран с обрезкой краёв (slice).
import os
from make_ps import wall_svg, shot, BUILD

HERE = os.path.dirname(os.path.abspath(__file__))
from config import SCREEN_W as W, SCREEN_H as H  # обои под настоящий размер экрана

def main():
    os.makedirs(BUILD, exist_ok=True)
    svg = wall_svg().replace('width="2000" height="2000"', 'width="100%" height="100%" preserveAspectRatio="xMidYMid slice"', 1)
    out = os.path.join(HERE, "markiz_blue_pc.png")
    shot(f'<html><body style="margin:0;width:{W}px;height:{H}px;background:#000">{svg}</body></html>', out, W, H)
    print(out)

if __name__ == "__main__":
    main()
