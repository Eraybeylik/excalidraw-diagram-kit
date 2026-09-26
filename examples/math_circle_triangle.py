"""Three uniform random points on a circle: probability their triangle contains the center (= 1/4)."""
import math

from exdraw import GRAY, GREEN, PURPLE, RED, TEXT, YELLOW, Scene, callout, steps


def _circle_figure(s, cx, cy, r, angles, color, caption, half_start=None):
    s.ellipse(cx, cy, r, color=GRAY, width=2)
    if half_start is not None:
        a0 = math.radians(half_start)
        arc = [(cx + r * math.cos(a0 + math.pi * t / 30), cy - r * math.sin(a0 + math.pi * t / 30))
               for t in range(31)]
        s.line(arc, RED.stroke, width=6, opacity=0.45)
        s.line([arc[0], arc[-1]], RED.stroke, dashed=True, width=1.5)
    pts = [(cx + r * math.cos(math.radians(a)), cy - r * math.sin(math.radians(a))) for a in angles]
    s.polygon(pts, color, fill=color.fill, width=2)
    for i, (x, y) in enumerate(pts, 1):
        s.dot(x, y, TEXT, r=5)
        s.text(x + (x - cx) * 0.18, y + (y - cy) * 0.18 + 5, f"P{i}", 14, align="center")
    s.dot(cx, cy, PURPLE.stroke, r=5)
    s.text(cx + 8, cy - 8, "O", 14, PURPLE.stroke)
    s.text(cx, cy + r + 40, caption, 14, color.stroke, align="center")


def build():
    s = Scene("Çemberde üç rastgele nokta", "Oluşan üçgenin çemberin merkezini içerme olasılığı")
    callout(s, 32, 100, 820, "Problem",
            "Bir çemberin üzerine bağımsız ve düzgün dağılımla üç nokta seçiliyor. Bu üç noktanın "
            "oluşturduğu üçgenin, çemberin merkezi O'yu içerme olasılığı nedir?", YELLOW)

    _circle_figure(s, 240, 355, 115, [100, 225, 330], GREEN, "O içeride: noktalar yarım çembere sığmıyor")
    _circle_figure(s, 640, 355, 115, [20, 75, 150], RED, "O dışarıda: hepsi bir yarım çemberde",
                   half_start=10)

    y = steps(s, 32, 545, 820, [
        ("Merkez üçgenin içindeyse, üç nokta hiçbir yarım çembere birlikte sığmaz; tersi de doğru.",
         ["O ∈ üçgen  ⇔  noktalar ortak bir yarım çemberde değil"]),
        ("Her i için A(i) olayı: diğer iki nokta, Pi'den saat yönünün tersine başlayan yarım çemberde. "
         "Diğer iki nokta bağımsız, her biri 1/2 olasılıkla o yarım çemberde.",
         ["P(A(i)) = (1/2)·(1/2) = 1/4"]),
        ("Noktalar ortak bir yarım çemberdeyse o yarım çemberin 'ilk' noktası tektir, yani A(1), A(2), "
         "A(3) ayrık olaylardır (eşit açılar olasılık 0).",
         ["P(hepsi bir yarım çemberde) = 3 · 1/4 = 3/4"]),
        ("Merkezi içerme olasılığı tümleyendir.", ["P(O ∈ üçgen) = 1 − 3/4 = 1/4"]),
    ], PURPLE)
    y = callout(s, 32, y + 6, 820, "Sonuç: 1/4",
                ["Aynı argüman n nokta için: P(hepsi bir yarım çemberde) = n / 2^(n−1) (Wendel, 1962).",
                 "Genelleme: kürede 4 nokta için tetrahedronun merkezi içerme olasılığı 1/8 (Putnam 1992 A6)."],
                GREEN)
    s.legend(32, y + 16, title="Gösterim", items=[
        ("box", GREEN, "merkezi içeren üçgen"), ("box", RED, "merkezi içermeyen üçgen"),
        ("arrow", RED.stroke, "noktaları kapsayan yarım çember"),
    ])
    return s


if __name__ == "__main__":
    build().save("examples/output/math_circle_triangle.excalidraw")
