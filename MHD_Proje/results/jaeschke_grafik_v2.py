import random
import math
import time

# --- DÜZELTME BAŞLANGICI ---
# Bu iki satır hatayı çözer: Grafiği ekrana basma, dosyaya yaz moduna alır.
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
# ---------------------------

# 1. VERİ GİRİŞİ: JAESCHKE (9 GÖREV, K=4)
K_HEDEF = 4
gorev_sureleri = {
    1: 5.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 4.0,
    6: 5.0, 7: 1.0, 8: 4.0, 9: 6.0
}
oncelikler = [
    (1, 2), (1, 3), (2, 4), (3, 4),
    (4, 5), (4, 6), (4, 7), (5, 8), (6, 9),
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
        adaylar = [t for t in yapilacaklar if all(p in bitenler for p in oncul_dict[t])]
        adaylar.sort(key=lambda x: oncelik_puanlari[x-1], reverse=True)
        secilen = adaylar[0]
        siralama.append(secilen)
        bitenler.add(secilen)
        yapilacaklar.remove(secilen)
    return siralama

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
                    possible = False; break
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
            if pos[oncul] > pos[task]: return False
    return True

# 3. TAVLAMA VE GRAFİK
def tavlama_calistir_grafikli():
    print(f"--- GRAFİKLİ TAVLAMA BAŞLIYOR (Jaeschke, K={K_HEDEF}) ---")
    
    num_tasks = len(gorev_sureleri)
    oncul_dict = get_oncul_listesi(num_tasks, oncelikler)
    
    current_puanlar = [random.random() for _ in range(num_tasks)]
    seq = sira_olustur(current_puanlar, gorev_sureleri, oncul_dict)
    current_c = cevrim_zamani_hesapla(seq, gorev_sureleri, K_HEDEF)
    
    best_c = current_c
    best_seq = seq
    
    sicaklik = 100.0
    sogutma_orani = 0.95
    durma_sicakligi = 0.01
    
    # Grafik verileri
    history_best = []
    history_current = []
    iterations = []
    iter_count = 0
    
    while sicaklik > durma_sicakligi:
        for _ in range(50):
            iter_count += 1
            yeni_sira = list(best_seq)
            idx1 = random.randint(0, num_tasks - 1)
            idx2 = random.randint(0, num_tasks - 1)
            yeni_sira[idx1], yeni_sira[idx2] = yeni_sira[idx2], yeni_sira[idx1]
            
            if not oncelik_kontrol(yeni_sira, oncul_dict):
                # Grafik kopmasın diye eski değeri tekrar ekle
                history_current.append(current_c)
                history_best.append(best_c)
                iterations.append(iter_count)
                continue
            
            yeni_C = cevrim_zamani_hesapla(yeni_sira, gorev_sureleri, K_HEDEF)
            fark = yeni_C - current_c
            
            kabul = False
            if fark < 0: kabul = True
            else:
                prob = math.exp(-fark / sicaklik)
                if random.random() < prob: kabul = True
            
            if kabul:
                current_c = yeni_C
                if current_c < best_c:
                    best_c = current_c
                    best_seq = yeni_sira
            
            history_current.append(current_c)
            history_best.append(best_c)
            iterations.append(iter_count)
        
        sicaklik *= sogutma_orani

    print(f"SONUÇ: En İyi C = {best_c:.4f}")
    
    # --- GRAFİĞİ DOSYAYA KAYDET ---
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, history_current, label='Mevcut Çözüm (C)', color='blue', alpha=0.3)
    plt.plot(iterations, history_best, label='En İyi Çözüm (Best C)', color='red', linewidth=2)
    plt.xlabel('İterasyon Sayısı')
    plt.ylabel('Çevrim Zamanı (C)')
    plt.title('Jaeschke Problemi - Tavlama Benzetimi Yakınsama Grafiği')
    plt.legend()
    plt.grid(True)
    
    # show() yerine savefig() kullanıyoruz
    dosya_adi = 'jaeschke_grafik.png'
    plt.savefig(dosya_adi)
    print(f"✅ Grafik başarıyla kaydedildi: {dosya_adi}")
    
if __name__ == "__main__":
    tavlama_calistir_grafikli()