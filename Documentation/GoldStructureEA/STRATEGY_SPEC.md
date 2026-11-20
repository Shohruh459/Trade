# GoldStructureEA: STRATEGY_SPEC (qoidalar spetsifikatsiyasi)

Holat: **LOYIHA v2 (DRAFT) — foydalanuvchi tasdig'ini kutmoqda; MUZLATILMAGAN.** Tasdiqlangandan keyin muzlatiladi; o'zgartirish faqat 15-bo'limdagi jurnal orqali, sababi bilan. **Kod yozilmagan.** Hech bir raqam "natija" emas: savdolar soni, g'alaba ulushi va daromad faqat tarixiy backtestda o'lchanadi.
v2 o'zgarishi: foydalanuvchi 10 ta aniqlashtirish so'radi (1–10); javoblar tegishli bo'limlarga kiritildi va 14-bo'limda xaritalandi.

## 0. Konventsiyalar
- Aktiv: XAUUSD. Ichki hisob UTC da; sessiya/kun chegaralari mahalliy vaqt zonalarida (Europe/London, America/New_York), DST har zona uchun **mustaqil** (UK: mart oxirgi yakshanba 01:00 UTC → oktyabr oxirgi yakshanba 01:00 UTC; AQSh: mart 2-yakshanba 02:00 mahalliy → noyabr 1-yakshanba 02:00 mahalliy).
- Faqat **to'liq yopilgan** barlar; **kelajak ma'lumoti ishlatilmaydi**, repaint yo'q. ATR(14) = oxirgi 14 ta yopilgan bar TR sining oddiy o'rtachasi (SMA).
- Birlik: narx **AQSh dollari/untsiya** (XAUUSD: 1 punkt = $0.01; 1 lot = 100 oz; $0.30 = 30 punkt = 3 "pip" (0.10); 1 lot da $0.30/oz = $30).
- Qaror vaqti: har yopilgan M5 bar yopilishida; kirish keyingi M5 bar ochilishida.

## 1. Swing (fractal)
Bar i — swing-high, agar High[i] oldingi k va keyingi k barning High laridan qat'iy yuqori (swing-low nosimmetrik). Swing faqat i+k bar yopilgandan keyin ma'lum bo'ladi. **k: H1 = 3, M15 = 3, M5 = 2.**

## 2. H1 bias (qaror 1)
- **EMA bias:** oxirgi yopilgan H1 yopilishi > EMA50 va EMA50 > EMA200 → Long; < EMA50 va EMA50 < EMA200 → Short; aks holda yo'q.
- **Struktura bias:** oxirgi 2 ta tasdiqlangan H1 swing-high va 2 ta swing-low: HH+HL → bullish; LH+LL → bearish; aralash → yo'q.
- **Yakuniy bias:** ikkalasi bir yo'nalishda bo'lsa; aks holda **savdo yo'q**. Faqat EMA asosida kirish yo'q.

## 3. M15 BOS va impuls sharti (A8) — savol 1 javobi
**Haqiqat (oldingi hujjatlarda):** v1 matnida impuls sharti **diapazon** (High−Low) ≥ 1.0×ATR(M15) edi, **tana emas**. Bu 41% M15 barlarda bajariladi (2018-04 → 2025-02, tavsifiy statistika, strategiya natijasi emas), ya'ni deyarli filtrlamaydi. "Oldingi 0.15 ATR qoidasi" GoldStructure hujjatlarida **yo'q**: 0.15×ATR faqat N3 tadqiqotida (`STRATEGY_N3.md`, minimal stop masofasi, ATR_H1) uchragan va bu strategiyaga aloqasi yo'q. Agar siz boshqa hujjatdagi qoidani nazarda tutgan bo'lsangiz, ko'rsating.

**Variantlar (M15 barlarining ulushi, 2018-04 → 2025-02, ATR = oldingi yopilgan barda):** (a) diapazon ≥ 1.0×ATR: **41.2%** barlar (zaif filtr); (b) **real tana |Close−Open| ≥ 1.0×ATR: 12.7%** (qat'iy "displacement"); (c) real tana ≥ 0.7×ATR: 24.4%; (d) real tana ≥ 1.5×ATR: 4.7%. Median M15 ATR ≈ $1.86 (10–90%: $0.87–$3.96), ya'ni (b) tana ≥ ~$1.9 degani.

**Taklif (qaror kutilmoqda, muzlatishdan oldin siz tanlaysiz):** **(b) real tana** — v2 default: `abs(Close − Open) ≥ 1.0 × ATR(M15)`. Sabab: sizning savolingiz tana nazarda tutilganini ko'rsatadi; tana impulsni (yo'nalishli yopilish) diapazondan yaxshiroq ifodalaydi (uzun soyali, ammo yopilishi zaif shamlarni chiqarib tashlaydi). Ta'siri: BOS signallari (va undan keyingi zonalar) ancha kamayadi (12.7% vs 41%); savdolar soni ko'p marta kamayishi mumkin; N < 100 bo'lib "xulosasiz" bo'lish xavfi oshadi. (c) — yumshoqroq alternativ; sezgirlik sifatida sinaladi.
**ATR manbai:** BOS shami **kirmaydi**: ATR(14) BOS shamidan **bitta oldingi** yopilgan M15 barda (bar B−1) hisoblanadi — BOS shami o'zi ATR ni oshirmasligi va kelajak ma'lumoti kirmasligi uchun.

**BOS ta'rifi (Long; Short nosimmetrik):** B — M15 bar, uning **yopilishi** B−1 yopilguncha tasdiqlangan oxirgi M15 swing-high H* dan yuqori (swing tasdig'i p+k ≤ B−1), B−1 yopilishi esa H* dan yuqori bo'lmagan (**birinchi** yopilish buzilishi) va A8 shart bajarilgan (BOS shami yo'nalishi bias bilan mos: Long uchun Close > Open).

## 4. Supply/Demand zona (A6) — savol 2 javobi: aniq algoritm
Faqat B shami yopilgandan keyin, faqat B va undan oldingi barlar ma'lumoti bilan (kelajak yo'q). **Long (demand):**
1. **Buzilgan swing:** p* — H* ning bar indeksi (B−1 yopilishida tasdiqlangan eng oxirgi M15 swing-high).
2. **Impuls boshi S:** (p*, B−1] oralig'idagi barlar orasida **eng past Low** li bar; teng bo'lsa **eng oxirgisi**. (p* dan keyin kamida k=3 bar bor, shuning uchun oraliq bo'sh emas.)
3. **Zona sham Z:** i = S, S−1, S−2, … (ko'pi bilan S−5 gacha, va i > p*) tartibida **birinchi bearish (Close < Open) M15 sham**. Topilmasa — zona yo'q (hodisa "no_zone" deb qayd etiladi).
4. **Tekshiruv (zona allaqachon buzilmagan):** (Z, B−1] oralig'ida hech bir M15 **yopilishi** zona Low dan pastda bo'lmasligi shart; bo'lsa zona yaratilmaydi ("pre_violated").
5. **Zona = [Low[Z], High[Z]]** (to'liq diapazon, A6). Yaratilish vaqti: B yopilishi. **Sifat filtri (A7):** 0.3 ≤ (High[Z]−Low[Z]) / ATR(M15, B−1) ≤ 1.5, aks holda zona yaroqsiz ("bad_height").
**Short (supply):** nosimmetrik: eng past → eng baland High (S), bearish → bullish sham, "Low dan pastda" → "High dan yuqorida".
**Bekor bo'lish:** (a) 96 M15 bar (24 soat) o'tsa; (b) M15 yopilishi zonaning qarshi tomonidan tashqarida (Long: yopilish < zona Low; Short: yopilish > zona High); (c) 3-retest sodir bo'lsa; (d) savdo ochilsa; (e) yangi BOS yangi zona yaratsa (bitta faol zona, eng yangisi).

## 5. Zona kengligi filtri (A7) — savol 3 javobi
- **Chegaralar:** zona balandligi 0.3–1.5 × ATR(M15, B−1). **Sabab (a priori, optimallashtirilmagan):** 0.3 dan past — zona deyarli bitta narx darajasi; M5 shovqini va spred (balandlik ~ $0.5 atrofida) zona ichida "tegish" va "qamrash" ma'nosiz qiladi. 1.5 dan yuqori — zona "zona" emas, butun harakat diapazoni; stop masofasi (zona balandligi + 0.2×ATR buffer) A1 dagi 2.0×ATR yuqori chegarasiga yaqinlashadi va TP 2R juda uzoq bo'ladi.
- **"Oldingi 1.0 ATR chegarasi":** zona kengligi uchun oldin 1.0 ATR chegarasi **bo'lmagan**: v1 hujjatlarda ham 0.3–1.5 edi. 1.0×ATR faqat BOS impulsida (A8) uchragan. Agar siz boshqa joydagi raqamni nazarda tutgan bo'lsangiz, ko'rsating.
- **A1 bilan bog'liqligi:** entry zona ichida bo'lganda stop masofasi s taxminan (entry − zona chegarasi) + 0.2×ATR; zona balandligi 1.5 ATR bo'lsa s ≈ 1.7 ATR gacha. Binding filtr — A1 (0.5–2.0×ATR); A7 zona sifatini, A1 esa konkret savdo masofasini cheklaydi.

## 6. Retest (A10)
Retest = zona yaratilgandan keyin M5 sham diapazoni zonaga kirishi (Long: M5 Low ≤ zona High va High ≥ zona Low; Short nosimmetrik). **Retest epizodi** zonaga birinchi kirgan M5 bardan boshlanadi (j0) va M5 sham zonadan to'liq tashqarida bo'lganda (Long: Low > zona High; Short: High < zona Low) tugaydi; keyingi kirish — yangi retest. B yopilganida narx allaqachon zonada bo'lsa, shu birinchi kirish sanalmaydi. **Maksimal 2 retest.** Savdo faqat 1- yoki 2-retest epizodida.

## 7. M5 tasdiq: Pattern + MSS (qaror 2, A11, A12) — savol 4 javobi
**Retest epizodi ichida** ikki hodisa kerak: **P** (sham patterni) va **M** (MSS):
- **P — pattern bar:** Engulfing YOKI Pin Bar, **va zona bilan aloqasi:** bar diapazoni zonani kesishi (Long: Low ≤ zona High va High ≥ zona Low) **va** M5 yopilishi zona Low dan yuqorida (Long) / zona High dan pastda (Short). 
  - *Bullish Engulfing:* sham yashil; oldingi sham qizil; Open ≤ oldingi Close va Close ≥ oldingi Open; Close > oldingi High. Bearish — teskari.
  - *Bullish Pin Bar:* pastki soya ≥ 2×tana va ≥ 60% diapazon; yuqori soya ≤ 25% diapazon. Bearish — teskari.
- **M — MSS bar:** M5 yopilishi shu paytda **tasdiqlangan** (k=2) oxirgi M5 swing-high (Long) / swing-low (Short) dan tashqarida; MSS bari retest epizodi boshlanganidan **keyin yoki shu barda** (j0 ≤ M) bo'lishi shart; reference swing dinamik, lekin faqat tasdiqlangan swinglar.
- **Tartib:** P va M **istalgan tartibda** kelishi mumkin (P birinchi, M birinchi yoki bir barda). **3 ketma-ket M5 bar ichida:** |indeks(M) − indeks(P)| ≤ 2. **Signal bari** = P va M dan keyingisi (yoki ikkalasi bir bar). **Bir epizodda ko'pi bilan 1 signal.**
- **Signalning eskirishi (staleness):** signal **faqat keyingi M5 bar ochilishida** bajariladi (bitta bar). Quyidagilardan biri bo'lsa signal **eskirgan**, savdo yo'q, kechiktirib ochilmaydi: sessiya/yangilik/spred/pozitsiya band/kunlik limit filtri; stop masofasi filtri (A1) o'tmasa; zona signaldan keyin bekor bo'lsa; signal bari retest epizodidan 12 M5 bar (1 soat) dan keyin bo'lsa. Eskirgan signal retest hisobini o'zgartirmaydi; epizod davom etsa yangi P/M qidiriladi.

## 8. Kirish, stop, TP (qaror 3, A1, A15)
- **Kirish:** signal shamidan keyingi M5 bar ochilishida, market (Long Ask da, Short Bid da).
- **Stop:** Long — zona Low − 0.2 × ATR(M15); Short — zona High + 0.2 × ATR(M15) (ATR — signal paytida oxirgi yopilgan M15 bar). **Sun'iy o'zgartirilmaydi.**
- **Stop masofasi filtri (A1):** s = |kirish − stop|; **s < 0.5×ATR(M15) yoki s > 2.0×ATR(M15) bo'lsa savdo o'tkaziladi.**
- **TP:** kirishdan 2×s. Qisman yopish yo'q, breakeven yo'q.

## 9. Risk va pozitsiya (qaror 5, A4, A16)
Risk: equity (floating bilan) ning 1% i = lot × s × kontrakt qiymati; lot qadamiga pastga yaxlitlanadi; minimal lotdan kichik bo'lsa savdo o'tkaziladi; maksimal lot konfiguratsiyada. **Bir vaqtda faqat bitta EA pozitsiyasi** (MagicNumber bo'yicha). Kuniga savdolar soniga limit yo'q.

## 10. Kunlik −4% limit (A2, A3) — savol 9 javobi
- **Kun boshi:** New York 17:00 mahalliy (DST avtomatik; yakshanba kuni bozor ochilganda 17:00 NY ham). Shu paytdagi **EA hisob equity** (balans + EA pozitsiyalari floating) qayd etiladi: E0.
- **Kunlik natija D** = (bugungi yopilgan EA savdolari sof natijasi: foyda + **komissiya + swap**) + (ochiq EA pozitsiyalari **floating** P&L, hozirgi bid/ask bo'yicha, spred hisobga olingan). Faqat EA (MagicNumber) bo'yicha (`LimitScope=EA_ONLY`, default); ixtiyoriy `ACCOUNT` — butun hisob equity si.
- **Limit:** D ≤ −0.04 × E0 bo'lsa:
  1. **blok bayrog'i** o'rnatiladi (keyingi NY 17:00 gacha yangi kirish yo'q) va u terminal qayta ishga tushganda ham saqlanadi (global o'zgaruvchi);
  2. **barcha EA pozitsiyalari** darhol yopiladi (retry tartibi 11-bandda, xuddi shu yopish mexanizmi);
  3. kutilayotgan orderlar (bo'lsa) o'chiriladi; log yoziladi (vaqt, D, E0, pozitsiyalar);
  4. keyingi **NY 17:00** da blok yechiladi, yangi E0 qayd etiladi.
- **Backtest:** M1 bo'yicha eng yomon (adverse) narxda D hisoblanadi; D = −4% ga teginsa, pozitsiya shu −4% ni beruvchi narxda yopiladi (spred kiritilgan).

## 11. Sessiyalar, rollover himoyasi, yangilik, spred (qaror 4, A5, A13, A14) — savol 10 javobi
- **Sessiyalar (S1):** London 08:00–12:00 (Europe/London), New York 08:00–12:00 (America/New_York); **yangi kirish** faqat shu soatlarda, dushanba–juma; konfiguratsiya `LondonStart/End`, `NewYorkStart/End` (HH:MM mahalliy). Ochiq pozitsiya sessiya tugashi bilan yopilmaydi.
- **Rollover himoyasi:** `PreRolloverCloseNY` (default 16:30 NY) da barcha EA pozitsiyalari yopiladi; vaqt konfiguratsiyada, o'chirib qo'yish mumkin.
- **Yopish muvaffaqiyatsiz bo'lsa (favqulodda tartib):**
  1. 16:30 dan 16:55 gacha **har 60 soniyada** qayta urinish (har urinishda retcode logga; `deviation` oshirilgan: `EmergencyDeviationPoints`, default 100 punkt = $1.00);
  2. 16:55 da **FAVQULODDA HOLAT:** yangi kirish bloklanadi (`EmergencyBlock`), foydalanuvchiga ogohlantirish (`Alert`, `SendNotification`, `SendMail` — konfiguratsiya) har daqiqa;
  3. **har 10 soniyada** yopishga urinish davom etadi (bozor ochiq va savdo ruxsat etilgan ekan);
  4. pozitsiyaning **server tomonidagi SL/TP** (ochilganda qo'yilgan) saqlanadi va **o'zgartirilmaydi** — maksimal yo'qotish 1% risk bilan cheklangan; stop kengaytirilmaydi, hedge ochilmaydi (netting hisoblarda mumkin emas);
  5. bozor yopilgan bo'lsa (hafta oxiri) yoki broker rad etsa — holat davom etadi, bozor ochilganda birinchi imkoniyatda yopishga urinish, blok yechilmaydi (qo'lda tasdiq kerak: `EmergencyAck=true`); log va bildirishnoma saqlanadi;
  6. kunlik −4% limitga yetilib yopish muvaffaqiyatsiz bo'lsa ham xuddi shu 1–5 tartib qo'llanadi.
  - Backtestda favqulodda holat modellashtirilmaydi (yopish 16:30 M1 yopilish narxida muvaffaqiyatli deb olinadi); "yopishsiz" variant sezgirlikda.
- **Yangilik (A13) — savol 5 javobi:** NFP, CPI (m/m, core m/m, y/y), GDP (advance/prelim/second/final), FOMC (Statement, Federal Funds Rate) — AQSh, yuqori ta'sir. Yangilikdan 60 daqiqa oldin va 30 daqiqa keyin **yangi kirish yo'q**. EA: MT5 Economic Calendar + qo'lda ro'yxat (`news_manual.csv`: `utc_datetime;name`). Backtest: 12.1-bandga qarang.
- **Spred filtri (A14):** spred > $0.50 bo'lsa kirish yo'q (EA); backtestda doimiy.

### 11.1 Yangilik ma'lumoti manbai va formati (backtest) — savol 5
- **Manba:** `Ehsanrs2/Forex_Factory_Calendar` (Hugging Face, `forex_factory_cache.csv`, ~68 MB, 2007-01 → **2025-04-04**); ustunlar: DateTime, Currency, Impact, Event, Actual, Forecast, Previous, Detail. Biz faqat `Currency=USD`, `Impact="High Impact Expected"` va yuqoridagi nomlar.
- **Vaqt muammosi:** fayldagi vaqtlarning **49.2%** (2018–2025) yarim tun "00:00:00" placeholder, qolganlarida Eron/AQSh DST farqidan 1 soatlik siljishlar bor (tekshirilgan, `STRATEGY_NEXT.md` jurnali). Shuning uchun **sana fayldan, vaqt esa standart ET jadvalidan** (NFP/CPI/GDP 08:30 ET; FOMC Statement/Federal Funds Rate 14:00 ET), AQSh DST bilan UTC ga o'tkaziladi.
- **Saqlash formati (kodlashdan keyin, tasdiq bilan):** `data/news/usd_high_impact.csv`: `event_utc, family (NFP|CPI|GDP|FOMC), event_name, date_source (ff_date), time_source (standard_et), ff_datetime_raw`; repoga qo'shiladi (~800 qator), qurilish skripti `tools/build_news_calendar.py` (qayta ishlab chiqarish mumkin).
- **Mavjudlik (tekshirilgan, 2018–2025-02, USD yuqori ta'sir, noyob sanalar/yil):** NFP 12/12/12/12/12/12/12 (2018–2024) — **hamma oylar mavjud (2018-04 → 2025-02 da yo'q oy yo'q)**; CPI 12 har yili, **hamma oylar mavjud**; FOMC 8–9/yil (2020: 9, favqulodda majlis), 2025 da 2 (yanvar, mart); **GDP to'liq emas**: 2018: 12, 2019: 8, 2020: 5, 2021: 7, 2022: 8, 2023: 12, 2024: 12 (kutilgan ~12: har chorakda 3 versiya) — 2019–2022 da GDP yozuvlari **yetishmaydi** (kalendar bo'shliqlari).
- **Ma'lumot yetishmasa:** backtestda yetishmayotgan yangilik uchun **blok qo'yilmaydi** (taxmin qilinmaydi) va u **"yangilik filtri tekshirilmagan" deb belgilanadi**; fallback jadval faqat NFP uchun (oy birinchi juma 08:30 ET, istisnolar fayldan) — lekin NFP/CPI to'liq bo'lgani uchun kerak emas; GDP/FOMC uchun fallback yo'q.
- **Yangilik filtri ishlamagan davrlar (alohida ko'rsatiladi):** (i) **GDP bo'shliqlari 2019–2022** (har yili ~4–7 ta GDP e'lon yo'q); (ii) **2025-03 dan keyingi hamma davr** (FF kesh 2025-04-04 gacha, bizning backtest 2025-02 gacha — ta'sir yo'q, lekin 2025-03+ da filtr yo'q); (iii) **2026-09/10 tavsifiy tekshiruv: kalendar yo'q, filtr o'chirilgan**. Natijalar "filtr to'liq" (NFP/CPI/FOMC, GDP bo'shliqsiz davrlar 2023–2025-02) va "filtr to'liq emas" qismlar bo'yicha ham alohida hisobot qilinadi.

## 12. Xarajatlar (savol 6)
- **Spred birligi:** $/oz (XAUUSD narx birligi). **Asosiy: $0.30**, **stress: $0.50** — **to'liq aylanma (round-turn)** spred, bir marta hisoblanadi: Long — kirish **Ask = Bid + S** da, chiqish Bid da (SL/TP Bid ga tegsa); Short — kirish Bid da, chiqish **Ask = Bid + S** da (SL/TP uchun Bid+S ga tegsa). Ya'ni M1 **BID** narxlaridan spred to'liq bir tomonlama qo'shiladi (oldingi tadqiqotlarga nisbatan aniqroq: Short uchun SL/TP Ask bo'yicha tekshiriladi).
- **Komissiya:** asosiy 0 (standart hisob, spred ichida); sezgirlik: **$7/lot aylanma = $0.07/oz** (raw-spread/ECN hisob).
- **Slippage:** asosiy 0 (optimistik); **stress:** kirishda **$0.10/oz** va stop-loss chiqishida **$0.10/oz** (TP — limit, slippage yo'q), spred $0.50 bilan birga.
- **Swap:** NY 16:30 yopish bilan pozitsiyalar rollover (17:00 NY) dan o'tmaydi: swap **0**; majburiy yopish o'chirilgan sezgirlik variantida **yiliga 3% × pozitsiya qiymati × tunlar** (+ chorshanba 3 kunlik) qo'llanadi.
- **Risk va xarajat:** net R = (foyda − spred − komissiya − slippage − swap) / (s × lot).

## 13. Parametrlar jadvali (muzlatiladi)
swing k H1/M15/M5 = 3/3/2 · **impuls: real tana ≥ 1.0×ATR(M15, B−1) (A8: (a)/(b)/(c) tanlov kutilmoqda; default (b))** · zona sham qidirish ≤ 5 bar (S dan orqaga) · zona balandligi 0.3–1.5×ATR(M15, B−1) · zona muddati 96 M15 bar · retest ≤ 2 · Pin Bar 2×/60%/25% · P–M oynasi 3 M5 bar, signal eskirishi 12 M5 bar · stop buferi 0.2×ATR(M15) · stop oralig'i 0.5–2.0×ATR(M15) · RR 2.0 · risk 1% (equity) · kunlik limit 4% (EA_ONLY, floating+komissiya+swap) · kun boshi NY 17:00 · sessiya S1 · rollover yopish NY 16:30 (retry 60 s → 16:55 → favqulodda) · yangilik −60/+30 · spred ≤ $0.50 · backtest spredi $0.30 (stress $0.50).

## 14. A1–A18 jadvali (yakuniy default'lar va ta'siri) va 10 ta aniqlashtirish xaritasi

| # | Masala | Qaror | Strategiyaga ta'siri |
|---|---|---|---|
| A1 | Stop masofasi | zona ± 0.2×ATR; masofa 0.5–2.0×ATR(M15) dan tashqarida → savdo o'tkaziladi; stop o'zgartirilmaydi | Juda keng (uzoq TP) va juda tor (xarajat ulushi) stoplar kesiladi |
| A2 | Kun boshi | NY 17:00 mahalliy, DST avtomatik | −4% har kuni bir nuqtadan; server vaqtiga bog'liq emas |
| A3 | −4% ga yetsa | blok + hamma EA pozitsiyalarini yopish, NY 17:00 gacha | Katta zarar kuni cheklanadi (10-bo'lim) |
| A4 | Risk asosi | equity (floating bilan) | Zarar paytida hajm kamayadi |
| A5 | Sessiyadan tashqari | yangi kirish faqat sessiyada; NY 16:30 (konfiguratsiya) da yopish; muvaffaqiyatsiz bo'lsa favqulodda tartib | Kechasi swap/gap/rollover xavfi kamayadi; ba'zi savdolar TP/SL ga yetmay yopiladi |
| A6 | Zona | 4-bo'limdagi aniq algoritm (S, Z, tekshiruv); to'liq diapazon; 24 soat | Eng ta'sirli: zona tanlash savdolar sonini va stopni belgilaydi |
| A7 | Zona kengligi | 0.3–1.5×ATR(M15, B−1) (5-bo'lim) | Juda tor/keng zonalar kesiladi |
| A8 | BOS impulsi | real tana ≥ 1.0×ATR(M15, B−1) (default (b); (a)/(c) tanlov kutilmoqda) | BOS 12.7% barlarda (vs 41%): savdolar ancha kam |
| A9 | Swing k | 3/3/2 | k kichik — shovqin, katta — kechikish |
| A10 | Retest | epizod ta'rifi (6-bo'lim); ≤ 2 | Eski zonalarda savdo yo'q |
| A11 | Tasdiq | P va M istalgan tartibda, 3 bar ichida; P zonaga tegishi; signal 1 barda bajariladi, 12 bardan keyin eskiradi (7-bo'lim) | Bir barda talab qilinsa savdo deyarli yo'q; 3 bar ruxsati ko'paytiradi |
| A12 | Pattern parametrlari | Pin 2×/60%/25%; Engulfing qat'iy | Qat'iy ta'rif: kam, lekin aniq signal |
| A13 | Yangilik | NFP/CPI/GDP/FOMC −60/+30; EA kalendar + qo'lda; backtest FF + standart ET (11.1) | EA/backtest manbasi farq qiladi; GDP 2019–2022 bo'shliq |
| A14 | Spred | ≤ $0.50 (EA); backtest doimiy | Backtestda spred kengayishi modellashtirilmaydi |
| A15 | TP | 2R; qisman yopish/BE yo'q | Natija −1R yoki +2R |
| A16 | Lot | risk$/(s×kontrakt), pastga, min lotdan kichik → o'tkaziladi | Kichik hisobda signallar o'tkazilishi mumkin |
| A17 | Aktiv | XAUUSD; FX tasdiq qo'shimcha dalil (qarorga kirmaydi) | Oltinda N kam bo'lsa FX ishonch beradi |
| A18 | Ma'lumot | M1 BID, doimiy spred, real tick yo'q | Sham ichi tartibi taxminiy (stop birinchi) |

**10 ta aniqlashtirish xaritasi:** 1 → 3-bo'lim; 2 → 4-bo'lim; 3 → 5-bo'lim; 4 → 7-bo'lim; 5 → 11 va 11.1-bo'lim; 6 → 12-bo'lim; 7 → test rejasi 6-bo'lim; 8 → test rejasi 3-bo'lim; 9 → 10-bo'lim; 10 → 11-bo'lim.

## 15. Muzlatishdan oldin qolgan qarorlar (sizdan)
1. **A8 varianti:** (b) real tana ≥ 1.0×ATR (default), (c) tana ≥ 0.7×ATR, yoki (a) diapazon ≥ 1.0×ATR. Tavsifiy: (b) = 12.7% barlar, (c) = 24.4%, (a) = 41.2%.
2. Zona tekshiruvi 4-bandda (Z dan B−1 gacha pastda yopilish bo'lsa zona yaratilmaydi): ma'qulmi?
3. Signal eskirishi 12 M5 bar (1 soat) ma'qulmi?
4. `LimitScope=EA_ONLY` (default) ma'qulmi?
5. Stress slippage ($0.10) va komissiya sezgirligi ($0.07/oz) ma'qulmi?
6. Favqulodda holat (11-bo'lim): hedge ochilmaydi va stop kengaytirilmaydi — ma'qulmi?

## 16. Ochiq cheklovlar
1. Zona sham tanlash (4-bo'lim) bir nechta mantiqiy ta'rifdan biri; boshqalari sinalmaydi.
2. Savdolar soni oldindan noma'lum; **hech bir taxmin natija sifatida e'lon qilinmaydi.** (A8 (b) bilan savdolar ancha kam bo'lishi mumkin, bu "xulosasiz" natijaga olib kelishi mumkin.)
3. MQL5 da kalendar API va DST qoidalari qo'lda; Strategy Tester'da kalendar ishlamasligi mumkin.
4. Rollover spredi, requote va favqulodda holat M1 BID ma'lumotda ko'rinmaydi.

## 17. O'zgartirishlar jurnali
(hozircha bo'sh; tasdiqdan keyin to'ldiriladi)
