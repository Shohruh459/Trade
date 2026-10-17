# Foydalanuvchi qoidasi (H1 bias + M5 EMA9 reclaim): natijalar (STRATEGY_LDN.md)

## Asosiy qoida (xarajat $0.30, risk 0.75%)
| davr          |    N |   meanR |   win_pct |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |   worst_month_pct |
|:--------------|-----:|--------:|----------:|------:|--------:|----------:|------------:|-----------------:|------------------:|
| Dev 2018-21   | 3117 | -0.2231 |      41.9 | 0.592 |       1 |     -99.5 |        99.5 |              6.2 |             -24.2 |
| Val 2022-23   | 1633 | -0.1848 |      41   | 0.647 |       1 |     -90   |        90.1 |              8.3 |             -19.8 |
| Final 2024-25 |  880 | -0.126  |      42.4 | 0.745 |       1 |     -57.3 |        62.3 |              7.1 |             -13.8 |
| Qaror 2022-25 | 2513 | -0.1642 |      41.5 | 0.68  |       1 |     -95.7 |        96.3 |              7.9 |             -19.8 |

## Stress ($0.50), qaror davri: meanR -0.2632, p 1.0, maxDD 99.4%

## Tasodifiy kirish nazorati (bias yo'nalishida, 1000): real meanR -0.1642; tasodifiy o'rtacha -0.1302 (5–95%: -0.1533 … -0.1066); p = 0.990

## Mezonlar
- C1 meanR>0, p<=0.10, N>=200: YO`Q
- C2 stress meanR>0: YO`Q
- C3 Val va Final alohida meanR>0: YO`Q
- C4 Dev ishonchli manfiy emas: YO`Q
- C5 random control p<=0.10: YO`Q
- C6 maxDD<=30% (qaror): YO`Q

**Xulosa: FAIL**

## Sezgirlik (qaror davri, faqat ma'lumot)
| variant                  |    N |   meanR |   win_pct |    PF |   p_one |   ret_pct |   maxDD_pct |   pos_months_pct |
|:-------------------------|-----:|--------:|----------:|------:|--------:|----------:|------------:|-----------------:|
| yangilik filtrisiz       | 2549 | -0.1644 |      41.4 | 0.68  |   1     |     -95.9 |        96.4 |              5.3 |
| risk 0.5%                | 2513 | -0.1642 |      41.5 | 0.68  |   1     |     -87.6 |        88.7 |              7.9 |
| risk 1%                  | 2513 | -0.1642 |      41.5 | 0.68  |   1     |     -98.5 |        98.8 |              7.9 |
| faqat Buy                | 1457 | -0.1377 |      43   | 0.726 |   1     |     -78.5 |        80.6 |             18.4 |
| faqat Sell               | 1056 | -0.2007 |      39.4 | 0.621 |   1     |     -80.1 |        81.5 |             17.1 |
| faqat London             | 1585 | -0.1845 |      40.8 | 0.649 |   1     |     -89.3 |        90.3 |              7.9 |
| faqat overlap            | 1683 | -0.1028 |      43.6 | 0.784 |   1     |     -73.7 |        76.4 |             23.7 |
| reclaim faqat oxirgi bar | 2373 | -0.1706 |      41.1 | 0.671 |   1     |     -95.5 |        95.9 |             10.5 |
| xarajatsiz               | 2513 | -0.0157 |      41.5 | 0.963 |   0.805 |     -29.7 |        50.4 |             42.1 |

## Yillar bo'yicha (qaror davri)
|   date |   count |    mean |
|-------:|--------:|--------:|
|   2022 |     812 | -0.1539 |
|   2023 |     821 | -0.2153 |
|   2024 |     733 | -0.1625 |
|   2025 |     147 |  0.0563 |
