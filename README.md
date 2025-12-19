# 🏭 Type-2 Assembly Line Balancing Optimization (SALBP-2)

## 🧰 Tools & Technologies

- 🧮 **GAMS** (Mathematical Modeling)
- ⚙️ **CPLEX** (Exact MIP Solver)
- 🐍 **Python** (Algorithm Development)
- 🔥 **Simulated Annealing** (Metaheuristic Optimization)
- 📊 **Matplotlib** (Visualization)
- 📈 **Operations Research / Optimization**


Bu proje, **Tip-2 Montaj Hattı Dengeleme Problemini (Minimize Cycle Time)** çözmeyi amaçlamaktadır. Projede kesin çözüm yöntemi olarak **GAMS (MIP)**, sezgisel çözüm yöntemi olarak ise **Python (Tavlama Benzetimi / Simulated Annealing)** kullanılmış ve sonuçlar karşılaştırılmıştır.

## 🎯 Proje Amacı
Sabit sayıda istasyon (K) verildiğinde, çevrim zamanını (C) en aza indirmek ve hat etkinliğini maksimize etmek.

## 🛠️ Kullanılan Teknolojiler ve Yöntemler

### 1. Kesin Yöntem (Exact Method)
* **Araç:** GAMS (General Algebraic Modeling System)
* **Solver:** CPLEX / MIP
* **Model:** Matematiksel tamsayılı programlama modeli kullanılarak global optimum sonuçlar elde edilmiştir.

### 2. Sezgisel Yöntem (Heuristic Method)
* **Dil:** Python 3.x
* **Algoritma:** Tavlama Benzetimi (Simulated Annealing)
* **Strateji:** Yerel tuzaklardan (Local Optima) kaçmak için **Swap (Takas)** ve **Insert (Araya Ekleme)** komşuluk yapıları hibrit olarak kullanılmıştır.
* **Görselleştirme:** Matplotlib ile yakınsama grafikleri (Convergence Plots) çizdirilmiştir.

## 📊 Veri Setleri ve Sonuçlar

Projede literatürdeki standart benchmark veri setleri kullanılmıştır: **Jaeschke (9 Görev)** .

| Veri Seti | İstasyon Sayısı (K) | GAMS Sonucu (Min C) | Python (SA) Sonucu | Sapma (%) | Durum |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Jaeschke** | 4 | **10.0** | **10.0** | %0 | ✅ Optimal |


> **Not:** Geliştirilen Tavlama Benzetimi algoritması, her iki problemde de saniyeler içerisinde GAMS ile aynı **optimal** sonucu bulmayı başarmıştır.

## 📈 Algoritma Performansı
Aşağıdaki grafik, Python algoritmasının iterasyonlar boyunca optimum sonuca nasıl yakınsadığını göstermektedir:

![Yakınsama Grafiği](MHD/results/jaeschke_grafik.png)


## 🚀 Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için:

1. Repoyu klonlayın:
   ```bash
   git clone [https://github.com/KULLANICI_ADIN/PROJE_ADIN.git](https://github.com/KULLANICI_ADIN/PROJE_ADIN.git)
