# Berkshire Hathaway 13F portfelini ko'chirish: tarixiy sinov (pre-registered reja)

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoidalar, davrlar, mezonlar test paytida o'zgartirilmaydi. O'zgartirish faqat 8-bo'limdagi jurnalga.

## 1. Savol
"Berkshire Hathaway ning 13F hisobotidagi eng yirik pozitsiyalarini ko'chirish (kechikish bilan) S&P 500 dan yaxshi natija beradimi?" (videodagi `trader-skill` g'oyasi). Tadqiqot **oylik/choraklik, aksiyalar**, kun ichi savdo emas.

## 2. Ma'lumot (muzlatilgan)
- **Holdings:** `eagle0504/sec-13f-holdings` (HF, CC0): 9 fondning 13F-HR (infotable.xml dan), shu jumladan Berkshire Hathaway (CIK 1067983), 53 chorak: 2013-06-30 → 2026-06-30; har qatorda `period` (chorak oxiri), `filed` (SEC ga topshirilgan sana), `cusip`, `shares`, `value_usd`.
- **Narxlar:** alohida narx manbai yo'q (SEC/Yahoo/Stooq mavjud emas), shuning uchun **13F dan implied narx**: price = value_usd / shares (faqat oddiy aksiya qatorlari: `share_type = SH`, `put_call` bo'sh, shares > 0). Har (cusip, chorak) uchun 9 fond bo'yicha **mediana** (ko'p fond bir xil aksiyani ushlaydi, shuning uchun qamrov keng). Narx faqat **chorak oxirida** mavjud.
- **Benchmark:** S&P 500 (Shiller, `datasets/s-and-p-500`, oylik o'rtacha) — oy o'rtasiga qo'yilgan qiymatlar orasida chiziqli interpolyatsiya; **faqat narx** (dividendsiz), nusxa portfel ham faqat narx bo'ladi (nisbat to'g'ri). Dividendlar ikki tomonga ham qo'shilmaydi (Berkshire portfeli dividend to'laydigan kompaniyalar bo'lgani uchun bu nusxa foydasiga biroz kamsitadi).
- **Davr:** portfel qarori 2013-Q2 dan; natija oynalari 2013 oxiridan 2026-06 gacha.

## 3. Strategiyalar (muzlatilgan)
- **C5:** har chorak oxiri bo'yicha Berkshire ning eng katta 5 ta (qiymat bo'yicha) oddiy aksiya pozitsiyasi, vaznlari qayta normallashtirilgan (repo misolidagidek). **C10:** eng katta 10. **CALL:** barcha oddiy aksiya pozitsiyalari, 13F vaznlari bilan.
- Har quarter chorak oxiridagi portfel ko'chiriladi. **Vaqt (kechikish) stsenariylari:**
  - **A (optimistik, 45 kunlik look-ahead):** q portfeli [q oxiri → q+1 oxiri] da ushlanadi. Bu real emas (hisobot q+~45 kunda chiqadi), yuqori chegara.
  - **B (taxminiy real):** q portfeli hisobot topshirilgan sana f_q dan keyingi f_{q+1} gacha ushlanadi. f dagi narx chorak oxiri narxlari orasidagi geometrik interpolyatsiya bilan: P(f)=P(q)·(P(q+1)/P(q))^(kun/chorak kunlari). Taxminiy (silliqlash).
  - **C (konservativ):** q portfeli [q+1 oxiri → q+2 oxiri] da ushlanadi (ma'lumot to'liq ma'lum, yana bir chorak kutiladi).
- Narx topilmagan aksiyalar (masalan, keyingi choraklarda hech bir fond ushlamagan) chiqarib tashlanadi, vaznlar qayta normallashtiriladi; qamrov (vazn bo'yicha topilgan ulush) har stsenariy uchun e'lon qilinadi.
- Xarajat: har qayta balanslashda aylanmaning 10 baza punkti (liquid large-cap uchun); stress 25 b.p.

## 4. O'lchovlar
Davr yillar bo'yicha, yillik daromad (CAGR), vol, Sharpe (rf = 0), maksimal drawdown, S&P ga nisbatan yillik ortiqcha daromad, oyna darajasidagi ortiqcha daromadning t-statistikasi (oddiy; N ~ 50, avtokorrelyatsiya kam), S&P dan yaxshi oynalar ulushi. Berkshire ning o'zi (BRK.B) narxi mavjud emas: shuning uchun "ko'chirish BRK.B dan yaxshimi" savoli ochiq qoladi (7-bo'lim).

## 5. Qaror mezonlari (hammasi bajarilishi shart; asosiy portfel C5 va C10 ikkalasi uchun alohida, stsenariy B va C)
- (a) B stsenariyda S&P ga nisbatan yillik ortiqcha daromad ≥ +1.0% va oyna t-statistikasi ≥ 1.65;
- (b) C stsenariyda ortiqcha daromad > 0;
- (c) B stsenariyda Sharpe ≥ S&P Sharpe;
- (d) B stsenariyda maksimal drawdown S&P drawdowndan kam emas yomon (≤ 1.1 × S&P drawdown);
- (e) xarajat stress (25 b.p.) bilan (a) ning ortiqcha daromadi > 0.
Hammasi bajarilsa — "ko'chirishda S&P dan yaxshi natija belgisi (dastlabki)"; aks holda "ustunlik topilmadi".

## 6. Natijaga qarab
Natija e'lon qilinadi; parametrlar (top-N, kechikish) natijaga qarab o'zgartirilmaydi.

## 7. Cheklovlar (oldindan)
Narx implied (13F qiymat/aksiya soni), chorak oxiri; B stsenariy interpolyatsiyali; S&P oylik o'rtacha narx; dividendlar yo'q; 13F faqat AQSh long aksiyalar (qisqa, naqd, chet el yo'q); faqat bitta investor (Berkshire) — omon qolish xatosi (Buffett mashhur bo'lgani uchun tanlangan) va 2013–2026 davri (kam mustaqil davr). Berkshire ning omon qolish bahosi (hindsight): Buffett g'oliblardan biri sifatida tanlangan; shuning uchun natija ijobiy bo'lsa ham umumiy "13F ko'chirish ishlaydi" degani emas.

## 8. O'zgartirishlar jurnali
- 2026-10-17 (birinchi ishga tushirishdan keyin, ikkala xato kodda edi, qoida/mezon o'zgarmadi): (1) S&P benchmark vaqt birligi xatosi (benchmark daromadi 0 chiqdi) tuzatildi; (2) **aksiya split tuzatmasi yo'q edi** (AAPL 7:1 va 4:1 splitlarida narx −75–85% ko'rinardi). Tuzatma qoida: fondlar bo'yicha aksiya soni nisbatining medianasi ≥ 1.8 (yoki ≤ 1/1.8) va xom narx nisbati < 0.7 (yoki > 1.4) bo'lsa, narx nisbati shu nisbatga ko'paytiriladi (natija 0.5…2.0 oralig'ida bo'lsa). Birinchi (split tuzatmasiz) natija hisobotda alohida ko'rsatilgan (C5 CAGR 4.5%, ortiqcha −7.6%); tuzatilgan natija: C5 9.5%, ortiqcha −2.6%. Mezonlar ikkala variantda ham bajarilmadi. Spin-off/birlashma kabi boshqa korporativ harakatlar tuzatilmagan (cheklov).
