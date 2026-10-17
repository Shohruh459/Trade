# Foydalanuvchi qoidasi (Daily bias + H4 EMA20 reclaim): natijalar (STRATEGY_H4.md)

## Asosiy qoida (xarajat $0.30 + 3% moliyalashtirish, risk 0.75%)
| davr          |   N |   meanR |   win_pct |    PF |   p_one |   hold_med_d |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |
|:--------------|----:|--------:|----------:|------:|--------:|-------------:|----------:|------------:|-----------------:|------------------:|
| Qaror 2019-25 | 172 |  0.0967 |      42.4 | 1.162 |   0.189 |          1.3 |      12.1 |        14   |             50.8 |              -2.4 |
| 2019-21       |  80 | -0.2319 |      33.8 | 0.665 |   0.945 |          1.3 |     -13.3 |        13.4 |             35.5 |              -2.4 |
| 2022-25       |  92 |  0.3824 |      50   | 1.742 |   0.007 |          1.3 |      29.4 |         4.5 |             64.7 |              -2.3 |

## Stress ($0.50, 5%), qaror davri: meanR 0.0562, p 0.303, maxDD 16.2%

## Tasodifiy kirish nazorati (bias yo'nalishida, 1000): real meanR 0.0967; tasodifiy o'rtacha 0.0672 (5–95%: -0.0826 … 0.2396); p = 0.374

## Mezonlar
- C1 meanR>0, p<=0.10, N>=60: YO`Q
- C2 stress meanR>0: OK
- C3 ikki yarimda meanR>0: YO`Q
- C4 profit factor>=1.2: YO`Q
- C5 random control p<=0.10: YO`Q
- C6 maxDD<=20%: OK

**Xulosa: FAIL**

## Sezgirlik (qaror davri, faqat ma'lumot)
| variant                   |   N |   meanR |   win_pct |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |
|:--------------------------|----:|--------:|----------:|------:|--------:|----------:|------------:|-----------------:|
| yangilik filtrisiz        | 173 |  0.0902 |      42.2 | 1.15  |   0.203 |      11.3 |        14.7 |             50.8 |
| risk 1%                   | 172 |  0.0967 |      42.4 | 1.162 |   0.189 |      16   |        18.4 |             50.8 |
| faqat Buy                 | 145 |  0.0998 |      41.4 | 1.164 |   0.209 |      10.5 |        13.8 |             51.8 |
| faqat Sell                |  28 |  0.156  |      50   | 1.299 |   0.249 |       3.2 |         3.7 |             60   |
| H4 kesishuv chiqishisiz   | 171 |  0.0895 |      42.7 | 1.148 |   0.21  |      11   |        14.2 |             50.8 |
| stop filtri (1.8 ATR) siz | 158 |  0.0534 |      41.8 | 1.09  |   0.317 |       5.6 |        14.2 |             53.1 |
| xarajatsiz                | 172 |  0.1574 |      42.4 | 1.276 |   0.077 |      21.3 |        11.5 |             50.8 |

## Yillar bo'yicha
|   date |   count |    mean |
|-------:|--------:|--------:|
|   2019 |      25 | -0.4648 |
|   2020 |      39 | -0.0915 |
|   2021 |      16 | -0.2104 |
|   2022 |      30 |  0.3576 |
|   2023 |      20 |  0.2949 |
|   2024 |      35 |  0.3038 |
|   2025 |       7 |  1.132  |
