# GoldStructureEA: qabul qilingan qarorlar (foydalanuvchi) va ochiq masalalar

Holat (2026-11-20, yangilanish): foydalanuvchi **S1 sessiyasini tanladi**, A1–A18 default'larini boshlang'ich qaror sifatida qabul qildi (A1 aniqlashtirildi: stop masofasi 0.5–2.0×ATR(M15) dan tashqarida bo'lsa savdo o'tkaziladi, stop sun'iy o'zgartirilmaydi; A5 aniqlashtirildi: NY 17:00 da emas, undan oldin yopish mexanizmi, vaqt konfiguratsiyada, ochiq pozitsiya sessiya tugashi bilan darhol yopilmaydi). Yakuniy hujjatlar: `STRATEGY_SPEC.md` va `STRATEGY_GOLDSTRUCTURE.md` (loyiha, tasdiq kutilmoqda). Eski holat: qarorlar yozildi, **EA kodi yozilmagan**. Implementatsiya foydalanuvchi tasdig'idan keyin (6-bo'lim). Bu hujjat `STRATEGY_AUDIT_PROPOSAL.md` ning 3.2, 3.6, 3.7 (stop) va 3.8 (sessiya/limit) bandlarini yangilaydi.

## 1. Qabul qilingan qarorlar (foydalanuvchi, 2026-11-20)
1. **H1 bias:** EMA50/200 **va** Market Structure ikkalasi bir yo'nalishni tasdiqlashi shart; mos kelmasa savdo yo'q. Faqat EMA asosida kirish **yo'q**.
2. **M5 tasdiq:** (**Engulfing YOKI Pin Bar**) **VA MSS** birgalikda bo'lishi shart (kamida bitta sham patterni + MSS).
3. **Stop-loss:** Supply/Demand zona chegarasidan tashqarida, M15 ATR(14) × 0.2 buffer bilan: BUY uchun zona pastki chegarasidan pastda, SELL uchun zona yuqori chegarasidan yuqorida.
4. **Sessiyalar:** London va New York, **mahalliy vaqt bo'yicha, DST avtomatik**; boshlanish/tugash soatlari konfiguratsiyada o'zgartiriladi. Default vaqtlar 3-bo'limda (tasdiq kutilmoqda).
5. **Kunlik cheklov:** kuniga savdolar soni bo'yicha **qat'iy limit yo'q**; bir vaqtda **faqat bitta EA pozitsiyasi**; kunlik equity yo'qotish limiti **4%**; savdo riski **1%**.

Bu qarorlardan kelib chiqadigan oqibatlar:
- Taklifdagi "kuniga ≤ 3 savdo" va "3 ketma-ket zarar → kun to'xtaydi" qoidalari **olib tashlanadi** (qaror 5). Yagona kun himoyasi: −4% equity limiti (1% riskda taxminan 4 ta zarar).
- Stop zona chegarasiga bog'langani uchun **stop masofasi o'zgaruvchan**: TP = 2R, ya'ni stop katta bo'lsa TP ham uzoq. Bu 4.3-bandda ochiq savol sifatida qoldirilgan.

## 2. Hali ham ochiq savollar (kod yozishdan oldin hal bo'lishi kerak)
Har bandda default taklif va oqibati. Javobingiz: "default" yoki o'zgartirish.

| # | Masala | Taklif (default) | Nega muhim |
|---|---|---|---|
| A1 | **Stop masofasi chegaralari** (qaror 3 ga qo'shimcha) | stop masofasi 0.5–2.0 × ATR(M15) oralig'ida bo'lmasa savdo o'tkaziladi | Juda keng zonada TP uzoq bo'lib, ehtimol past; juda torda xarajat ulushi katta. Chegarasiz sinov ham mumkin (sezgirlik sifatida) |
| A2 | **Kun boshi (kunlik −4% hisobi uchun)** | New York 17:00 (kunlik rollover); alternativ: 00:00 UTC yoki broker serveri yarim tuni | −4% "qaysi kun"ga nisbatan; DST bilan siljimasligi kerak (NY 17:00 DST ga avtomatik moslashadi) |
| A3 | **−4% limitga yetganda** | ochiq pozitsiyani yopish + keyingi kun boshigacha savdo yo'q | Qo'l bilan yoki avtomatik; ochiq pozitsiya qoldiriladimi |
| A4 | **Equity yoki balans** asosida 1% risk va 4% limit | Equity (floating bilan) | Floating zarar paytida yangi lot hajmi |
| A5 | **Sessiyadan tashqari pozitsiya** | Sessiya faqat **yangi kirish** uchun; ochiq pozitsiya TP/SL gacha ushlanadi, lekin New York 17:00 da majburan yopiladi | Kechasi swap, gap, Osiyo sessiyasi xavfi |
| A6 | **Zona**: to'liq diapazon yoki tana; muddati | to'liq diapazon [Low, High]; muddati 24 soat (96 M15 bar); qarshi tomondan yopilsa bekor | Eng ta'sirli noaniqlik |
| A7 | **Zona sifati filtri** | zona balandligi 0.3–1.5 × ATR(M15) | Juda tor/keng zonalar |
| A8 | **M15 BOS impulsi** | BOS shami diapazoni ≥ 1.0 × ATR(M15) | "Haqiqiy" BOS ni sust buzilishdan ajratish |
| A9 | **Swing k** | H1 va M15 k=3; M5 k=2 | Struktura va MSS sezgirligi |
| A10 | **Retest ta'rifi** | M5 High/Low zonaga kirsa; zonadan chiqib qayta kirsa keyingi retest; max 2; zona yaratilganda allaqachon ichida bo'lsa birinchi kirish sanalmaydi | "Maksimal 2 retest" aniqligi |
| A11 | **Tasdiq vaqti** | MSS va (Engulfing YOKI Pin Bar) retest bilan bir M5 bar ichida yoki ketma-ket 3 M5 bar ichida; pattern sham zonaga tegishi shart | Bir vaqtda talab juda kam savdo beradi |
| A12 | **Pin Bar / Engulfing parametrlari** | Pin: soya ≥ 2×tana va ≥ 60% diapazon, qarama-qarshi soya ≤ 25%; Engulfing: tana oldingi tanani to'liq qamraydi va oldingi High/Low dan tashqarida yopiladi | Standart ta'riflar farq qiladi |
| A13 | **Yangilik filtri** | NFP, CPI, FOMC, GDP (AQSh, yuqori ta'sir): −60/+30 daqiqa yangi kirish yo'q; EA: MT5 kalendari + qo'lda ro'yxat (fayl formati kelishiladi); backtest: Forex Factory (standart ET jadvali) | EA va backtest bir xil bo'lmaydi |
| A14 | **Spred filtri** | spred > $0.50 bo'lsa kirish yo'q | Real EA da; backtestda doimiy $0.30 |
| A15 | **TP / chiqish** | TP = 2R; boshqa chiqish yo'q (qisman yopish, breakeven yo'q) | Soddalik |
| A16 | **Lot hisobi** | risk$ / (stop masofasi × kontrakt qiymati); lot qadamiga pastga yaxlitlanadi; minimal lotdan kichik bo'lsa o'tkaziladi; maksimal lot chegarasi (konfiguratsiya) | Kichik hisob muammosi |
| A17 | **Aktiv va tasdiqlash** | XAUUSD; FX (EUR/USD) tasdiqlash ixtiyoriy | Sinov dizayni |
| A18 | **Tick/spred ma'lumoti** | M1 BID + doimiy spred; real tick yo'q | Sinov aniqligi |

## 3. Sessiya vaqtlari: variantlar (qaror 4; tasdiq kerak)
Mahalliy vaqt bo'yicha, DST avtomatik (UK: mart/oktyabr oxirgi yakshanba; AQSh: mart 2-yakshanba / noyabr 1-yakshanba). Jadvalda UTC ekvivalenti ko'rsatilgan (qish/yoz).

| Variant | London (mahalliy) | New York (mahalliy) | UTC qish | UTC yoz | Izoh |
|---|---|---|---|---|---|
| **S1 (default, tavsiya)** | 08:00–12:00 | 08:00–12:00 | 08–12 va 13–17 | 07–11 va 12–16 | Ikkala sessiyaning faol ochilish qismi; 12:00–13:00 London (NY 07:00–08:00) kirish yo'q. Oldingi sinovlarimiz (yoz 07–16 UTC) bilan mos |
| S2 (kengaytirilgan) | 08:00–16:30 | 08:00–17:00 | 08:00–22:00 UTC birlashtirilgan | 07:00–21:00 | Uzun; London yopilishi va NY kechki sessiya (past likvidlik) ham kiradi; savdolar ko'p, sifat pastroq |
| S3 (overlap) | 13:00–17:00 | 08:00–12:00 | 13–17 | 12–16 | Faqat London–NY kesishmasi (eng yuqori likvidlik); London ertalabki qismi yo'q |
| S4 (ochilish oynalari) | 08:00–11:00 | 08:20–11:30 | 08–11 va 13:20–16:30 | 07–10 va 12:20–15:30 | NY 08:20 = COMEX oltin ochilishi; eng qisqa |

Tavsiya: **S1** (konfiguratsiyada `LondonStart/End`, `NewYorkStart/End` — mahalliy HH:MM). Sessiyalar kesishsa (S2/S3) bitta sessiya sifatida birlashtiriladi. MQL5 da DST qoidalari qo'lda kodlanadi (MQL5 da timezone bazasi yo'q), Python backtestda `zoneinfo` (Europe/London, America/New_York).

## 4. Qarorlar jadvali (yangilangan qoidalar xulosasi)
- H1: EMA50/200 **va** struktura mos (majburiy). M15: BOS + Supply/Demand zona. M5: (Engulfing yoki Pin Bar) **va** MSS. Max 2 retest.
- SL: zona chegarasi ± 0.2 × ATR(M15). TP: 2R. Risk 1% (equity), kunlik −4%. Bir vaqtda 1 pozitsiya, kuniga savdolar soniga limit yo'q.
- Sessiyalar: London + New York, mahalliy vaqt, DST avtomatik, konfiguratsiya orqali (default S1).
- Yangilik: MT5 kalendari + qo'lda zaxira.

## 5. Kutilma (oldindan, halol)
Qoidalar juda ko'p filtr (H1 ikkalasi mos + zona + retest + pattern + MSS) beradi: savdolar kam bo'ladi (taxminan yiliga 10–40), bu statistik xulosa uchun yetarli bo'lmasligi mumkin. Stop zona bilan bog'langani uchun RR 1:2 uzoq TP bo'ladi: g'alaba ulushi past bo'lishi mumkin. Natija: ehtimol "xulosasiz yoki ustunlik yo'q". Bu sinov qarorni asosli qiladi.

## 6. Tasdiq va keyingi qadam
Siz tasdiqlaysiz: (1) S1–S4 dan sessiya varianti, (2) 2-bo'limdagi A1–A18 default'lari (yoki o'zgartirishlar). Shundan keyin:
1. `STRATEGY_SPEC.md` (muzlatilgan spetsifikatsiya) va `STRATEGY_GOLDSTRUCTURE.md` (pre-registered sinov rejasi) yoziladi va commit qilinadi;
2. Python backtest yoziladi va ishga tushiriladi (MQL5 emas);
3. MQL5 EA faqat natija PASS bo'lsa.
**Tasdiqsiz hech qanday kod (Python ham, MQL5 ham) yozilmaydi.**
