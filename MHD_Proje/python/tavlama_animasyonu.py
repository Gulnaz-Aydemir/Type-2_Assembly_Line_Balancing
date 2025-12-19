import random
import math

# --- Matplotlib ayarları (Tk hatasını önlemek için) ---
import matplotlib
matplotlib.use("Agg")  # Ekran açmaya çalışmaz, direkt dosyaya yazar
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
# ------------------------------------------------------

# 1. VERİ GİRİŞİ: JAESCHKE (9 GÖREV, K=4)
K_HEDEF = 4
gorev_sureleri = {
    1: 5.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 4.0,
    6: 5.0, 7: 1.0, 8: 4.0, 9: 6.0
}
oncelikler = [
    (1, 2), (1, 3), (2, 4), (2, 6),
    (3, 5), (4, 7), (5, 8), (6, 8),
    (7, 9), (8, 9)
]

# 2. YARDIMCI FONKSİYONLAR
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
        adaylar = [
            t for t in yapilacaklar
            if all(p in bitenler for p in oncul_dict[t])
        ]
        # oncelik_puanlari dizisi 0-index, görevler 1'den başlıyor
        adaylar.sort(key=lambda x: oncelik_puanlari[x - 1], reverse=True)
        secilen = adaylar[0]
        siralama.append(secilen)
        bitenler.add(secilen)
        yapilacaklar.remove(secilen)
    return siralama

def cevrim_zamani_hesapla(siralama, task_data, K):
    # Tip-2: K sabit, C minimize
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

def oncelik_kontrol(siralama, preds_dict):
    pos = {task: i for i, task in enumerate(siralama)}
    for task, onculer in preds_dict.items():
        for oncul in onculer:
            if pos[oncul] > pos[task]:
                return False
    return True

# 3. TAVLAMA + ANİMASYON
def tavlama_animasyon():
    print(f"--- ANİMASYONLU TAVLAMA BAŞLIYOR (Jaeschke, K={K_HEDEF}) ---")

    num_tasks = len(gorev_sureleri)
    oncul_dict = get_oncul_listesi(num_tasks, oncelikler)

    # Başlangıç çözümü
    current_puanlar = [random.random() for _ in range(num_tasks)]
    seq = sira_olustur(current_puanlar, gorev_sureleri, oncul_dict)
    current_c = cevrim_zamani_hesapla(seq, gorev_sureleri, K_HEDEF)

    best_c = current_c
    best_seq = seq[:]

    # Tavlama parametreleri
    sicaklik = 100.0
    sogutma_orani = 0.95
    durma_sicakligi = 0.01

    # Animasyon verileri
    iterations = []
    current_values = []
    best_values = []

    fig, ax = plt.subplots(figsize=(10, 6))

    # Kaç frame olsun? (her frame içinde 50 komşu deneniyor)
    MAX_FRAMES = 200

    def update(frame):
        nonlocal seq, current_c, best_c, best_seq, sicaklik

        # Sıcaklık durma seviyesinin altına inerse artık çok az değişecek
        if sicaklik < durma_sicakligi:
            # Yine de grafiğe son hâli ekleyelim
            iterations.append(frame)
            current_values.append(current_c)
            best_values.append(best_c)
        else:
            # Her frame'de birkaç deneme yap (ör: 50 komşu çözüm)
            for _ in range(50):
                yeni_sira = list(best_seq)
                idx1 = random.randint(0, num_tasks - 1)
                idx2 = random.randint(0, num_tasks - 1)
                yeni_sira[idx1], yeni_sira[idx2] = yeni_sira[idx2], yeni_sira[idx1]

                if not oncelik_kontrol(yeni_sira, oncul_dict):
                    continue

                yeni_C = cevrim_zamani_hesapla(yeni_sira, gorev_sureleri, K_HEDEF)
                fark = yeni_C - current_c

                kabul = False
                if fark < 0:
                    kabul = True
                else:
                    # Tavlama kabul olasılığı
                    prob = math.exp(-fark / sicaklik)
                    if random.random() < prob:
                        kabul = True

                if kabul:
                    current_c = yeni_C
                    seq = yeni_sira
                    if current_c < best_c:
                        best_c = current_c
                        best_seq = yeni_sira

            sicaklik *= sogutma_orani

            iterations.append(frame)
            current_values.append(current_c)
            best_values.append(best_c)

        # Grafiği güncelle
        ax.clear()
        ax.plot(iterations, current_values,
                label='Mevcut Çözüm (C)', alpha=0.3)
        ax.plot(iterations, best_values,
                label='En İyi Çözüm (Best C)', linewidth=2)
        ax.set_xlabel('İterasyon (frame bazında)')
        ax.set_ylabel('Çevrim Zamanı (C)')
        ax.set_title('Jaeschke Problemi - Tavlama Benzetimi Yakınsama Animasyonu')
        ax.legend()
        ax.grid(True)

    ani = FuncAnimation(fig, update, frames=range(1, MAX_FRAMES + 1), repeat=False)

    # GIF OLARAK KAYDET (ImageMagick GEREKMEZ)
    gif_adi = "tavlama_animasyon.gif"
    print("⏳ Animasyon oluşturuluyor, lütfen bekleyin...")
    writer = PillowWriter(fps=10)
    ani.save(gif_adi, writer=writer)
    print(f"✅ Animasyon kaydedildi: {gif_adi}")
    print(f"SONUÇ: En iyi bulunan C ≈ {best_c:.4f}")
    print(f"En iyi görev sıralaması: {best_seq}")

if __name__ == "__main__":
    tavlama_animasyon()
