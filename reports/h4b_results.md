# Foydalanuvchi qoidasi (Daily bias + H4 Donchian breakout): natijalar (STRATEGY_H4_BREAKOUT.md)

## Asosiy qoida (xarajat $0.30 + 3% moliyalashtirish, risk 0.75%)
| davr          |   N |   meanR |   win_pct |    PF |   p_one |   hold_med_d |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |
|:--------------|----:|--------:|----------:|------:|--------:|-------------:|----------:|------------:|-----------------:|------------------:|
| Qaror 2019-25 | 197 |  0.0908 |      37.1 | 1.198 |   0.154 |          0.5 |      13.4 |         6.7 |             56.1 |              -3.1 |
| 2019-21       |  90 |  0.1085 |      40   | 1.248 |   0.206 |          0.5 |       7.2 |         4   |             54.8 |              -2.7 |
| 2022-25       | 107 |  0.0759 |      34.6 | 1.16  |   0.265 |          0.5 |       5.8 |         6.7 |             57.1 |              -3.1 |

## Stress ($0.50, 5%), qaror davri: meanR 0.0519, p 0.279, maxDD 7.8%

## Tasodifiy kirish nazorati (bias yo'nalishida, 1000): real meanR 0.0908; tasodifiy o'rtacha -0.0160 (5–95%: -0.0971 … 0.0811); p = 0.036

## Mezonlar
- C1 meanR>0, p<=0.10, N>=60: YO`Q
- C2 stress meanR>0: OK
- C3 ikki yarimda meanR>0: OK
- C4 profit factor>=1.2: YO`Q
- C5 random control p<=0.10: OK
- C6 maxDD<=20%: OK

**Xulosa: FAIL**

## Sezgirlik (qaror davri, faqat ma'lumot)
| variant                   |   N |   meanR |   win_pct |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |
|:--------------------------|----:|--------:|----------:|------:|--------:|----------:|------------:|-----------------:|
| yangilik filtrisiz        | 198 |  0.0873 |      36.9 | 1.19  |   0.163 |      12.9 |         6.7 |             56.1 |
| risk 1%                   | 197 |  0.0908 |      37.1 | 1.198 |   0.154 |      17.8 |         8.8 |             56.1 |
| faqat Buy                 | 168 |  0.0837 |      38.1 | 1.18  |   0.198 |      10.3 |         8.2 |             56.1 |
| faqat Sell                |  28 |  0.1222 |      28.6 | 1.285 |   0.287 |       2.5 |         2.8 |             50   |
| kanal-chiqishsiz          | 184 |  0.0618 |      44   | 1.105 |   0.278 |       7.8 |        11.7 |             60.6 |
| stop filtri (2.0 ATR) siz | 193 |  0.1225 |      38.3 | 1.284 |   0.094 |      18.5 |         9.1 |             56.7 |
| xarajatsiz                | 197 |  0.1491 |      37.1 | 1.346 |   0.049 |      23.6 |         5.6 |             59.1 |

## Yillar bo'yicha
|   date |   count |    mean |
|-------:|--------:|--------:|
|   2019 |      35 |  0.0695 |
|   2020 |      40 |  0.1539 |
|   2021 |      15 |  0.0786 |
|   2022 |      32 |  0.0847 |
|   2023 |      30 | -0.0309 |
|   2024 |      34 |  0.2541 |
|   2025 |      11 | -0.2091 |
