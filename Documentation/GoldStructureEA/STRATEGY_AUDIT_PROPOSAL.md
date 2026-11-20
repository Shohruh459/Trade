# GoldStructureEA: Strategy Audit taklifi (kod yo'q, faqat ta'riflar va sinov rejasi)

Holat: **taklif, tasdiqlash kutilmoqda.** Bu hujjat strategiyani audit qiladi: har bir tushunchani **aniq, kodlanadigan qoidaga** aylantiradi, noaniq joylarni ko'rsatadi, sinov rejasini taklif qiladi. Hech qanday savdo kodi yozilmagan. Tasdiqlangan ta'riflar `Documentation/GoldStructureEA/STRATEGY_SPEC.md` (muzlatilgan spetsifikatsiya) va pre-registered sinov rejasiga ko'chiriladi.

## 1. Strategiya (sizning matningiz)
XAUUSD kun ichi. **H1:** EMA50/200 + bozor strukturasi. **M15:** BOS + Supply/Demand zona. **M5:** Engulfing, Pin Bar, MSS tasdig'i. Zonaga maksimal 2 retest. Risk 1%/savdo, kunlik equity zarar limiti 4%, RR 1:2. London + New York sessiyalari. MT5 Economic Calendar + qo'lda yangilik zaxirasi.

## 2. Audit xulosasi
| Qism | Holat | Muammo |
|---|---|---|
| H1 EMA50/200 | aniq | "Trend" sharti yozilmagan (faqat EMA kesishuvimi yoki narx joylashuvi ham) |
| H1 struktura | **noaniq** | Swing ta'rifi, HH/HL/LH/LL qachon "buzilgan" hisoblanadi |
| M15 BOS | **noaniq** | Qaysi swing, close yoki wick, "impuls" talabi |
| Supply/Demand zona | **juda noaniq** | Zona qaysi sham(lar)dan, body yoki to'liq diapazon, amal qilish muddati, bekor bo'lish |
| Retest hisobi | **noaniq** | "Retest" = zona chegarasiga tegish yoki ichiga kirish; qayta sanash qoidasi |
| M5 Engulfing / Pin Bar | o'rtacha | Standart ta'riflar bor, parametrlar kerak |
| M5 MSS | **noaniq** | M5 da qaysi swing, qaysi yo'nalishda |
| Tasdiq mantiq | **noaniq** | Engulfing, Pin Bar, MSS "VA" yoki "YOKI" |
| Kirish / SL / TP | qisman | SL joyi (zona chegarasi yoki sham ekstremumi), kirish turi |
| Risk/limit | aniq | Kunlik 4% — kun boshidagi equity ga nisbatan (floating bilan) |
| Sessiyalar | qisman | Aniq UTC soatlari |
| Yangilik | qisman | Qaysi yangiliklar, oyna uzunligi; backtestda kalendar manbai |

Umumiy: **erkinlik darajasi yuqori** (taxminan 25–30 parametr). Oldindan muzlatish va optimallashtirmaslik shart.

## 3. Taklif qilinadigan aniq ta'riflar (default; sizning tasdig'ingiz kerak)

### 3.1 Umumiy
- Faqat **to'liq yopilgan** barlar, **repaint yo'q**. Barcha vaqt UTC. ATR = SMA(TR, 14), mos vaqt oralig'ida.
- **Swing (fractal) k:** H1 va M15 uchun k = 3, M5 uchun k = 2: bar i swing-high, agar High[i] oldingi k va keyingi k barning High laridan qat'iy yuqori. Swing faqat k bar o'tgandan keyin (tasdiqlanganda) ma'lum.

### 3.2 H1 bias
- **EMA bias:** oxirgi yopilgan H1 yopilishi > EMA50 va EMA50 > EMA200 → Long bias; teskari → Short bias; aks holda savdo yo'q.
- **Struktura bias:** oxirgi ikkita tasdiqlangan H1 swing-high va ikkita swing-low: HH+HL → bullish; LH+LL → bearish; aralash → bias yo'q.
- **Yakuniy bias:** EMA bias va struktura bias **ikkalasi mos** bo'lsa (default). Alternativ A: faqat EMA. Alternativ B: faqat struktura.

### 3.3 M15 BOS (Break of Structure)
- Bias yo'nalishida: M15 sham **yopilishi** oxirgi tasdiqlangan M15 swing-high (Long) / swing-low (Short) dan tashqarida.
- **Impuls (displacement) sharti:** BOS shamining diapazoni ≥ 1.0 × ATR(M15) **yoki** BOS shami tanasi ≥ 60% diapazonning. (Default: birinchi shart.)
- BOS faqat bias yo'nalishida; teskari BOS bias o'zgarishi hisoblanmaydi (faqat zonani bekor qiladi).

### 3.4 Supply/Demand zona
- BOS ni keltirib chiqargan impuls harakat boshlanishidan oldingi **oxirgi qarama-qarshi rangli M15 sham** (Long uchun oxirgi qizil sham, Short uchun oxirgi yashil) = **zona sham** (order-block turi).
- **Zona chegaralari:** to'liq diapazon [Low, High] (default); alternativ: faqat tana [Open, Close].
- **Amal qilish:** zona BOS shami yopilganda yaratiladi. Muddati 96 M15 bar (24 soat). Narx zonaning qarshi tomonidan **yopilish bilan** o'tsa (Long: yopilish < zona Low; Short: yopilish > zona High) — zona bekor.
- Bir vaqtda faqat bitta faol zona (eng yangisi, bias yo'nalishida).
- **Zona sifati filtri:** zona balandligi ≥ 0.3 × ATR(M15) va ≤ 1.5 × ATR(M15) (juda tor/keng zonalarni o'tkazish).

### 3.5 Retest
- **Retest** = zona yaratilgandan keyin narx (M5 sham High/Low) zona ichiga kirishi (Long: M5 Low ≤ zona High; Short: M5 High ≥ zona Low). Zonadan chiqib, keyin yana kirsa — keyingi retest. Zona yaratilgan zahoti allaqachon ichida bo'lsa, birinchi kirish sanalmaydi.
- **Maksimal 2 retest:** 1-retest va 2-retest da savdo qilish mumkin; 3-retestda zona bekor. Savdo ochilgandan keyin zona ishlatilgan hisoblanadi.

### 3.6 M5 tasdiq (retest paytida)
- **Bullish Engulfing:** joriy yopilgan M5 sham yashil, tanasi oldingi qizil sham tanasini to'liq qamraydi (Open ≤ prev Close va Close ≥ prev Open) va yopilish > oldingi High. Bearish teskari.
- **Pin Bar (bullish):** pastki soya ≥ 2 × tana va ≥ 60% diapazon, yuqori soya ≤ 25% diapazon, Low zona ichida. Bearish teskari.
- **MSS (Market Structure Shift) M5:** retest boshlangandan keyin M5 sham yopilishi oxirgi tasdiqlangan M5 swing-high (Long) / swing-low (Short) dan tashqarida (pullback tugab, kichik struktura bias tomonga siljiganini bildiradi).
- **Tasdiq mantiqi (default):** (**Engulfing YOKI Pin Bar**) **VA MSS** — ikkala tasdiq ham, retest bo'yicha bir M5 bar ichida yoki 3 bar ichida. Alternativ A: faqat (Engulfing YOKI Pin Bar). Alternativ B: faqat MSS.

### 3.7 Kirish, stop, TP
- **Kirish:** tasdiq shami yopilgach keyingi M5 bar ochilishida, market.
- **Stop:** zona qarama-qarshi chegarasidan (Long: zona Low; Short: zona High) 0.2 × ATR(M15) narida. Stop masofasi > 2.0 × ATR(M15) yoki < 0.5 × ATR(M15) bo'lsa o'tkaziladi.
- **TP:** 2R (RR 1:2). **Qo'shimcha chiqish:** yo'q (default); sezgirlikda: H1 bias o'zgarsa yopish; vaqt chiqishi 24 soat.
- **Risk:** equity ning 1% i (R = stop masofasi × lot).

### 3.8 Filtrlar
- **Sessiya:** kirish 07:00–11:00 (London) va 12:00–16:00 (New York ochilishi) UTC, dushanba–juma. (Matnda aniq soat yo'q: default taklif.)
- **Kunlik limit:** kun boshidagi equity ga nisbatan floating bilan −4% ga yetsa — pozitsiyalar yopiladi, shu kunga savdo yo'q. Ketma-ket 3 zarar: shu kun to'xtaydi (taklif).
- **Bir vaqtda 1 pozitsiya;** kuniga ko'pi bilan 3 savdo (taklif).
- **Yangilik:** NFP, CPI, FOMC, GDP (AQSh, yuqori ta'sir): yangilikdan 60 daqiqa oldin va 30 daqiqa keyin yangi savdo yo'q. EA da MT5 kalendari (+ qo'lda zaxira ro'yxat), backtestda Forex Factory kalendari (standart ET jadvali) ishlatiladi.
- **Spred filtri:** spred > $0.50 bo'lsa kirish yo'q (EA da); backtestda spred doimiy $0.30.

## 4. Parametrlar jadvali (muzlatiladi)
swing k (H1=3, M15=3, M5=2); impuls ≥ 1.0 ATR(M15); zona balandligi 0.3–1.5 ATR(M15); zona muddati 96 M15 bar; retest ≤ 2; Pin Bar 2×/60%/25%; MSS M5 k=2; tasdiq oynasi 3 M5 bar; stop buferi 0.2 ATR; stop oralig'i 0.5–2.0 ATR; RR 2.0; sessiya 07–11 va 12–16 UTC; kunlik −4%; kuniga ≤ 3 savdo; yangilik −60/+30 daqiqa.
**Qoida:** parametrlar natijaga qarab o'zgartirilmaydi. Sezgirlik (±) faqat tavsifiy.

## 5. Ochiq savollar (javobingiz kerak; default'lar bilan "ha" desangiz yetarli)
1. H1 bias: EMA **va** struktura ikkalasi mos (default) yoki faqat EMA?
2. Zona: to'liq diapazon (default) yoki faqat tana? Zona muddati 24 soatmi?
3. Tasdiq: (Engulfing YOKI Pin Bar) **VA** MSS (default) yoki yengilroq (faqat sham pattern)?
4. Sessiya soatlari: 07–11 va 12–16 UTC (default) yoki boshqa?
5. Stop zona chegarasida (default) yoki tasdiq shami ekstremumida (stop ancha tor, RR yaxshi, lekin shovqinli)?
6. Kuniga maksimal savdo (3) va 3 zararli savdodan keyin to'xtash qoidalari ma'qulmi?
7. "Kunlik equity zarar limiti 4%": kun boshidagi balansdanmi yoki equity dan (default: equity, floating bilan)?
8. Maqsad aktiv: faqat XAUUSD; FX (EUR/USD) tasdiqlash sifatida kerakmi?
9. Real brokerda spred/tick ma'lumoti bormi (Dukascopy hozircha cheklangan)?

## 6. Sinov rejasi (taklif; tasdiqdan keyin yoziladi va commit qilinadi)
- **Bosqich 1 (Python, MQL5 emas):** ta'riflar `backtest/` ga kodlanadi, **natijani ko'rishdan oldin** muzlatilgan reja (`STRATEGY_GOLDSTRUCTURE.md`) commit qilinadi. Ma'lumot: XAUUSD M1 BID (2018-01 → 2025-02), M5/M15/H1 M1 dan; xarajat spred $0.30 (stress $0.50); davrlar: Dev 2019–2021, Val 2022–2023, Final 2024-01 → 2025-02; 2026-09/10 tavsifiy tekshiruv (MetaQuotes demo M1).
- **Mezonlar (taklif):** o'rtacha sof R > 0, hafta-klasterlangan p ≤ 0.10, N ≥ 100 (N kam bo'lsa "xulosasiz"); stress xarajatda > 0; har davrda > 0; **tasodifiy kirish nazorati** p ≤ 0.10 (zona/sessiya/yangilik filtrlari o'tgan vaqtlarda bias yo'nalishida tasodifiy kirish); maksimal drawdown ≤ 20% (1% riskda); profit factor ≥ 1.2; FX tasdiqlash (EUR/USD, GBP/USD) ixtiyoriy.
- **Qo'shimcha o'lchovlar:** savdolar soni yiliga (kutilma: 15–60), har komponent hissasi (BOS+zona vs M5 tasdiq), qaysi filtr savdolar sonini qanchaga kamaytiradi.
- **Bosqich 2 (faqat PASS bo'lsa):** MQL5 EA (modullar `Include/GoldStructureEA/`: Structure, Zones, Confirmation, Risk, News, Sessions), Strategy Tester + demo ≥ 3 oy (24 oy/60 savdodan keyin real pul haqida gap).
- **FAIL bo'lsa:** qoida rad etiladi, parametrlar "yaxshilanmaydi", MQL5 yozilmaydi.

## 7. Xavflar (oldindan)
- **Savdolar soni kam** (filtrlar ko'p): statistik kuch past; N < 100 bo'lsa natija xulosasiz.
- **Erkinlik darajasi yuqori:** ta'riflarning boshqa variantlari ham mumkin; faqat default sinaladi.
- **M5 kirish va kichik stop:** xarajat ulushi (spred $0.30 / stop $3–6) 5–10% R; oldingi M5/M15 sinovlarida shu tufayli zarar bo'lgan.
- **Subyektiv "to'g'ri" zona:** kodlangan ta'rif treyderning ko'z bilan tanlashidan farq qiladi; natija "SMC ishlaydimi" emas, "mana shu ta'rif ishlaydimi" ni o'lchaydi.
- **Hindsight:** 2018–2025 davri oldingi tadqiqotlarda ishlatilgan; natija dastlabki.
- **MQL5 tomoni:** zonalar va swinglarni repaint'siz yuritish, kalendar API tester'da cheklangan, H4/H1 server vaqti UTC dan farq qiladi.

## 8. Keyingi qadamlar
1. 5-bo'limdagi savollarga javob (yoki "default'lar").
2. Men `STRATEGY_SPEC.md` (muzlatilgan spetsifikatsiya) va `STRATEGY_GOLDSTRUCTURE.md` (pre-registered sinov rejasi) tayyorlayman, commit qilaman.
3. Python backtest yoziladi va ishga tushiriladi; natija sizga yuboriladi. MQL5 — faqat PASS bo'lsa.
