# N30 Gold Reversion TickRobust (n30dyn4m1c/gold-pro-scalper) — mustaqil sinov, XAUUSD M1, 2018-01 → 2025-02

Qoidalar EA'ning standart `Inp*` qiymatlari bilan, parametrlar o'zgartirilmagan. Bar-darajasidagi port: EA qarorni faqat yangi bar ochilishida, yopilgan bar ma'lumotlari bilan qabul qiladi, shuning uchun port EA mantiqiga yaqin. Ko'chirilmagan: MQL5 yangiliklar kalendari filtri (ma'lumot yo'q). Spred doimiy (ma'lumotda yo'q). Broker vaqti = Yevropa/Afina (ma'lumot manbai serveri vaqti). Boshlang'ich balans $10 000.


## Stsenariylar

|                                             |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |   at_1pct_risk_maxDD_pct | avg_R (95% CI)                    |
|:--------------------------------------------|---------:|----------:|-----:|--------:|----------:|-----------------------:|-------------------------:|:----------------------------------|
| T1 standart (spred $0.25, dinamik risk)     |      176 |      65.9 | 0.8  |  -0.02  |   -1067.3 |                   -3.6 |                      6.2 | -0.020 R (95% CI -0.064 … +0.024) |
| T2 spred $0.15                              |      390 |      66.7 | 0.81 |  -0.015 |   -1697.1 |                   -5.8 |                      7.2 | -0.015 R (95% CI -0.039 … +0.009) |
| T3 spred $0.40                              |       45 |      60   | 0.66 |  -0.061 |    -816.8 |                   -2.7 |                      3.8 | -0.061 R (95% CI -0.188 … +0.067) |
| T4 doimiy 2% risk (InpUseDynamicRisk=false) |      176 |      65.9 | 0.8  |  -0.02  |    -715.7 |                   -3.6 |                      6.2 | -0.020 R (95% CI -0.064 … +0.024) |
| T5 spred $0.25 + komissiya $7/lot           |      176 |      64.8 | 0.73 |  -0.029 |   -1444.3 |                   -5.1 |                      7.2 | -0.029 R (95% CI -0.073 … +0.015) |

`at_1pct_risk_*`: shu bitimlar har birida 1% risk bilan bo'lganda. Mezonimiz: PF>1.3, DD<15%, 200+ bitim.


### T1 standart (spred $0.25, dinamik risk)

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |        1 |       0   | 0    |  -0.049 |     -14.4 |                   -0   |
| 2019 |        6 |      66.7 | 0.22 |  -0.162 |    -286.4 |                   -1   |
| 2020 |       39 |      79.5 | 1.7  |   0.04  |     446.2 |                    1.6 |
| 2021 |       32 |      53.1 | 0.77 |  -0.028 |    -274.5 |                   -0.9 |
| 2022 |       37 |      64.9 | 0.66 |  -0.041 |    -453   |                   -1.5 |
| 2023 |       17 |      70.6 | 0.91 |  -0.006 |     -33.1 |                   -0.1 |
| 2024 |       32 |      59.4 | 0.52 |  -0.079 |    -699.9 |                   -2.5 |
| 2025 |       12 |      75   | 3.57 |   0.079 |     248   |                    1   |

Oylar: 86 oydan **35 foydali, 24 zararli, 27 bitimsiz** (R bo'yicha). Chiqishlar: {'z_revert': 109, 'tp': 44, 'sl': 23}. Yo'nalish: buy 95, sell 81. O'rtacha ushlab turish: 11.6 bar (M1).


### T2 spred $0.15

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |       17 |      29.4 | 0.14 |  -0.077 |    -384   |                   -1.3 |
| 2019 |       19 |      52.6 | 0.25 |  -0.09  |    -478.1 |                   -1.7 |
| 2020 |       71 |      78.9 | 1.24 |   0.017 |     316.8 |                    1.2 |
| 2021 |       79 |      60.8 | 0.83 |  -0.013 |    -312.4 |                   -1.1 |
| 2022 |       77 |      71.4 | 1.13 |   0.009 |     178.4 |                    0.7 |
| 2023 |       52 |      67.3 | 0.47 |  -0.06  |    -850.5 |                   -3.1 |
| 2024 |       56 |      67.9 | 0.68 |  -0.03  |    -429.8 |                   -1.7 |
| 2025 |       19 |      68.4 | 2.88 |   0.057 |     262.7 |                    1.1 |

Oylar: 86 oydan **42 foydali, 37 zararli, 7 bitimsiz** (R bo'yicha). Chiqishlar: {'z_revert': 211, 'tp': 119, 'sl': 57, 'time': 2, 'friday': 1}. Yo'nalish: buy 210, sell 180. O'rtacha ushlab turish: 11.1 bar (M1).


### T3 spred $0.40

|      |   trades |   win_pct |    PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|------:|--------:|----------:|-----------------------:|
| 2019 |        1 |       0   |  0    |  -1     |    -296   |                   -1   |
| 2020 |        6 |      83.3 |  2.38 |   0.092 |     156.3 |                    0.6 |
| 2021 |       10 |      50   |  0.79 |  -0.032 |     -97   |                   -0.3 |
| 2022 |        8 |      62.5 |  0.72 |  -0.054 |    -129.6 |                   -0.4 |
| 2023 |        4 |      25   |  0.09 |  -0.27  |    -310.6 |                   -1.1 |
| 2024 |       12 |      66.7 |  0.56 |  -0.094 |    -318.3 |                   -1.1 |
| 2025 |        4 |      75   | 35.99 |   0.166 |     178.4 |                    0.7 |

Oylar: 86 oydan **19 foydali, 13 zararli, 54 bitimsiz** (R bo'yicha). Chiqishlar: {'z_revert': 27, 'tp': 9, 'sl': 8, 'sl_gap': 1}. Yo'nalish: buy 27, sell 18. O'rtacha ushlab turish: 11.5 bar (M1).


### T4 doimiy 2% risk (InpUseDynamicRisk=false)

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |        1 |       0   | 0    |  -0.049 |      -9.7 |                   -0   |
| 2019 |        6 |      66.7 | 0.22 |  -0.162 |    -193.9 |                   -1   |
| 2020 |       39 |      79.5 | 1.73 |   0.04  |     301.5 |                    1.6 |
| 2021 |       32 |      53.1 | 0.77 |  -0.028 |    -176.4 |                   -0.9 |
| 2022 |       37 |      64.9 | 0.66 |  -0.041 |    -306.1 |                   -1.5 |
| 2023 |       17 |      70.6 | 0.9  |  -0.006 |     -25.9 |                   -0.1 |
| 2024 |       32 |      59.4 | 0.51 |  -0.079 |    -476.4 |                   -2.5 |
| 2025 |       12 |      75   | 3.56 |   0.079 |     171.3 |                    1   |

Oylar: 86 oydan **35 foydali, 24 zararli, 27 bitimsiz** (R bo'yicha). Chiqishlar: {'z_revert': 109, 'tp': 44, 'sl': 23}. Yo'nalish: buy 95, sell 81. O'rtacha ushlab turish: 11.6 bar (M1).


### T5 spred $0.25 + komissiya $7/lot

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |        1 |       0   | 0    |  -0.057 |     -17   |                   -0.1 |
| 2019 |        6 |      66.7 | 0.19 |  -0.171 |    -301.7 |                   -1   |
| 2020 |       39 |      76.9 | 1.55 |   0.031 |     350.8 |                    1.2 |
| 2021 |       32 |      53.1 | 0.71 |  -0.036 |    -354.1 |                   -1.2 |
| 2022 |       37 |      64.9 | 0.6  |  -0.05  |    -525.8 |                   -1.9 |
| 2023 |       17 |      64.7 | 0.8  |  -0.015 |     -74.1 |                   -0.3 |
| 2024 |       32 |      59.4 | 0.48 |  -0.088 |    -732.8 |                   -2.8 |
| 2025 |       12 |      75   | 3.15 |   0.071 |     210.4 |                    0.9 |

Oylar: 86 oydan **35 foydali, 24 zararli, 27 bitimsiz** (R bo'yicha). Chiqishlar: {'z_revert': 109, 'tp': 44, 'sl': 23}. Yo'nalish: buy 95, sell 81. O'rtacha ushlab turish: 11.6 bar (M1).
