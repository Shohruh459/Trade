# Oltin oylik qoidalar: forward kuzatuv va amaliy foydalanish rejasi (pre-registered)

Holat: **yozilgan sanada kelajak ma'lumoti ko'rilmagan holda commit qilingan.** Qoidalar muzlatilgan; o'zgartirish taqiqlanadi. Har qanday o'zgartirish 8-bo'limdagi jurnalga sababi bilan yoziladi va yangi forward kuzatuv deb hisoblanadi.

## 1. Maqsad
`STRATEGY_PORTFOLIO.md` tadqiqotidan o'tgan va qiziq chiqqan narsalarni **yangi, ko'rilmagan oylarda** kuzatish: o'tgan ma'lumotda sinalgan qoida kelajakda ham mos kelayaptimi. Bu savdo robot emas, oyiga bir marta tekshiriladigan oddiy qoidalar.

## 2. Kuzatiladigan qoidalar (muzlatilgan)
1. **SMA10 filtri (xavfni kamaytirish):** oy oxirida narx > oxirgi 10 oy (joriy oy bilan) o'rtachasi bo'lsa — oltin ushlanadi (LONG), aks holda NAQD. O'tish xarajati 10 baza punkti.
2. **Oltin ulushi:** diversifikatsiya uchun 60/40 portfelning ~10% i (20% emas). Forward'da alohida baholanmaydi (ma'lumot kam), faqat eslatma.
3. **Mavsumiylik (gipoteza):** sentyabr–fevral oylarida o'rtacha oylik daromad mart–avgustdan yuqori.
4. **Momentum (kuzatuv):** 12 oylik momentum (ln(P_t/P_{t−12})) keyingi 12 oylik daromadni ijobiy bashorat qiladi.

## 3. Jarayon (har oy oxirida, 5 daqiqa)
1. Oltin (XAUUSD spot) **oy oxirgi kunining yopilish narxini** oling (broker/xarita).
2. `python tools/gold_monthly_check.py --add YYYY-MM NARX` (narxni `forward_test/gold_prices.csv` ga qo'shadi, hisobot va `forward_test/log.csv` ni yangilaydi; `forward_test/latest.md` ni yozadi).
3. SMA10 holatini ko'ring; faqat holat **o'zgarganda** harakat qiling (LONG ↔ NAQD), oraliq kunlarda emas.
4. Log fayli **qulflangan**: bir marta yozilgan snapshot qayta yozilmaydi; keyingi oy narxi kelganda shu qatorga realizatsiya qilingan daromad to'ldiriladi.

## 4. Boshlanish va ko'rilmagan oylar
- Forward kuzatuv **2026-09 oy oxiri** signalidan boshlanadi (uning daromadi 2026-10 da ma'lum bo'ladi). Boshlanish holati: narx $4,319, SMA10 $4,528 (−4.6%), **NAQD**; oxirgi o'zgarish 2026-06 da.
- 2026-07…09 oylari tadqiqotga (2026-06 da tugagan) kirmagan, lekin forward'dan oldin ma'lum: filtr −0.1% / 0.0% / 0.0%, ushlab turish −3.7% / +8.3% / −2.1% (avgustdagi +8.3% o'tkazib yuborilgan). **Bu 3 oy anekdot, xulosa emas**, forward hisobiga kirmaydi.
- Narx manbasi: tarixiy qism `datasets/gold-prices` (oylik o'rtacha, 2024-01 → 2026-09), yangi oylar foydalanuvchi kiritgan oy oxiri yopilishi (`source=user`). Ikki manba aralashishi SMA10 da kichik nomuvofiqlik beradi (hujjatlashtirilgan).

## 5. Baholash nuqtalari va mezonlar (oldindan)
- **SMA10 filtri:** har 12 oyda hisobot. **Baholanadi faqat** forward oynasida ushlab turish (buy&hold) kamida **15% cho'qqidan-quyiga drawdown** ko'rsatgan bo'lsa. Shunda filtr **mos** deb hisoblanadi, agar (i) uning maksimal drawdowni buy&hold ning 80% idan oshmasa va
  (ii) umumiy daromadi buy&hold dan 10 foiz punktdan ko'p past bo'lmasa. Aks holda "mos emas". Drawdown bo'lmasa — "ma'lumot yetarli emas", xulosa chiqarilmaydi.
- **Mavsumiylik:** xulosa **kamida 24 oydan** keyin (≥ 4 yarim yil: sentyabr–fevral ×2, mart–avgust ×2). Farq (mavsumiy − boshqa) > 0 va bir tomonlama p ≤ 0.10 (HAC t) bo'lsa "tasdiqlandi"; aks holda "tasdiqlanmadi". 24 oygacha faqat ma'lumot, xulosa yo'q.
- **Momentum:** kamida **36 ta** realizatsiya qilingan 12 oylik natija bo'lganda (ya'ni ≥ 48 oy) mom12 va keyingi 12 oylik daromad Spearman korrelyatsiyasi > 0 va bir tomonlama p ≤ 0.10. Undan oldin faqat jurnal.
- Natijadan qat'i nazar, hisobotlar to'liq e'lon qilinadi; qoidalar natijaga qarab o'zgartirilmaydi.

## 6. Amaliy foydalanish qoidalari
- **Birinchi bosqich (kamida 12 oy):** qog'ozda/demo kuzatuv, real pulsiz. Maqsad: signal tezligi, almashtirishlar va xatolarni kuzatish.
- Real pul bo'lsa: oltin portfelning ≤ 10%, SMA10 faqat **oltin ulushi (sleeve)** uchun; boshqa aktivlarga tegilmaydi. Naqdga o'tgan qism odatdagi xavfsiz vositada turadi.
- Almashtirish xarajati (spred/komissiya), soliq oqibatlari va likvidlik hisobga olinadi. Orqaga qaytish signalidan keyin yana "yolg'on" almashtirish (whipsaw) bo'lishi mumkin; tadqiqotda yiliga o'rtacha ~1.3 almashtirish bo'lgan, ammo ketma-ket yolg'on signallar ehtimoli bor.
- Qaror faqat oy oxirida; stop-loss yoki kunlik "yaxshilash" qo'shilmaydi.
- Bu moliyaviy maslahat emas; yo'qotishlar mumkin.

## 7. Cheklovlar
Backtest oylik **o'rtacha** narxlarda o'tkazilgan; live'da oy oxiri yopilishi ishlatiladi (natija biroz farq qilishi mumkin; kechiktirilgan variant bunga qisman o'xshash natija bergan). Mavsumiylik Holm tuzatmasidan o'tmagan edi (p = 0.018, 11 test oilasida); u faqat kuzatuv gipotezasi. Momentum bashorati ishora qoidasi bilan buy&hold dan farq qilmagan.

## 8. O'zgartirishlar jurnali
(hozircha bo'sh)
