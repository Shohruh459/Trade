# GoldStructureEA: STRATEGY_SPEC (qoidalar spetsifikatsiyasi)

Holat: **LOYIHA (DRAFT) — foydalanuvchi tasdig'ini kutmoqda.** Tasdiqlangandan keyin muzlatiladi; o'zgartirish faqat 12-bo'limdagi jurnal orqali, sababi bilan. **Kod yozilmagan.** Hech bir raqam "natija" emas: savdolar soni, g'alaba ulushi va daromad faqat tarixiy backtestda o'lchanadi.

## 0. Konventsiyalar
- Aktiv: XAUUSD. Barcha ichki hisob-kitob UTC da; sessiya/kun chegaralari mahalliy vaqt zonalarida (Europe/London, America/New_York), DST har zona uchun **mustaqil** hisoblanadi (UK: mart oxirgi yakshanba 01:00 UTC → oktyabr oxirgi yakshanba 01:00 UTC; AQSh: mart 2-yakshanba 02:00 mahalliy → noyabr 1-yakshanba 02:00 mahalliy).
- Faqat **to'liq yopilgan** barlar ishlatiladi; repaint yo'q. ATR(14) = oxirgi 14 TR ning oddiy o'rtachasi (SMA), tegishli vaqt oralig'ida.
- Qaror vaqti: har yopilgan M5 barning yopilishida; kirish keyingi M5 bar ochilishida.

## 1. Swing (fractal)
Bar i — swing-high, agar High[i] oldingi k va keyingi k barning High laridan qat'iy yuqori (swing-low nosimmetrik). Swing faqat i+k bar yopilgandan keyin ma'lum. **k: H1 = 3, M15 = 3, M5 = 2.**

## 2. H1 bias (qaror 1)
- **EMA bias:** oxirgi yopilgan H1 yopilishi > EMA50 va EMA50 > EMA200 → Long; yopilish < EMA50 va EMA50 < EMA200 → Short; aks holda yo'q.
- **Struktura bias:** oxirgi 2 ta tasdiqlangan H1 swing-high va 2 ta swing-low: HH+HL → bullish; LH+LL → bearish; aralash → yo'q.
- **Yakuniy bias:** EMA bias **va** struktura bias bir xil yo'nalishda bo'lsa (Long/Short); aks holda **savdo yo'q**. Faqat EMA asosida kirish yo'q.

## 3. M15 BOS
Bias yo'nalishida: M15 sham **yopilishi** oxirgi tasdiqlangan M15 swing-high (Long) / swing-low (Short) dan tashqarida. **Impuls sharti (A8):** BOS shami diapazoni (High−Low) ≥ 1.0 × ATR(M15). Teskari yo'nalishdagi BOS yangi savdo bermaydi (faqat zonani bekor qilishi mumkin, 4-bo'lim).

## 4. Supply/Demand zona
- **Zona sham:** Long uchun — BOS bilan buzilgan swing-high dan keyingi eng past Low li bar S (impuls boshi); zona sham = S dan boshlab orqaga ko'pi bilan 5 bar ichidagi **oxirgi bearish (close < open) M15 sham** (S o'zi bearish bo'lsa S). Bunday sham topilmasa zona yo'q. Short uchun nosimmetrik (bullish sham, S = eng baland High).
- **Chegaralar (A6):** zona sham **to'liq diapazoni** [Low, High].
- **Yaratilish:** BOS shami yopilganda. **Muddati:** 96 M15 bar (24 soat). Bekor bo'ladi: (a) muddat tugasa; (b) M15 yopilishi zonaning qarshi tomonidan tashqarida (Long: yopilish < zona Low; Short: yopilish > zona High); (c) 3-retest sodir bo'lsa; (d) savdo ochilsa (zona ishlatilgan); (e) yangi BOS yangi zona yaratsa (faqat bitta faol zona, eng yangisi).
- **Sifat filtri (A7):** zona balandligi 0.3–1.5 × ATR(M15) oralig'ida bo'lmasa zona yaroqsiz.

## 5. Retest (A10)
Retest = zona yaratilgandan keyin M5 sham diapazoni zonaga kirishi (Long: M5 Low ≤ zona High; Short: M5 High ≥ zona Low), zonadan chiqib keyin qayta kirsa — keyingi retest. BOS shami yopilgan paytda narx allaqachon zonada bo'lsa, shu birinchi kirish sanalmaydi. **Maksimal 2 retest;** savdo faqat 1- yoki 2-retest davomida mumkin.

## 6. M5 tasdiq (qaror 2, A11, A12)
Retest davomida (narx zonada yoki zonadan chiqayotgan paytda) **ikki shart birgalikda**, ketma-ket **3 M5 bar ichida** (bir bar ham mumkin):
1. **Sham patterni (Engulfing YOKI Pin Bar)**, pattern sham diapazoni zonaga tegishi shart:
   - *Bullish Engulfing:* sham yashil, Open ≤ oldingi Close va Close ≥ oldingi Open (oldingi sham qizil), Close > oldingi High. Bearish — teskari.
   - *Bullish Pin Bar:* pastki soya ≥ 2 × tana va ≥ 60% diapazon, yuqori soya ≤ 25% diapazon. Bearish — teskari.
2. **MSS (M5):** retest boshlangandan keyin M5 sham yopilishi oxirgi tasdiqlangan M5 swing-high (Long) / swing-low (Short) dan tashqarida.
Ikkala shart bajarilgan **oxirgi bar** yopilgach kirish signali tug'iladi.

## 7. Kirish, stop, TP (qaror 3, A1, A15)
- **Kirish:** signal shamidan keyingi M5 bar ochilishida, market.
- **Stop:** Long — zona Low − 0.2 × ATR(M15); Short — zona High + 0.2 × ATR(M15). Stop **sun'iy o'zgartirilmaydi.**
- **Stop masofasi filtri (A1):** s = |kirish − stop|. **s < 0.5 × ATR(M15) yoki s > 2.0 × ATR(M15) bo'lsa savdo o'tkazib yuboriladi.**
- **TP:** kirishdan 2 × s (RR 1:2). Qisman yopish yo'q, breakeven yo'q.

## 8. Risk va pozitsiya (qaror 5, A4, A16)
- **Risk:** equity (floating bilan) ning 1% i = lot × s × kontrakt qiymati. Lot qadamiga pastga yaxlitlanadi; minimal lotdan kichik bo'lsa savdo o'tkaziladi; maksimal lot — konfiguratsiya.
- **Bir vaqtda faqat bitta EA pozitsiyasi.** Kuniga savdolar soniga limit yo'q.

## 9. Kunlik equity limiti (A2, A3)
- **Kun boshi:** New York 17:00 mahalliy (DST avtomatik). Kun boshidagi equity qayd etiladi.
- **Limit:** equity (floating bilan) kun boshidagi qiymatdan 4% ga kamaysa — ochiq pozitsiya yopiladi va **keyingi kun boshigacha** yangi savdo yo'q.

## 10. Sessiyalar, yopish, yangilik, spred (qaror 4, A5, A13, A14)
- **Sessiyalar (default S1):** London 08:00–12:00 (Europe/London), New York 08:00–12:00 (America/New_York); yangi kirish faqat shu soatlarda, dushanba–juma. Konfiguratsiya: `LondonStart/End`, `NewYorkStart/End` (HH:MM mahalliy). Sessiya **faqat yangi kirishni** cheklaydi; ochiq pozitsiya sessiya tugashi bilan yopilmaydi.
- **Rollover himoyasi (A5):** ochiq pozitsiya **NY 16:30 (konfiguratsiyada `PreRolloverCloseNY`, default 16:30)** da yopiladi — rollover (17:00 NY) dagi spred kengayishidan va broker cheklovlaridan oldin. Yopish bajarilmasa (rad etilsa/spred yuqori) har daqiqa qayta uriniladi 16:55 gacha. `0` yoki o'chirilgan bo'lsa majburiy yopish yo'q (sezgirlik sifatida sinaladi). Hafta oxiri: juma uchun ham xuddi shu vaqt.
- **Yangilik (A13):** NFP, CPI, FOMC, GDP (AQSh, yuqori ta'sir): yangilikdan 60 daqiqa oldin va 30 daqiqa keyin yangi kirish yo'q (ochiq pozitsiya o'z holicha). EA: MT5 Economic Calendar + qo'lda ro'yxat (fayl formati keyin kelishiladi). Backtest: Forex Factory (sana kalendardan, vaqt standart ET jadvalidan; 08:30 ET NFP/CPI/GDP, 14:00 ET FOMC), 2025-04 gacha.
- **Spred filtri (A14):** spred > $0.50 bo'lsa kirish yo'q (EA); backtestda spred doimiy $0.30.

## 11. Parametrlar jadvali (muzlatiladi)
swing k (H1/M15/M5) = 3/3/2 · impuls ≥ 1.0×ATR(M15) · zona sham qidirish ≤ 5 bar · zona balandligi 0.3–1.5×ATR(M15) · zona muddati 96 M15 bar · retest ≤ 2 · Pin Bar 2×/60%/25% · tasdiq oynasi 3 M5 bar · stop buferi 0.2×ATR(M15) · stop oralig'i 0.5–2.0×ATR(M15) · RR 2.0 · risk 1% (equity) · kunlik limit 4% · kun boshi NY 17:00 · sessiya S1 (London 08–12, NY 08–12 mahalliy) · rollover yopish NY 16:30 · yangilik −60/+30 daqiqa · spred ≤ $0.50.

## 12. A1–A18: yakuniy qarorlar va strategiyaga ta'siri

| # | Masala | Qaror | Strategiyaga ta'siri |
|---|---|---|---|
| A1 | Stop masofasi | zona ± 0.2×ATR; masofa 0.5–2.0×ATR(M15) dan tashqarida bo'lsa **savdo o'tkaziladi**; stop sun'iy o'zgartirilmaydi | Juda keng stop (uzoq TP, past ehtimol) va juda tor stop (xarajat ulushi katta) kesiladi; savdolar kamayadi |
| A2 | Kun boshi | NY 17:00 mahalliy, DST avtomatik | −4% hisobi har kuni bir xil nuqtadan; yarim tun/server vaqtiga bog'liq emas |
| A3 | −4% ga yetsa | pozitsiya yopiladi, keyingi kun boshigacha savdo yo'q | Katta zarar kunini cheklaydi; keyingi kuni "qaytarib olish" yo'q |
| A4 | Risk asosi | equity (floating bilan) | Zarar paytida hajm kamayadi; kompaund ta'sir |
| A5 | Sessiya tashqarisi | yangi kirish faqat sessiyada; ochiq pozitsiya TP/SL gacha; NY 16:30 (konfiguratsiya) da majburan yopiladi | Kechasi swap/gap va rollover spredidan himoya; ba'zi savdolar TP/SL ga yetmasdan yopiladi (natijaga ta'siri backtestda o'lchanadi) |
| A6 | Zona | to'liq diapazon [Low, High], 24 soat, qarshi tomondan yopilsa bekor | Tana-variantga nisbatan zona kengroq: ko'proq retest, stop uzoqroq |
| A7 | Zona sifati | balandlik 0.3–1.5×ATR(M15) | Juda tor/keng zonalar kesiladi; savdolar kamayadi |
| A8 | BOS impulsi | BOS sham diapazoni ≥ 1.0×ATR(M15) | Sust buzilishlar kesiladi; faqat kuchli harakatdan keyingi zonalar qoladi |
| A9 | Swing k | H1/M15 = 3, M5 = 2 | k kichik — ko'p swing (shovqin), katta — kech signal |
| A10 | Retest | zonaga kirish; chiqib qayta kirsa keyingi; ≤ 2 | Eski, "charchagan" zonalarda savdo yo'q |
| A11 | Tasdiq vaqti | pattern + MSS ketma-ket 3 M5 bar ichida; pattern zonaga tegishi shart | Bir barda ikkalasi talab qilinsa savdo deyarli bo'lmaydi; 3 bar ruxsati savdolar sonini oshiradi |
| A12 | Pattern parametrlari | Pin: 2×tana, 60%, 25%; Engulfing: tanani qamrash + oldingi ekstremumdan tashqarida yopilish | Qat'iy ta'rif: kamroq, lekin aniqroq signal |
| A13 | Yangilik | NFP/CPI/FOMC/GDP −60/+30; EA kalendar + qo'lda; backtest FF | EA va backtest bir xil emas (kalendar manbai farq qiladi) |
| A14 | Spred | ≤ $0.50 (EA); backtestda doimiy $0.30 | Spred kengayganda kirish yo'q; backtestda yangilik/rollover spredi modellashtirilmaydi |
| A15 | TP | 2R, qisman yopish va breakeven yo'q | Bitta natija (−1R yoki +2R) — sodda, hisob-kitob oson |
| A16 | Lot | risk$ / (s × kontrakt); pastga yaxlitlanadi; min lotdan kichik → o'tkaziladi; max lot konfiguratsiya | Kichik hisobda ko'p signal o'tkazilishi mumkin |
| A17 | Aktiv | XAUUSD; FX tasdiqlash qo'shimcha dalil (qarorga kirmaydi) | Oltin ma'lumotida savdolar kam bo'lsa FX qo'shimcha ishonch beradi |
| A18 | Ma'lumot | M1 BID + doimiy spred; real tick yo'q | Sham ichidagi tartib taxminiy (stop birinchi) |

## 13. Ochiq cheklovlar (muzlatishdan oldin ma'lum)
1. Zona sham tanlash (4-bo'lim) — bir nechta mantiqiy ta'rifdan biri; boshqalari sinalmaydi.
2. Savdolar soni oldindan noma'lum; **hech qanday taxmin natija sifatida e'lon qilinmaydi**, faqat backtest o'lchaydi.
3. MQL5 da kalendar API va DST qoidalari qo'lda; Strategy Tester'da kalendar ishlamasligi mumkin.
4. Rollover spredi va broker cheklovlari M1 BID ma'lumotda ko'rinmaydi.

## 14. O'zgartirishlar jurnali
(hozircha bo'sh; tasdiqdan keyin to'ldiriladi)
