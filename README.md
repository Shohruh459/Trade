# Trade: oltin va valyutalar uchun algoritmik savdo g'oyalarini halol sinash

Bu repo savdo robotlari (EA) va qoidalarini **ishonchli usulda** sinash bo'yicha tadqiqot: xarajatlar hisobga olingan, natijadan oldin yozilgan mezonlar,
vaqt bo'yicha bo'lingan va mustaqil ma'lumotlarda tasdiqlangan testlar. Maqsad "foydali robot topish" edi; asosiy natija esa aniq: **oddiy texnik qoidalar
bilan, shu ma'lumotlarda, xarajatdan keyin ishonchli ustunlik topilmadi.** Quyida nima sinalgani, nima chiqqani va nimani o'rganganimiz.

> Ogohlantirish: bu moliyaviy maslahat emas. Tarixiy natijalar kelajakni kafolatlamaydi. Leveraged (CFD/forex) savdoda butun hisobni yo'qotish mumkin.

## 1. Qisqa xulosa
| Yo'nalish | Nima sinaldi | Natija |
|---|---|---|
| Oltin uchun ochiq manbali EA'lar (6 variant) | FvgGold, gold-pro-scalper (TickRobust, klassik MR, Trend Breakout), Trillex 10S | **Hech biri xarajatdan keyin foyda bermadi** |
| Oltinda skalping hodisa tadqiqoti | O'ta katta 1 daqiqalik portlashdan keyingi 3–10 daqiqa (tick ma'lumoti) | Xarajatdan oldin ham ustunlik yo'q; spred ~$0.4/bitim |
| EUR/USD va oltin, H1, 8 strategiya × 5 chiqish | Trend, breakout, qaytish, sessiya breakouti | In-sample mezonidan o'tgan variant: 0/40 (ikkala bozorda) |
| Kunlik trend/momentum (oltin, 4 signal) + 9 aktivda tasdiqlash | TSMOM, ansambl, MA kesishuvi, Donchian | 4 hujayradan 0 PASS; sof Sharpe 0.11–0.31 (buy&hold 0.63) |
| Ko'p vaqt oralig'i (M1·M5·M15·H1·H4) tuzilma tadqiqoti + chiqqan qoida (MTF2) | Trend shakllanishi, davom etish va qaytish | Qoida: **FAIL** (oltin +0.03 R, FX −0.02 R); tavsifiy topilmalar bor |
| Oltin: portfeldagi roli, xavfni kamaytirish, fundamental omillar (oylik, 50 yil) | 60/40 ga oltin qo'shish; 10 oylik SMA filtri; real foiz/dollar/qiymat/inflyatsiya/mavsumiylik | 10% oltin: Sharpe +0.07 (p=0.02); **SMA10 filtri drawdownni ~2 baravar kamaytirdi**; fundamental predikator: **yo'q** |

## 2. Nimani o'rgandik (tavsifiy topilmalar, takrorlangan)
- H1 trend boshlanganda M1, M5, M15 hammasi shu tomonda bo'lsa va H1 "trendli" (Kaufman ER ≥ 0.30) bo'lsa, trend **uzoqroq davom etadi** (mediana ~40–59 H1 bar ga qarshi 21–33; ikkala davrda ham p < 0.02). Lekin buni xarajatdan keyin foydaga aylantirib bo'lmadi (MTF2).
- H4 yo'nalishi bilan bog'liq dastlabki topilma (t = −2.85) keyingi davrda **takrorlanmadi**: tipik overfitting.
- Oltinda qisqa muddatli bashorat deyarli yo'q: 1–5 daqiqalik qaytishlar korrelyatsiyasi −0.01…−0.05 va 2023 dan ~0; ertalabki harakat tushdan keyingisini bashorat qilmaydi.
- Oltin o'zgaruvchanligi 2018 → 2025 da ~3 baravar oshdi (soatlik diapazon $2 → $5.8): punktlarga qotirilgan parametrlar tez eskiradi; spredning nisbiy ulushi esa kamaydi.

## 3. Ochiq manbali EA'lar bo'yicha aniq topilmalar
- **FvgGold:** buyurtmalar muddatsiz (GTC) va `MaxTrades=1` kutilayotgan buyurtmani hisoblaydi, shuning uchun narx qochib ketsa EA yillar davomida **to'xtab qoladi** (testda 2019-05 dan). README'dagi "+48.7%" kod va 0.01 lot bilan arifmetik jihatdan mumkin emas (~128 baravar katta). Parametrlar "yutuq ulushi" uchun optimallashtirilgan.
- **gold-pro-scalper (TickRobust):** yaxshi muhandislik (yopilgan bar qarorlari), lekin xarajat darvozasi tufayli juda kam bitim (7 yilda 176), PF 0.80, natija nolga yaqin.
- **Klassik MR:** spred ≤ M1 ATR × 12% sharti vaqtning ~1% ida bajariladi; foyda 2020-yilga bog'liq; arzon spredda PF 0.88, drawdown 23%.
- **Trend Breakout:** 6615 bitim, PF 0.63, aniq zarar.
- **Trillex 10S:** signal xarajatdan oldin ham nol (12 840 bitim), spred hammasini yeydi; lot qoidasi `1 × 10^floor(log10(balans/1000))` bitta SL'da balansning 20–40% ini xavf ostiga qo'yadi.

To'liq jadval: `reports/summary_gold_EAs.md`.

## 4. Metodologiya (qayta ishlatish uchun)
1. **Xarajat birinchi:** natija har doim spred, komissiya va moliyalashtirish (swap) bilan; stress (xarajat ×1.5–2).
2. **Pre-registration:** gipoteza, ta'rif, davrlar, mezonlar natijadan OLDIN `STRATEGY*.md` ga yoziladi va commit qilinadi.
3. **Vaqt bo'yicha bo'lish:** Discovery → Validation → Final (bir marta). Har bosqichdan keyin nomzodlar ro'yxati qulflanadi.
4. **Mustaqil tasdiqlash:** boshqa aktivlar/juftlar (FX, Brent) va tasodifiy-vaqt (timing) nazorati.
5. **Ko'p test tuzatmasi** (FDR/Bonferroni), klasterlangan standart xatolar, ishonch oralig'lari; kichik namunada "xulosasiz" deyish.
6. **Kod to'g'riligi:** birlik testlari (`tests/`), qo'lda hisob bilan solishtirish, haqiqiy ma'lumotdagi sanity-tekshiruvlar.
7. **Port cheklovlari ochiq yoziladi:** bar-darajasidagi port MT5 tick sinovi emas; aniq tasdiq uchun MT5 Strategy Tester va demo kerak.

## 5. Real savdo uchun amaliy tavsiyalar
- "Yaxshi baholangan" robotni darhol ishlatmang: yulduz soni va README'dagi natija foyda isboti emas. Tekshiruv ro'yxati:
  kod ochiqmi; natija davri qisqami/optimallashtirilganmi; lot/risk qoidasi (martingale, lot zinapoyasi, bitimga ≥ 2% risk) xavfli emasmi; kutilayotgan buyurtma/holat xatolari bormi;
  natija xarajatdan **keyin**mi; mustaqil davrda tasdiqlanganmi.
- Har qanday qoidani avval **demo hisobda kamida 3 oy**, keyin juda kichik risk (≤ 0.25–0.5% bitimga, kunlik limit 2%) bilan sinang.
- Skalping eng qiyin yo'nalish: spred hajmi har bitimda ~$0.3–0.45 (oltin). Brokerning haqiqiy spredi, kechikishi va sirpanishini o'lchamasdan boshlamang.
- "Har oy foyda" va'dasi ishonchsiz belgi; ishonchli maqsad: uzoq muddatli ijobiy kutilma va nazoratdagi drawdown.

## 6. Repo tuzilishi
- `STRATEGY.md`, `STRATEGY_GOLD.md`, `STRATEGY_TREND.md`, `STRATEGY_MTF.md`, `STRATEGY_MTF2.md`, `STRATEGY_PORTFOLIO.md`, `STRATEGY_FORWARD.md`: oldindan yozilgan rejalar va qoidalar.
- `backtest/`: engine (`engine.py`), strategiyalar, har bir EA porti (`fvggold.py`, `n30_*.py`, `trillex.py`), hodisa tadqiqoti (`event_study.py`), kunlik trend (`trend.py`), MTF (`mtf.py`, `mtf2.py`), hisobot skriptlari.
- `tools/`: ma'lumot yuklash/yig'ish (Dukascopy, Hugging Face, oltin vaqt zonasini tuzatish).
- `reports/`: barcha natijalar (`summary_gold_EAs.md`, `fvggold.md`, `trillex.md`, `n30_*.md`, `event_study_H1.md`, `trend_results.md`, `mtf_*.md`, `mtf2_results.md`).
- `forward_test/`: oylik narxlar (`gold_prices.csv`), qulflangan forward jurnal (`log.csv`), oxirgi hisobot (`latest.md`).
- `tests/`: engine va MTF2 chiqish mantig'i uchun birlik testlari (`pytest -q tests`).
- `data/`: kichik tayyor CSV'lar (EURUSD H1 2020–2026, XAUUSD H1 2018–2025). Katta xom ma'lumotlar repoda yo'q.

## 7. Qayta ishlab chiqarish
```
python -m venv .venv && .venv/bin/pip install pandas numpy pyarrow tabulate statsmodels scipy pytest
.venv/bin/python -m pytest -q tests
.venv/bin/python tools/build_h1_from_hf.py eur_usd           # EURUSD H1 (Hugging Face qleap dataseti)
.venv/bin/python tools/build_gold.py <XAU_1h_data.jsonl>      # oltin H1 (Afina vaqtidan UTC ga)
.venv/bin/python -m backtest.protocol                         # H1 IS/OOS protokoli
```
Ba'zi skriptlar katta ma'lumot keshlariga (`/tmp/claude-0/...`: oltin M1/kunlik, Dukascopy tick namunalari, FX M1) tayanadi; yo'llar skriptlar boshida, ma'lumot manbalari tegishli `STRATEGY*.md` da ko'rsatilgan.

## 8. Ma'lumot manbalari va cheklovlar
- Oltin: `ZombitX64/xauusd-gold-price-historical-data-2004-2025` (MT server vaqti, Europe/Athens; UTC ga o'tkazilgan; mustaqil BID dataset bilan solishtirilgan), 2025-04 dan keyin bo'shliqlar.
- EUR/USD va FX M1: `qleap/dukascopy-ticks-ohlcv`; oltin tick: `mito0o852/dukascopy-ticks`; FX kunlik: Federal Reserve H.10 (`datasets/exchange-rates`); Brent: EIA (`datasets/oil-prices`).
- Spred ko'p testlarda doimiy faraz qilingan; haqiqiy spred vaqt bo'yicha o'zgaradi; kechikish/sirpanish stress bilan qisman qoplangan.
- Natijalar tarixiy; 2018–2025-fevral oltin ma'lumoti MTF2 dan keyin to'liq "ishlatilgan": yangi g'oyalar uchun yangi (2025-mart dan keyingi) ma'lumot kerak.
- Ochiq qolgan, tasdiqlanmagan trek: oltin/EURUSD da RSI-qaytish (C strategiyasi) 2023–2025 da qisqa muddatda yaxshi ko'ringan, IS da zarar edi; yangi juftlarda tasdiqlanmagan.

## 9a. Oylik hisoblagich va forward kuzatuv
`python tools/gold_monthly_check.py --add YYYY-MM NARX` oy oxirida SMA10 holatini (LONG/NAQD), 12 oylik momentum va mavsumiy oyni ko'rsatadi, qulflangan jurnalni (`forward_test/log.csv`) yuritadi. Qoidalar, baholash nuqtalari va amaliy qoidalar: `STRATEGY_FORWARD.md`. Hozirgi holat (2026-09): NAQD (narx SMA10 dan −4.6% past).

## 9. Portfel/risk natijalari (STRATEGY_PORTFOLIO.md, `reports/portfolio_results.md`)
- **Oltin ulushi:** 60/40 portfelga 10% oltin qo'shish risk-moslashtirilgan natijani oz bo'lsa ham yaxshiladi (Sharpe +0.07, bootstrap p = 0.02; 2000 dan keyin +0.13, 1976–1999 da deyarli o'zgarishsiz). 20% oltin ikkala davrda ishonchli emas.
- **Xavfni kamaytirish:** oltin uchun 10 oylik SMA filtri (narx SMA dan pastda bo'lsa naqd) maksimal drawdownni ~2 baravar kamaytirdi (62% → 31%, 39% → 22%), Sharpe yomonlashmadi, yilida ~1.3 marta almashtirish. Vol-maqsad ishlamadi.
- **Fundamental omillar:** real foiz, dollar, qiymat va inflyatsiya hech qanday OOS bashorat bermadi; faqat oltin momentumi statistik ahamiyatli, lekin "ishora" qoidasi bilan buy&hold'dan farq qilmadi. Sentyabr–fevral mavsumiyligi (+0.97%/oy) ikkala davrda barqaror, lekin ko'p test tuzatmasidan o'tmadi.
- **Ehtiyot:** oylik o'rtacha narxlar va approksimatsiyalar; nisbiy solishtirish ishonchli, mutlaq raqamlar emas.


## 9b. N1 va N3 natijalari (STRATEGY_NEXT.md, STRATEGY_N3.md)
- **N1 (ko'p aktivli oylik SMA10 portfel): PASS.** 1976–2026: CAGR 9.2%, Sharpe 0.96, maksimal drawdown 12.7% (teng vaznli buy&hold: 38%), foydali oylar 63.5%, eng yomon oy −9.5%. 1 oy kechiktirilgan variant ham o'tdi (drawdown 18.4%). Xavfni arzon kamaytiradi, daromadni oshirmaydi. Forward kuzatuv kerak. `reports/n1_results.md`.
- **N3 (oltin M1 swing-trend + ATR filtri + kunlik ±10%): FAIL.** Xarajatdan keyin o'rtacha −0.15 R, yutuq 40%, tasodifiy kirishdan farq yo'q (p=0.86); 1% riskda hisob deyarli to'liq yo'qoladi. Kunlik ±10% chegara deyarli ishlamadi (4 kun, hammasi −10%). `reports/n3_results.md`.
- **N2 (rejadagi AQSh yangiliklari atrofida oltin): FAIL (Discovery).** 96 hodisa, 6 hujayra ham xarajatdan keyin manfiy (−0.14…−0.29 R). Validation/Final ishlatilmadi. `reports/n2_discovery.md`.
- N1 uchun oylik hisoblagich: `tools/n1_monthly_check.py` (forward kuzatuv, `STRATEGY_FORWARD.md` 9-bo'lim).
