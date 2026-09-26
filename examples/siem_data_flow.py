"""Windows event logs → Universal Forwarder → Splunk indexes (grouped boxes + labeled flows)."""
from exdraw import BLUE, GRAY, GREEN, MUTED, ORANGE, PURPLE, TEAL, TEXT, Scene, flow


def build():
    s = Scene("SIEM veri akışı", "Her Windows makinede bir Universal Forwarder; log'lar doğrudan Splunk'a")

    def machine(y, name, ip, color, logs):
        s.rect(40, y, 470, 170, color, soft=True)
        s.inline(58, y + 28, [(name, 16, color.stroke, False), ("   " + ip, 14, MUTED, True)])
        s.box(58, y + 46, 280, 52, ORANGE, logs, size=14)
        s.box(58, y + 108, 280, 44, ORANGE, "Sysmon/Operational", size=14)
        s.box(400, y + 76, 90, 50, TEAL, "UF")
        s.arrow([(340, y + 72), (398, y + 94)], MUTED, width=1.6)
        s.arrow([(340, y + 130), (398, y + 110)], MUTED, width=1.6)
        return y + 101

    u1 = machine(100, "WS01", "10.0.0.30", GREEN, "Security / System / PowerShell")
    u2 = machine(340, "DC01", "10.0.0.20", PURPLE, "Security / System / Directory Svc")
    s.box(600, 250, 220, 80, TEAL, "Splunk", ["indexer · 10.0.0.10"])
    s.arrow([(492, u1), (598, 280)], TEAL.stroke, label="TCP 9997", label_at=0.55)
    s.arrow([(492, u2), (598, 300)], TEAL.stroke, label="TCP 9997", label_at=0.55)
    s.box(600, 400, 220, 44, BLUE, "index=windows", size=14)
    s.box(600, 460, 220, 44, BLUE, "index=sysmon", size=14)
    s.arrow([(710, 332), (710, 398)], MUTED, width=1.6)
    s.text(720, 370, "index'e yazar", 12, MUTED)
    s.arrow([(822, 290), (845, 290), (845, 482), (822, 482)], MUTED, width=1.6)
    s.arrow([(275, 272), (275, 338)], GRAY.stroke, dashed=True, width=1.8, label="DNS, Kerberos, LDAP")

    s.text(40, 560, "Aynı akış, aşamalar olarak:", 15, TEXT)
    flow(s, 40, 580, [("Collect", ["UF"], ORANGE), ("Parse", ["TA / sourcetype"], TEAL),
                      ("Index", ["disk, bucket"], BLUE), ("Search", ["SPL"], PURPLE)],
         ["gönderir", "yazar", "sorgulanır"], w=140, h=70)
    s.legend(40, 680, title="Gösterim", items=[
        ("box", ORANGE, "event log kanalı"), ("box", TEAL, "toplama / SIEM"), ("box", BLUE, "index"),
        ("arrow", TEAL.stroke, "log gönderimi"), ("dashed-arrow", GRAY.stroke, "domain trafiği (log değil)"),
    ])
    return s


if __name__ == "__main__":
    build().save("examples/output/siem_data_flow.excalidraw")
