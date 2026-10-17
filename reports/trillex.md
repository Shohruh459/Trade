# TRILLEX 10S BASIC (NadirAliOfficial/trillex-10s-ea) — tick sinovi, XAUUSD, Dukascopy tick ma'lumoti

Namuna oldindan belgilangan qoida bilan tanlangan: har yil (2019–2026) mart va sentyabr oyining boshidan boshlanadigan birinchi fayl, jami 15 fayl (15 kunlik yoki 30 kunlik oynalar). EA'ning 10 soniyalik sintetik bar mexanizmi tick darajasida ko'chirilgan; parametrlar standart, o'zgartirilmagan. R = bitim foydasi / SL masofasi ($2.00/oz); xarajatdan oldingi (gross) R — o'rta narxdan o'rta narxga.


## Stsenariylar (R bo'yicha, 1 uns/bitim)

|                                                       |   trades |   win_pct |   PF_R |   avg_R | avgR_CI       |   gross_avg_R |   med_hold_s | files_pos   |
|:------------------------------------------------------|---------:|----------:|-------:|--------:|:--------------|--------------:|-------------:|:------------|
| S1 Insane, haqiqiy spred (EA 30-pt cheklovi bilan)    |     6289 |      23.2 |   0.54 |  -0.118 | -0.137…-0.099 |         0.02  |          147 | 3/15        |
| S2 Insane, spred $0.25 (doimiy)                       |    12840 |      23.2 |   0.52 |  -0.118 | -0.130…-0.107 |         0.007 |          102 | 1/15        |
| S3 Insane, spred $0.10 (juda arzon)                   |    12840 |      29.8 |   0.77 |  -0.045 | -0.056…-0.033 |         0.005 |          104 | 1/15        |
| S4 Normal rejim (InpUseInsaneMode=false), spred $0.25 |    54140 |      14.8 |   0.33 |  -0.122 | -0.126…-0.118 |         0.003 |           11 | 0/15        |
| S5 Insane, spred $0.25, chiqish EMA5 bo'yicha         |    12838 |      14.6 |   0.34 |  -0.126 | -0.134…-0.118 |        -0.001 |           30 | 0/15        |

`gross_avg_R` — spred hisobga olinmagan o'rtacha R; `avg_R` — xarajatdan keyin. `files_pos` — namunalardan nechtasida jami R musbat.


## S2 Insane, spred $0.25 (doimiy): namunalar bo'yicha

|         |   trades |   avg_R |   gross_R |   win_pct |
|:--------|---------:|--------:|----------:|----------:|
| 2019-03 |      963 |  -0.122 |     0.003 |      15.1 |
| 2019-09 |     1206 |  -0.126 |    -0.001 |      20.6 |
| 2020-03 |     1150 |  -0.136 |    -0.011 |      25.8 |
| 2020-09 |     1167 |  -0.145 |    -0.02  |      24.7 |
| 2021-03 |     1184 |  -0.131 |    -0.006 |      22.5 |
| 2021-09 |     1313 |  -0.13  |    -0.005 |      20.2 |
| 2022-03 |      640 |  -0.113 |     0.012 |      28.3 |
| 2022-09 |      643 |  -0.094 |     0.031 |      23.6 |
| 2023-03 |      655 |  -0.095 |     0.03  |      27.8 |
| 2023-09 |      666 |  -0.133 |    -0.008 |      15.3 |
| 2024-03 |      566 |  -0.085 |     0.04  |      25.6 |
| 2024-09 |      669 |  -0.151 |    -0.026 |      22.3 |
| 2025-03 |      607 |  -0.147 |    -0.022 |      24.4 |
| 2025-09 |      777 |  -0.1   |     0.025 |      30.2 |
| 2026-03 |      634 |   0.002 |     0.127 |      28.7 |


## Haqiqiy Dukascopy spredi va EA'ning 30-punkt cheklovi

|         |   median_spread_usd |   pct_ticks_le_30pt |
|:--------|--------------------:|--------------------:|
| 2019-03 |                0.29 |                69.7 |
| 2019-09 |                0.3  |                48.4 |
| 2020-03 |                0.48 |                 7.1 |
| 2020-09 |                0.41 |                 7.3 |
| 2021-03 |                0.35 |                16.8 |
| 2021-09 |                0.32 |                33.2 |
| 2022-03 |                0.39 |                12.8 |
| 2022-09 |                0.33 |                24.9 |
| 2023-03 |                0.34 |                 7.1 |
| 2023-09 |                0.31 |                42.2 |
| 2024-03 |                0.33 |                 6.7 |
| 2024-09 |                0.39 |                 2.1 |
| 2025-03 |                0.54 |                 0.4 |
| 2025-09 |                0.56 |                 0.5 |
| 2026-03 |                0.79 |                 0.1 |


## EA'ning o'z lot qoidasi (kodda): lot = 1 × 10^floor(log10(balans/1000))

| Balans | Lot | 100 uns/lot, SL $2 | Bitta SL zarari | Balansga nisbatan |
|---|---|---|---|---|
| $500 | 1 | 100 oz | $200 | 40% |
| $1,000 | 1 | 100 oz | $200 | 20% |
| $5,000 | 1 | 100 oz | $200 | 4% |
| $9,999 | 1 | 100 oz | $200 | 2% |
| $10,000 | 10 | 1000 oz | $2,000 | 20% |
| $50,000 | 10 | 1000 oz | $2,000 | 4% |
| $100,000 | 100 | 10000 oz | $20,000 | 20% |

S2 stsenariysi EA'ning o'z lot qoidasi bilan (har namuna alohida boshlangan):

|:--------|:---------------------------------------------|
| $1,000  | 15/15 namunada balans yarmidan pastga tushdi |
| $10,000 | 15/15 namunada balans yarmidan pastga tushdi |
