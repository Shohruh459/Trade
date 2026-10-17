# Oltin uchun kunlik trend/momentum: oldindan yozilgan (pre-registered) tadqiqot rejasi

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Quyidagi qoidalar, ma'lumot, mezonlar test paytida o'zgartirilmaydi. Har qanday o'zgartirish
7-bo'limdagi "O'zgartirishlar jurnali"ga sababi va sanasi bilan yoziladi va natijaga qarab moslashtirilgan deb belgilanadi.

## 1. Nega bu reja
Skalping bo'yicha 6 ta ochiq EA va 1 ta hodisa tadqiqoti xarajatdan keyin foyda bermadi (reports/summary_gold_EAs.md, reports/event_study_H1.md): spred har bitimda
~$0.3–0.45 oladi, qisqa muddatli narx harakati esa bashorat qilinmaydi. Kunlik vaqt oralig'ida xarajat ahamiyatsiz (spred ~$0.4, kunlik diapazon ~$30) va
trend/momentum ("time-series momentum", masalan Moskowitz–Ooi–Pedersen 2012; Hurst–Ooi–Pedersen 2017) ko'p aktivlarda tadqiq qilingan. Bu **foyda kafolati emas**:
oxirgi yillarda natijalar pasaygan, drawdownlar uzoq davom etadi. Reja gipotezani halol sinash uchun yozilgan: sinov o'zi "ishlamaydi" degan javob berishi mumkin.

## 2. Ma'lumot (muzlatilgan)
- **Asosiy (Stage 1): XAUUSD kunlik.** Manba: `ZombitX64/xauusd-gold-price-historical-data-2004-2025`, fayl `XAU_1d_data.jsonl` (MT server vaqti, kunlik yopilish narxi).
  Davr: 2004-06-11 → **2025-02-28** (2025-04 dan keyin ma'lumotda bo'shliqlar bor, shuning uchun kesiladi). Faqat yopilish narxi (close) ishlatiladi.
  Sifat tekshiruvi (natijadan mustaqil, test oldidan): 2018–2025-02 oralig'ida kunlik yopilishlar M1/H1 ma'lumotimizdan qayta qurilgan kunliklar bilan solishtiriladi
  (kunlik daromadlar korrelyatsiyasi ≥ 0.99 kutiladi); mos kelmasa sabab yoziladi va o'zgartirish jurnaliga kiritiladi.
- **Tasdiqlash (Stage 2), mustaqil aktivlar, 2000-01-03 → 2025-12-31:**
  - 8 valyuta kursi, AQSh Federal Reserve H.10 kunlik (`datasets/exchange-rates`): Euro, United Kingdom, Japan, Switzerland, Canada, Australia, New Zealand, Sweden.
  - Brent xom neft, EIA kunlik spot (`datasets/oil-prices/brent-daily.csv`).
  - WTI **kiritilmaydi** (2020-yil aprelda manfiy narx bor, daromad hisoblanmaydi). Bo'sh qiymatlar oldingi qiymat bilan to'ldirilmaydi: o'sha kun tashlanadi.
  - FX va neft uchun faqat narx (carry/swap va fyuchers roll daromadi yo'q): bu "signal haqiqiyligi" tekshiruvi, haqiqiy P&L emas.
- Hamma seriya uchun dastlabki 260 savdo kuni faqat signalni boshlash uchun (warm-up), P&L shundan keyin hisoblanadi.

## 3. Signallar (4 ta "hujayra", hammasi long/short, parametrlar muzlatilgan, sozlanmaydi)
P_t = kunlik yopilish, r_t = P_t/P_{t−1} − 1. Signal s_t t kuni yopilishigacha bo'lgan ma'lumotdan hisoblanadi.
- **S1 TSMOM-252:** s_t = sign(P_t/P_{t−252} − 1).
- **S2 Ansambl:** s_t = ¼ · Σ_{L∈{21,63,126,252}} sign(P_t/P_{t−L} − 1) (qiymat −1…+1).
- **S3 MA kesishuvi:** s_t = sign(SMA50_t − SMA200_t).
- **S4 Donchian (yopilish bo'yicha):** holat u_t ∈ {−1,0,+1}, boshida 0. P_t > max(P_{t−55..t−1}) bo'lsa u=+1; P_t < min(P_{t−20..t−1}) bo'lsa long yopiladi (u=0);
  P_t < min(P_{t−55..t−1}) bo'lsa u=−1; P_t > max(P_{t−20..t−1}) bo'lsa short yopiladi (u=0); aks holda holat saqlanadi. s_t = u_t.
- *Tavsif uchun (qarorga ta'sir qilmaydi):* shu signallarning long/flat varianti (s_t < 0 → 0).

## 4. Pozitsiya hajmi, ijro va xarajat modeli
- **O'zgaruvchanlikka moslash:** σ̂_t = sqrt(252 · v_t), v_t = 0.94·v_{t−1} + 0.06·r_t² (v ning boshlang'ich qiymati dastlabki 60 kun dispersiyasi). Maqsad σ* = **10%** yillik.
  Kuchaytirish k_t = min(3, σ*/σ̂_t). Maqsad pozitsiya w*_t = s_t · k_t (kapitalga nisbatan nominal).
- **Deadband:** |w*_t − w_{t−1}| < 0.10 bo'lsa pozitsiya o'zgarmaydi; aks holda w_t = w*_t.
- **Ijro:** t kuni yopilishda signal va hajm aniqlanadi, w_t pozitsiya shu yopilish narxida olinadi; keyingi kun daromadi: pnl_{t+1} = w_t · r_{t+1} − xarajat_t.
- **Xarajat:** xarajat_t = |w_t − w_{t−1}| · c − |w_t| · f/252.
  - Oltin: c = $0.50/uns ÷ P_t (spred+sirpanish), f = **3%** yillik (CFD moliyalashtirish/swap, konservativ, ikkala tomon uchun).
  - FX: c = 1.5 baza punkti, f = 0. Brent: c = 5 baza punkti, f = 0.

## 5. O'lchovlar va testlar
- Sof (net) kunlik daromadlar bo'yicha: yillik Sharpe = o'rtacha/std·√252 (kapital nol foizli), t-statistika Newey–West (10 lag), maksimal drawdown, pozitsiya almashtirishlar soni, yillik aylanma.
- **Timing testi (tasodifiy vaqtga qarshi):** pozitsiya qatori w_t (xarajat bilan birga) tasodifiy δ ∈ [252, T−252] kunga aylana bo'ylab siljitiladi (5000 marta),
  har safar Sharpe hisoblanadi. p = siljitilgan Sharpe ≥ haqiqiy Sharpe bo'lgan ulush. Bu natija shunchaki oltin o'sishidan (beta) emas, vaqtlash mahoratidan kelganini tekshiradi.
- **Davrlar (oltin):** A = P&L boshlanishi → 2011-12-31; B = 2012-01-01 → 2018-12-31; C = 2019-01-01 → 2025-02-28.
- **Portfel (Stage 2):** 9 aktivning har biri alohida 10% vol maqsad bilan; portfel = o'sha kunda mavjud aktivlarning teng vazndagi sof daromadi. Timing testi har aktiv uchun mustaqil δ bilan.
- Benchmark (tavsif uchun): oltin buy&hold Sharpe va maksimal drawdown; strategiyaning oltinga beta va alfa (HAC t) regressiyasi.

## 6. O'tish mezonlari (hammasi bajarilishi shart)
**Stage 1 (oltin, har hujayra alohida):**
(a) sof Sharpe ≥ 0.30; (b) Newey–West t ≥ 2.0; (c) timing p ≤ 0.10; (d) sof Sharpe 3 davrdan kamida 2 tasida > 0 va uchinchisida ≥ −0.30;
(e) maksimal drawdown ≤ 25%; (f) xarajat 2 baravar (c ×2) va f = 5% bilan ham sof Sharpe > 0; (g) pozitsiya almashtirishlar ≥ 20.
**Stage 2 (shu hujayra, o'zgartirilmasdan, 9 aktiv):**
(h) portfel sof Sharpe ≥ 0.20 va t ≥ 1.65; (i) 9 aktivdan kamida 6 tasida sof Sharpe > 0; (j) portfel timing p ≤ 0.10.
- Hujayra **PASS** bo'ladi, agar (a)–(j) hammasi bajarilsa. Bir nechtasi o'tsa, afzallik tartibi: S2 > S1 > S3 > S4 (ansambl parametr xavfini kamaytiradi).
- Ko'p test tuzatmasi: 4 hujayra tanlovi mustaqil Stage 2 tasdig'i bilan himoyalanadi (nol gipotezada ikkala bosqichdan o'tish ehtimoli kichik).
- Barcha 4 hujayra natijalari o'tish/o'tmasligidan qat'i nazar to'liq e'lon qilinadi.

## 7. Natijaga qarab nima qilamiz
- **Biror hujayra PASS:** kunlik qoidalar (kirish/chiqish, vol-maqsad bo'yicha lot, risk chegaralari) EA uchun aniq yoziladi, MT5'da sinash uchun kod, keyin demo hisobda
  kamida 3 oy forward-test. Haqiqiy pulga o'tish faqat demo natijasi kutilganga mos kelganda.
- **Stage 1 o'tdi, Stage 2 o'tmadi:** natija oltinga xos (ehtimol 2005–2011 va 2019–2025 o'sishidan, hindsight xavfi); ishonch past, faqat kichik risk bilan demo va ochiq ogohlantirish.
- **Stage 1 o'tmadi:** kunlik trend oltin uchun rad etiladi. Qolgan variantlar: ko'p aktivli portfel (agar Stage 2 o'tgan bo'lsa), yoki xulosa: "oddiy qoidalar bilan ishonchli edge topilmadi".
- Hech qanday holatda sinalgan parametrlar natijaga qarab "yaxshilanmaydi" (qaytadan sinash faqat yangi oldindan yozilgan reja bilan).

**O'zgartirishlar jurnali:** (hozircha bo'sh)

## 8. Ma'lum xavflar va cheklovlar
- **Hindsight:** oltin 2005–2011 va 2019–2025 yillarda kuchli trendda bo'lganini bilamiz; mustaqil trend kuzatuvlari soni kam (21 yilda bir necha uzun trend). Shuning uchun Stage 2 va timing testi qo'yilgan.
- **Oltin ma'lumoti uchinchi tomondan** (MT server kunlik yopilishi); brokeringiz yopilishi biroz farq qilishi mumkin.
- **CFD/spot xususiyatlari:** moliyalashtirish (swap) 3% farazi, real broker swapi o'zgaruvchan; spread kengayishi, gaplar, hafta oxiri xavfi.
- **FX/neft faqat narx:** carry va roll daromadlari yo'q; Stage 2 signal haqiqiyligini tekshiradi, P&L ni emas.
- **Ijro:** kunlik yopilishda ijro faraz qilinadi; amalda yopilishdan bir necha daqiqa kechikish va sirpanish bo'ladi (xarajat modeli bunga qisman o'rin ajratadi).
- Trend strategiyalari uzoq yon bozorda (yillar) zarar qilishi va katta drawdown berishi mumkin; 25% drawdown chegarasi shu uchun.
