import random
import math
import time

# ==========================================
# 1. VERİ GİRİŞİ: JAESCHKE (9 GÖREV, K=4)
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
# 3. İTERASYON LOGLU TAVLAMA FONKSİYONU
# ==========================================
def tavlama_calistir_loglu():
    print(f"--- DETAYLI TAVLAMA LOGU (Jaeschke, K={K_HEDEF}) ---")
    
    num_tasks = len(gorev_sureleri)
    oncul_dict = get_oncul_listesi(num_tasks, oncelikler)
    
    # Başlangıç
    current_puanlar = [random.random() for _ in range(num_tasks)]
    seq = sira_olustur(current_puanlar, gorev_sureleri, oncul_dict)
    current_c = cevrim_zamani_hesapla(seq, gorev_sureleri, K_HEDEF)
    
    best_c = current_c
    best_seq = seq
    
    # Parametreler
    sicaklik = 100.0
    sogutma_orani = 0.90 # Biraz hızlı soğusun ki loglar çok uzamasın
    durma_sicakligi = 0.5 # Log örneği için erken durduruyorum
    
    # BAŞLIKLARI YAZDIR
    print("-" * 85)
    print(f"{'İTERASYON':<10} | {'SICAKLIK (T)':<12} | {'MEVCUT C':<10} | {'EN İYİ C':<10} | {'DURUM':<20}")
    print("-" * 85)
    
    iterasyon_sayaci = 0
    
    while sicaklik > durma_sicakligi:
        # Her sıcaklık seviyesinde bir miktar deneme yap
        for _ in range(10): 
            iterasyon_sayaci += 1
            
            yeni_sira = list(best_seq)
            idx1 = random.randint(0, num_tasks - 1)
            idx2 = random.randint(0, num_tasks - 1)
            yeni_sira[idx1], yeni_sira[idx2] = yeni_sira[idx2], yeni_sira[idx1]
            
            # Kural ihlali varsa loga yazmadan geç (veya 'Geçersiz' diye yazdırabiliriz)
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
                # Eşitse de kabul edelim (çeşitlilik için)
                kabul = True
                durum_mesaji = "⏺️ EŞİT (Kabul)"
            else:
                prob = math.exp(-fark / sicaklik)
                if random.random() < prob: 
                    kabul = True
                    durum_mesaji = "⚠️ KÖTÜLEŞME (Kabul)"
                else:
                    kabul = False
                    durum_mesaji = "❌ RED"
            
            if kabul:
                current_c = yeni_C
                if current_c < best_c:
                    best_c = current_c
                    best_seq = yeni_sira
                    durum_mesaji = "⭐ REKOR KIRILDI!"
            
            # --- İŞTE İSTEDİĞİNİZ SATIR SATIR ÇIKTI ---
            # Sadece değişiklik olduğunda veya 5 adımda bir yazdıralım ki takip edilebilir olsun
            # Veya her adımı yazdırabiliriz:
            print(f"{iterasyon_sayaci:<10} | {sicaklik:<12.2f} | {current_c:<10.4f} | {best_c:<10.4f} | {durum_mesaji}")
            
        # Soğutma
        sicaklik *= sogutma_orani
        
    print("-" * 85)
    print(f"SONUÇ: En İyi C = {best_c:.4f}")
    print(f"Sıralama: {best_seq}")

if __name__ == "__main__":
    tavlama_calistir_loglu()