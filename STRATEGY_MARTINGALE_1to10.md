# Martingale 1$ → 10$ (oltin): pre-registered sinov rejasi

Holat: **natijani ko'rishdan OLDIN yozilgan va commit qilingan.** Qoida foydalanuvchi tomonidan berilgan; yozilmagan joylarni (6-bo'lim) natijani ko'rmasdan muzlatdim. O'zgartirish faqat 8-bo'limdagi jurnalga.

## 1. Halol kutish (oldindan)
Martingale (zarar bilan lotni ikki barobar) foydali kutilgan qiymat yaratmaydi: u kichik foydani tez-tez, katta zararni kamdan-kam olishga aylantiradi. Xarajat (spred) bilan kutilgan natija **manfiy**. 5 kunda 1$ → 10$ (10x) ni adolatli (xarajatsiz, ustunliksiz) o'yinda olish ehtimoli ≤ ~10%; qolgan ~90% holatda balans tushadi. Sinov shuni empirik o'lchaydi; **muvaffaqiyat mezoni "kamida bir marta 10$ ga yetish" emas**, chunki bu tasodifan ham bo'ladi (4-bo'lim).

## 2. Qoida (foydalanuvchi matni bo'yicha)
- XAUUSD, M1 ma'lumot (M1 narx yo'li bo'yicha). Boshlang'ich balans 1.00$, maqsad 10.00$ (equity = balans + floating ≥ 10), sliv: equity ≤ 0.10$ yoki margin call.
- Birinchi pozitsiya oyna boshida ochiladi (eng kichik lot). Narx **oxirgi ochilgan pozitsiya kirish narxidan** step ga qarshi ketsa, yangi pozitsiya ochiladi, lot 2 baravar. Hamma pozitsiyalar bir yo'nalishda. Maksimal pog'ona: 9 pozitsiya (lot 1, 2, 4, …, 256 × boshlang'ich).
- Maqsadga yetsa barcha pozitsiyalar yopiladi (muvaffaqiyat); sliv bo'lsa to'xtaydi; 5 savdo kuni ichida ikkalasi ham bo'lmasa — oyna oxirida hamma pozitsiyalar yopiladi va yakuniy balans yoziladi.
- Boshqa chiqish (TP, stop) yo'q: faqat umumiy maqsad, sliv va oyna oxiri.

## 3. Ma'lumot va oynalar
XAUUSD M1 BID (ZombitX64, UTC), 2018-01-02 → 2025-02-28. **Oynalar:** ketma-ket, bir-birini kesmaydigan 5 savdo kunlik bloklar (ma'lumotdagi ketma-ket 5 ta sana), butun davr bo'yicha (~370 oyna) + alohida "oxirgi 30 oyna". Har oyna birinchi M1 bar ochilishida boshlanadi.
Yo'nalish: **Sell** (video bo'yicha, asosiy), shuningdek **Buy** alohida. Ikkala tomonning natijasi alohida e'lon qilinadi (tasodifiy tanlov emas).

## 4. Parametrlar (muzlatilgan)
- Boshlang'ich lot: **0.01 oz** (eng kichik tortiladigan hajm, cent/micro hisob; ochiq farazi: 1 oz kontrakt bilan 1$ hisobda hatto bitta pozitsiyani ochib bo'lmaydi, 6.1 ga qarang). Sezgirlik: 0.1 oz.
- **Step:** 0.65$ (5–8 pip oralig'ining o'rtasi; 1 pip = 0.10$ farazi). Sezgirlik: 0.50$ va 0.80$.
- Leverage 1:500; margin = lot(oz) × narx / 500; margin call (stop-out): margin level (equity / ishlatilgan margin) ≤ 50%. Yangi pozitsiya ochish uchun bo'sh margin yetarli bo'lishi kerak (aks holda ochilmaydi).
- Xarajat: spred $0.30/oz har pozitsiyaga ochilganda darhol floating ga kiritiladi (konservativ). Komissiya va swap yo'q (kun ichi-5 kun). Balans manfiy bo'lmaydi (0 dan quyi tushmaydi).
- **Shamlar ichidagi tartib (konservativ):** ochilish → qarshi ekstremum (Sell: high, Buy: low) → qulay ekstremum → yopilish. Qarshi nuqtada avval step/pog'ona ochiladi, keyin sliv tekshiriladi, keyin maqsad; qulay nuqtada faqat maqsad.
- Pog'onalar M1 ochilishidagi gap bo'lsa gap narxida, aks holda step darajasida to'ldiriladi.

## 5. O'lchovlar (foydalanuvchi so'ragan)
Jami oynalar soni; 10$ ga yetgan foizi; sliv foizi; ikkalasi ham bo'lmagan (5 kun ichida) foizi; o'rtacha kun (10$ ga yetganda); o'rtacha kun (sliv bo'lganda; kun = oyna boshidan o'tgan soat/24); 5 kunda ikkalasi ham bo'lmaganda yakuniy balans (o'rtacha, min, max); eng yaxshi va eng yomon oyna; **barcha oynalar bo'yicha o'rtacha yakuniy balans** (boshlang'ich 1.00$ ga nisbatan: kutilgan qiymat); pog'onalar soni taqsimoti.
**Qaror ko'rsatkichi:** o'rtacha yakuniy balans 1.00$ dan yuqorimi va 10$ ga yetish foizi adolatli o'yin chegarasi (~10%) dan ishonchli yuqorimi (Wilson 95% oralig'i bilan).

## 6. Aniqlashtirishlar va cheklovlar (muzlatilgan)
1. **1$ hisob haqiqatan mumkinmi:** standart kontraktda (1 lot = 100 oz) eng kichik lot 0.01 = 1 oz, margin ~ narx/500 ≈ 8$ (hozirgi narxda), ya'ni 1$ hisobda hech narsa ochilmaydi. Shu sababli 0.01 **oz** (cent/micro hisob yoki ba'zi brokerlarning 0.0001 lot) farazi ishlatiladi. Haqiqiy brokerda bu faraz bajarilmasligi mumkin.
2. Spred doimiy (real spred yangiliklar paytida kengayadi, sirpanish yo'q): natija optimistik.
3. Tarixiy oynalar ~370 ta; ular mustaqil emas (oltin trendi, mavsumiylik), lekin kesishmaydi.
4. Bu qoida pul ishlashga emas, "yutuq ehtimoli/ zarar kattaligi" nisbatini o'lchashga mo'ljallangan; real pulga tavsiya emas.

## 7. Natijaga qarab nima qilamiz
Natija e'lon qilinadi. Agar 10$ ga yetish foizi ~10% ga yaqin va o'rtacha yakuniy balans 1$ dan past bo'lsa — qoida ijobiy kutilgan qiymatga ega emas (martingale xususiyati tasdiqlanadi). Parametrlarni "yaxshilash" yo'q.

## 8. O'zgartirishlar jurnali
(hozircha bo'sh)
