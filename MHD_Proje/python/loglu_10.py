import random
import math
import time

# ==========================================
# 1. VERİ GİRİŞİ: JAESCHKE (K=4)
# ==========================================
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

# ==========================================
# 2. YARDIMCI FONKSİYONLAR
# ==========================================
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
    # Binary search aralığı
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
# 3. GELİŞMİŞ TAVLAMA FONKSİYONU
# ==========================================
def tavlama_calistir_kesin():
    print(f"--- GELİŞMİŞ TAVLAMA (Swap + Insert) ---")
    
    num_tasks = len(gorev_sureleri)
    oncul_dict = get_oncul_listesi(num_tasks, oncelikler)
    
    # Başlangıç
    current_puanlar = [random.random() for _ in range(num_tasks)]
    seq = sira_olustur(current_puanlar, gorev_sureleri, oncul_dict)
    current_c = cevrim_zamani_hesapla(seq, gorev_sureleri, K_HEDEF)
    
    best_c = current_c
    best_seq = seq
    
    # Parametreler (Daha dengeli)
    sicaklik = 200.0
    sogutma_orani = 0.98
    durma_sicakligi = 0.5
    
    print("-" * 85)
    print(f"{'ADIM':<8} | {'SICAKLIK':<10} | {'MEVCUT C':<10} | {'EN İYİ C':<10} | {'DURUM':<20}")
    print("-" * 85)
    
    iterasyon_sayaci = 0
    
    while sicaklik > durma_sicakligi:
        for _ in range(100): # Her sıcaklıkta 100 deneme
            iterasyon_sayaci += 1
            
            yeni_sira = list(best_seq) # Greedy yaklaşım (En iyiden türet)
            
            # --- YENİLİK: Sadece Swap değil, Insert de yapıyoruz ---
            if random.random() < 0.5:
                # YÖNTEM 1: SWAP (Takas)
                idx1 = random.randint(0, num_tasks - 1)
                idx2 = random.randint(0, num_tasks - 1)
                yeni_sira[idx1], yeni_sira[idx2] = yeni_sira[idx2], yeni_sira[idx1]
            else:
                # YÖNTEM 2: INSERT (Araya Ekleme) - Bu kilitleri açar
                idx1 = random.randint(0, num_tasks - 1)
                task_to_move = yeni_sira.pop(idx1)
                idx2 = random.randint(0, num_tasks - 2) # List boyutu küçüldüğü için -2
                yeni_sira.insert(idx2, task_to_move)
            
            # Geçersizse atla
            if not oncelik_kontrol(yeni_sira, oncul_dict):
                continue
            
            yeni_C = cevrim_zamani_hesapla(yeni_sira, gorev_sureleri, K_HEDEF)
            fark = yeni_C - current_c
            
            durum_mesaji = ""
            kabul = False
            
            if fark < 0: 
                kabul = True
                durum_mesaji = "✅ İYİLEŞME"
            elif fark == 0:
                kabul = True # Eşitleri kabul et ki gezinsin
            else:
                prob = math.exp(-fark / sicaklik)
                if random.random() < prob: 
                    kabul = True
                    durum_mesaji = "⚠️ KÖTÜLEŞME"
            
            if kabul:
                current_c = yeni_C
                if current_c < best_c:
                    best_c = current_c
                    best_seq = yeni_sira
                    durum_mesaji = "⭐ REKOR!"
            
            if "REKOR" in durum_mesaji:
                 print(f"{iterasyon_sayaci:<8} | {sicaklik:<10.2f} | {current_c:<10.4f} | {best_c:<10.4f} | {durum_mesaji}")
            
        sicaklik *= sogutma_orani
        
        # Eğer 10'u bulduysak boşuna bekleme, bitir.
        if best_c < 10.001:
            print(f"\n🎯 HEDEF BULUNDU! C = {best_c:.4f}")
            break
            
    print("-" * 85)
    print(f"SONUÇ: En İyi C = {best_c:.4f}")
    print(f"Sıralama: {best_seq}")
    
    # 10 Bulunduysa Tabloyu Bas
    if best_c < 10.001:
        tabloyu_ciz(best_seq, best_c, gorev_sureleri)

# Tablo Fonksiyonunu da ekleyelim ki görelim
def tabloyu_ciz(siralama, C, task_data):
    print("\n" + "="*65)
    print(f" DETAYLI İSTASYON ATAMA TABLOSU (C = {C:.4f})")
    print("="*65)
    print(f"{'İstasyon':<10} | {'Görevler':<20} | {'Yük':<6} | {'Boş':<10}")
    print("-" * 65)
    current_station = 1
    current_load = 0
    station_tasks = []
    
    for t in siralama:
        time_val = task_data[t]
        if current_load + time_val <= C + 0.0001:
            station_tasks.append(t)
            current_load += time_val
        else:
            print(f"{current_station:<10} | {str(station_tasks):<20} | {current_load:<6g} | {C-current_load:<10.4f}")
            current_station += 1
            station_tasks = [t]
            current_load = time_val
    print(f"{current_station:<10} | {str(station_tasks):<20} | {current_load:<6g} | {C-current_load:<10.4f}")
    print("=" * 65)

if __name__ == "__main__":
    tavlama_calistir_kesin()