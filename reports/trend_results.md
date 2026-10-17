# Kunlik trend/momentum — natijalar (reja: STRATEGY_TREND.md, commit ac9c18a)

Oltin: 2004-06-11 … 2025-02-28, 5322 kun. Tasdiqlash: Euro, United Kingdom, Japan, Switzerland, Canada, Australia, New Zealand, Sweden, Brent (2000-01-03 … 2025-12-31). Hamma parametrlar rejadagidek, sozlanmagan.

Ma'lumot sifati: kunlik oltin yopilishi mustaqil manba (alshahri BID H1) bilan solishtirildi; to'liq kunlarda (≥20 bar) kunlik daromadlar korrelyatsiyasi **0.998** (talab ≥0.99, bajarildi). Barcha kunlar bo'yicha 0.987: farq mustaqil manbaning to'liq bo'lmagan kunlaridan. M1 bilan solishtirish mustaqil emas (bir manba).


## Stage 1: oltin (sof, 10% vol maqsad, $0.50 xarajat, 3% moliyalashtirish)

| cell              |   net_sharpe |   nw_t |   timing_p |   eraA |   eraB |   eraC |   maxDD_pct |   stress_sharpe |   changes |   ann_ret_pct |   avg_abs_pos |
|:------------------|-------------:|-------:|-----------:|-------:|-------:|-------:|------------:|----------------:|----------:|--------------:|--------------:|
| S1 TSMOM-252      |        0.232 |   0.99 |     0.0466 |   0.93 |  -0.34 |   0.15 |        48.1 |           0.053 |       135 |          2.4  |          0.69 |
| S2 Ansambl        |        0.314 |   1.36 |     0.0184 |   0.85 |  -0.25 |   0.31 |        25.2 |           0.111 |       483 |          2.49 |          0.42 |
| S3 MA50/200       |        0.16  |   0.68 |     0.2062 |   0.94 |  -0.65 |   0.26 |        52.1 |           0.009 |        29 |          1.65 |          0.69 |
| S4 Donchian 55/20 |        0.11  |   0.47 |     0.1598 |   0.38 |  -0.34 |   0.33 |        36.3 |          -0.029 |       177 |          0.91 |          0.41 |


Tavsif (qarorga ta'sir qilmaydi): oltinga nisbatan alfa/beta va long/flat varianti:

| cell              |   alpha_pct_yr |   alpha_t |   beta |   LF_sharpe |   LF_maxDD_pct |
|:------------------|---------------:|----------:|-------:|------------:|---------------:|
| S1 TSMOM-252      |          -0.15 |     -0.06 |  0.235 |       0.515 |           28.6 |
| S2 Ansambl        |           0.74 |      0.43 |  0.162 |       0.471 |           19.2 |
| S3 MA50/200       |          -0.37 |     -0.16 |  0.187 |       0.47  |           36.7 |
| S4 Donchian 55/20 |          -0.09 |     -0.04 |  0.092 |       0.539 |           19.2 |


Benchmark: oltin buy&hold (shu davr, 2005-06-24 dan) Sharpe 0.63, maksimal drawdown 44.6%.


## Stage 2: mustaqil aktivlar portfeli (8 valyuta + Brent, faqat narx)

| cell              |   port_sharpe |   port_t |   timing_p | positive   |   maxDD_pct |
|:------------------|--------------:|---------:|-----------:|:-----------|------------:|
| S1 TSMOM-252      |         0.21  |     1.05 |     0.037  | 8/9        |        18.3 |
| S2 Ansambl        |         0.173 |     0.88 |     0.024  | 7/9        |        16.2 |
| S3 MA50/200       |         0.193 |     1    |     0.096  | 6/9        |        24.8 |
| S4 Donchian 55/20 |         0.07  |     0.36 |     0.2293 | 6/9        |        17.9 |


Aktivlar bo'yicha sof Sharpe:

|                |   S1 TSMOM-252 |   S2 Ansambl |   S3 MA50/200 |   S4 Donchian 55/20 |
|:---------------|---------------:|-------------:|--------------:|--------------------:|
| Euro           |           0.08 |         0.29 |          0.2  |                0.27 |
| United Kingdom |           0.02 |         0.16 |         -0.03 |                0.06 |
| Japan          |           0.24 |         0.15 |         -0.02 |                0.03 |
| Switzerland    |          -0.02 |        -0.14 |          0    |               -0.02 |
| Canada         |           0.01 |        -0.08 |         -0.06 |                0.01 |
| Australia      |           0.2  |         0.02 |          0.14 |               -0.26 |
| New Zealand    |           0.18 |         0.09 |          0.13 |               -0.07 |
| Sweden         |           0.09 |         0.19 |          0.45 |                0.22 |
| Brent          |           0.28 |         0.25 |          0.19 |                0.13 |


## Oldindan belgilangan mezon bo'yicha qaror

(a) Sharpe≥0.30, (b) t≥2.0, (c) timing p≤0.10, (d) davrlar, (e) DD≤25%, (f) stress, (g) ≥20 almashtirish | (h) portfel Sharpe≥0.20 & t≥1.65, (i) ≥6/9 aktiv>0, (j) portfel timing p≤0.10

| cell              |   a |   b |   c |   d |   e |   f |   g |   h |   i |   j |   PASS |
|:------------------|----:|----:|----:|----:|----:|----:|----:|----:|----:|----:|-------:|
| S1 TSMOM-252      |   0 |   0 |   1 |   0 |   0 |   1 |   1 |   0 |   1 |   1 |      0 |
| S2 Ansambl        |   1 |   0 |   1 |   1 |   0 |   1 |   1 |   0 |   1 |   1 |      0 |
| S3 MA50/200       |   0 |   0 |   0 |   0 |   0 |   1 |   1 |   0 |   1 |   1 |      0 |
| S4 Donchian 55/20 |   0 |   0 |   0 |   0 |   0 |   0 |   1 |   0 |   1 |   0 |      0 |


## Kod to'g'riligi tekshiruvi (natijadan keyin)
- Realized yillik vol (sof daromad): S1 10.3%, S2 7.9%, S3 10.3%, S4 8.2% (maqsad 10%; S2/S4 pozitsiyalari ko'p vaqt kichik, shuning uchun past). Maksimal |leverage| ≤ 1.53.
- Bitta kun (2010-05-04, S1) qo'lda hisoblandi: −0.007016, kod bilan bir xil.
- S1 ning 48.1% drawdowni 2014-11-05 → 2023-10-05 (9 yil): trend strategiyasi gold yon harakat/qaytishlarida yangi cho'qqiga chiqa olmadi.

## Xulosa
- **Hech bir hujayra mezondan o'tmadi** (4 ta hujayradan 0 ta PASS). Stage 1 da hamma hujayra uchun (b) t ≥ 2.0 bajarilmadi (t = 0.47…1.36), (a) Sharpe ≥ 0.30 faqat S2 da (0.314), lekin S2 ning drawdowni 25.2% (> 25%).
- Oltin buy&hold shu davrda Sharpe 0.63 (maksimal drawdown 44.6%) ko'rsatgan: strategiyalar bundan past. Oltinga nisbatan alfa ≈ 0 (alfa t = −0.16…0.43).
- Stage 2 (mustaqil aktivlar, faqat narx): portfel Sharpe 0.07…0.21, t ≤ 1.05, ya'ni (h) bajarilmadi.
- Tavsif (qarorga ta'sir qilmaydi): long/flat variantlari Sharpe 0.47…0.54 (buy&hold dan past), drawdown 19–37%.
