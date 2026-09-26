"""Langley's adventitious angles (1922): find ∠BDE in the 80-80-20 triangle."""
import math

from exdraw import BLUE, GREEN, ORANGE, PURPLE, RED, TEXT, YELLOW, Scene, callout, steps


def _dir(deg):
    return math.cos(math.radians(deg)), math.sin(math.radians(deg))


def _intersect(p, d1, q, d2):
    det = d1[0] * -d2[1] - d1[1] * -d2[0]
    t = ((q[0] - p[0]) * -d2[1] - (q[1] - p[1]) * -d2[0]) / det
    return p[0] + t * d1[0], p[1] + t * d1[1]


def build():
    s = Scene("Langley problemi: 80-80-20 üçgeni",
              "Sadece açı takibiyle çıkmayan ünlü problem; çözüm tek bir yardımcı noktaya dayanıyor")

    # Geometry in unit coordinates (B at origin, BC = 1), then mapped to pixels.
    B, C = (0.0, 0.0), (1.0, 0.0)
    A = (0.5, 0.5 * math.tan(math.radians(80)))
    AB, AC = (A[0] - B[0], A[1] - B[1]), (A[0] - C[0], A[1] - C[1])
    E = _intersect(C, _dir(130), B, AB)   # ∠ECB = 50°
    D = _intersect(B, _dir(60), C, AC)    # ∠DBC = 60°
    F = _intersect(B, _dir(20), C, AC)    # auxiliary: ∠FBC = 20°

    unit, ox, oy = 150, 110, 700

    def px(p):
        return ox + p[0] * unit, oy - p[1] * unit

    s.polygon([px(A), px(B), px(C)], PURPLE, width=2)
    s.line([px(B), px(D)], BLUE.stroke, width=2)
    s.line([px(C), px(E)], BLUE.stroke, width=2)
    s.line([px(B), px(F)], ORANGE.stroke, dashed=True, width=2)
    s.line([px(E), px(F)], ORANGE.stroke, dashed=True, width=2)
    s.line([px(D), px(E)], RED.stroke, width=3)
    for name, p, dx, dy in [("A", A, -6, -12), ("B", B, -24, 18), ("C", C, 10, 18), ("D", D, 12, 4),
                            ("E", E, -26, 4), ("F", F, 12, 10)]:
        x, y = px(p)
        s.dot(x, y, TEXT, r=4)
        s.text(x + dx, y + dy, name, 18)
    for t, (x, y), color in [("20°", (px(A)[0] - 11, px(A)[1] + 44), PURPLE.stroke),
                             ("60°", (px(B)[0] + 22, px(B)[1] - 30), BLUE.stroke),
                             ("20°", (px(B)[0] + 44, px(B)[1] - 6), ORANGE.stroke),
                             ("50°", (px(C)[0] - 48, px(C)[1] - 8), BLUE.stroke),
                             ("x = ?", (px(D)[0] - 64, px(D)[1] + 8), RED.stroke)]:
        s.text(x, y, t, 14, color)

    callout(s, 32, 100, 340, "Problem", "ABC ikizkenar, ∠A = 20°, ∠B = ∠C = 80°. D ∈ AC ile ∠DBC = 60°, "
            "E ∈ AB ile ∠ECB = 50°. ∠BDE kaç derece?", YELLOW)

    y = steps(s, 400, 100, 460, [
        ("F ∈ AC noktasını ∠FBC = 20° olacak şekilde seç (yardımcı nokta).",
         ["△BCF: 20° + 80° + 80°  →  BF = BC"]),
        ("△BCE'de ∠EBC = 80°, ∠ECB = 50°, kalan açı da 50°.",
         ["∠BEC = 50°  →  BE = BC"]),
        ("BE = BC = BF ve aradaki açı 80° − 20° = 60°.",
         ["△BEF eşkenar  →  EF = BF"]),
        ("△BFD'de ∠FBD = 60° − 20° = 40°, ∠BFD = 180° − 80° = 100°.",
         ["∠BDF = 40°  →  FD = FB"]),
        ("FD = FB = FE, yani △FDE ikizkenar; tepe açısı 100° − 60°.",
         ["∠EFD = 40°  →  ∠FDE = (180° − 40°) / 2 = 70°"]),
        ("İstenen açı, iki açının farkı:",
         ["∠BDE = ∠FDE − ∠FDB = 70° − 40° = 30°"]),
    ], BLUE)
    y = callout(s, 400, y + 6, 460, "Sonuç: ∠BDE = 30°",
                "Anahtar fikir: BC'ye eşit uzunlukları (BE, BF, FD, FE) zincirleyip eşkenar ve ikizkenar "
                "üçgenlere dönüştürmek.", GREEN)
    s.legend(32, max(y, 730) + 20, title="Gösterim", items=[
        ("box", PURPLE, "verilen üçgen"), ("arrow", BLUE.stroke, "verilen doğrular"),
        ("dashed-arrow", ORANGE.stroke, "yardımcı yapı (F)"), ("arrow", RED.stroke, "aranan: DE"),
    ])
    return s


if __name__ == "__main__":
    build().save("examples/output/math_langley.excalidraw")
