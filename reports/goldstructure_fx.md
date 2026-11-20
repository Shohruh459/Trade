# GoldStructureEA muzlatilgan qoida: FX qo'shimcha dalil (qarorga kirmaydi)

EURUSD, GBPUSD, AUDUSD M1 (Dukascopy, 2020-04 → 2025-12), entry 2020-07-01 → 2025-12-31. Qoida va parametrlar oltindagi bilan bir xil; xarajat: spred 1.0 pip (0.0001), stress 1.5 pip; komissiya va slippage yo'q. Bir marta ishga tushirildi.

## ASOSIY (spred 1.0 pip)
| juft            |   N |   per_year |   win_pct |   meanR |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:----------------|----:|-----------:|----------:|--------:|------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| eur_usd         |   6 |        1.5 |      33.3 |  0      | 1     |   0.5   |      -0.1 |         3.9 |             40   |                -1 |             60 |
| gbp_usd         |   4 |        0.8 |      50   |  0.1577 | 1.315 |   0.401 |       0.6 |         1   |             50   |                -1 |             82 |
| aud_usd         |   4 |        0.8 |      25   | -0.25   | 0.667 |   0.65  |      -1   |         2   |             25   |                -1 |             39 |
| birlashtirilgan |  14 |        2.8 |      35.7 | -0.0264 | 0.959 |   0.532 |      -0.5 |         4   |             33.3 |                -1 |             56 |

### Birlashtirilgan, davrlar bo'yicha
| davr             |   N |   per_year |   win_pct |   meanR |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:-----------------|----:|-----------:|----------:|--------:|------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| 2020-07..2022-12 |   6 |        2.8 |      33.3 |  0      | 1     |   0.5   |      -0.1 |         2   |             20   |                -1 |             70 |
| 2023-01..2025-12 |   8 |        3.3 |      37.5 | -0.0461 | 0.926 |   0.548 |      -0.4 |         3.9 |             42.9 |                -1 |             47 |

### Yillar bo'yicha (birlashtirilgan)
|   entry |   count |   mean |
|--------:|--------:|-------:|
|    2020 |       2 | -1     |
|    2021 |       3 |  1     |
|    2022 |       1 | -1     |
|    2023 |       2 |  0.5   |
|    2024 |       2 | -1     |
|    2025 |       4 |  0.158 |

## STRESS (spred 1.5 pip)
| juft            |   N |   per_year |   win_pct |   meanR |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:----------------|----:|-----------:|----------:|--------:|------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| eur_usd         |   6 |        1.5 |      16.7 | -0.5    | 0.4   |   0.856 |      -3   |         4.9 |               20 |                -2 |             60 |
| gbp_usd         |   4 |        0.8 |      50   |  0.1519 | 1.304 |   0.404 |       0.6 |         1   |               50 |                -1 |             82 |
| aud_usd         |   4 |        0.8 |      25   | -0.25   | 0.667 |   0.65  |      -1   |         2   |               25 |                -1 |             39 |
| birlashtirilgan |  14 |        2.8 |      28.6 | -0.2423 | 0.661 |   0.762 |      -3.4 |         6.8 |               25 |                -2 |             56 |

### Voronka (asosiy ssenariy)
|                    |   eur_usd |   gbp_usd |   aud_usd |
|:-------------------|----------:|----------:|----------:|
| bos_ok             |       899 |       828 |       854 |
| z_created          |       671 |       606 |       601 |
| z_no_zone          |        45 |        35 |        43 |
| z_pre_violated     |        15 |        18 |        23 |
| z_bad_height       |       168 |       169 |       187 |
| episodes           |       702 |       622 |       633 |
| episodes_P         |       238 |       223 |       221 |
| episodes_M         |        52 |        35 |        41 |
| signals            |        20 |        14 |        16 |
| retest3_cancel     |       126 |       126 |       129 |
| zone_expired       |        80 |        70 |        60 |
| zone_replaced      |       209 |       186 |       189 |
| zone_invalid_close |       250 |       220 |       219 |
| exp_window         |         0 |         0 |         0 |
| exp_session        |         7 |         5 |         9 |
| exp_news           |         0 |         0 |         1 |
| exp_busy           |         0 |         0 |         0 |
| exp_block          |         0 |         0 |         0 |
| exp_bias           |         3 |         1 |         0 |
| exp_zone           |         0 |         0 |         1 |
| exp_a1             |         1 |         3 |         1 |
| exp_gap            |         1 |         0 |         0 |
| exp_pre_start      |         2 |         1 |         0 |
| exp_noroom         |         0 |         0 |         0 |
| trades             |         6 |         4 |         4 |
| breach_exits       |         0 |         0 |         0 |
| force_exits        |         0 |         1 |         0 |
| m_checks           |      3156 |      2839 |      2669 |
