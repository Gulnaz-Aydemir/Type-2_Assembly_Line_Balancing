import random
import math

# --- Tk/Tcl hatasını önlemek için ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# -----------------------------------

# 1) VERİ: JAESCHKE (9 görev)
K_HEDEF = 4
gorev_sureleri = {
    1: 5.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 4.0,
    6: 5.0, 7: 1.0, 8: 4.0, 9: 6.0
}
oncelikler = [
    (1, 2), (1, 3), (2, 4), (3, 4),
    (4, 5), (4, 6),(4, 7), (5, 8), (6, 9),
    (7, 9), (8, 9)
]

# 2) YARDIMCI FONKSİYONLAR
def get_oncul_listesi(num_tasks, preds_list):
    oncul_dict = {i: [] for i in range(1, num_tasks + 1)}
    for u, v in preds_list:
        oncul_dict[v].append(u)
    return oncul_dict

def sira_olustur(oncelik_puanlari, task_data, oncul_dict):
    yapilacaklar = list(task_data.keys())
    bitenler = set()
    siralama = []
    while yapilacaklar:
        adaylar = [t for t in yapilacaklar if all(p in bitenler for p in oncul_dict[t])]
        adaylar.sort(key=lambda x: oncelik_puanlari[x - 1], reverse=True)
        secilen = adaylar[0]
        siralama.append(secilen)
        bitenler.add(secilen)
        yapilacaklar.remove(secilen)
    return siralama

def oncelik_kontrol(siralama, preds_dict):
    pos = {task: i for i, task in enumerate(siralama)}
    for task, onculer in preds_dict.items():
        for oncul in onculer:
            if pos[oncul] > pos[task]:
                return False
    return True

def cevrim_zamani_hesapla(siralama, task_data, K):
    low = max(max(task_data.values()), sum(task_data.values()) / K)
    high = sum(task_data.values())
    best_c_found = high
    epsilon = 0.001

    while high - low > epsilon:
        mid = (low + high) / 2
        target_c = mid
        stations = 1
        current_load = 0
        possible = True

        for t in siralama:
            time_val = task_data[t]
            if current_load + time_val <= target_c:
                current_load += time_val
            else:
                stations += 1
                current_load = time_val
                if stations > K:
                    possible = False
                    break

        if possible:
            best_c_found = mid
            high = mid
        else:
            low = mid

    return best_c_found

def istasyonlara_bol(siralama, task_data, K, C):
    """
    Verilen sıra ve çevrim zamanı C ile greedy şekilde istasyonlara böl.
    K istasyonu aşarsa, yine de kalanları yeni istasyona açar (raporda görmek için).
    """
    stations = []
    cur = []
    cur_load = 0.0
    for t in siralama:
        p = task_data[t]
        if cur and cur_load + p > C:
            stations.append((cur, cur_load))
            cur = [t]
            cur_load = p
        else:
            cur.append(t)
            cur_load += p
    if cur:
        stations.append((cur, cur_load))

    # İstersen K'dan azsa boş istasyon ekleme (gerek yok)
    return stations

def istasyon_yazdir_ve_kaydet(best_seq, best_c, out_txt="istasyon_atamalari.txt"):
    stations = istasyonlara_bol(best_seq, gorev_sureleri, K_HEDEF, best_c)

    lines = []
    lines.append(f"K = {K_HEDEF}, C ≈ {best_c:.4f}\n")
    for i, (tasks, load) in enumerate(stations, start=1):
        lines.append(f"{i}. İstasyon: {tasks}   | Yük = {load:.1f}\n")

    # Terminale bas
    print("----- İSTASYON ATAMALARI -----")
    for line in lines:
        print(line, end="")

    # Dosyaya yaz
    with open(out_txt, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n✅ İstasyon çıktısı kaydedildi: {out_txt}")

# 3) TAVLAMA + ADIM TABLOSU (PNG)
def tavlama_calistir_ve_tablo_png(
    tablo_adim_sayisi=20,        # fotoğraftaki gibi ilk kaç adımı tabloya yazalım
    frame_deneme=1,              # her “adım” için kaç komşu denenecek (tablo için genelde 1 iyi)
    sicaklik0=100.0,
    sogutma_orani=0.95,
    durma_sicakligi=0.01,
    max_adim=5000,
    png_adi="tavlama_adim_tablosu.png"
):
    num_tasks = len(gorev_sureleri)
    oncul_dict = get_oncul_listesi(num_tasks, oncelikler)

    # Başlangıç çözümü
    current_puanlar = [random.random() for _ in range(num_tasks)]
    current_seq = sira_olustur(current_puanlar, gorev_sureleri, oncul_dict)
    current_c = cevrim_zamani_hesapla(current_seq, gorev_sureleri, K_HEDEF)

    best_seq = current_seq[:]
    best_c = current_c

    print(f"--- TAVLAMA BAŞLIYOR (Jaeschke, K={K_HEDEF}) ---")
    print(f"Başlangıç C: {current_c:.4f}")

    # Tablo logları (fotoğraftaki mantık)
    # Kolonlar: i, T, s, s', f(s), f(s'), Δ, e^{-Δ/T}, u, kabul, best
    logs = []

    T = sicaklik0
    step = 0

    while T > durma_sicakligi and step < max_adim:
        # tablo için her adımda 1 komşu denemek daha okunaklı
        for _ in range(frame_deneme):
            step += 1

            s_str = str(current_seq)
            fs = current_c

            # komşu üret (swap)
            yeni_sira = list(current_seq)
            i1 = random.randint(0, num_tasks - 1)
            i2 = random.randint(0, num_tasks - 1)
            yeni_sira[i1], yeni_sira[i2] = yeni_sira[i2], yeni_sira[i1]

            # Öncelik bozulursa: reddet
            if not oncelik_kontrol(yeni_sira, oncul_dict):
                # tabloya yine de yazalım
                if len(logs) < tablo_adim_sayisi:
                    logs.append([
                        step, f"{T:.3f}", s_str, str(yeni_sira),
                        f"{fs:.4f}", "-", "-", "-", "-", "RED (öncelik)", f"{best_c:.4f}"
                    ])
                continue

            fsp = cevrim_zamani_hesapla(yeni_sira, gorev_sureleri, K_HEDEF)
            delta = fsp - fs

            kabul = False
            acc_prob = "-"
            u = "-"

            if delta <= 0:
                kabul = True
                acc_prob = "1.000"
                u = f"{random.random():.3f}"  # yine yazalım
            else:
                acc_prob_val = math.exp(-delta / T)
                u_val = random.random()
                acc_prob = f"{acc_prob_val:.3f}"
                u = f"{u_val:.3f}"
                if u_val < acc_prob_val:
                    kabul = True

            if kabul:
                current_seq = yeni_sira
                current_c = fsp
                if current_c < best_c:
                    best_c = current_c
                    best_seq = current_seq[:]

            if len(logs) < tablo_adim_sayisi:
                logs.append([
                    step, f"{T:.3f}", s_str, str(yeni_sira),
                    f"{fs:.4f}", f"{fsp:.4f}", f"{delta:+.4f}",
                    acc_prob, u,
                    "KABUL" if kabul else "RED",
                    f"{best_c:.4f}"
                ])

        T *= sogutma_orani

    print("\n------------------------------")
    print("SONUÇ:")
    print(f"Python (Tavlama) Sonucu: {best_c:.4f}")
    print(f"Bulunan Sıralama: {best_seq}")

    # İstasyon atamalarını yazdır + dosyaya kaydet
    istasyon_yazdir_ve_kaydet(best_seq, best_c)

    # PNG tablo üret (matplotlib table)
    headers = ["i", "T", "s", "s'", "f(s)", "f(s')", "Δ", "e^{-Δ/T}", "u", "Karar", "Best"]
    cell_text = logs if logs else [["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"]]

    # Fig boyutu (kolon çok, geniş yap)
    fig_w = 18
    fig_h = 1 + 0.45 * (len(cell_text) + 1)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")

    table = ax.table(
        cellText=cell_text,
        colLabels=headers,
        loc="center",
        cellLoc="center"
    )

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.3)

    plt.title("Tavlama Benzetimi - Adım Adım Kabul Tablosu (Jaeschke)", pad=20)
    plt.tight_layout()
    plt.savefig(png_adi, dpi=200)
    print(f"\n✅ Tavlama adım tablosu PNG kaydedildi: {png_adi}")

if __name__ == "__main__":
    # Fotoğraftaki gibi ilk 15-25 adım çok iyi duruyor
    tavlama_calistir_ve_tablo_png(
        tablo_adim_sayisi=25,
        frame_deneme=1,
        png_adi="tavlama_adim_tablosu.png"
    )
