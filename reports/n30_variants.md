# gold-pro-scalper: klassik MR va Trend Breakout — mustaqil sinov, XAUUSD M1, 2018-01 → 2025-02

Parametrlar EA standarti, o'zgartirilmagan. M1 bar-darajasidagi port (tick-darajali mantiqning bir qismi taxminiy: 3-tick tasdiq, tezlik bloki, jonli indikatorlar). Yangiliklar filtri yo'q (ma'lumot yo'q). R = foyda / SL masofasi. Mezon: PF>1.3, DD<15%, 200+ bitim.


## Umumiy

|                             |   trades |   win_pct |   PF |   avg_R | avgR_CI       |   at_1pct_net_pct |   at_1pct_maxDD_pct |
|:----------------------------|---------:|----------:|-----:|--------:|:--------------|------------------:|--------------------:|
| Klassik MR, spred $0.25     |       81 |      58   | 1.43 |   0.09  | -0.043…+0.223 |               7.4 |                 5.1 |
| Klassik MR, spred $0.15     |      845 |      54.7 | 0.88 |  -0.019 | -0.043…+0.005 |             -15.1 |                23   |
| Klassik MR, spred $0.40     |       16 |      68.8 | 2.65 |   0.385 | -0.073…+0.843 |               6.3 |                 2   |
| Trend Breakout, spred $0.25 |     6615 |      28.1 | 0.63 |  -0.029 | -0.034…-0.024 |             -85.7 |                85.8 |
| Trend Breakout, spred $0.15 |     5770 |      30.3 | 0.72 |  -0.021 | -0.026…-0.015 |             -69.7 |                69.9 |
| Trend Breakout, spred $0.40 |     5825 |      24.3 | 0.49 |  -0.044 | -0.048…-0.039 |             -92.2 |                92.2 |

- Klassik MR, spred $0.25: ATR-nisbiy spred cheklovi (spred ≤ M1 ATR × 12%) savdo oynasi vaqtining **1.3%** da o'tadi.

- Klassik MR, spred $0.15: ATR-nisbiy spred cheklovi (spred ≤ M1 ATR × 12%) savdo oynasi vaqtining **8.6%** da o'tadi.

- Klassik MR, spred $0.40: ATR-nisbiy spred cheklovi (spred ≤ M1 ATR × 12%) savdo oynasi vaqtining **0.2%** da o'tadi.


### Klassik MR, spred $0.25

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2020 |       49 |      67.3 | 2.51 |   0.225 |    3724.4 |                   11.5 |
| 2021 |        3 |       0   | 0    |  -0.664 |    -795.1 |                   -2   |
| 2022 |        5 |      40   | 0.2  |  -0.343 |    -649.3 |                   -1.7 |
| 2024 |       19 |      47.4 | 0.92 |  -0.015 |    -118.6 |                   -0.3 |
| 2025 |        5 |      60   | 1.15 |   0.047 |      71.3 |                    0.2 |

Oylar: 86 oydan **9 foydali, 11 zararli, 66 bitimsiz**. Chiqishlar: {'gravity': 47, 'sl': 31, 'tp': 2, 'sl_gap': 1}. O'rtacha ushlab turish: 5 min.


### Klassik MR, spred $0.15

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2019 |        9 |      33.3 | 0.62 |  -0.071 |    -187.4 |                   -0.6 |
| 2020 |      289 |      60.6 | 1.16 |   0.027 |    2258.1 |                    7.7 |
| 2021 |       82 |      53.7 | 0.59 |  -0.066 |   -1845.2 |                   -5.3 |
| 2022 |      104 |      48.1 | 0.66 |  -0.059 |   -1729.4 |                   -6   |
| 2023 |       73 |      46.6 | 0.62 |  -0.064 |   -1115.3 |                   -4.6 |
| 2024 |      238 |      55.9 | 0.9  |  -0.015 |    -784.9 |                   -3.5 |
| 2025 |       50 |      46   | 0.68 |  -0.064 |    -626   |                   -3.2 |

Oylar: 86 oydan **23 foydali, 40 zararli, 23 bitimsiz**. Chiqishlar: {'gravity': 472, 'sl': 364, 'sl_gap': 6, 'tp': 2, 'friday': 1}. O'rtacha ushlab turish: 6 min.


### Klassik MR, spred $0.40

|      |   trades |   win_pct |     PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-------:|--------:|----------:|-----------------------:|
| 2020 |       14 |      71.4 |   3.52 |   0.472 |    2086.9 |                    6.8 |
| 2022 |        1 |       0   |   0    |  -1     |    -360   |                   -1   |
| 2024 |        1 |     100   | inf    |   0.548 |     188.3 |                    0.5 |

Oylar: 86 oydan **2 foydali, 1 zararli, 83 bitimsiz**. Chiqishlar: {'gravity': 9, 'sl': 4, 'tp': 2, 'sl_gap': 1}. O'rtacha ushlab turish: 4 min.


### Trend Breakout, spred $0.25

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |     1024 |      22.9 | 0.44 |  -0.029 |   -2217   |                  -25.7 |
| 2019 |     1075 |      26.5 | 0.43 |  -0.031 |   -1868.6 |                  -28.6 |
| 2020 |      806 |      26.3 | 0.67 |  -0.038 |   -1332.1 |                  -26.8 |
| 2021 |      855 |      27.7 | 0.6  |  -0.032 |   -1444.1 |                  -24.3 |
| 2022 |      891 |      30.4 | 0.68 |  -0.028 |    -855.4 |                  -22   |
| 2023 |      914 |      30.4 | 0.75 |  -0.02  |    -568.1 |                  -16.7 |
| 2024 |      914 |      32.8 | 0.75 |  -0.026 |    -569.8 |                  -21.3 |
| 2025 |      136 |      31.6 | 0.61 |  -0.039 |    -107.1 |                   -5.2 |

Oylar: 86 oydan **13 foydali, 73 zararli, 0 bitimsiz**. Chiqishlar: {'sl': 6544, 'sl_gap': 61, 'tp': 10}. O'rtacha ushlab turish: 13 min.


### Trend Breakout, spred $0.15

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |      898 |      26.8 | 0.55 |  -0.02  |   -1407.6 |                  -16.6 |
| 2019 |      931 |      28.5 | 0.49 |  -0.025 |   -1534.6 |                  -21.1 |
| 2020 |      692 |      29.8 | 0.7  |  -0.027 |   -1015   |                  -17.4 |
| 2021 |      743 |      29.6 | 0.68 |  -0.023 |    -786.7 |                  -15.9 |
| 2022 |      790 |      31.4 | 0.84 |  -0.015 |    -619.9 |                  -11.5 |
| 2023 |      805 |      33.2 | 0.89 |  -0.008 |    -373.5 |                   -6.2 |
| 2024 |      795 |      33.2 | 0.73 |  -0.024 |   -1015.8 |                  -17.7 |
| 2025 |      116 |      32.8 | 0.7  |  -0.028 |    -127.8 |                   -3.2 |

Oylar: 86 oydan **16 foydali, 70 zararli, 0 bitimsiz**. Chiqishlar: {'sl': 5709, 'sl_gap': 51, 'tp': 10}. O'rtacha ushlab turish: 13 min.


### Trend Breakout, spred $0.40

|      |   trades |   win_pct |   PF |   avg_R |   net_usd |   at_1pct_risk_net_pct |
|-----:|---------:|----------:|-----:|--------:|----------:|-----------------------:|
| 2018 |     1125 |      20.2 | 0.33 |  -0.041 |   -3219.8 |                  -37.1 |
| 2019 |     1195 |      21.1 | 0.32 |  -0.045 |   -2798.7 |                  -41.9 |
| 2020 |      909 |      25.9 | 0.53 |  -0.049 |   -1799.9 |                  -36   |
| 2021 |      951 |      25.3 | 0.49 |  -0.046 |   -1149.2 |                  -35.6 |
| 2022 |     1010 |      27.6 | 0.55 |  -0.045 |    -494.8 |                  -36.6 |
| 2023 |      635 |      28.8 | 0.64 |  -0.032 |    -204.5 |                  -18.6 |

Oylar: 86 oydan **1 foydali, 67 zararli, 18 bitimsiz**. Chiqishlar: {'sl': 5774, 'sl_gap': 44, 'tp': 7}. O'rtacha ushlab turish: 13 min.
