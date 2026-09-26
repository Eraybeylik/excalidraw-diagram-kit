"""Active Directory logical structure: forest > domain > containers / OUs > objects (nested-box tree)."""
from exdraw import BLUE, GRAY, GREEN, LINE, MUTED, ORANGE, PURPLE, RED, TEXT, YELLOW, Scene

PRIV = {"stroke": RED.stroke}


def build():
    s = Scene("Active Directory: mantıksal yapı",
              "Domain Controller'daki dizin veritabanının içi: forest → domain → container / OU → nesneler")

    s.rect(20, 96, 820, 1068, PURPLE, dashed=True, soft=True)
    s.inline(40, 126, [("FOREST", 13, PURPLE.stroke, False), ("   example.internal", 18, TEXT, False)])
    s.text(40, 148, "En dış güvenlik sınırı; tüm domain'ler aynı schema'yı paylaşır.", 14, MUTED)

    s.rect(40, 164, 780, 984, PURPLE, soft=True)
    s.inline(60, 194, [("DOMAIN", 13, PURPLE.stroke, False), ("   example.internal", 18, TEXT, False),
                       ("   NetBIOS: EXAMPLE", 14, MUTED, False)])
    s.text(60, 218, "DN: DC=example,DC=internal", 14, mono=True)
    s.text(60, 240, "SID: S-1-5-21-1111111111-2222222222-3333333333", 14, MUTED, mono=True)
    w = s.chip(60, 254, "GPO: Default Domain Policy", YELLOW)
    s.text(60 + w + 14, 273, "parola politikası burada tanımlanır", 14, MUTED)

    trunk, cx, cw, mids = 76, 100, 700, []

    def node(y, h, name, kind, desc):
        ou = kind == "OU"
        s.rect(cx, y, cw, h, PURPLE if ou else GRAY, dashed=not ou, soft=True)
        s.inline(cx + 18, y + 27, [(name, 17, TEXT, False), ("   " + kind, 13, (PURPLE if ou else GRAY).stroke, False),
                                   ("  ·  " + desc, 14, MUTED, False)])
        mids.append(y + 21)

    node(296, 84, "Builtin", "container", "domain'in yerleşik yerel grupları")
    s.chips(cx + 18, 338, [("Administrators", ORANGE), ("Users", ORANGE), ("Remote Desktop Users", ORANGE),
                           ("Backup Operators", ORANGE), ("…", GRAY)])
    node(394, 74, "Computers", "container", "domain'e katılan makinelerin varsayılan yeri")
    s.text(cx + 18, 450, "Join sırasında -OUPath verilirse makine doğrudan hedef OU'ya gider.", 14, MUTED)
    node(482, 162, "Users", "container", "yerleşik hesaplar ve gruplar")
    s.chips(cx + 18, 522, [("Administrator · RID 500", GREEN, PRIV), ("Guest · 501 · kapalı", GRAY),
                           ("krbtgt · 502 · kapalı", GREEN, PRIV)])
    s.chips(cx + 18, 560, [("Domain Admins · 512", ORANGE, PRIV), ("Domain Users · 513", ORANGE),
                           ("Domain Computers · 515", ORANGE)])
    s.chips(cx + 18, 598, [("Enterprise Admins · 519", ORANGE, PRIV), ("Schema Admins · 518", ORANGE, PRIV),
                           ("Domain Controllers · 516", ORANGE)])
    node(658, 90, "Domain Controllers", "OU", "DC'ler burada kalmalı")
    x = s.chips(cx + 18, 698, [("DC01 · 10.0.0.20", BLUE)])
    s.chip(x, 698, "GPO: Default Domain Controllers Policy", YELLOW)

    ly, sub_x, sub_w, st, subs = 762, cx + 60, cw - 78, cx + 34, []
    node(ly, 372, "Corp", "OU", "kurumun kendi yapısı")

    def sub(y, h, name, desc):
        s.rect(sub_x, y, sub_w, h, PURPLE)
        s.inline(sub_x + 16, y + 26, [(name, 16, TEXT, False), ("   OU", 13, PURPLE.stroke, False),
                                      ("  ·  " + desc, 14, MUTED, False)])
        subs.append(y + 20)

    sub(ly + 44, 76, "Users", "günlük iş hesapları + iş grupları")
    x = s.chips(sub_x + 16, ly + 78, [("alice", GREEN), ("bob", GREEN), ("carol", GREEN)])
    s.chip(x + 8, ly + 78, "Finance (grup) · üye: bob", ORANGE)
    sub(ly + 132, 76, "Admins", "ayrı yönetim hesapları (tiering)")
    x = s.chips(sub_x + 16, ly + 166, [("adm-alice", GREEN, PRIV)])
    s.text(x + 4, ly + 185, "Domain Admins üyesi", 14, RED.stroke)
    sub(ly + 220, 76, "Workstations", "domain'e katılan istemciler")
    s.chips(sub_x + 16, ly + 254, [("WS01 · 10.0.0.30", BLUE)])
    sub(ly + 308, 50, "Servers", "domain üyesi sunucular")
    s.line([(st, ly + 42), (st, subs[-1])], PURPLE.stroke, opacity=0.7)
    for m in subs:
        s.line([(st, m), (sub_x, m)], PURPLE.stroke, opacity=0.7)
    s.line([(trunk, 282), (trunk, mids[-1])], LINE, width=2)
    for m in mids:
        s.line([(trunk, m), (cx, m)], LINE, width=2)

    s.legend(40, 1180, title="Gösterim", items=[
        ("box", PURPLE, "OU: GPO bağlanır"), ("dashed-box", GRAY, "container: GPO bağlanamaz"),
        ("chip", GREEN, "kullanıcı"), ("chip", BLUE, "bilgisayar"), ("chip", ORANGE, "grup"),
        ("chip", YELLOW, "GPO"), ("dashed-box", RED, "kırmızı çerçeve = ayrıcalıklı"),
    ])
    return s


if __name__ == "__main__":
    build().save("examples/output/ad_hierarchy.excalidraw")
