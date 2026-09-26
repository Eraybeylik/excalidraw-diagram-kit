"""Buffon's needle: probability that a needle of length l <= d crosses one of the parallel lines."""
import math

from exdraw import BG, BLUE, GRAY, GREEN, MUTED, RED, TEAL, TEXT, YELLOW, Scene, callout, steps


def build():
    s = Scene("Buffon'un iğnesi", "Rastgele atılan bir iğneden π nasıl çıkar?")
    top = callout(s, 32, 100, 400, "Problem",
            "Aralarında d mesafe olan paralel çizgilerin üzerine l ≤ d uzunluğunda bir iğne rastgele "
            "atılıyor. İğnenin bir çizgiyi kesme olasılığı nedir?", YELLOW)

    # --- figure 1: the floor with needles (d = 80 px, l = 70 px)
    fx, fy, fw, d, length = 32, top + 34, 400, 80, 70
    for i in range(4):
        s.line([(fx, fy + i * d), (fx + fw, fy + i * d)], TEXT, width=2)
    s.text(fx + fw + 8, fy + d / 2 + 5, "d", 16, MUTED)
    s.arrow([(fx + fw - 6, fy + 2), (fx + fw - 6, fy + d - 2)], MUTED, width=1.4, start=True)
    needles = [(40, 40, 60), (115, 22, 100), (150, 125, 20), (60, 150, 140), (205, 60, 170),
               (240, 195, 75), (95, 215, 30), (355, 38, 120), (365, 200, 10), (185, 170, 110)]
    for ox, oy, deg in needles:
        cx, cy, theta = fx + ox, fy + oy, math.radians(deg)
        dx, dy = length / 2 * math.cos(theta), length / 2 * math.sin(theta)
        y1, y2 = cy - dy, cy + dy
        crosses = any(min(y1, y2) <= fy + k * d <= max(y1, y2) for k in range(4))
        s.line([(cx - dx, y1), (cx + dx, y2)], (RED if crosses else GRAY).stroke, width=2.5)
    # highlighted needle with x and θ
    mx, my, th = fx + 300, fy + d + 26, math.radians(38)
    hx, hy = length / 2 * math.cos(th), length / 2 * math.sin(th)
    s.line([(mx - hx, my + hy), (mx + hx, my - hy)], BLUE.stroke, width=3.5)
    s.dot(mx, my, BLUE.stroke, r=4)
    s.line([(mx, my), (mx, fy + d)], TEAL.stroke, dashed=True, width=1.8)
    s.text(mx + 6, my - 8, "x", 15, TEAL.stroke)
    s.text(mx + 26, my + 2, "θ", 15, BLUE.stroke)
    s.text(fx, fy + 3 * d + 30, "kırmızı: çizgiyi kesen iğne · gri: kesmeyen", 13, MUTED)

    # --- figure 2: sample space (θ, x) with the crossing region under x = (l/2)·sin θ (here l = d)
    gx, gy, gw, gh = 70, fy + 3 * d + 90, 330, 170
    s.rect(gx, gy, gw, gh, GRAY, fill=BG, rounded=False)
    curve = [(gx + gw * t / 40, gy + gh - gh * math.sin(math.pi / 2 * t / 40)) for t in range(41)]
    s.polygon(curve + [(gx + gw, gy + gh), (gx, gy + gh)], GREEN, fill=GREEN.fill, width=2)
    s.text(gx + gw / 2, gy + gh + 24, "θ: 0 → π/2", 13, MUTED, align="center")
    s.rotated_text(gx - 22, gy + gh / 2, "x: 0 → d/2", 13, MUTED)
    s.text(gx + gw * 0.55, gy + gh * 0.72, "kesişim bölgesi", 13, GREEN.stroke)
    s.text(gx + 12, gy + 22, "x = (l/2)·sin θ", 13, GREEN.stroke, mono=True)
    s.text(32, gy - 14, "Örnek uzayı (l = d için)", 14, MUTED)

    y = steps(s, 460, 100, 420, [
        ("İki rastgele değişken: iğnenin ortasının en yakın çizgiye uzaklığı ve iğnenin çizgilerle "
         "yaptığı dar açı.", ["x ~ U[0, d/2]    θ ~ U[0, π/2]"]),
        ("İğnenin dikey yarı-boyu x'ten büyükse iğne çizgiyi keser.", ["kesişim ⇔ x ≤ (l/2)·sin θ"]),
        ("x ve θ bağımsız ve düzgün; ortak yoğunluk sabit.", ["f(x, θ) = (2/d)·(2/π) = 4/(πd)"]),
        ("Olasılık, kesişim bölgesi üzerindeki integraldir.",
         ["P = ∫₀^(π/2) ∫₀^((l/2)sin θ) 4/(πd) dx dθ"]),
        ("İç integral (l/2)·sin θ verir; ∫ sin θ dθ = 1.", ["P = (4/(πd))·(l/2)·1 = 2l/(πd)"]),
    ], BLUE)
    y = callout(s, 460, y + 6, 420, "Sonuç: P = 2l / (πd)",
                ["l = d ise P = 2/π ≈ 0.637.",
                 "n iğne atıp k tanesi keserse: π ≈ 2n / k. Rastgelelikle π tahmin etmek, Monte Carlo "
                 "yönteminin ilk örneklerinden biri."], GREEN)
    s.legend(32, max(y, 790) + 16, title="Gösterim", items=[
        ("arrow", RED.stroke, "çizgiyi kesen iğne"), ("arrow", GRAY.stroke, "kesmeyen iğne"),
        ("arrow", BLUE.stroke, "incelenen iğne"), ("dashed-arrow", TEAL.stroke, "x uzaklığı"),
        ("box", GREEN, "kesişim olasılığı = alan"),
    ])
    return s


if __name__ == "__main__":
    build().save("examples/output/math_buffon.excalidraw")
