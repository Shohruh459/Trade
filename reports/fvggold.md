# FvgGold (foeed/FvgGold-EA) — mustaqil sinov, XAUUSD M15, 2018-01 → 2025-02

Muallif parametrlarini 2026-yil (Yan–Iyul) ma'lumotiga optimallashtirgan; bu davr ma'lumotimizda yo'q. Biz EA'ning standart sozlamalarini (`FvgGold.set`) o'zgartirmasdan, 2018–2025-fevral davrida sinaymiz: bu muallif ko'rmagan ma'lumot. Port Python'da bar-darajasida, taxminiy (MT5 tick sinovi emas). Spred $0.25/oz, komissiya $7/100 oz.


## Stsenariylar (pessimistic fill, 0.01 lot)

|                                                         |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |   at_1pct_risk_maxDD_pct |
|:--------------------------------------------------------|---------:|----------:|-----:|--------:|----------:|-----------------------:|-------------------------:|
| S1 EA standarti (CloseAtEOD=false)                      |      139 |       4.3 | 0.34 |  -0.126 |     -78.8 |                  -16.2 |                     16.2 |
| S2 EA'ning CloseAtEOD=true opsiyasi                     |     1445 |      10   | 0.58 |  -0.089 |    -581.8 |                  -73.2 |                     75.1 |
| S3 S2 + break-even o'chiq                               |     1039 |      40.1 | 0.86 |  -0.081 |    -376.8 |                  -59.4 |                     61.6 |
| S4 bizning o'zgartirish: pending 20 baradan keyin bekor |     3580 |       9.7 | 0.62 |  -0.09  |   -1444.7 |                  -96.2 |                     96.5 |
| S5 S4 + break-even o'chiq                               |     2487 |      36.3 | 0.83 |  -0.111 |   -1245.1 |                  -94.8 |                     95.3 |

`at_1pct_risk_*`: shu bitimlar har birida 1% risk bilan bo'lganda (miqyosdan mustaqil). Mezonimiz: PF>1.3, DD<15%, 200+ bitim. S1 - EA qanday e'lon qilingan bo'lsa shunday. S2-S3 - EA'ning o'z sozlamalari. S4-S5 - bizning o'zgartirishimiz (EA'da yo'q).


S1: oxirgi bitim 2019-05-28. Undan keyingi ~5 yil davomida EA bitta ham bitim ochmadi: 2019-05-31 da qo'yilgan buy-limit (1293.74) narx 1294 dan 2950 ga ko'tarilib qaytmagani uchun hech qachon bajarilmadi, buyurtma GTC va MaxTrades=1 uni hisoblagani uchun EA to'xtab qoldi (kodda kutilayotgan buyurtmani o'chiradigan joy faqat CloseEOD, u standartda o'chiq).


### S2 EA'ning CloseAtEOD=true opsiyasi: yillar bo'yicha

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |      162 |       7.4 | 0.41 |  -0.1   |     -72.7 |                  -15.1 |
| 2019 |      178 |       9   | 0.43 |  -0.103 |     -82.5 |                  -16.9 |
| 2020 |      193 |      10.4 | 0.53 |  -0.125 |    -108.6 |                  -21.8 |
| 2021 |      282 |      11   | 0.79 |  -0.041 |     -51.8 |                  -11.3 |
| 2022 |      219 |      10   | 0.69 |  -0.062 |     -61.1 |                  -13   |
| 2023 |      197 |       9.6 | 0.49 |  -0.111 |     -98.1 |                  -19.8 |
| 2024 |      149 |       8.7 | 0.38 |  -0.164 |    -109.8 |                  -21.8 |
| 2025 |       65 |      16.9 | 1.04 |   0.01  |       2.9 |                    0.5 |

Oylar: 86 oydan **7 foydali, 42 zararli, 37 bitimsiz** (R bo'yicha). Chiqishlar: {'sl': 741, 'sl_gap': 533, 'tp': 108, 'eod': 63}


### S3 S2 + break-even o'chiq: yillar bo'yicha

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |      103 |      41.7 | 0.71 |  -0.145 |     -67.3 |                  -14.3 |
| 2019 |      111 |      30.6 | 0.44 |  -0.318 |    -158.7 |                  -30.1 |
| 2020 |      147 |      42.2 | 0.95 |  -0.029 |     -18.9 |                   -5   |
| 2021 |      206 |      44.2 | 1.08 |   0.045 |      42.1 |                    8.2 |
| 2022 |      159 |      40.3 | 0.85 |  -0.086 |     -61.9 |                  -13.7 |
| 2023 |      149 |      41.6 | 0.95 |  -0.031 |     -20.7 |                   -5.4 |
| 2024 |      113 |      34.5 | 0.68 |  -0.195 |     -98.9 |                  -20.3 |
| 2025 |       51 |      43.1 | 1.06 |   0.032 |       7.4 |                    1.3 |

Oylar: 86 oydan **19 foydali, 30 zararli, 37 bitimsiz** (R bo'yicha). Chiqishlar: {'sl': 548, 'tp': 310, 'eod': 179, 'sl_gap': 2}


### S4 bizning o'zgartirish: pending 20 baradan keyin bekor: yillar bo'yicha

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |      368 |       3.3 | 0.27 |  -0.13  |    -214.7 |                  -38.2 |
| 2019 |      414 |       7.7 | 0.55 |  -0.096 |    -178.2 |                  -33.2 |
| 2020 |      581 |      10.3 | 0.57 |  -0.115 |    -300.1 |                  -49.3 |
| 2021 |      512 |       8.6 | 0.56 |  -0.1   |    -229.6 |                  -40.5 |
| 2022 |      572 |      11.4 | 0.78 |  -0.047 |    -121.2 |                  -24.5 |
| 2023 |      495 |      10.3 | 0.66 |  -0.08  |    -178.2 |                  -33.4 |
| 2024 |      549 |      12.8 | 0.69 |  -0.083 |    -206.2 |                  -37.6 |
| 2025 |       89 |      14.6 | 0.84 |  -0.041 |     -16.5 |                   -3.8 |

Oylar: 86 oydan **12 foydali, 74 zararli, 0 bitimsiz** (R bo'yicha). Chiqishlar: {'sl': 1994, 'sl_gap': 1240, 'tp': 346}


### S5 S4 + break-even o'chiq: yillar bo'yicha

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |      197 |      27.9 | 0.56 |  -0.319 |    -283.2 |                  -47.4 |
| 2019 |      249 |      29.7 | 0.62 |  -0.269 |    -301.4 |                  -49.7 |
| 2020 |      432 |      36.6 | 0.84 |  -0.104 |    -202   |                  -38.2 |
| 2021 |      370 |      36.2 | 0.83 |  -0.111 |    -184.6 |                  -35.4 |
| 2022 |      392 |      39.5 | 0.95 |  -0.028 |     -50   |                  -13.1 |
| 2023 |      353 |      37.1 | 0.85 |  -0.1   |    -158.8 |                  -31.6 |
| 2024 |      427 |      38.9 | 0.93 |  -0.044 |     -85.3 |                  -19.8 |
| 2025 |       67 |      43.3 | 1.12 |   0.067 |      20.1 |                    4   |

Oylar: 86 oydan **21 foydali, 65 zararli, 0 bitimsiz** (R bo'yicha). Chiqishlar: {'sl': 1577, 'tp': 901, 'sl_gap': 9}


## README da'vosini arifmetik tekshiruv

Kod bo'yicha SL masofasi = FVGBuffer×1.5 = $4.5/oz, TP = ×1.5 = $6.75/oz. 0.01 lot = 1 oz. README: 64 bitim, yutuq ulushi 45.3%: kutilgan foyda = 64×(0.453×6.75 − 0.547×4.5) = $38. Hatto 64 ta bitimning hammasi yutsa ham = $432 (+4.3%). README'dagi +$4 874 (+48.7%) ushbu kod va 0.01 lot bilan mos kelmaydi (≈128 baravar katta).
