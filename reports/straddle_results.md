# Yangilik straddle (oltin): natijalar (STRATEGY_STRADDLE.md)

AQSh yuqori ta'sirli yangilik hodisalari (M1 to'liq): 293, 2018-01 → 2025-02. Asosiy: masofa $2.50, stop $3.00, maqsad $5.00, ushlash 10 daq, spred $0.80, sirpanish $0.50.

R = 2% risk/hodisa (stop masofasiga nisbatan); F = full margin (1:500). final: 1.00 dan boshlab; maxdd: butun yo'l.

| variant                             |   hodisalar |   tolgan_pct |   whipsaw_pct |   tolmagan_pct |   yutuq_pct |   mean_R |   mean_R_pct_hisob |   mean_F_pct |   R_final |   R_maxdd_pct |   F_final |   F_maxdd_pct |   F_yoqolgan |
|:------------------------------------|------------:|-------------:|--------------:|---------------:|------------:|---------:|-------------------:|-------------:|----------:|--------------:|----------:|--------------:|-------------:|
| asosiy                              |         293 |         72.4 |           9.9 |           17.7 |        37.5 |   -0.087 |             -0.173 |        -0.82 |      0.55 |          59.6 |         0 |           100 |            1 |
| stress (spred 1.50, sirpanish 1.00) |         293 |         72.4 |           9.9 |           17.7 |        32.1 |   -0.502 |             -1.004 |       -19.71 |      0.05 |          95.3 |         0 |           100 |            1 |
| spred 0.30, sirpanish 0.25          |         293 |         72.4 |           9.9 |           17.7 |        40.6 |    0.109 |              0.219 |        10.04 |      1.76 |          38.9 |         0 |           100 |            1 |
| masofa 1.50                         |         293 |         74.7 |          17.7 |            7.5 |        42.3 |   -0.118 |             -0.237 |        -0.93 |      0.46 |          64.4 |         0 |           100 |            1 |
| masofa 4.00                         |         293 |         61.8 |           4.8 |           33.4 |        29.7 |   -0.145 |             -0.291 |        -6.46 |      0.4  |          63.9 |         0 |           100 |            1 |
| stop 2.00                           |         293 |         72.4 |           9.9 |           17.7 |        35.8 |   -0.054 |             -0.109 |        -2.96 |      0.62 |          72   |         0 |           100 |            1 |
| stop 5.00                           |         293 |         72.4 |           9.9 |           17.7 |        39.2 |   -0.103 |             -0.206 |         3.48 |      0.52 |          50.9 |         0 |           100 |            1 |
| ushlash 5 daq                       |         293 |         72.4 |           9.9 |           17.7 |        36.5 |   -0.087 |             -0.174 |        -1.99 |      0.56 |          58.9 |         0 |           100 |            1 |
| ushlash 20 daq                      |         293 |         72.4 |           9.9 |           17.7 |        40.6 |   -0.06  |             -0.12  |         1.94 |      0.65 |          56.6 |         0 |           100 |            1 |
| stopsiz                             |         293 |         72.4 |           9.9 |           17.7 |        40.3 |   -0.098 |             -0.196 |         5.61 |      0.5  |          68.2 |         0 |           100 |            1 |
| maqsad 8.00                         |         293 |         72.4 |           9.9 |           17.7 |        34.1 |    0.012 |              0.023 |         6.84 |      0.94 |          60   |         0 |           100 |            1 |

## Yarmlar (asosiy): 2018–2021: n=159, mean_R=-0.230; 2022–2025: n=134, mean_R=0.084

## Yillar bo'yicha (asosiy)
|    t |   n |   mean_R |   tolgan |   whipsaw |
|-----:|----:|---------:|---------:|----------:|
| 2018 |  44 |   -0.225 |       27 |         0 |
| 2019 |  40 |   -0.108 |       25 |         2 |
| 2020 |  37 |   -0.709 |       22 |         4 |
| 2021 |  38 |    0.101 |       31 |         5 |
| 2022 |  40 |    0.212 |       32 |         3 |
| 2023 |  43 |    0.034 |       36 |         6 |
| 2024 |  44 |   -0.008 |       34 |         8 |
| 2025 |   7 |    0.236 |        5 |         1 |

## Tasodifiy vaqt nazorati (20,000 tasodifiy daqiqa, yangilik bo'lmagan): tasodifiy mean_R -0.019 (5–95% bootstrap: -0.040 … 0.001); real -0.087; p = 1.000. F: tasodifiy -1.25% / hodisa, real -0.82%; p = 0.320

## Mezonlar (R varianti)
- S1 mean>0 va tasodifiy nazorat p<=0.10: YO`Q
- S2 stress mean>0: YO`Q
- S3 ikki yarimda mean>0: YO`Q
- S4 maxDD<=30% va hisob yo'qolmaydi (R varianti): YO`Q
- S5 hodisalar>=150: OK

**Xulosa: O'TMADI**
