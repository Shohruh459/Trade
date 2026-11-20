# GoldStructureEA: STRATEGY_SPEC (qoidalar spetsifikatsiyasi)

Holat: **MUZLATILGAN v3 (2026-11-20; foydalanuvchi "Boshlaymiz" deb ruxsat berdi).** O'zgartirish faqat 18-bo'limdagi jurnal orqali, sababi bilan; muzlatilgan qoidalarni natijaga qarab o'zgartirish taqiqlanadi. **Kod yozilmagan; kod yozishga alohida ruxsat kerak.** Hech bir raqam "natija" emas: savdolar soni, g'alaba ulushi va daromad faqat tarixiy backtestda o'lchanadi. **Test natijasiga qarab parametrlar o'zgartirilmaydi.**
v3: foydalanuvchining 6 ta qarori (A8 (b), zona tekshiruvi simmetriyasi, signal eskirishi, kunlik limit EA-only, stress hisoboti, favqulodda tartib tiklanishi) kiritildi; BUY/SELL simmetriyasi yagona formulada berildi; **har parametr uchun qiymat/birlik/hisoblash usuli** 13-bo'limda; o'zgarishlar ro'yxati 17-bo'limda.

## 0. Konventsiyalar
- Aktiv: XAUUSD. Ichki hisob UTC; sessiya/kun chegaralari mahalliy vaqt zonalarida (Europe/London, America/New_York), DST har zona uchun **mustaqil** (UK: mart oxirgi yakshanba 01:00 UTC → oktyabr oxirgi yakshanba 01:00 UTC; AQSh: mart 2-yakshanba 02:00 mahalliy → noyabr 1-yakshanba 02:00 mahalliy).
- **Faqat to'liq yopilgan barlar**; kelajak ma'lumoti ishlatilmaydi, repaint yo'q. ATR(14) = oxirgi 14 ta yopilgan bar TR sining oddiy o'rtachasi (SMA), TR = max(High−Low, |High−oldingi Close|, |Low−oldingi Close|).
- **Birlik:** narx = AQSh dollari/untsiya ($/oz). XAUUSD: 1 punkt = $0.01; 1 pip = $0.10 (10 punkt); 1 lot = 100 oz. Shuning uchun $1.00/oz narx harakati = 1 lot uchun $100.
- Qaror vaqti: har yopilgan M5 bar yopilishida; kirish keyingi M5 bar ochilishida.
- **BUY/SELL simmetriyasi:** barcha qoidalar `d ∈ {+1 (BUY/demand), −1 (SELL/supply)}` bilan yagona formulada yoziladi; faqat ijro narxi tomoni (BUY — Ask, SELL — Bid) bozor mexanikasi tufayli asimmetrik. Pozitsiya yo'nalishi `d`.

## 1. Swing (fractal)
Bar i — **swing-high**, agar High[i] oldingi k va keyingi k barning High laridan qat'iy yuqori; **swing-low** — Low[i] oldingi/keyingi k barning Low laridan qat'iy past. Swing faqat i+k bar yopilgandan keyin ma'lum. k: H1 = 3, M15 = 3, M5 = 2. Belgi: `SW_d` — d=+1 uchun swing-high turi, d=−1 uchun swing-low turi (ya'ni yo'nalishni **buzadigan** daraja); `OP_d` — qarama-qarshi tur.

## 2. H1 bias (qaror 1)
- **EMA yo'nalishi `dE`:** oxirgi yopilgan H1: Close > EMA50 va EMA50 > EMA200 → +1; Close < EMA50 va EMA50 < EMA200 → −1; aks holda 0.
- **Struktura yo'nalishi `dS`:** oxirgi 2 ta tasdiqlangan H1 swing-high va 2 ta swing-low: HH va HL → +1; LH va LL → −1; aks holda 0.
- **Bias `d` = dE, agar dE = dS ≠ 0; aks holda savdo yo'q.** Faqat EMA asosida kirish yo'q.

## 3. M15 BOS va impuls (A8 — qaror 1)
B — BOS bari (M15). `L*` — B−1 yopilgunga qadar tasdiqlangan (p+k ≤ B−1) oxirgi M15 `SW_d` swing darajasi (d=+1: swing-high High si; d=−1: swing-low Low si), p* — uning bar indeksi. Shartlar (hammasi):
1. `d × (Close[B] − L*) > 0` va `d × (Close[B−1] − L*) ≤ 0` (**birinchi** yopilish bilan buzilish);
2. `d × (Close[B] − Open[B]) > 0` (BOS shami yo'nalishda yopilgan);
3. **Impuls (A8, b):** `abs(Close[B] − Open[B]) ≥ 1.0 × ATR14_M15[B−1]` — **real tana** (soya emas), ATR **BOS shamidan oldingi yopilgan** M15 bar (B−1) bo'yicha.
Agar N < 100 bo'lsa, bu parametr **o'zgartirilmaydi**, natija "xulosasiz" deb belgilanadi (test rejasi 7-bo'lim). (a) diapazon va (c) tana ≥ 0.7×ATR faqat tavsifiy sezgirlik.

## 4. Supply/Demand zona (A6) — aniq algoritm (kelajak ma'lumoti yo'q)
B yopilgandan keyin, faqat B va undan oldingi **yopilgan** M15 barlar bo'yicha:
1. **Buzilgan swing:** p* (3-bandda).
2. **Impuls boshi S:** (p*, B−1] oralig'idagi barlar orasida d=+1 uchun **eng past Low**, d=−1 uchun **eng baland High** li bar; teng bo'lsa **eng oxirgisi**.
3. **Zona sham Z:** i = S, S−1, S−2, … tartibida (ko'pi bilan S−5 gacha va i > p*) **birinchi sham, rangi d ga qarama-qarshi** (d=+1: bearish, Close < Open; d=−1: bullish, Close > Open). Topilmasa — zona yo'q (`no_zone`).
4. **Zona oldindan buzilmaganligi (simmetrik tekshiruv, qaror 2):** `[Z, B−1]` oralig'idagi **hech bir M15 sham yopilishi** zonaning **uzoq chetidan** tashqarida bo'lmasligi shart: **Demand (d=+1):** hech bir Close < zona **pastki** chegarasi (Low[Z]); **Supply (d=−1):** hech bir Close > zona **yuqori** chegarasi (High[Z]). Aks holda zona yaratilmaydi (`pre_violated`).
5. **Zona:** `[Lz, Hz] = [Low[Z], High[Z]]` (to'liq diapazon). Uzoq chet `Fz` = (d=+1: Lz; d=−1: Hz), yaqin chet `Nz` = (d=+1: Hz; d=−1: Lz).
6. **Sifat filtri (A7):** `0.3 ≤ (Hz − Lz) / ATR14_M15[B−1] ≤ 1.5`, aks holda zona yaroqsiz (`bad_height`).
**Yaratilish vaqti:** B yopilishi. **Bekor bo'lish:** (a) 96 M15 bar (24 soat) o'tsa; (b) keyingi M15 yopilishi `Fz` dan tashqarida (d=+1: Close < Lz; d=−1: Close > Hz); (c) 3-retest sodir bo'lsa; (d) savdo ochilsa; (e) yangi BOS yangi zona yaratsa (bitta faol zona, eng yangisi).

## 5. Zona kengligi (A7)
0.3–1.5 × ATR14_M15[B−1]. Sabab (a priori, optimallashtirilmagan): 0.3 dan past — zona deyarli bitta narx (spred va M5 shovqini ma'nosiz qiladi); 1.5 dan yuqori — zona butun harakat diapazoni, stop (balandlik + 0.2×ATR) A1 dagi 2.0×ATR chegarasiga yaqinlashadi. Oldin 1.0 ATR chegarasi zona kengligida **bo'lmagan** (1.0 faqat A8 da). Binding filtr — A1; A7 zona sifati uchun.

## 6. Retest (A10)
Retest = zona yaratilgandan keyin M5 sham diapazoni zonani kesishi: `Low ≤ Hz` va `High ≥ Lz` (simmetrik). **Retest epizodi** zonani kesgan birinchi M5 bardan (`j0`, epizodning 1-bari) boshlanadi va M5 sham zonadan **narx tomonida** to'liq tashqarida bo'lganda tugaydi (d=+1: Low > Hz; d=−1: High < Lz); keyingi kesish — yangi retest. B yopilganida narx allaqachon zonada bo'lsa, shu birinchi kesish sanalmaydi. **Maksimal 2 retest;** savdo faqat 1- yoki 2-retest epizodida.

## 7. M5 tasdiq: Pattern + MSS (qaror 2, A11, A12); signal eskirishi (qaror 3)
Retest epizodi ichida ikki hodisa:
- **P — pattern bar** (Engulfing YOKI Pin Bar), **zona bilan aloqasi shart:** bar diapazoni zonani kesadi (`Low ≤ Hz` va `High ≥ Lz`) **va** `d × (Close − Fz) > 0` (yopilish zonaning uzoq chetidan narx tomonida):
  - *Engulfing(d):* sham rangi d tomonda (d=+1 yashil, d=−1 qizil); oldingi sham qarama-qarshi rangda; d=+1: Open ≤ prevClose va Close ≥ prevOpen; d=−1: Open ≥ prevClose va Close ≤ prevOpen; hamda `d × (Close − (d=+1 ? prevHigh : prevLow)) > 0`.
  - *Pin Bar(d):* rad etuvchi soya (d=+1 pastki; d=−1 yuqori) ≥ 2 × tana va ≥ 60% diapazon; qarama-qarshi soya ≤ 25% diapazon.
- **M — MSS bar:** epizodning (`j0` dan boshlab) **birinchi** M5 bari, uning yopilishi shu paytdagi oxirgi **tasdiqlangan** (k=2) M5 `SW_d` darajasidan d tomonda tashqarida (d=+1: oxirgi swing-high dan yuqori; d=−1: swing-low dan past).
- **Tartib va oyna:** P va M istalgan tartibda yoki bir barda; `|indeks(M) − indeks(P)| ≤ 2` (3 ketma-ket M5 bar). **Signal bari** = P va M dan keyingisi. Bir epizodda ko'pi bilan 1 signal.
- **Signal eskirishi:** (i) **vaqt:** signal bari retest epizodining dastlabki **12 M5 bari** ichida bo'lishi shart (`j0` = 1-bar; signal bari indeksi ≤ j0 + 11) — 12 bar = 1 soat, **epizod boshlanishidan hisoblanadi**; (ii) **bajarilish:** signal **faqat keyingi M5 bar ochilishida** bajariladi; shu paytda bajarilmasa (sessiya/yangilik/spred/band pozitsiya/kunlik blok/A1 filtri/zona bekor) signal **eskiradi**, kechiktirib ochilmaydi. Eskirgan signal retest hisobini o'zgartirmaydi; epizod davom etsa va oyna ichida bo'lsa yangi P/M qidiriladi.

## 8. Kirish, stop, TP (qaror 3 [oldingi], A1, A15)
- **Kirish:** keyingi M5 bar ochilishida, market; ijro narxi `Pe` = d=+1: **Ask**, d=−1: **Bid**.
- **Stop:** `Ps = Fz − d × 0.2 × ATR14_M15[signal]` (d=+1: Lz − 0.2×ATR; d=−1: Hz + 0.2×ATR); ATR — signal bari paytidagi oxirgi yopilgan M15 bar. **Sun'iy o'zgartirilmaydi.**
- **Masofa:** `s = d × (Pe − Ps)` ($/oz). **A1 filtri:** `s < 0.5×ATR14_M15` yoki `s > 2.0×ATR14_M15` bo'lsa savdo **o'tkaziladi**.
- **TP:** `Pt = Pe + d × 2.0 × s` (RR 1:2). Qisman yopish yo'q, breakeven yo'q.

## 9. Risk va pozitsiya (qaror 5, A4, A16)
Risk $ = **hisob equity (ACCOUNT_EQUITY, floating bilan) × 1%**; `lot = risk$ / (s × 100)` (1 lot = 100 oz; $/oz × oz); lot qadamiga pastga yaxlitlanadi; minimal lotdan kichik bo'lsa savdo o'tkaziladi; maksimal lot konfiguratsiyada. **Bir vaqtda faqat bitta EA pozitsiyasi** (MagicNumber). Kuniga savdolar soniga limit yo'q.

## 10. Kunlik −4% limit (A2, A3 — qaror 4)
- **Kun boshi:** New York 17:00 mahalliy (DST avtomatik; yakshanba bozor ochilishida ham). Shu paytda **hisob equity** E0 qayd etiladi (limit nisbati uchun; risk hajmi ham equity dan).
- **Hisobga kiradi (faqat EA — MagicNumber):** bugun (kun boshidan) yopilgan **EA savdolarining sof natijasi** (foyda + **komissiya** + **swap**) + ochiq **EA pozitsiyalarining floating P&L i** (bid/ask bo'yicha, spred hisobga olingan, ochilish komissiyasi kiritilgan): `D`.
- **Hisobga KIRMAYDI:** boshqa EA lar, **qo'lda ochilgan** pozitsiyalar va ularning natijalari (MagicNumber boshqa bo'lgan hamma narsa). `LimitScope` konfiguratsiyasi **yo'q**: faqat EA_ONLY (qat'iy).
- **Limit:** `D ≤ −0.04 × E0` bo'lsa: (1) **blok** o'rnatiladi (keyingi NY 17:00 gacha **yangi kirish yo'q**) va qayta ishga tushganda tiklanadi (11.3); (2) **EA ning barcha pozitsiyalari** yopiladi (11.2 tartibi bilan: retry va favqulodda holat); (3) kutilayotgan EA orderlari o'chiriladi; (4) log (vaqt, D, E0, pozitsiyalar); (5) NY 17:00 da blok yechiladi, yangi E0 qayd etiladi.
- **Backtest:** M1 adverse narx bo'yicha D hisoblanadi; D = −4% ga teginsa pozitsiya shu −4% ni beruvchi narxda yopiladi.

## 11. Sessiyalar, rollover, favqulodda holat, yangilik, spred
### 11.1 Sessiyalar (S1) va rollover himoyasi (A5)
- London 08:00–12:00 (Europe/London), New York 08:00–12:00 (America/New_York); **yangi kirish** faqat shu soatlarda, dushanba–juma; konfiguratsiya: `LondonStart/End`, `NewYorkStart/End` (HH:MM mahalliy). Ochiq pozitsiya sessiya tugashi bilan yopilmaydi.
- `PreRolloverCloseNY` (default **16:30 NY**) da EA ning barcha pozitsiyalari yopiladi; vaqt konfiguratsiyada, o'chirish mumkin.

### 11.2 Yopishga urinish va favqulodda holat (qaror 6)
1. Yopish buyrug'i (16:30, kunlik limit yoki boshqa sabab) rad etilsa **har 60 soniyada qayta uriniladi** 16:55 gacha (kunlik limit holatida — pozitsiya yopilguncha, bir xil tartib); har urinish `retcode` bilan logga yoziladi; `deviation = EmergencyDeviationPoints` (default 100 punkt = $1.00/oz).
2. 16:55 da (yoki 60 soniyalik urinishlar tugagach) **FAVQULODDA HOLAT:** yangi kirish **bloklanadi** (`EmergencyBlock`); `Alert`, `SendNotification`, `SendMail` (konfiguratsiya) har daqiqa; **har 10 soniyada** yopishga urinish **pozitsiya yopilguncha davom etadi**.
3. **Hedge ochilmaydi. SL/TP kengaytirilmaydi va o'zgartirilmaydi** (server tomonidagi himoya SL saqlanadi).
4. Bozor yopiq (hafta oxiri) yoki broker rad etsa — holat saqlanadi, bozor ochilgach birinchi imkoniyatda yopishga urinish; blok **qo'lda tasdiqlanmaguncha** (`EmergencyAck=true`) yechilmaydi.
5. Favqulodda holat hisobotda alohida hodisa sifatida qayd etiladi (backtestda modellashtirilmaydi: yopish 16:30 M1 yopilish narxida muvaffaqiyatli deb olinadi; "yopishsiz" variant sezgirlikda).

### 11.3 Holatni saqlash va tiklash (qaror 6)
EA quyidagi holatni **terminal global o'zgaruvchilarida va jurnal faylida** saqlaydi: `DayBlockUntil` (UTC), `E0`, `EmergencyBlock`, `EmergencyAck`, favqulodda holat boshlangan vaqt, urinishlar soni va oxirgi `retcode`, signal/zona holati (faol zona koordinatalari, retest soni). `OnInit` da: holat o'qiladi; ochiq EA pozitsiyasi bo'lsa va blok/favqulodda holat faol bo'lsa — yopish tartibi **davom ettiriladi**; `DayBlockUntil` kelmagan bo'lsa blok saqlanadi; jurnalga "tiklandi" yoziladi. Pozitsiya yopilmaguncha har urinish, ogohlantirish va holat o'zgarishi **jurnalga yoziladi** (Journal + `GSEA_state.log`).

### 11.4 Yangilik (A13)
NFP, CPI (m/m, core m/m, y/y), GDP (advance/prelim/second/final), FOMC (Statement, Federal Funds Rate) — AQSh, yuqori ta'sir: yangilikdan **60 daqiqa oldin va 30 daqiqa keyin yangi kirish yo'q** (ochiq pozitsiya o'z holicha). EA: MT5 Economic Calendar + qo'lda ro'yxat (`news_manual.csv`: `utc_datetime;name`). Backtest manbasi va mavjudligi: 11.5.

### 11.5 Yangilik ma'lumoti (backtest)
- **Manba:** `Ehsanrs2/Forex_Factory_Calendar` (Hugging Face, `forex_factory_cache.csv`, ~68 MB, 2007-01 → **2025-04-04**); faqat `Currency=USD`, `Impact="High Impact Expected"` va yuqoridagi nomlar.
- **Vaqt:** fayldagi vaqtlarning 49.2% i (2018–2025) yarim tun "00:00:00" placeholder, qolganlarida DST farqidan 1 soatlik siljish bor; shuning uchun **sana fayldan, vaqt standart ET jadvalidan** (NFP/CPI/GDP 08:30 ET; FOMC 14:00 ET), AQSh DST bilan UTC ga.
- **Format (kodlashdan keyin):** `data/news/usd_high_impact.csv`: `event_utc, family, event_name, date_source, time_source, ff_datetime_raw`; `tools/build_news_calendar.py` bilan qayta ishlab chiqariladi.
- **Mavjudlik (2018–2025-02):** NFP va CPI har oyda bor (yo'q oy yo'q); FOMC 8–9/yil; **GDP to'liq emas**: 2018: 12, 2019: 8, 2020: 5, 2021: 7, 2022: 8, 2023: 12, 2024: 12 (kutilgan ~12).
- **Yetishmasa:** blok qo'yilmaydi (taxmin yo'q), davr "yangilik filtri tekshirilmagan" deb belgilanadi. **Filtr to'liq bo'lmagan davrlar alohida hisobot qilinadi:** GDP bo'shliqlari 2019–2022; 2025-03 dan keyin kalendar yo'q; 2026 tavsifiy tekshiruvida filtr o'chirilgan.

### 11.6 Spred filtri (A14)
Spred > $0.50 bo'lsa kirish yo'q (EA); backtestda spred doimiy ($0.30 / stress $0.50).

## 12. Xarajatlar (qaror 5)
**Hisobotda alohida ikki ssenariy: "Asosiy" va "Stress"; komissiya sezgirligi — uchinchi alohida jadval.**

| Komponent | Asosiy | Stress | Birlik | 1 lot (100 oz) uchun |
|---|---|---|---|---|
| Spred (to'liq aylanma) | 0.30 | 0.50 | $/oz | $30 / $50 |
| Komissiya (aylanma) | 0 | 0 (sezgirlik: **0.07**) | $/oz | 0 (sezgirlik: **$7**) |
| Slippage — kirish | 0 | 0.10 | $/oz | $10 |
| Slippage — SL bajarilishi | 0 | 0.10 | $/oz | $10 |
| Slippage — TP (limit) | 0 | 0 | $/oz | 0 |
| Swap | 0 (NY 16:30 yopish) | 0 | $/oz/tun | — (yopishsiz sezgirlikda: yiliga 3% × qiymat × tunlar) |

Hisoblash: BUY — kirish Ask = Bid + S, chiqish Bid; SELL — kirish Bid, chiqish Ask = Bid + S (SL/TP SELL uchun Bid+S bo'yicha tekshiriladi). Slippage kirishda har doim **zarar tomonga** (BUY: kirish narxi +0.10; SELL: −0.10), SL chiqishida ham zarar tomonga. **Net R** = (foyda($/oz) − spred − komissiya − slippage − swap) / s.

## 13. Parametrlar reyestri (qiymat, birlik, hisoblash usuli; muzlatiladi)

| # | Parametr | Qiymat | Birlik | Hisoblash usuli / izoh | Konfiguratsiya nomi |
|---|---|---|---|---|---|
| 1 | swing k, H1 / M15 / M5 | 3 / 3 / 2 | bar | 1-bo'lim (qat'iy ekstremum, k+k bar) | `SwingK_H1/M15/M5` |
| 2 | H1 EMA tezkor / sekin | 50 / 200 | davr (H1 yopilishi, EMA, α=2/(n+1)) | 2-bo'lim | `EmaFast/Slow` |
| 3 | ATR davri | 14 | bar (SMA of TR) | 0-bo'lim; M15 uchun | `AtrPeriod` |
| 4 | BOS impuls tana ATR ko'paytmasi | 1.0 | × ATR14_M15[B−1] | abs(Close−Open) ≥ 1.0×ATR | `ImpulseBodyAtr` |
| 5 | Zona sham qidirish chuqurligi | 5 | M15 bar (S dan orqaga) | 4-bo'lim | `ZoneLookbackBars` |
| 6 | Zona balandligi min / max | 0.3 / 1.5 | × ATR14_M15[B−1] | (Hz−Lz)/ATR | `ZoneHeightMinAtr/MaxAtr` |
| 7 | Zona muddati | 96 | M15 bar (24 soat) | 4-bo'lim (a) | `ZoneMaxAgeBars` |
| 8 | Maksimal retest | 2 | marta | 6-bo'lim | `MaxRetests` |
| 9 | Pin: soya / tana | 2.0 | × tana | rad etuvchi soya ≥ 2×tana | `PinWickBody` |
| 10 | Pin: soya / diapazon | 60 | % | rad etuvchi soya ≥ 60% diapazon | `PinWickRangePct` |
| 11 | Pin: qarshi soya max | 25 | % diapazon | qarama-qarshi soya ≤ 25% | `PinOppWickMaxPct` |
| 12 | P–M oynasi | 3 | ketma-ket M5 bar | |ind(M)−ind(P)| ≤ 2 | `ConfirmWindowBars` |
| 13 | Signal eskirish vaqti | 12 | M5 bar (1 soat), epizod boshidan | signal bari ≤ j0+11 | `SignalMaxBars` |
| 14 | Stop buferi | 0.2 | × ATR14_M15[signal] | Ps = Fz − d·0.2·ATR | `StopBufferAtr` |
| 15 | Stop masofasi min / max (A1) | 0.5 / 2.0 | × ATR14_M15[signal] | s = d·(Pe−Ps) | `StopMinAtr/StopMaxAtr` |
| 16 | RR (TP) | 2.0 | × s | Pt = Pe + d·2·s | `RewardRisk` |
| 17 | Risk | 1.0 | % hisob equity | lot = (equity·1%)/(s·100) | `RiskPercent` |
| 18 | Lot qadami / min / max | broker / broker / konfig | lot | pastga yaxlitlash; min dan kichik → o'tkazish | `MaxLot` |
| 19 | Kunlik equity limiti | 4.0 | % E0 (EA P&L) | D ≤ −4%·E0 (10-bo'lim) | `DailyLossPercent` |
| 20 | Kun boshi | 17:00 | NY mahalliy | DST avtomatik | `DayStartNY` |
| 21 | London sessiya | 08:00–12:00 | Europe/London mahalliy | yangi kirish | `LondonStart/End` |
| 22 | New York sessiya | 08:00–12:00 | America/New_York mahalliy | yangi kirish | `NewYorkStart/End` |
| 23 | Rollover oldi yopish | 16:30 | NY mahalliy | 11.1 | `PreRolloverCloseNY` |
| 24 | Yopish qayta urinish davri / oxiri | 60 s / 16:55 | soniya / NY mahalliy | 11.2 | `CloseRetrySec` |
| 25 | Favqulodda urinish davri | 10 | soniya | 11.2 | `EmergencyRetrySec` |
| 26 | Favqulodda deviation | 100 | punkt ($1.00/oz) | 11.2 | `EmergencyDeviationPoints` |
| 27 | Yangilik oynasi oldin / keyin | 60 / 30 | daqiqa | 11.4 | `NewsBeforeMin/AfterMin` |
| 28 | Spred filtri (EA) | 0.50 | $/oz | spred > 0.50 → kirish yo'q | `MaxSpread` |
| 29 | Backtest spredi asosiy / stress | 0.30 / 0.50 | $/oz | 12-bo'lim | (test) |
| 30 | Komissiya sezgirligi | 0.07 | $/oz ($7/lot) | 12-bo'lim | (test) |
| 31 | Stress slippage kirish / SL | 0.10 / 0.10 | $/oz | 12-bo'lim | (test) |
| 32 | Swap (yopishsiz sezgirlik) | 3 | % yiliga × qiymat × tunlar | | (test) |

## 14. A1–A18 jadvali (default'lar va ta'siri)

| # | Masala | Qaror | Strategiyaga ta'siri |
|---|---|---|---|
| A1 | Stop masofasi | zona ± 0.2×ATR; masofa 0.5–2.0×ATR dan tashqarida → savdo o'tkaziladi; stop o'zgartirilmaydi | Juda keng (uzoq TP) va juda tor (xarajat) stoplar kesiladi |
| A2 | Kun boshi | NY 17:00 mahalliy, DST avtomatik | −4% har kuni bir nuqtadan |
| A3 | −4% ga yetsa | blok + EA ning hamma pozitsiyasini yopish, NY 17:00 gacha | Katta zarar kuni cheklanadi |
| A4 | Risk asosi | hisob equity (floating bilan) | Zarar paytida hajm kamayadi |
| A5 | Sessiyadan tashqari | yangi kirish faqat sessiyada; NY 16:30 yopish; favqulodda tartib | Kechasi swap/gap/rollover xavfi kamayadi |
| A6 | Zona | 4-bo'lim algoritmi; simmetrik oldindan-buzilmaganlik tekshiruvi | Zona tanlash savdolar sonini va stopni belgilaydi |
| A7 | Zona kengligi | 0.3–1.5×ATR | Tor/keng zonalar kesiladi |
| A8 | BOS impulsi | real tana ≥ 1.0×ATR(B−1) | BOS ~12.7% barlarda: savdolar kam; N<100 → xulosasiz |
| A9 | Swing k | 3/3/2 | k kichik — shovqin, katta — kechikish |
| A10 | Retest | epizod ta'rifi; ≤ 2 | Eski zonalarda savdo yo'q |
| A11 | Tasdiq | P va M ixtiyoriy tartibda 3 bar ichida; signal 12 bar (epizoddan) va keyingi ochilishda bajarilmasa eskiradi | Kechikkan kirishlar yo'q |
| A12 | Pattern | Pin 2×/60%/25%; Engulfing qat'iy | Kam, lekin aniq signal |
| A13 | Yangilik | NFP/CPI/GDP/FOMC −60/+30; EA kalendar + qo'lda; backtest FF + ET | GDP 2019–2022 bo'shliq |
| A14 | Spred | ≤ $0.50 (EA) | Backtestda spred kengayishi yo'q |
| A15 | TP | 2R | −1R yoki +2R |
| A16 | Lot | pastga yaxlitlash, min dan kichik → o'tkazish | Kichik hisobda signallar o'tkaziladi |
| A17 | Aktiv | XAUUSD; FX qo'shimcha dalil | N kam bo'lsa FX ishonch beradi |
| A18 | Ma'lumot | M1 BID, doimiy spred | Sham ichi tartibi taxminiy (stop birinchi) |

## 15. Foydalanuvchi qarorlari (v3 asosi)
1. A8 = (b): real tana ≥ 1.0×ATR(M15) (ATR — BOS dan oldingi yopilgan bar); N<100 → parametr o'zgarmaydi, "xulosasiz". 2. Zona tekshiruvi simmetrik (3-bandda). 3. Signal eskirishi 12 M5 bar, retest epizodi boshidan; keyingi ochilishda bajarilmasa eskiradi. 4. Kunlik −4%: faqat EA P&L (floating, komissiya, swap bilan); boshqa EA va qo'lda ochilgan pozitsiyalar kirmaydi; limitda EA ning hamma pozitsiyasi yopiladi, NY 17:00 gacha blok. 5. Stress: spred $0.30/$0.50, komissiya $0.07/oz sezgirligi, stress slippage $0.10 (kirish va SL); asosiy va stress alohida hisobot; birliklar/1 lot qiymati ko'rsatilgan. 6. Favqulodda tartib: hedge yo'q, SL kengaytirilmaydi, yangi savdo bloklanadi, urinishlar/ogohlantirishlar davom etadi, holat jurnalga yoziladi va qayta ishga tushganda tiklanadi.

## 16. Ochiq cheklovlar
1. Zona sham tanlash bir nechta mantiqiy ta'rifdan biri; boshqalari sinalmaydi.
2. Savdolar soni oldindan noma'lum; **hech bir taxmin natija sifatida e'lon qilinmaydi.** A8 (b) bilan savdolar kam bo'lib, "xulosasiz" natija chiqishi mumkin.
3. MQL5 da kalendar API va DST qoidalari qo'lda; Strategy Tester'da kalendar ishlamasligi mumkin.
4. Rollover spredi, requote va favqulodda holat M1 BID ma'lumotda ko'rinmaydi.

## 17. v2 → v3 o'zgarishlar ro'yxati
1. A8: "(b) tanlov kutilmoqda" → **(b) qat'iy qaror**; (a)/(c) faqat sezgirlik; N<100 → parametr o'zgarmaydi (3, 14, 15).
2. Zona tekshiruvi: "(Z, B−1] da hech bir yopilish zona Low dan pastda emas" → **simmetrik Demand/Supply, [Z, B−1] oraliqda** (4-bandning 4-qadami).
3. Signal eskirishi: "12 M5 bar" aniqlashtirildi: **epizod boshidan** (j0 = 1-bar, signal bari ≤ j0+11) **va** keyingi ochilishda bajarilmasa eskiradi (7-bo'lim).
4. Kunlik limit: `LimitScope` (EA_ONLY/ACCOUNT) **olib tashlandi** — faqat EA; boshqa EA va qo'lda pozitsiyalar kirmasligi aniq yozildi; komissiya, swap, floating kiritilgan (10-bo'lim).
5. Xarajatlar: jadval (asosiy/stress alohida, komissiya sezgirligi, slippage), birlik va 1 lot qiymati (12-bo'lim); hisobotda alohida ssenariylar.
6. Favqulodda tartib: urinishlar/ogohlantirishlar davomiyligi, SL o'zgartirilmasligi, hedge yo'qligi, **holatni saqlash va qayta ishga tushganda tiklash** (11.2, 11.3) qo'shildi.
7. BUY/SELL **yagona formula** (d = ±1) bilan simmetrik qilindi: BOS, zona, pre-violation, retest tugashi, Engulfing, Pin Bar, MSS, stop, TP (0, 1–8 bandlar).
8. **Parametrlar reyestri** (13-bo'lim): 32 parametr — qiymat, birlik, hisoblash usuli, konfiguratsiya nomi.
9. Birlik va 1 lot qiymati konventsiyasi (0-bo'lim: 1 punkt, pip, lot).
10. Yangilik ma'lumoti (11.5) ixchamlashtirildi (mazmun v2 bilan bir xil).

## 18. O'zgartirishlar jurnali (muzlatilgandan keyin)
- 2026-11-20: v3 muzlatildi (qoralama commit `d6f01d9` asosida; xeshlar `FREEZE_MANIFEST.md` da). Mazmun o'zgartirilmadi.
