# GoldStructureEA: tasdiqlovchi sinov natijalari (STRATEGY_GOLDSTRUCTURE.md v3, muzlatilgan)

Bitta tasdiqlovchi ishga tushirish; parametrlar muzlatilgan SPEC (v3) bo'yicha, hech biri o'zgartirilmagan. Ishlab chiqish davrida faqat 2018-04..2018-07 kesimida smoke test (kod xatolarini tuzatish uchun) o'tkazilgan.

Birliklar: narx $/oz; spred to'liq aylanma ($/oz); 1 lot = 100 oz. Risk 1% hisob equity; net R = (foyda − xarajatlar)/s.

## 1. ASOSIY ssenariy (spred $0.30, komissiya 0, slippage 0) — hisoblash 1.0s

| davr                     |   N |   per_year |   win_pct |    meanR |      PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:-------------------------|----:|-----------:|----------:|---------:|--------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| Dev 2018-04..2021-12     |   8 |        3   |      37.5 |  -0.0331 |   0.94  |   0.531 |      -0.3 |         2.4 |             28.6 |                -1 |             87 |
| Val 2022-01..2023-12     |   2 |        2   |     100   | nan      | nan     | nan     |       4   |         0   |            100   |                 2 |             83 |
| Final 2024-01..2025-02   |   4 |        7.5 |      50   |   0.5    |   2     |   0.252 |       2   |         1   |             50   |                -1 |            158 |
| Hammasi 2018-04..2025-02 |  14 |        2.6 |      50   |   0.4097 |   1.895 |   0.142 |       5.7 |         2.4 |             46.2 |                -1 |             96 |

### Filtrlar voronkasi (hamma davr)
|                    |   soni |
|:-------------------|-------:|
| bos_ok             |    946 |
| z_created          |    672 |
| z_no_zone          |     51 |
| z_pre_violated     |     22 |
| z_bad_height       |    201 |
| episodes           |    702 |
| episodes_P         |    269 |
| episodes_M         |     51 |
| signals            |     27 |
| retest3_cancel     |    134 |
| zone_expired       |     85 |
| zone_replaced      |    192 |
| zone_invalid_close |    245 |
| exp_window         |      0 |
| exp_session        |     11 |
| exp_news           |      0 |
| exp_busy           |      0 |
| exp_block          |      0 |
| exp_bias           |      1 |
| exp_zone           |      0 |
| exp_a1             |      1 |
| exp_gap            |      0 |
| exp_pre_start      |      0 |
| exp_noroom         |      0 |
| trades             |     14 |
| breach_exits       |      0 |
| force_exits        |      2 |
| m_checks           |   3140 |

### Chiqish sabablari
| reason                   |   soni |
|:-------------------------|-------:|
| SL                       |      6 |
| TP                       |      6 |
| NY 16:30 majburiy yopish |      2 |

### Yillar bo'yicha
|   entry |   count |   mean |
|--------:|--------:|-------:|
|    2019 |       3 | -0.618 |
|    2020 |       2 |  2     |
|    2021 |       3 | -0.803 |
|    2022 |       1 |  2     |
|    2023 |       1 |  2     |
|    2024 |       4 |  0.5   |

### Yangilik filtri qismlari
| qism                                                       |   N |   per_year |   win_pct |   meanR |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:-----------------------------------------------------------|----:|-----------:|----------:|--------:|------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| F1: filtr to'liq (2018-04..2018-12 va 2023-01..2025-02)    |   5 |        4.1 |      60   |  0.8    | 3     |   0.112 |       4   |         1   |             60   |                -1 |            108 |
| F2: filtr to'liq emas (GDP bo'shliqlari, 2019-01..2022-12) |   9 |        2.9 |      44.4 |  0.1928 | 1.394 |   0.332 |       1.7 |         2.4 |             37.5 |                -1 |             77 |

## 2. STRESS ssenariy (spred $0.50, slippage kirish $0.10 + SL $0.10)
| davr                     |   N |   per_year |   win_pct |    meanR |      PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:-------------------------|----:|-----------:|----------:|---------:|--------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| Dev 2018-04..2021-12     |   8 |        3   |      37.5 |  -0.2255 |   0.608 |   0.734 |      -1.8 |         2.5 |             28.6 |                -1 |            136 |
| Val 2022-01..2023-12     |   2 |        2   |     100   | nan      | nan     | nan     |       4   |         0   |            100   |                 2 |             84 |
| Final 2024-01..2025-02   |   4 |        7.5 |      25   |  -0.279  |   0.642 |   0.664 |      -1.1 |         3.1 |             25   |                -1 |             64 |
| Hammasi 2018-04..2025-02 |  14 |        2.6 |      42.9 |   0.0772 |   1.14  |   0.413 |       1   |         3.1 |             38.5 |                -1 |             86 |

## 3. KOMISSIYA sezgirligi (asosiy + $0.07/oz = $7/lot)
| davr                     |   N |   per_year |   win_pct |    meanR |      PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |   hold_med_min |
|:-------------------------|----:|-----------:|----------:|---------:|--------:|--------:|----------:|------------:|-----------------:|------------------:|---------------:|
| Dev 2018-04..2021-12     |   8 |        3   |      37.5 |  -0.0603 |   0.894 |   0.556 |      -0.5 |         2.4 |             28.6 |                -1 |             87 |
| Val 2022-01..2023-12     |   2 |        2   |     100   | nan      | nan     | nan     |       4   |         0   |            100   |                 2 |             83 |
| Final 2024-01..2025-02   |   4 |        7.5 |      50   |   0.4757 |   1.927 |   0.263 |       1.9 |         1   |             50   |                -1 |            158 |
| Hammasi 2018-04..2025-02 |  14 |        2.6 |      50   |   0.3835 |   1.813 |   0.158 |       5.4 |         2.4 |             46.2 |                -1 |             96 |

## 4. Tasodifiy kirish nazorati (1000/1000 to'plam; eligible M5 barlar 45775)
Real o'rtacha net R 0.4097; tasodifiy o'rtacha -0.1861 (5–95%: -0.7169 … 0.3869); **p = 0.039**

## 5. Qaror mezonlari (oltin, qaror davri 2018-04..2025-02)
- G1 N>=100, meanR>0, p<=0.10: YO`Q
- G2 stress meanR>0: OK
- G3 Dev/Val/Final meanR>0 (N>=15, kamida 2 davr): YO`Q
- G4 profit factor >= 1.2: OK
- G5 tasodifiy nazorat p<=0.10: OK
- G6 maxDD <= 20%: OK

**Xulosa: XULOSASIZ (N=14 < 100): qoida o'tmagan hisoblanadi; parametr o'zgartirilmaydi**

## 6. Sezgirlik (faqat tavsifiy, qarorga ta'sir qilmaydi)
| variant                                          |   N |   per_year |   win_pct |   meanR |    PF |   p_one |   ret_pct |   maxDD_pct |
|:-------------------------------------------------|----:|-----------:|----------:|--------:|------:|--------:|----------:|------------:|
| A8 (a): diapazon >= 1.0 ATR                      |  13 |        2.4 |      53.8 |  0.4727 | 2.024 |   0.123 |       6.2 |         2   |
| A8 (c): tana >= 0.7 ATR                          |  13 |        2.4 |      53.8 |  0.4727 | 2.024 |   0.123 |       6.2 |         2   |
| sessiya S2                                       |  16 |        3   |      50   |  0.421  | 1.909 |   0.121 |       6.8 |         2.4 |
| sessiya S3                                       |   7 |        1.3 |      57.1 |  0.5337 | 2.55  |   0.154 |       3.7 |         1.4 |
| sessiya S4                                       |  11 |        2   |      36.4 |  0.1446 | 1.248 |   0.367 |       1.5 |         2.4 |
| NY 16:30 yopishsiz (swap bilan)                  |  14 |        2.6 |      50   |  0.4896 | 1.976 |   0.094 |       6.9 |         3   |
| zona = tana                                      |   3 |        0.6 |      33.3 |  0      | 1     |   0.5   |      -0   |         1   |
| M15 swing k=2                                    |  14 |        2.3 |      57.1 |  0.5818 | 2.358 |   0.066 |       8.3 |         2   |
| M15 swing k=4                                    |   9 |        1.7 |      33.3 | -0.1405 | 0.766 |   0.64  |      -1.3 |         2.4 |
| P-M oynasi 1 bar                                 |   8 |        1.7 |      62.5 |  0.9488 | 4.15  |   0.025 |       7.8 |         1.4 |
| A1 stop filtrisiz                                |  15 |        2.8 |      46.7 |  0.3157 | 1.639 |   0.194 |       4.7 |         2.4 |
| MSS episodni tugatuvchi barda ham (spec talqini) |  15 |        2.8 |      53.3 |  0.5157 | 2.207 |   0.083 |       7.9 |         1.8 |
| zona muddati 48                                  |  14 |        2.6 |      50   |  0.4097 | 1.895 |   0.142 |       5.7 |         2.4 |
| zona muddati 192                                 |  14 |        2.6 |      50   |  0.4097 | 1.895 |   0.142 |       5.7 |         2.4 |
| faqat BUY                                        |   5 |        0.9 |      60   |  0.5471 | 2.94  |   0.18  |       2.7 |         1   |
| faqat SELL                                       |   9 |        1.9 |      44.4 |  0.3333 | 1.6   |   0.251 |       2.9 |         2   |
| yangilik filtri GDP siz                          |  14 |        2.6 |      50   |  0.4097 | 1.895 |   0.142 |       5.7 |         2.4 |
| yangilik filtrisiz                               |  14 |        2.6 |      50   |  0.4097 | 1.895 |   0.142 |       5.7 |         2.4 |

## 7. Tavsifiy: 2026-09 va 2026-10 (MetaQuotes demo M1, yangilik filtri yo'q; qarorga kirmaydi)
Savdo yo'q.

Voronka: {'bos_ok': 24, 'z_created': 18, 'z_no_zone': 2, 'z_pre_violated': 0, 'z_bad_height': 4, 'episodes': 24, 'episodes_P': 7, 'episodes_M': 4, 'signals': 0, 'retest3_cancel': 6, 'zone_expired': 2, 'zone_replaced': 3, 'zone_invalid_close': 6, 'exp_window': 0, 'exp_session': 0, 'exp_news': 0, 'exp_busy': 0, 'exp_block': 0, 'exp_bias': 0, 'exp_zone': 0, 'exp_a1': 0, 'exp_gap': 0, 'exp_pre_start': 0, 'exp_noroom': 0, 'trades': 0, 'breach_exits': 0, 'force_exits': 0, 'm_checks': 92}


Jami hisoblash vaqti: 13 s. Kod: backtest/goldstructure.py, backtest/gs_run.py.
