"""Kerberos interactive logon as a sequence diagram, tagged with the Windows events each step produces."""
from exdraw import BLUE, GREEN, MUTED, PURPLE, RED, TEXT, YELLOW, Scene, Sequence, callout


def build():
    s = Scene("Kerberos: bir kullanıcı oturum açınca ne olur?",
              "Domain'e katılmış bir istemcide etkileşimli oturum açma ve her adımın bıraktığı Windows event'i")
    seq = Sequence(s, [("alice", "klavye başında", GREEN), ("WS01", "LSASS", BLUE),
                       ("DC01", "DNS · KDC (port 88)", PURPLE)], x=130, spacing=280, top=100)
    seq.message(1, 2, "DNS: DC nerede? (SRV)", 200, step=1)
    seq.reply(2, 1, "dc01 = 10.0.0.20", 236)
    seq.message(0, 1, "EXAMPLE\\alice + parola", 296, step=2)
    seq.message(1, 2, "AS-REQ: şifreli zaman damgası", 356, step=3)
    seq.reply(2, 1, "AS-REP + TGT (krbtgt ile şifreli)", 396)
    seq.event(2, 408, "4768  TGT verildi")
    seq.message(1, 2, "TGS-REQ: host/WS01 bileti", 470, step=4)
    seq.reply(2, 1, "servis bileti", 510)
    seq.event(2, 522, "4769  bilet verildi")
    seq.note(1, 566, ["bilet doğrulandı,", "oturum açıldı"], step=5)
    seq.event(1, 578, "4624  Logon Type 2", dx=110)
    seq.reply(1, 0, "masaüstü açılır", 662)
    seq.finish(700)

    y = callout(s, 40, 720, 780, "Akılda tut", [
        "Parola ağda hiç gitmez; yalnızca parolayla şifrelenmiş zaman damgası gider.",
        "Saat farkı 5 dakikayı aşarsa KDC isteği reddeder: NTP zinciri kritik.",
        "Kerberos kullanılamazsa (ör. IP ile erişim) NTLM'e düşülür → DC'de 4776.",
        "krbtgt hash'i çalınırsa saldırgan istediği TGT'yi üretir: Golden Ticket.",
    ], YELLOW)
    s.legend(40, y + 16, title="Gösterim", items=[
        ("arrow", TEXT, "istek"), ("dashed-arrow", MUTED, "cevap"),
        ("chip", RED, "Windows event ID (yanındaki makinede loglanır)"),
    ])
    return s


if __name__ == "__main__":
    build().save("examples/output/kerberos_logon.excalidraw")
