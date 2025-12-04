import asyncio
import json
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================== НАСТРОЙКИ ==================

BOT_TOKEN = "8528765987:AAEZywnRgOwPPRm2QpvlctalL_Pg3Pha5RE"  # 👉 сюда вставь токен
ADMIN_ID = 2143553458                    # твой Telegram ID (админ)

DATA_FILE = "results.json"   # сюда будут сохраняться результаты
POINTS_CORRECT = 10          # за правильный ответ
POINTS_WRONG = 0             # за неправильный (0 – без штрафа; хочешь -10, поставь -10)


# ================== ПРЕДМЕТЫ / ТЕМЫ / ТЕСТЫ ==================
# SUBJECTS — я оставляю без изменений (как ты прислала)

SUBJECTS = {
    "konstruk": {
        "title": "Ayollar kiyimini konstruksiyalash va modellashtirish",
        "topics": {
            "t1": {
                "title": "Dasturga kirish",
                "questions": [
                    {
                        "text": "Ayollar kiyimlari assortimentiga nimalar kiradi?",
                        "options": [
                            "Faqat yubkalar va ko‘ylaklar",
                            "Turli fason va vazifali kiyim turlari",
                            "Faqat maxsus ish kiyimlari",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Kompozitsiya tushunchasi nimani bildiradi?",
                        "options": [
                            "Faqat rang tanlash jarayonini",
                            "Kiyim detallarining uyg‘un joylashuvi va nisbatlarini",
                            "Faqat bichish chiziqlarini",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Zamonaviy kiyim assortimentini tavsiflashda eng muhimi nima?",
                        "options": [
                            "Faslga, funksiyaga va iste’molchiga mosligini aniqlash",
                            "Faqat narxlarini taqqoslash",
                            "Faqat ishlab chiqaruvchi firmalarni sanab o‘tish",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Kiyim detali deganda nimani tushunamiz?",
                        "options": [
                            "Faqat butun tayyor mahsulotni",
                            "Kiyimning alohida qismlari: yeng, etak, yoqa va hokazo",
                            "Faqat gazlama turini",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Eskiz tayyorlash qoidalari nimalarga yordam beradi?",
                        "options": [
                            "Model g‘oyasini aniq va tushunarli ifodalashga",
                            "Faqat gazlama sarfini kamaytirishga",
                            "Faqat dazmollash texnologiyasini tanlashga",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t2": {
                "title": "Kiyim tashqi shakli",
                "questions": [
                    {
                        "text": "Shakl predmetning qaysi jihatini ifodalaydi?",
                        "options": [
                            "Tarkibi va tolalari",
                            "Tashqi ko‘rinishi va konturlari",
                            "Faqat rangi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Siluet tushunchasi nimani bildiradi?",
                        "options": [
                            "Kiyimning umumiy tashqi kontur ko‘rinishini",
                            "Faqat yoqa ko‘rinishini",
                            "Faqat yeng uzunligini",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Kiyim shaklining asosiy qismlariga nimalar kiradi?",
                        "options": [
                            "Gazlama tolalari va bo‘yalishi",
                            "Etak, yeng, yoqa, bel qismi va hokazo",
                            "Faqat tugma va fermuarlar",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Qaysi siluet gavdaga yopishiq ko‘rinishni beradi?",
                        "options": [
                            "Yopishiq (pritalenniy) siluet",
                            "To‘g‘ri siluet",
                            "“Trape­siya” silueti",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Kiyim tashqi shaklini o‘zgartirishning eng sodda usuli?",
                        "options": [
                            "Fasolni o‘zgartirish",
                            "Gazlama turini o‘zgartirishsiz bo‘yash",
                            "Faqat tugmalarni almashtirish",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t3": {
                "title": "Ayollar kiyimlariga qo‘yiladigan talablar",
                "questions": [
                    {
                        "text": "Funktsional talablar nimani anglatadi?",
                        "options": [
                            "Kiyimning ma’lum vazifani bajarishga qulayligi",
                            "Faqat kiyimning arzon bo‘lishi",
                            "Faqat modaga mosligi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Estetik talablar qaysi omilga tegishli?",
                        "options": [
                            "Rang, shakl, bezak va umumiy go‘zallik",
                            "Faqat gazlama zichligi",
                            "Faqat tikuv mashinasi turiga",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Ergonomik talablar nimalarni hisobga oladi?",
                        "options": [
                            "Gavda tuzilishi, harakat erkinligi va o‘lchamlar mosligini",
                            "Faqat ishlab chiqarish narxini",
                            "Faqat dazmollash qulayligini",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Qaysi javobda sifat talablari to‘g‘ri keltirilgan?",
                        "options": [
                            "Chidamlilik, gigiyena, tikuvlar mustahkamligi",
                            "Faqat yorqin ranglar",
                            "Faqat ko‘p bezak elementlari",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Kiyimning ekspluatatsion talablari nimaga taalluqli?",
                        "options": [
                            "Yuvish, dazmollash, kiyganda shaklini saqlash xususiyatlariga",
                            "Faqat tikish tezligiga",
                            "Faqat model nomiga",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t4": {
                "title": "Gavdadan o‘lchov olish",
                "questions": [
                    {
                        "text": "Gavdadan о‘lchov olishdan oldin birinchi navbatda nima qilinadi?",
                        "options": [
                            "Gazlamani dazmollash",
                            "O‘lchanayotgan shaxsni to‘g‘ri holatda turishini ta’minlash",
                            "Yubka uzunligini taxmin qilish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Bel о‘lchovi qaysi chiziq bo‘ylab olinadi?",
                        "options": [
                            "Eng keng son qismidan",
                            "Ko‘krak chizig‘idan",
                            "Gavdaning tabiiy bel chizig‘idan",
                        ],
                        "correct": 2,
                    },
                    {
                        "text": "Bo‘y о‘lchovi qayerdan qayergacha olinadi?",
                        "options": [
                            "Yelkadan tizzagacha",
                            "Bosh tepasi dan oyoq tagigacha",
                            "Bo‘yindan belgacha",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Gavda tiplarini aniqlash nima uchun kerak?",
                        "options": [
                            "Faqat modellashtirish uchun",
                            "To‘g‘ri konstruksiya va qo‘shimchalarni tanlash uchun",
                            "Faqat gazlama sarfini aniqlash uchun",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "O‘lchov olishda lenta bilan ishlashda nimalarga e’tibor beriladi?",
                        "options": [
                            "Lenta juda tortib qo‘yiladi",
                            "Lenta gavdaga yotqizilgan, burilmagan bo‘lishi kerak",
                            "Lenta faqat kiyim ustidan o‘lchanadi",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t5": {
                "title": "Ayollar kiyimlarini konstruksiyalash metodlari",
                "questions": [
                    {
                        "text": "Muljay metodi asosida model yaratishda asosiy bosqich qaysi?",
                        "options": [
                            "Avval tayyor gazlama sotib olish",
                            "Asosiy konstruksiyani olib, unga o‘zgarishlar kiritish",
                            "Faqat bezak elementlarini chizish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Detallar chizish usullari qaysi maqsadga xizmat qiladi?",
                        "options": [
                            "Gazlamani bo‘yash",
                            "Kiyimning aniq shaklini chizmada ifodalash",
                            "Faqat tikuv mashinasini tanlash",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Sanoat konstruksiyalash usullarining asosiy xususiyati?",
                        "options": [
                            "Modelni faqat bitta o‘lchamda yaratish",
                            "Seriyali ishlab chiqarish uchun moslashganligi",
                            "Faqat qo‘lda o‘lchashga asoslanishi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Qaysi metod modelni eskizdan tayyor konstruksiyagacha olib boradi?",
                        "options": [
                            "Muljay metodi",
                            "Faqat tajriba yo‘li bilan taxmin qilish",
                            "Faqat tayyor andazadan nusxa olish",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Konstruksiyalash metodini tanlashda nimaga e’tibor beriladi?",
                        "options": [
                            "Faqat talabaning xohishiga",
                            "Mahsulot turi, ishlab chiqarish sharoiti va aniqlik talabiga",
                            "Faqat gazlama rangiga",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t6": {
                "title": "Belda turadigan kiyimlarni loyihalash xususiyatlari",
                "questions": [
                    {
                        "text": "Belda turadigan kiyimlarga qaysi tur kiradi?",
                        "options": [
                            "Yubka va shim",
                            "Faqat palto",
                            "Faqat ko‘ylak",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Yubka fasonini tanlashda asosiy omil?",
                        "options": [
                            "Gavda tipi va siluetga mosligi",
                            "Faqat modaning yangi ranglari",
                            "Faqat gazlama qalinligi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Bel bo‘ylab qo‘shimcha berishning maqsadi nima?",
                        "options": [
                            "Belni imkon qadar tor qilish",
                            "Harakat erkinligi va qulaylikni ta’minlash",
                            "Faqat gazlama sarfini oshirish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yubka turlaridan qaysi biri eng sodda hisoblanadi?",
                        "options": [
                            "To‘g‘ri yubka",
                            "Godet yubka",
                            "Ko‘p taxlamali yubka",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Bel chizig‘ida joylashgan vitachkalar nima uchun kerak?",
                        "options": [
                            "Kiyimni gavdaga moslashtirish uchun",
                            "Faqat bezak sifatida",
                            "Faqat bichishda xatoni yashirish uchun",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t7": {
                "title": "To‘g‘ri ikki chokli yubka asosini hisoblash va chizish",
                "questions": [
                    {
                        "text": "Ikki chokli yubkaning asosiy choklari qayerda joylashadi?",
                        "options": [
                            "Old va orqa markazida",
                            "Yon tomonlarda",
                            "Etak chizig‘ida",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yubka bazasini hisoblashda birinchi navbatda qaysi o‘lchov olinadi?",
                        "options": [
                            "Ko‘krak girih о‘lchovi",
                            "Bel va son girih о‘lchовlari",
                            "Yelka uzunligi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yubka uzunligi qayerdan о‘lчанади?",
                        "options": [
                            "Yelkadan pastga",
                            "Bel chizig‘idan pastga etakgacha",
                            "Tizzadan yuqoriga",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Old va orqa bo‘laklar nisbatini taqsimlashda maqsad nima?",
                        "options": [
                            "Faqat old bo‘lakni kattaroq qilish",
                            "Gavda shakliga mos tushishini ta’minlash",
                            "Faqat orqa chokni uzun qilish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yubka asos chizmasida bel chizig‘i qanday chiziladi?",
                        "options": [
                            "To‘g‘ri gorizontal chiziq sifatida",
                            "Yarim doira ko‘rinишида",
                            "Faqat yon chiziqlarga tik",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t8": {
                "title": "Turli bichimdagi yubkalarni konstruksiyalash va modellashtirish",
                "questions": [
                    {
                        "text": "Godet yubkaning asosiy xususiyati nima?",
                        "options": [
                            "Etagi kengaytirilgan klinlar yordamida hosil bo‘lishi",
                            "Bel chizig‘ining past bo‘lishi",
                            "Faqat juda qisqa bo‘lishi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "To‘rt, olti, sakkiz bo‘lakli yubkalarda bo‘laklar qanday joylashadi?",
                        "options": [
                            "Faqat old bo‘lakda",
                            "Bel aylanasi bo‘ylab teng taqsimlangan holda",
                            "Faqat orqa qismida",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Taxlamali yubkalarda gazlama ko‘proq sarf bo‘lishining sababi?",
                        "options": [
                            "Taxlamalar uchun qo‘shimча kenglik kerak bo‘lishi",
                            "Faqat gazlama og‘irligi",
                            "Faqat rang uyg‘unligi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Kokteyl yubkalari ko‘proq qaysi vaziyat uchun mo‘ljallangan?",
                        "options": [
                            "Har kungi ish kiyimi sifatida",
                            "Bayram va tadbirlar uchun",
                            "Faqat sport bilan shug‘ullanish uchun",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Modellashtirishda asosiy konstruksiyadan foydalanishning afzalligi?",
                        "options": [
                            "Har safar yangidan konstruksiya chizish shart emas",
                            "Faqat tikuv tezlashadi",
                            "Faqat о‘lчов olishга hojat qolmaydi",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t9": {
                "title": "Ayollar shim asosini konstruksiyasini qurish",
                "questions": [
                    {
                        "text": "Shim konstruksiyasida eng muhim o‘lchovlardan biri?",
                        "options": [
                            "Yelka kengligi",
                            "Son girih va oyoq uzunligi",
                            "Bilak girihi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Shimning o‘tirish chizig‘i nimani belgilaydi?",
                        "options": [
                            "Bel bantining kengligini",
                            "Son qismining balandligini va qulay o‘tirishni",
                            "Etak kengligini",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Cho‘ntak joylashuvi noto‘g‘ri bo‘lsa, nimaga olib keladi?",
                        "options": [
                            "Faqat dazmollash qiyinlashadi",
                            "Shimning tashqi ko‘rinishi va qulayligi buziladi",
                            "Gazlama zichligi ortadi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Bel chizig‘idagi vitachkalar shimda nima uchun kerak?",
                        "options": [
                            "Gavdaning bel qismiga moslash uchun",
                            "Faqat bezak sifatida",
                            "Faqat fermuarni yashirish uchun",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Shim o‘lchamlarini noto‘g‘ri olish oqibati?",
                        "options": [
                            "Faqat gazlama iqtisodi oshadi",
                            "Kiyim tor yoki bo‘sh bo‘lib, harakatni cheklaydi",
                            "Faqat rang o‘zgaradi",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t10": {
                "title": "Ayollar ko‘ylagini asos chizmasini hisoblash va chizish",
                "questions": [
                    {
                        "text": "Ko‘ylak bazasini qurishda birinchi navbatда qaysi chiziq chiziladi?",
                        "options": [
                            "Etak chizig‘i",
                            "Bo‘y va ko‘krak balandligiga asoslangan asosiy to‘rtburchak",
                            "Yeng chizig‘i",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Vitshachkalarni joylashtirishning asosiy maqsadi?",
                        "options": [
                            "Kiyimni ko‘proq bezash",
                            "Ko‘krak va bel sohasida gavдaga moslash",
                            "Gazlama sarfini oshirish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Ko‘ylak kengligini hisoblashда nimaga e’tibor beriladi?",
                        "options": [
                            "Harakat erkinligi uchun etarli qo‘shimchalar berishga",
                            "Faqat yelка kengligiga",
                            "Faqat bo‘y uzunligiga",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Asos chizmada yelka chizig‘i qaysi о‘lчовга tayanadi?",
                        "options": [
                            "Ko‘krak girihiga",
                            "Yelka uzunligi va qiyaligi о‘lчовlariga",
                            "Bel girihiga",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Ko‘ylak bazasini to‘g‘ri qurиш natijasida nima ta’minланади?",
                        "options": [
                            "Faqat yoqaning chiroyli ko‘rinishi",
                            "Butun modelning to‘g‘ri o‘tirishi va modellashtirish qulayligi",
                            "Faqat etak uzunligi",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t11": {
                "title": "Ayollar ko‘ylagi bir chokli yeng asosini chizish",
                "questions": [
                    {
                        "text": "Yeng balandligini aniqlashда qaysi о‘lчовlardan foydalaniladi?",
                        "options": [
                            "Bel girihi va bo‘y uzunligi",
                            "Yelka uchidan tirsakkacha bo‘lган masofa",
                            "Ko‘krak girihi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Bir chokli yengнинг asosий choki qayerда joylashadi?",
                        "options": [
                            "O‘rtada, pastdan yuqoriga qarab",
                            "Yon tomonda, pastdan yelka tomon",
                            "Bo‘yin chizig‘i bo‘ylab",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yeng kengлигини oshirish учун nima qilinadi?",
                        "options": [
                            "Faqat uzunligi qisqartiriladi",
                            "Yon chiziqlar bo‘ylab qo‘shimcha kenglik qo‘shiladi",
                            "Vitachkalar olib tashланади",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Eskiz asosida yeng chizmasини qurишda birinchi qadam?",
                        "options": [
                            "Yeng pastki qismidan boshlash",
                            "Asosiy yeng to‘rtburchagini chizish",
                            "Faqat manjetni chizish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Qo‘shimчalar noto‘g‘ri tanlansa, nimaga olib keladi?",
                        "options": [
                            "Yeng juda tor yoki keng bo‘lib qoladi",
                            "Faqat rang o‘zgaradi",
                            "Faqat gazlama zichligi kamayadi",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t12": {
                "title": "Ayollar o‘taqzma yengli ko‘ylagi asosini modellashtirish",
                "questions": [
                    {
                        "text": "O‘taqzma yengli ko‘ylakda vitachkalarni ko‘chirishning maqsadi?",
                        "options": [
                            "Faqat yeng uzunлигини о‘zgартириш",
                            "Shaklни о‘zgартириб, modelga mos ko‘rinish berish",
                            "Gazlama sarfини kamaytirish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Konsruktsion chizish nimani anglatadi?",
                        "options": [
                            "Faqat bezak chiziqlarини chizish",
                            "Modelning barcha konstruktiv chiziqlarini aniq belgilash",
                            "Faqат yoqa shaklini tanlash",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "O‘taqzma yengli ko‘ylaklarda yeng qaysi qismga biriktiriladi?",
                        "options": [
                            "Faqat bel chizig‘iga",
                            "Yelка ва ko‘krak sohasiga birgalikda",
                            "Faqat etakka",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Modellashtirishда yangi chiziq qayerдан olinadi?",
                        "options": [
                            "Eskizdagi istalgan yo‘nalish bo‘yicha asos chizmadan kesib-ko‘chirib",
                            "Faqat tayyor andazadan nusxa olib",
                            "Faqat taxminiy chizib",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "O‘taqzma yengli modelning afzalligi?",
                        "options": [
                            "Harakat erkinligi va zamonaviy ko‘rinish",
                            "Faqat gazlama sarfini kamaytirish",
                            "Faqat tikish tezligi",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t13": {
                "title": "Ayollar turli bichimdagi yenglarini modellashtirish",
                "questions": [
                    {
                        "text": "Kimono yengining o‘ziga xosligi nimada?",
                        "options": [
                            "Alohida tikiladigan yeng bo‘lishi",
                            "Yelка ва yengning bir butun konstruksiya bo‘lishi",
                            "Faqat juda tor bo‘lishi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Reglan yengda chok qayerдан o‘tadi?",
                        "options": [
                            "Bo‘yin atrofidan qo‘ltiqqacha",
                            "Faqat yon tomondan",
                            "Faqat pastki qismдан",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Ikki chokли yengда qo‘shimcha chok nima beradi?",
                        "options": [
                            "Shaklни yaxшiroq gavдaga moslash имконини",
                            "Faqat tikishni qiyinlashtiradi",
                            "Faqat manjetni qisqartiradi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Manjetli yenglarning asosий vazifasi?",
                        "options": [
                            "Faqat bezak bo‘lishi",
                            "Yeng pastki qismini shakllantirish ва mustahkamlash",
                            "Faqat yengни cho‘zish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yenglarni modellashtirishда nimalar о‘zgarиши мумкин?",
                        "options": [
                            "Faqat rang",
                            "Shakl, kenglik, uzunлик ва chok chiziqlari",
                            "Faqat gazlama tarkibi",
                        ],
                        "correct": 1,
                    },
                ],
            },
        },
    },

    "detallar": {
        "title": "Kiyim mayda detallariga ishlov berish (o‘quv amaliyoti)",
        "topics": {
            "t1": {
                "title": "O‘quv ustaxonasida mehnatni muhofaza qilish va xavfsizlik",
                "questions": [
                    {
                        "text": "Tikuv ustaxonasida xavfsizlikning birinchi talabi?",
                        "options": [
                            "Mashinalarni doimiy maksimal tezlikda ishlatish",
                            "Asbob-uskunadan to‘g‘ri foydalanish va ko‘rsatmalarga rioya qilish",
                            "Elektr simlarini ochiq qoldirish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Qo‘l choklaridan qaysi biri eng sodda hisoblanadi?",
                        "options": [
                            "Sidirg‘a chok",
                            "Yashirin chok",
                            "Ilmoq chok",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Puxtalash choki qaysi maqsadda ishlatiladi?",
                        "options": [
                            "Faqat bezak sifatida",
                            "Choklarning mustahkamligini oshirish uchun",
                            "Gazlamani vaqtincha tutib turish uchun",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Ish boshlashdan oldin nima qilish kerak?",
                        "options": [
                            "Asboblarni tartibga keltirish va ish joyini tayyorlash",
                            "Faqat gazlamani kesib qo‘yish",
                            "Faqat dazmolni yoqish",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Xavfsizlik qoidalariga rioya qilinmasa, nimaga olib keladi?",
                        "options": [
                            "Faqat ish sekinlashadi",
                            "Jarohatlanish va uskunaning buzilish xavfi ortadi",
                            "Gazlama rangi o‘zgaradi",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t2": {
                "title": "Universal mashinalar va ularda chok tikish",
                "questions": [
                    {
                        "text": "Universal tikuv mashinasi qanday chokni bajarishi mumkin?",
                        "options": [
                            "Faqat to‘g‘ri chokni",
                            "To‘g‘ri, zigzag va ayrim dekorativ choklarni",
                            "Faqat qo‘l choki",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "To‘g‘ри chok qaysi holatda ko‘proq qo‘llaniladi?",
                        "options": [
                            "Asosiy birlashtiruvchi chok sifatida",
                            "Faqat bezak sifatida",
                            "Faqat rezina tikishda",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Zigzag chokining afzalligi nimada?",
                        "options": [
                            "Kiyimni ixcham qilish",
                            "Kesilgan qirralarni so‘kilishdan saqlash",
                            "Faqat chiroyli ko‘rinish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Mashina chokining sifati qaysiga bog‘liq?",
                        "options": [
                            "Ip tarangligi, igna va gazlama mosligiga",
                            "Faqat mashina rangi",
                            "Faqat gazlama narxi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Birlashtiruvchi chokning vazifasi?",
                        "options": [
                            "Detal chetini bezash",
                            "Ikki yoki bir nechta detallarni mustahkam ulash",
                            "Faqat vaqtinchalik tutib turish",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t3": {
                "title": "Maxsus tikuv mashinalari turlari",
                "questions": [
                    {
                        "text": "Tugma qadash mashinasi nima uchun mo‘ljallangan?",
                        "options": [
                            "Faqat chokni tekislash",
                            "Gazlama qirrasini kesish",
                            "Tugmalarni avtomatik qadash",
                        ],
                        "correct": 2,
                    },
                    {
                        "text": "Overlok mashinasining asosiy vazifasi?",
                        "options": [
                            "Gazlamani cho‘zish",
                            "Qirralarni qirqib, bir vaqtning o‘zida chok bilan mustahkamlash",
                            "Faqat bezak choklarini bajarish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "N.I.I ishlov berishda qaysi mashina ko‘p qo‘llaniladi?",
                        "options": [
                            "Maxsus puxtalash mashinalari",
                            "Faqat qo‘l ignasi",
                            "Faqat to‘g‘ri chok mashinasi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Maxsus mashinalarning afzalligi nimada?",
                        "options": [
                            "Ishni tez va sifatli bajarish imkonini berishi",
                            "Faqat kamroq elektr sarfi",
                            "Faqat rang-barang bo‘lishi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Namunalarni bajarganda nimalarga e’tibor beriladi?",
                        "options": [
                            "Mashina sozligi, ip tanlovi va texnologik ketma-ketlikka",
                            "Faqat gazlama narxiga",
                            "Faqat ish vaqti uzunligiga",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t4": {
                "title": "Kiymlardagi taqilma turlarini tikish (old)",
                "questions": [
                    {
                        "text": "Taqilma (planka) nima uchun kerak?",
                        "options": [
                            "Faqat bezak sifatida",
                            "Tugma, fermuar joylashadigan va old bo‘lakni mustahkamlovchi detal sifatida",
                            "Faqat gazlama qoldiqlaridan foydalanish uchun",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yashirin taqilmaning xususiyati?",
                        "options": [
                            "Tugmalar ochiq ko‘rinadi",
                            "Tugma va teshiklar tashqaridan ko‘rinmaydi",
                            "Faqat fermuar bilan tikiladi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Ikki tomonlama taqilma qayerda ko‘p ishlatiladi?",
                        "options": [
                            "Faqat ichki kiyimlarda",
                            "Ko‘ylak, kurtka, palto kabi ustki kiyimlarda",
                            "Faqat sport kiyimlarida",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Taqilma qismlarini tayyorlashда birinchi bosqich?",
                        "options": [
                            "Tugmalarni qadash",
                            "Gazlamani andaza bo‘yicha kesish va dazmollash",
                            "Fermuarni tikish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Old bo‘lakka taqilma tikishda eng muhim omil?",
                        "options": [
                            "Markaziy chiziqlarni to‘g‘ri mos tushirish",
                            "Faqat ip rangini tanlash",
                            "Faqat bezak qo‘shish",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t5": {
                "title": "Kiymlardagi qoplama va chokda joylashgan cho‘ntaklar",
                "questions": [
                    {
                        "text": "Qoplama cho‘ntakning asosiy farqi nimada?",
                        "options": [
                            "Faqat old bo‘lakда bo‘lishi",
                            "Cho‘ntak detali alohida tikilib, ustiga qoplanishi",
                            "Faqat ichki tomonda bo‘lishi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Cho‘ntak qoplamasini tayyorlashда nimalar hisobga olinadi?",
                        "options": [
                            "Faqat gazlama rangi",
                            "Gazlama yo‘nalishi, qirra va burchaklarning aniqligi",
                            "Faqat tugma soni",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Presslash jarayoni nimaga xizmat qiladi?",
                        "options": [
                            "Gazlamani namlash",
                            "Choklarni yotqizish va shaklni mustahkamlash",
                            "Faqat dog‘larni ketkazish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Cho‘ntak joylashuvi noto‘g‘ri bo‘lsa, nima bo‘ladi?",
                        "options": [
                            "Kiyimning tashqi ko‘rinishi buziladi",
                            "Gazlama mustahkamlanadi",
                            "Ip kamroq sarf bo‘ladi",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Chokda joylashgan cho‘ntaklar qayerга tikiladi?",
                        "options": [
                            "Yon yoki o‘rta choklarning ichki qismiga",
                            "Faqat yoqa chizig‘iga",
                            "Faqat etak chizig‘iga",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t6": {
                "title": "Kiyimda joylashgan qirqma cho‘ntaklarni tikish",
                "questions": [
                    {
                        "text": "Qirqma cho‘ntak qopqog‘ining vazifasi?",
                        "options": [
                            "Faqat bezak sifatida",
                            "Cho‘ntak og‘zini yopib, shaklini saqlash",
                            "Faqat gazlamani qalinlashtirish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Qirqma cho‘ntak joylashuvi qanday belgilanadi?",
                        "options": [
                            "Eskiz va konstruksiyaga ko‘ra chizilgan belgilar bo‘yicha",
                            "Faqat taxminan ko‘z bilan",
                            "Faqat andazasiz kesib",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Cho‘ntakни matога joylashtirishда nimalar muhim?",
                        "options": [
                            "Chiziqlar to‘g‘riligi va juft qismlarning simmetriyasi",
                            "Faqat ipning qalinligi",
                            "Faqat dazmol harorati",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Qirqma cho‘ntakni noto‘g‘ri tikish oqibati?",
                        "options": [
                            "Faqat gazlama cho‘ziladi",
                            "Kiyim deformatsiyalanib, cho‘ntak og‘zi bujmaydi",
                            "Faqat ip sarfi ortadi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Cho‘ntakni mustahkamlash uchun nima ishlatiladi?",
                        "options": [
                            "Faqat rangli ip",
                            "Kleyli dublyorin yoki qo‘shimcha qatlam",
                            "Faqat suv bilan namlash",
                        ],
                        "correct": 1,
                    },
                ],
            },
            "t7": {
                "title": "Kiymlardagi turli bichimdagi yenglarni tikish",
                "questions": [
                    {
                        "text": "Kimono yengni tikishda asosiy qiyinchilik?",
                        "options": [
                            "Yeng детали alohida tikilishi",
                            "Yelka va yeng bir butun bo‘lgani uchun gazlama sarfi va konstruksiya murakkabligi",
                            "Faqat manjet tikish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Reglan yengning choklari qayerдан o‘tadi?",
                        "options": [
                            "Bo‘yindan qo‘ltiqqacha",
                            "Faqat yon chok bo‘ylab",
                            "Faqat pastki etak bo‘ylab",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Ikki chokli yengni tikishda nimalar muhim?",
                        "options": [
                            "Har ikki chokни uzunligini teng saqlash",
                            "Faqat manjetni keng qilish",
                            "Faqat gazlamani qalin tanlash",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Manjetli yenglarni presslash tartibi nima beradi?",
                        "options": [
                            "Faqat rangi tiniqlashadi",
                            "Choklar yotqizilib, shakl aniq bo‘ladi",
                            "Gazlama yupqalashadi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yeng o‘rnatilganda qo‘l harakati nimaga bog‘liq?",
                        "options": [
                            "Yeng o‘rnatish chizig‘i va qo‘shimchalarning to‘g‘ri taqsimланишига",
                            "Faqat yoqa turiga",
                            "Faqat gazlama tarkibiga",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t8": {
                "title": "Kiymlardagi yoqa turlarini tikish",
                "questions": [
                    {
                        "text": "Tik yoqaning xususiyati?",
                        "options": [
                            "Bo‘yin atrofiga yotqizilib turadi",
                            "Bo‘yin atrofini mahkam o‘rab turadi",
                            "Faqat old bo‘lakда ko‘rinadi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yotqizilgan yoqa qayerga yotadi?",
                        "options": [
                            "Ko‘krak va yelka sohasiga",
                            "Faqat belga",
                            "Faqat yengга",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Bort yoqa ko‘proq qaysi kiyimlarda ishlatiladi?",
                        "options": [
                            "Palto, jaket kabi ustki kiyimlarda",
                            "Faqat ichki futbolkalarda",
                            "Faqat sport shimlarida",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Yoqani bichishda asosiy о‘lчов?",
                        "options": [
                            "Bo‘y uzunligi",
                            "Bo‘yin aylanasi",
                            "Bilak girihi",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Yoqani presslash nega muhim?",
                        "options": [
                            "Shaklini aniq saqlash ва choklarni yotqizish uchun",
                            "Faqat gazlamani quritish uchun",
                            "Faqat rangi о‘zgarmasligi uchun",
                        ],
                        "correct": 0,
                    },
                ],
            },
            "t9": {
                "title": "Kiyimning bel qismiga ishlov berish",
                "questions": [
                    {
                        "text": "Kamarning asosiy vazifasi?",
                        "options": [
                            "Faqat bezak elementini ko‘paytirish",
                            "Bel qismni mahkamlash va shakl berish",
                            "Faqat cho‘ntakni ushlab turish",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Rezina tikilgan bel qismi qaysi kiyimlarda ko‘p uchraydi?",
                        "options": [
                            "Sport va maishiy qulay kiyimlarda",
                            "Faqat ish kostюмларида",
                            "Faqat palto va plashlarda",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Bel qismiga ishlov berishda bo‘y о‘lчови nima uchun kerak?",
                        "options": [
                            "Kamar kengligini aniqlash uchun",
                            "Bel atrofini aniq mos tushishini ta’minlash uchun",
                            "Faqat etak uzunligini hisoblash uchun",
                        ],
                        "correct": 1,
                    },
                    {
                        "text": "Bel qismi noto‘g‘ri ishlansa, nimaga olib keladi?",
                        "options": [
                            "Kiyim qulay o‘tirмайди, yuqoriga chiqib ketishi yoki bo‘sh bo‘lishi",
                            "Faqat rangi xira bo‘ladi",
                            "Faqat gazlama mustahкамланади",
                        ],
                        "correct": 0,
                    },
                    {
                        "text": "Yakuniy ishlov berish bosqichiga nimalar kiradi?",
                        "options": [
                            "Faqat yuvish",
                            "Presslash, ip uchlarini tozalash, tekshirish",
                            "Faqat yorliq tikish",
                        ],
                        "correct": 1,
                    },
                ],
            },
        },
    },
}


# ================== ХРАНЕНИЕ ДАННЫХ ==================
# ⚠ ВАЖНО: история теперь ведётся по ИМЕНИ, а не по user_id

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"students": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {"students": {}}
    if "students" not in data:
        data["students"] = {}
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


DATA = load_data()


def ensure_student(full_name: str):
    """Гарантируем, что студент с таким именем есть в DATA."""
    if full_name not in DATA["students"]:
        DATA["students"][full_name] = {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "results": {},  # subject -> topic -> stats
        }


def update_stats(full_name: str, subject_key: str, topic_key: str, is_correct: bool):
    """Обновляем статистику по ИМЕНИ."""
    ensure_student(full_name)
    student = DATA["students"][full_name]
    user_results = student["results"]

    if subject_key not in user_results:
        user_results[subject_key] = {}
    if topic_key not in user_results[subject_key]:
        user_results[subject_key][topic_key] = {
            "correct": 0,
            "wrong": 0,
            "points": 0,
        }

    rec = user_results[subject_key][topic_key]
    if is_correct:
        rec["correct"] += 1
        rec["points"] += POINTS_CORRECT
    else:
        rec["wrong"] += 1
        rec["points"] += POINTS_WRONG  # 0 yoki -10 bo‘lishi mumkin

    save_data(DATA)


def get_user_stats_text(full_name: str) -> str:
    """Текст статистики по конкретному имени."""
    student = DATA["students"].get(full_name)
    if not student:
        return f"{full_name} учун ҳали натижалар йўқ."

    res = student.get("results", {})
    if not res:
        return f"{full_name} учун ҳали натижалар йўқ."

    lines = [f"📊 Натижалар: {full_name}"]
    total_points = 0

    for subj_key, topics in res.items():
        subj_title = SUBJECTS.get(subj_key, {}).get("title", subj_key)
        lines.append(f"\n📚 {subj_title}:")
        for topic_key, r in topics.items():
            topic_title = (
                SUBJECTS.get(subj_key, {})
                .get("topics", {})
                .get(topic_key, {})
                .get("title", topic_key)
            )
            lines.append(
                f"  • {topic_title}: тўғри={r['correct']}, хато={r['wrong']}, балл={r['points']}"
            )
            total_points += r["points"]

    lines.append(f"\nЖами балл: {total_points}")
    return "\n".join(lines)


def get_global_stats_text() -> str:
    """Общая статистика по всем именам."""
    if not DATA["students"]:
        return "Ҳали ҳеч ким тест ечмаган."

    subj_totals = {}
    for full_name, student in DATA["students"].items():
        for subj_key, topics in student.get("results", {}).items():
            if subj_key not in subj_totals:
                subj_totals[subj_key] = {
                    "correct": 0,
                    "wrong": 0,
                    "points": 0,
                    "users": set(),
                }
            for topic_key, r in topics.items():
                subj_totals[subj_key]["correct"] += r["correct"]
                subj_totals[subj_key]["wrong"] += r["wrong"]
                subj_totals[subj_key]["points"] += r["points"]
                if r["correct"] or r["wrong"]:
                    subj_totals[subj_key]["users"].add(full_name)

    lines = ["🌍 Умумий статистика:"]
    for subj_key, info in subj_totals.items():
        subj_title = SUBJECTS.get(subj_key, {}).get("title", subj_key)
        lines.append(
            f"\n📚 {subj_title}:\n"
            f"  • иштирокчилар сони: {len(info['users'])}\n"
            f"  • тўғри жавоблар: {info['correct']}\n"
            f"  • хато жавоблар: {info['wrong']}\n"
            f"  • жами балл: {info['points']}"
        )

    return "\n".join(lines)


# ================== СОСТОЯНИЯ ПОЛЬЗОВАТЕЛЕЙ (в памяти) ==================
# user_id -> dict

user_state = {}


def get_state(user_id: int) -> dict:
    if user_id not in user_state:
        user_state[user_id] = {
            "awaiting_name": False,  # ждём ли сейчас ФИО
            "full_name": None,       # текущее активное имя
            "subject": None,
            "topic": None,
            "q_index": None,
        }
    return user_state[user_id]


# ================== КЛАВИАТУРЫ ==================

def subjects_keyboard():
    kb = InlineKeyboardBuilder()
    for subj_key, subj in SUBJECTS.items():
        kb.button(text=subj["title"], callback_data=f"subject:{subj_key}")
    kb.button(text="📊 Менинг натижаларим", callback_data="menu:mystats")
    kb.button(text="✅ Тестни якунлаш", callback_data="menu:finish")
    kb.adjust(1)
    return kb.as_markup()


def topics_keyboard(subj_key: str):
    kb = InlineKeyboardBuilder()
    topics = SUBJECTS[subj_key]["topics"]
    for topic_key, topic in topics.items():
        kb.button(text=topic["title"], callback_data=f"topic:{subj_key}:{topic_key}")
    kb.button(text="🏠 Бош саҳифа", callback_data="menu:main")
    kb.button(text="✅ Тестни якунлаш", callback_data="menu:finish")
    kb.adjust(1)
    return kb.as_markup()


def question_keyboard(subj_key: str, topic_key: str, q_index: int):
    kb = InlineKeyboardBuilder()
    questions = SUBJECTS[subj_key]["topics"][topic_key]["questions"]
    q = questions[q_index]
    labels = ["A", "B", "C"]
    for i, opt in enumerate(q["options"]):
        kb.button(
            text=f"{labels[i]}) {opt}",
            callback_data=f"answer:{subj_key}:{topic_key}:{q_index}:{i}",
        )
    # Кнопки меню
    kb.button(text="🏠 Бош саҳифа", callback_data="menu:main")
    kb.button(text="✅ Тестни якунлаш", callback_data="menu:finish")
    kb.adjust(1)
    return kb.as_markup()


def after_topic_keyboard(subj_key: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Бошқа мавзу", callback_data=f"topics:{subj_key}")
    kb.button(text="📖 Бошқа фан", callback_data="menu:subjects")
    kb.button(text="📊 Менинг натижаларим", callback_data="menu:mystats")
    kb.button(text="✅ Тестни якунлаш", callback_data="menu:finish")
    kb.button(text="🏠 Бош саҳифа", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def build_question_text(subj_key: str, topic_key: str, q_index: int) -> str:
    subject_title = SUBJECTS[subj_key]["title"]
    topic_title = SUBJECTS[subj_key]["topics"][topic_key]["title"]
    questions = SUBJECTS[subj_key]["topics"][topic_key]["questions"]
    q = questions[q_index]
    return (
        f"📚 {subject_title}\n"
        f"🧵 {topic_title}\n\n"
        f"Савол {q_index + 1}/{len(questions)}:\n\n"
        f"{q['text']}"
    )


# ================== ХЕНДЛЕРЫ ==================

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    state = get_state(user_id)
    # Полная очистка состояния с точки зрения сессии
    state["awaiting_name"] = True
    state["full_name"] = None
    state["subject"] = None
    state["topic"] = None
    state["q_index"] = None

    await message.answer(
        "👋 Ассалому алайкум!\n\n"
        "Мазкур бот тадқиқотчи Мусаева Умида томонидан таълим жараёнини рақамлаштириш ва талабаларнинг билимни ўзлаштириш даражасини самарали баҳолаш мақсадида яратилган. Бот орқали тақдим этиладиган тестлар, ўқув материаллари ва интерактив савол-жавоблар сизга фаннинг асосий тушунчаларини мустаҳкамлаш, анализ ва фикрлаш қобилиятингизни ривожлантиришга ёрдам беради. Ушбу платформа сизга ўз устида ишлаш ва янги билимларга эришишда ишончли ёрдамчи бўлади..\n\n"
        "Илтимос, исм-фамилиянгизни киритинг (кириллицада ёзишингиз мумкин):"
    )


@router.message(Command("mystats"))
async def cmd_mystats(message: Message):
    user_id = message.from_user.id
    state = get_state(user_id)
    full_name = state.get("full_name")

    if not full_name:
        await message.answer(
            "Аввал /start буйруғи орқали исм-фамилиянгизни киритинг."
        )
        return

    text = get_user_stats_text(full_name)
    await message.answer(text)


@router.message(Command("adminstats"))
async def cmd_adminstats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Бу буйруқ фақат админ учун.")
        return
    text = get_global_stats_text()
    await message.answer(text)


@router.message()
async def handle_name_or_text(message: Message):
    user_id = message.from_user.id
    state = get_state(user_id)

    # Агар ҳали исм-фамилия кутилса – сақлаймиз (история по имени)
    if state.get("awaiting_name"):
        full_name = (message.text or "").strip()
        if not full_name:
            await message.answer("Илтимос, тўғри исм-фамилияни киритинг.")
            return

        state["awaiting_name"] = False
        state["full_name"] = full_name

        ensure_student(full_name)
        save_data(DATA)

        await message.answer(
            f"Рахмат, {full_name}! ✅\n\n"
            "Энди фанни танланг:",
            reply_markup=subjects_keyboard(),
        )
        return

    # Акс ҳолда – асосий меню
    await message.answer(
        "Менюдан фойдаланинг.\n"
        "Фан танлаш учун /start ёки қуйидаги тугмалардан фойдаланинг.",
        reply_markup=subjects_keyboard(),
    )


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Асосий меню. Фанни танланг:", reply_markup=subjects_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu:subjects")
async def cb_subjects_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 Фанни танланг:", reply_markup=subjects_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "menu:mystats")
async def cb_mystats(callback: CallbackQuery):
    state = get_state(callback.from_user.id)
    full_name = state.get("full_name")
    if not full_name:
        await callback.answer(
            "Аввал /start орқали исм-фамилиянгизни киритинг.",
            show_alert=True,
        )
        return
    text = get_user_stats_text(full_name)
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "menu:finish")
async def cb_finish(callback: CallbackQuery):
    """Завершение теста: показываем результат и обнуляем сессию (но история остаётся)."""
    state = get_state(callback.from_user.id)
    full_name = state.get("full_name")

    if not full_name:
        await callback.answer(
            "Аввал /start буйруғи орқали тестни бошланг.",
            show_alert=True,
        )
        return

    # Текст статистики по имени
    stats_text = get_user_stats_text(full_name)

    # Обнуляем сессионные данные (но full_name оставляем до нового /start)
    state["subject"] = None
    state["topic"] = None
    state["q_index"] = None

    # Удаляем старую клавиатуру, чтобы по старым кнопкам нельзя было кликать
    try:
        await callback.message.edit_text(
            stats_text
            + "\n\n✅ Тест якунланди.\n"
              "Янги тестни бошлаш учун /start буйруғини юборинг.",
        )
    except Exception:
        # Если не получилось редактировать (например, старое сообщение),
        # просто отправим новое.
        await callback.message.answer(
            stats_text
            + "\n\n✅ Тест якунланди.\n"
              "Янги тестни бошлаш учун /start буйруғини юборинг.",
        )

    await callback.answer()


@router.callback_query(F.data.startswith("subject:"))
async def cb_subject(callback: CallbackQuery):
    _, subj_key = callback.data.split(":", 1)
    user_id = callback.from_user.id
    state = get_state(user_id)
    state["subject"] = subj_key
    state["topic"] = None
    state["q_index"] = None

    await callback.message.edit_text(
        f"📚 {SUBJECTS[subj_key]['title']}\n\nМавзуни танланг:",
        reply_markup=topics_keyboard(subj_key),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topics:"))
async def cb_topics(callback: CallbackQuery):
    _, subj_key = callback.data.split(":", 1)
    await callback.message.edit_text(
        f"📚 {SUBJECTS[subj_key]['title']}\n\nБошқа мавзуни танланг:",
        reply_markup=topics_keyboard(subj_key),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topic:"))
async def cb_topic(callback: CallbackQuery):
    _, subj_key, topic_key = callback.data.split(":")
    user_id = callback.from_user.id
    state = get_state(user_id)
    state["subject"] = subj_key
    state["topic"] = topic_key
    state["q_index"] = 0

    text = build_question_text(subj_key, topic_key, 0)
    await callback.message.edit_text(
        text, reply_markup=question_keyboard(subj_key, topic_key, 0)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("answer:"))
async def cb_answer(callback: CallbackQuery):
    parts = callback.data.split(":")
    _, subj_key, topic_key, q_index_str, ans_index_str = parts
    q_index = int(q_index_str)
    ans_index = int(ans_index_str)

    state = get_state(callback.from_user.id)
    full_name = state.get("full_name")

    if not full_name:
        await callback.answer(
            "Аввал /start буйруғи орқали исм-фамилиянгизни киритинг.",
            show_alert=True,
        )
        return

    questions = SUBJECTS[subj_key]["topics"][topic_key]["questions"]
    question = questions[q_index]
    is_correct = ans_index == question["correct"]
    update_stats(full_name, subj_key, topic_key, is_correct)

    labels = ["A", "B", "C"]
    if is_correct:
        fb = "✅ Тўғри жавоб!"
    else:
        correct_label = labels[question["correct"]]
        fb = f"❌ Нотоғри. Тўғри жавоб: {correct_label}"

    await callback.answer(fb, show_alert=False)

    next_index = q_index + 1
    if next_index < len(questions):
        state["q_index"] = next_index
        text = build_question_text(subj_key, topic_key, next_index)
        await callback.message.edit_text(
            text, reply_markup=question_keyboard(subj_key, topic_key, next_index)
        )
    else:
        topic_title = SUBJECTS[subj_key]["topics"][topic_key]["title"]
        state["q_index"] = None
        await callback.message.edit_text(
            f"✅ «{topic_title}» мавзусидаги тестлар якунланди.\n\n"
            "Бошқа мавзу ёки фанни танлашингиз мумкин, ёки натижаларингизни кўринг.",
            reply_markup=after_topic_keyboard(subj_key),
        )


# ================== ЗАПУСК БОТА ==================

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())


