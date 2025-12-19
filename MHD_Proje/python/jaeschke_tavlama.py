import random
import math
import time
import copy

# ==========================================
# 1. VERİ GİRİŞİ: JAESCHKE (9 GÖREV)
# ==========================================
K_HEDEF = 4  # GAMS'te kullandığımız İstasyon Sayısı

# Görev Süreleri (GAMS çıktınızdaki doğru süreler)
gorev_sureleri = {
    1: 5.0, 2: 3.0, 3: 4.0, 4: 5.0, 5: 4.0,
    6: 5.0, 7: 1.0, 8: 4.0, 9: 6.0
}

# Öncelik İlişkileri (Kim -> Kime)
oncelikler = [
    (1, 2), (1, 3), (2, 4), (3, 4),
    (4, 5), (4, 6), (4, 7), (5, 8), (6, 9),
    (7, 9), (8, 9)
]

# ==========================================
# 2. YARDIMCI FONKSİYONLAR
# ==========================================

def get_predecessors(num_tasks, relations):
    """Hangi işin öncülleri kimler, listesini çıkarır"""
    preds = {i: [] for i in range(1, num_tasks + 1)}
    for u, v in relations:
        preds[v].append(u)
    return preds

def rastgele_gecerli_siralama(tasks, preds_dict):
    """
    Önceliklere uygun Rastgele bir başlangıç sıralaması oluşturur.
    """
    kalanlar = list(tasks.keys())
    bitenler = set()
    siralama = []
    
    while kalanlar:
        # Yapılabilir işleri bul (tüm öncülleri bitmiş olanlar)
        yapilabilir = [t for t in kalanlar if all(p in bitenler for p in preds_dict[t])]
        
        # Rastgele birini seç ve listeye ekle
        secilen = random.choice(yapilabilir)
        siralama.append(secilen)
        bitenler.add(secilen)
        kalanlar.remove(secilen)
        
    return siralama

def cozum_hesapla(siralama, tasks, K):
    """
    Verilen iş sırasını (siralama) K adet istasyona dağıtır
    ve gereken Çevrim Zamanını (C) hesaplar.
    """
    # Alt sınır ve üst sınır belirle
    toplam_is = sum(tasks.values())
    max_tekil = max(tasks.values())
    low = max(max_tekil, toplam_is / K)
    high = toplam_is
    
    best_local_c = high
    epsilon = 0.001 
    
    # Binary Search ile bu sıralama için en iyi C'yi bul
    while high - low > epsilon:
        mid = (low + high) / 2
        
        # mid değeri C olsa sığar mı?
        stations = 1
        current_load = 0
        possible = True
        
        for t in siralama:
            time_val = tasks[t]
            if current_load + time_val <= mid:
                current_load += time_val
            else:
                stations += 1
                current_load = time_val
        
        if possible and stations <= K:
            best_local_c = mid
            high = mid
        else:
            low = mid
            
    return best_local_c

def oncelik_kontrol(siralama, preds_dict):
    """Sıralamanın bozulup bozulmadığını kontrol eder"""
    # İşlerin listedeki indekslerini (pozisyonlarını) kaydet
    pos = {task: i for i, task in enumerate(siralama)}
    
    for task, onculer in preds_dict.items():
        for oncul in onculer:
            # Eğer öncül iş, asıl işten daha sonra geliyorsa kural bozulmuştur
            if pos[oncul] > pos[task]: 
                return False
    return True

# ==========================================
# 3. TAVLAMA BENZETİMİ DÖNGÜSÜ
# ==========================================

def tavlama_calistir():
    print(f"--- TAVLAMA BAŞLIYOR (Jaeschke, K={K_HEDEF}) ---")
    
    # Hazırlık
    num_tasks = len(gorev_sureleri)
    preds_dict = get_predecessors(num_tasks, oncelikler)
    
    # 1. Başlangıç Çözümü
    mevcut_sira = rastgele_gecerli_siralama(gorev_sureleri, preds_dict)
    mevcut_C = cozum_hesapla(mevcut_sira, gorev_sureleri, K_HEDEF)
    
    en_iyi_sira = list(mevcut_sira)
    en_iyi_C = mevcut_C
    
    # Parametreler
    sicaklik = 100.0
    sogutma_orani = 0.95
    durma_sicakligi = 0.01
    
    print(f"Başlangıç C: {mevcut_C:.4f}")
    
    iterasyon = 0
    while sicaklik > durma_sicakligi:
        iterasyon += 1
        
        # 2. KOMŞU ÜRET (SWAP - Yer Değiştirme)
        yeni_sira = list(mevcut_sira)
        
        # Rastgele iki iş seç ve yerlerini değiştir
        idx1 = random.randint(0, num_tasks - 1)
        idx2 = random.randint(0, num_tasks - 1)
        yeni_sira[idx1], yeni_sira[idx2] = yeni_sira[idx2], yeni_sira[idx1]
        
        # 3. KONTROL: Öncelik bozuldu mu?
        if not oncelik_kontrol(yeni_sira, preds_dict):
            continue # Bozuksa atla
            
        # 4. HESAPLA
        yeni_C = cozum_hesapla(yeni_sira, gorev_sureleri, K_HEDEF)
        fark = yeni_C - mevcut_C
        
        # 5. KABUL KRİTERİ
        kabul = False
        if fark < 0: # Daha iyi
            kabul = True
        else: # Daha kötü (Olasılıkla kabul)
            olasilik = math.exp(-fark / sicaklik)
            if random.random() < olasilik:
                kabul = True
        
        if kabul:
            mevcut_sira = list(yeni_sira)
            mevcut_C = yeni_C
            
            if mevcut_C < en_iyi_C:
                en_iyi_C = mevcut_C
                en_iyi_sira = list(mevcut_sira)
        
        sicaklik *= sogutma_orani
        
    print("-" * 30)
    print(f"SONUÇ:")
    print(f"GAMS Sonucu (Referans): 10.0000")
    print(f"Python (Tavlama) Sonucu: {en_iyi_C:.4f}")
    print(f"Bulunan Sıralama: {en_iyi_sira}")

if __name__ == "__main__":
    tavlama_calistir()