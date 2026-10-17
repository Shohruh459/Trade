# Portfel/risk/fundamental tadqiqot — natijalar (reja: STRATEGY_PORTFOLIO.md)

Hamma ta'rif va mezonlar rejadagidek, sozlanmagan. 1 oy kechiktirilgan variant — rejaga natijadan oldin qo'shilgan qo'shimcha tekshiruv (vaqt artefaktini aniqlash uchun).


## A. Oltinning portfeldagi roli

|                                        |   CAGR_pct |   vol_pct |   Sharpe |   maxDD_pct |   worst12m_pct |   Calmar |
|:---------------------------------------|-----------:|----------:|---------:|------------:|---------------:|---------:|
| ('E1 1976-1999', 'P0 60/40')           |      13.53 |      8.75 |    1.501 |        15.6 |           -8.4 |     0.87 |
| ('E1 1976-1999', 'P1 54/36/10')        |      12.64 |      8.1  |    1.516 |        13.7 |           -9.9 |     0.92 |
| ('E1 1976-1999', 'P2 48/32/20')        |      11.71 |      7.97 |    1.434 |        15.7 |          -12.8 |     0.75 |
| ('E1 1976-1999', 'P3 risk parity')     |       9.42 |      7.35 |    1.265 |        13   |          -12.3 |     0.73 |
| ('E1 1976-1999', 'P4 faqat oltin')     |       3.01 |     19.1  |    0.243 |        62.1 |          -36.4 |     0.05 |
| ('E2 2000-2026', 'P0 60/40')           |       6.78 |      7.54 |    0.91  |        27.4 |          -23.8 |     0.25 |
| ('E2 2000-2026', 'P1 54/36/10')        |       7.27 |      6.99 |    1.042 |        23.4 |          -21.8 |     0.31 |
| ('E2 2000-2026', 'P2 48/32/20')        |       7.74 |      6.71 |    1.147 |        20.5 |          -19.8 |     0.38 |
| ('E2 2000-2026', 'P3 risk parity')     |       6.93 |      5.3  |    1.295 |        14.2 |          -12.7 |     0.49 |
| ('E2 2000-2026', 'P4 faqat oltin')     |      10.74 |     12.94 |    0.856 |        39.3 |          -27.5 |     0.27 |
| ("To'liq 1976-2026", 'P0 60/40')       |       9.94 |      8.18 |    1.203 |        27.4 |          -23.8 |     0.36 |
| ("To'liq 1976-2026", 'P1 54/36/10')    |       9.79 |      7.57 |    1.277 |        23.4 |          -21.8 |     0.42 |
| ("To'liq 1976-2026", 'P2 48/32/20')    |       9.6  |      7.35 |    1.289 |        20.5 |          -19.8 |     0.47 |
| ("To'liq 1976-2026", 'P3 risk parity') |       8.1  |      6.36 |    1.261 |        14.2 |          -12.7 |     0.57 |
| ("To'liq 1976-2026", 'P4 faqat oltin') |       7    |     16.18 |    0.496 |        62.1 |          -36.4 |     0.11 |


Sharpe farqi (P0 60/40 ga nisbatan), harakatlanuvchi blok bootstrap (12 oy, 5000):

|                |   dSharpe |   CI90_lo |   CI90_hi |   p_dSharpe_le0 |   E1_ok | E2_ok   |
|:---------------|----------:|----------:|----------:|----------------:|--------:|:--------|
| P1 54/36/10    |     0.073 |     0.017 |     0.142 |          0.0218 |       1 | True    |
| P2 48/32/20    |     0.085 |    -0.032 |     0.228 |          0.1044 |       0 | True    |
| P3 risk parity |     0.058 |    -0.205 |     0.368 |          0.3176 |       0 | True    |


**Mezon bo'yicha foydali (oltin vazni):** {'P1 54/36/10': True, 'P2 48/32/20': False, 'P3 risk parity': False}  (P3 risk parity — ma'lumot uchun; mezon P1, P2 uchun)


Tavsif (qarorga ta'sir qilmaydi):

|    |   corr_gold_equity |   corr_gold_bond |   gold_avg_ret_in_equity_down5_pct |   n_months_equity_down5 |
|:---|-------------------:|-----------------:|-----------------------------------:|------------------------:|
| E1 |               0.03 |            -0.06 |                              -1.31 |                       9 |
| E2 |              -0.01 |             0.25 |                               1.89 |                      22 |


## B. Oltinga trend filtri va vol nazorati

|                                                   |   Sharpe |   BH_Sharpe |   maxDD_pct |   BH_maxDD_pct |   CAGR_pct |   BH_CAGR_pct |   worst12m_pct |   BH_worst12m_pct |   switches |
|:--------------------------------------------------|---------:|------------:|------------:|---------------:|-----------:|--------------:|---------------:|------------------:|-----------:|
| ('O1 SMA10 (asosiy)', 'E1')                       |    0.471 |       0.243 |        31.2 |           62.1 |       6.69 |          3.01 |          -20.4 |             -36.4 |        nan |
| ('O1 SMA10 (asosiy)', 'E2')                       |    0.894 |       0.856 |        22.4 |           39.3 |       9.81 |         10.74 |          -12   |             -27.5 |        nan |
| ('O1 SMA10 (asosiy)', "To'liq")                   |    0.643 |       0.496 |        33.1 |           62.1 |       8.32 |          7    |          -20.4 |             -36.4 |         70 |
| ('O2 vol-maqsad (asosiy)', 'E1')                  |    0.156 |       0.243 |        56.1 |           62.1 |       1.21 |          3.01 |          -30.1 |             -36.4 |        nan |
| ('O2 vol-maqsad (asosiy)', 'E2')                  |    0.929 |       0.856 |        37.4 |           39.3 |      10.68 |         10.74 |          -25.8 |             -27.5 |        nan |
| ('O2 vol-maqsad (asosiy)', "To'liq")              |    0.541 |       0.496 |        56.1 |           62.1 |       6.07 |          7    |          -30.1 |             -36.4 |        nan |
| ('O1 SMA10 (1 oy kechiktirilgan)', 'E1')          |    0.47  |       0.243 |        24.4 |           62.1 |       6.44 |          3.01 |          -18   |             -36.4 |        nan |
| ('O1 SMA10 (1 oy kechiktirilgan)', 'E2')          |    0.818 |       0.856 |        29.4 |           39.3 |       9.06 |         10.74 |          -16.2 |             -27.5 |        nan |
| ('O1 SMA10 (1 oy kechiktirilgan)', "To'liq")      |    0.618 |       0.496 |        29.4 |           62.1 |       7.81 |          7    |          -18   |             -36.4 |         70 |
| ('O2 vol-maqsad (1 oy kechiktirilgan)', 'E1')     |    0.18  |       0.243 |        54.7 |           62.1 |       1.56 |          3.01 |          -31   |             -36.4 |        nan |
| ('O2 vol-maqsad (1 oy kechiktirilgan)', 'E2')     |    0.931 |       0.856 |        37.6 |           39.3 |      10.65 |         10.74 |          -25.6 |             -27.5 |        nan |
| ('O2 vol-maqsad (1 oy kechiktirilgan)', "To'liq") |    0.548 |       0.496 |        54.7 |           62.1 |       6.23 |          7    |          -31   |             -36.4 |        nan |


**Mezon bo'yicha qimmatli overlay (ikkala davrda DD ≥20% kam va Sharpe ≥ BH−0.05):** {'O1 SMA10 (asosiy)': True, 'O2 vol-maqsad (asosiy)': False, 'O1 SMA10 (1 oy kechiktirilgan)': True, 'O2 vol-maqsad (1 oy kechiktirilgan)': False}


## C. Fundamental omillar (OOS 1990-01 →, kengayuvchi oyna, Clark–West, Holm)

| variant             |   h | predictor          |   N |   OOS_R2 |   CW_t |   CW_p |   R2_1990_2007 |   R2_2008_ |
|:--------------------|----:|:-------------------|----:|---------:|-------:|-------:|---------------:|-----------:|
| asosiy              |   3 | x1 real foiz o'zg. | 434 |  -0.1331 |  -1.56 | 0.941  |        -0.1013 |    -0.1547 |
| asosiy              |   3 | x2 dollar 12m      | 435 |  -0.0208 |   0.46 | 0.3219 |         0.0049 |    -0.0379 |
| asosiy              |   3 | x3 oltin momentum  | 435 |   0.0344 |   2.28 | 0.0112 |         0.0559 |     0.0202 |
| asosiy              |   3 | x4 qiymat          | 430 |  -0.0329 |   0.62 | 0.2666 |        -0.0518 |    -0.0195 |
| asosiy              |   3 | x5 inflyatsiya     | 434 |  -0.0078 |  -0.48 | 0.6835 |        -0.0084 |    -0.0075 |
| asosiy              |  12 | x1 real foiz o'zg. | 426 |  -0.181  |  -1.4  | 0.919  |        -0.146  |    -0.2035 |
| asosiy              |  12 | x2 dollar 12m      | 426 |  -0.063  |   0.39 | 0.348  |         0.0296 |    -0.1221 |
| asosiy              |  12 | x3 oltin momentum  | 426 |   0.0811 |   2.86 | 0.0021 |         0.0763 |     0.0842 |
| asosiy              |  12 | x4 qiymat          | 426 |  -0.1338 |   0.28 | 0.3879 |        -0.2384 |    -0.0657 |
| asosiy              |  12 | x5 inflyatsiya     | 426 |  -0.0166 |  -0.7  | 0.7581 |        -0.0345 |    -0.0053 |
| 1 oy kechiktirilgan |   3 | x1 real foiz o'zg. | 433 |  -0.1115 |  -1.34 | 0.9097 |        -0.0815 |    -0.1312 |
| 1 oy kechiktirilgan |   3 | x2 dollar 12m      | 434 |  -0.0303 |  -0.34 | 0.6331 |        -0.0017 |    -0.0488 |
| 1 oy kechiktirilgan |   3 | x3 oltin momentum  | 434 |   0.0286 |   2.16 | 0.0152 |         0.0452 |     0.0178 |
| 1 oy kechiktirilgan |   3 | x4 qiymat          | 430 |  -0.0225 |   0.82 | 0.2059 |        -0.0199 |    -0.0243 |
| 1 oy kechiktirilgan |   3 | x5 inflyatsiya     | 433 |  -0.0052 |  -0.54 | 0.7049 |        -0.0066 |    -0.0042 |
| 1 oy kechiktirilgan |  12 | x1 real foiz o'zg. | 425 |  -0.1345 |  -1.27 | 0.8974 |        -0.1028 |    -0.1549 |
| 1 oy kechiktirilgan |  12 | x2 dollar 12m      | 425 |  -0.0639 |   0.22 | 0.4143 |         0.0224 |    -0.1188 |
| 1 oy kechiktirilgan |  12 | x3 oltin momentum  | 425 |   0.0484 |   2.52 | 0.0058 |         0.0337 |     0.0578 |
| 1 oy kechiktirilgan |  12 | x4 qiymat          | 425 |  -0.1432 |   0.21 | 0.4162 |        -0.2432 |    -0.0781 |
| 1 oy kechiktirilgan |  12 | x5 inflyatsiya     | 425 |  -0.0203 |  -0.63 | 0.7371 |        -0.0441 |    -0.0052 |


Mavsumiylik H_S (sentyabr–fevral − qolgan oylar): farq/oy = 0.97% , t = 2.09, bir tomonlama p = 0.0183; davrlar bo'yicha farq: E1 +0.97%, E2 +0.96%


Holm tuzatmasi (11 test, asosiy variant):

| test                    |      p | Holm_rad_etildi(5%)   |
|:------------------------|-------:|:----------------------|
| x1 real foiz o'zg. h=3  | 0.941  | False                 |
| x2 dollar 12m h=3       | 0.3219 | False                 |
| x3 oltin momentum h=3   | 0.0112 | False                 |
| x4 qiymat h=3           | 0.2666 | False                 |
| x5 inflyatsiya h=3      | 0.6835 | False                 |
| x1 real foiz o'zg. h=12 | 0.919  | False                 |
| x2 dollar 12m h=12      | 0.348  | False                 |
| x3 oltin momentum h=12  | 0.0021 | True                  |
| x4 qiymat h=12          | 0.3879 | False                 |
| x5 inflyatsiya h=12     | 0.7581 | False                 |
| mavsumiylik             | 0.0183 | False                 |


**Qabul qilingan predikatorlar (Holm + ikki yarim + iqtisodiy sinov):** yo`q


## Qo'shimcha: x3 (oltin momentumi) iqtisodiy sinovi nima uchun o'tmadi (natijadan keyin, tavsifiy)
x3 h=12 uchun bashorat deyarli har oy musbat (oltinning o'rtacha o'sishi tufayli), shuning uchun "bashorat > 0 bo'lsa long, aks holda naqd" qoidasi **100% vaqt long** va buy&hold bilan bir xil
(1990–2007: Sharpe 0.417 ga qarshi 0.419; 2008–2026: 0.668 ga qarshi 0.676). h=3 da 85% vaqt long: 1990–2007 da DD 38.6% → 29.9%, lekin 2008–2026 da farq yo'q (38.5% ga qarshi 39.3%).
Ya'ni momentumning bashorat aniqligi (OOS R² ≈ 3–8%) statistik jihatdan haqiqiy va takrorlangan, lekin "ishora bo'yicha" qoida bilan foydaga aylanmaydi.

## Xulosa
- **A (portfel):** 10% oltin (54/36/10) 60/40 dan mezon bo'yicha **foydali**: to'liq namunada Sharpe +0.073 (90% oraliq +0.017…+0.142, p = 0.022), ikkala davrda Sharpe yuqori va drawdown kam emas
  (E1: Sharpe +0.015, DD 15.6 → 13.7%; E2: +0.13, DD 27.4 → 23.4%). **20% oltin mezondan o'tmadi:** E1 da Sharpe past (1.434 ga qarshi 1.501), E2 da yaxshi. Risk parity ishonchli emas (p = 0.32).
  Oltinning aksiyaga korrelyatsiyasi ≈ 0; aksiya oylik −5% dan ko'p tushganda oltin E1 da o'rtacha −1.3% (9 oy), E2 da +1.9% (22 oy): "inqiroz himoyasi" bir xil emas.
- **B (xavf kamaytirish):** **O1 SMA10 mezondan o'tdi** (asosiy va 1 oy kechiktirilgan variantlarda ham): maksimal drawdown E1 da 62% → 31% (kechiktirilgan 24%), E2 da 39% → 22% (kechiktirilgan 29%), Sharpe past emas, yillik ~1.3 almashtirish.
  **O2 vol-maqsad o'tmadi** (E1 da Sharpe pastroq: 0.16 ga qarshi 0.24, drawdown deyarli kamaymadi).
- **C (fundamental):** hech bir predikator qabul qilinmadi. Real foiz o'zgarishi, dollar, qiymat va inflyatsiya OOS da manfiy R² berdi (benchmarkdan yomon). Faqat oltin momentumi (x3) statistik ahamiyatli
  (12 oyda OOS R² 8.1%, Holm-p 0.002, ikki yarimda ham musbat, 1 oy kechiktirilganda 4.8%) lekin tradable emas (yuqorida). Mavsumiylik (sentyabr–fevral +0.97%/oy, ikkala davrda ham +0.96–0.97%) bir tomonlama p = 0.018,
  lekin 11 testli Holm tuzatmasidan o'tmadi.
- **Cheklovlar:** oylik o'rtacha narxlar (drawdown va vol past ko'rsatilgan, Sharpe darajalari yuqori; nisbiy solishtirish muhim); obligatsiya/aksiya daromadlari approksimatsiya; oltinning ~4–5 katta tsikli.
