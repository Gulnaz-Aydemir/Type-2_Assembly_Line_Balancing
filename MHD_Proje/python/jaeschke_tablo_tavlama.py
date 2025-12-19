import random
import math
import time

# ==========================================
# 1. VERİ GİRİŞİ: JAESCHKE (9 GÖREV)
# ==========================================
K_HEDEF = 4  # İstenen İstasyon Sayısı (Burada K_HEDEF ismini kullandık)

gorev_sureleri = {
    1: 5.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 4.0,
    6: 5.0, 7: 1.0, 8: 4.0, 9: 6.0
}

oncelikler = [
    (1, 2), (1, 3), (2, 4), (3, 4),
    (4, 5), (4, 6), (4, 7), (5, 8), (6, 9),
    (7, 9), (8, 9)
    
]

# ==========================================
# 2. YARDIMCI FONKSİYONLAR
# ==========================================

def get_oncul_listesi(num_tasks, preds_list):
    oncul_dict = {i: [] for i in range(1, num_tasks + 1)}
    for u, v in preds_list:
        oncul_dict[v].append(u)
    return oncul_dict

def sira_olustur(oncelik_puanlari, task_data, oncul_dict):
    """Rastgele puanlara göre geçerli bir iş sırası oluşturur"""
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
    """Binary Search ile en iyi C'yi bulur"""
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

# ==========================================
# 3. TABLO OLUŞTURMA FONKSİYONU
# ==========================================
def tabloyu_ciz(siralama, C, task_data):
    print("\n" + "="*65)
    print(f" DETAYLI İSTASYON ATAMA TABLOSU (C = {C:.4f})")
    print("="*65)
    print(f"{'İstasyon':<10} | {'Görevler':<20} | {'Süreler':<15} | {'Yük':<6} | {'Boş (Idle)':<10}")
    print("-" * 65)
    
    current_station = 1
    current_load = 0
    station_tasks = []
    station_times = []
    
    total_idle = 0
    
    for t in siralama:
        time_val = task_data[t]
        if current_load + time_val <= C + 0.0001:
            station_tasks.append(t)
            station_times.append(time_val)
            current_load += time_val
        else:
            idle = C - current_load
            total_idle += idle
            tasks_str = ", ".join(map(str, station_tasks))
            times_str = "+".join(map(str, [int(x) if x.is_integer() else x for x in station_times]))
            
            print(f"{current_station:<10} | {tasks_str:<20} | {times_str:<15} | {current_load:<6g} | {idle:<10.4f}")
            
            current_station += 1
            station_tasks = [t]
            station_times = [time_val]
            current_load = time_val
            
    idle = C - current_load
    total_idle += idle
    tasks_str = ", ".join(map(str, station_tasks))
    times_str = "+".join(map(str, [int(x) if x.is_integer() else x for x in station_times]))
    print(f"{current_station:<10} | {tasks_str:<20} | {times_str:<15} | {current_load:<6g} | {idle:<10.4f}")
    
    print("-" * 65)
    print(f"TOPLAM BOŞ ZAMAN (Total Idle Time): {total_idle:.4f}")
    
    toplam_is = sum(task_data.values())
    verimlilik = (toplam_is / (current_station * C)) * 100
    print(f"HAT ETKİNLİĞİ (Line Efficiency): %{verimlilik:.2f}")
    print("=" * 65)

# ==========================================
# 4. TAVLAMA DÖNGÜSÜ
# ==========================================

def tavlama_calistir():
    print(f"--- TAVLAMA BAŞLIYOR (Jaeschke, K={K_HEDEF}) ---")
    
    num_tasks = len(gorev_sureleri)
    oncul_dict = get_oncul_listesi(num_tasks, oncelikler)
    
    # Başlangıç
    current_puanlar = [random.random() for _ in range(num_tasks)]
    seq = sira_olustur(current_puanlar, gorev_sureleri, oncul_dict)
    
    # DÜZELTME BURADA: K_ISTASYON_SAYISI yerine K_HEDEF kullanıldı
    current_c = cevrim_zamani_hesapla(seq, gorev_sureleri, K_HEDEF)
    
    best_c = current_c
    best_seq = seq
    
    # Parametreler
    sicaklik = 100.0
    sogutma_orani = 0.95
    durma_sicakligi = 0.01
    
    while sicaklik > durma_sicakligi:
        for _ in range(50):
            yeni_sira = list(best_seq)
            
            idx1 = random.randint(0, num_tasks - 1)
            idx2 = random.randint(0, num_tasks - 1)
            yeni_sira[idx1], yeni_sira[idx2] = yeni_sira[idx2], yeni_sira[idx1]
            
            if not oncelik_kontrol(yeni_sira, oncul_dict): continue
            
            # DÜZELTME BURADA: K_HEDEF kullanıldı
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
        
        sicaklik *= sogutma_orani
        
    print(f"\nSONUÇ:")
    print(f"GAMS Sonucu (Referans): 10.00")
    print(f"Python (Tavlama) Sonucu: {best_c:.4f}")
    
    tabloyu_ciz(best_seq, best_c, gorev_sureleri)

if __name__ == "__main__":
    tavlama_calistir()