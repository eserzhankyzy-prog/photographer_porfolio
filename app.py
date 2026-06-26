import os

from flask import Flask, current_app, redirect, render_template, request, session, url_for
from flask_login import LoginManager
from sqlalchemy import text
from werkzeug.security import generate_password_hash

from models import Photo, Review, User, db


SUPPORTED_LANGUAGES = {
    "kk": "Қазақша",
    "ru": "Русский",
    "en": "English",
}

STAFF_DASHBOARD_ROLES = {"admin", "manager", "employee", "moderator"}

TRANSLATIONS = {
    "kk": {
        "site_title": "Ailaer",
        "site_name": "Ailaer",
        "nav_home": "Басты бет",
        "nav_gallery": "Галерея",
        "nav_services": "Қызметтер",
        "nav_reviews": "Пікірлер",
        "nav_contact": "Байланыс",
        "nav_order": "Брондау",
        "nav_login": "Кіру",
        "nav_register": "Тіркелу",
        "nav_logout": "Шығу",
        "nav_dashboard": "Кабинет",
        "language": "Тіл",
        "hero_kicker": "Үйлену, портрет, отбасы және іс-шара фотосы",
        "hero_title": "Сәттерді табиғи, жылы және кәсіби кадрларға айналдырамын.",
        "hero_text": "Минималистік стиль, жұмсақ жарық және эмоцияға толы репортаж. Әр түсірілім алдын ала жоспарланып, дайын галерея ретінде тапсырылады.",
        "hero_cta": "Фотосессия брондау",
        "hero_secondary": "Галереяны көру",
        "hero_stat_1": "Жоба",
        "hero_stat_2": "Бағыт",
        "hero_stat_3": "Жеткізу",
        "hero_stat_1_value": "120+",
        "hero_stat_2_value": "4",
        "hero_stat_3_value": "7 күн",
        "about_title": "Фотограф туралы",
        "about_text": "Мен адамдардың шынайы эмоциясын, отбасының жақындығын және маңызды күндердің атмосферасын кадрда сақтауға көмектесемін. Жұмысымда артық эффектіден гөрі таза композиция, табиғи түс және оқиғаға жақын репортаж маңызды.",
        "about_point_1": "Түсірілімге дейін moodboard және маршрут дайындау",
        "about_point_2": "Түсті кәсіби өңдеу және авторлық ретушь",
        "about_point_3": "Онлайн галерея арқылы ыңғайлы тапсыру",
        "gallery_preview_title": "Галерея",
        "gallery_preview_text": "Wedding, Portrait, Family және Event бағыттарына арналған таңдаулы кадрлар.",
        "view_all": "Барлығын көру",
        "services_title": "Қызметтер",
        "services_text": "Әр пакет түсірілім мақсатына, локацияға және дайын материал көлеміне қарай бейімделеді.",
        "service_wedding": "Wedding Photography",
        "service_wedding_text": "Той күні, love story, салтанатты рәсім және кешкі репортаж.",
        "service_portrait": "Portrait Photography",
        "service_portrait_text": "Жеке бренд, lifestyle портрет және студиялық образдар.",
        "service_family": "Family Photography",
        "service_family_text": "Отбасылық серуен, үйдегі жылы кадрлар және балалар фотосы.",
        "service_event": "Event Photography",
        "service_event_text": "Конференция, туған күн, корпоратив және мәдени іс-шаралар.",
        "reviews_title": "Клиент пікірлері",
        "review_1": "Кадрлар өте табиғи шықты. Фотограф түсірілім кезінде өзімізді еркін сезіндірді.",
        "review_1_author": "Айгерім, wedding shoot",
        "review_2": "Портреттерім LinkedIn және portfolio үшін дәл керек стильде дайын болды.",
        "review_2_author": "Арман, portrait session",
        "review_3": "Отбасылық фотосессия жайлы өтті, балалар да камерадан қысылған жоқ.",
        "review_3_author": "Дана, family session",
        "contact_title": "Байланыс",
        "contact_text": "Күніңізді, түсірілім түрін және қалаған стильді жазыңыз. Мен сізге қолайлы пакет ұсынамын.",
        "contact_phone": "Телефон",
        "contact_email": "Email",
        "contact_location": "Қала",
        "footer_text": "Заманауи фотограф портфолиосы және университеттік жоба.",
        "gallery_title": "Фото галерея",
        "gallery_text": "Таңдаулы фотосериялар: той, портрет, отбасы және іс-шара кадрлары.",
        "filter_all": "Барлығы",
        "filter_wedding": "Wedding",
        "filter_portrait": "Portrait",
        "filter_family": "Family",
        "filter_event": "Event",
        "album_empty": "Бұл альбомда әзірге фото жоқ.",
        "search_title": "Іздеу нәтижелері",
        "search_label": "Іздеу",
        "no_results": "Нәтиже табылмады.",
        "login_title": "Жүйеге кіру",
        "register_title": "Аккаунт ашу",
        "username": "Пайдаланушы аты",
        "email": "Email",
        "password": "Құпиясөз",
        "role": "Рөл",
        "submit_login": "Кіру",
        "submit_register": "Тіркелу",
        "have_account": "Аккаунтыңыз бар ма?",
        "need_account": "Аккаунт керек пе?",
        "invalid_login": "Email немесе құпиясөз қате.",
        "login_success": "Қош келдіңіз!",
        "logout_success": "Сіз жүйеден шықтыңыз.",
        "register_success": "Тіркелу сәтті аяқталды. Енді кіре аласыз.",
        "duplicate_user": "Бұл email немесе username бұрын тіркелген.",
        "order_title": "Фотосессия брондау",
        "order_text": "Атыңызды және түсірілім түрін қалдырыңыз.",
        "customer_name": "Атыңыз",
        "service_type": "Түсірілім түрі",
        "send_order": "Өтінім жіберу",
        "review_title": "Пікір қалдыру",
        "review_text": "Түсірілім туралы әсеріңізді жазыңыз.",
        "author": "Атыңыз",
        "review_body": "Пікіріңіз",
        "rating": "Баға",
        "send_review": "Жіберу",
        "open_photo": "Суретті ашу",
        "close": "Жабу",
        "dashboard_title": "Рөлдік кабинет",
        "dashboard_text": "Бұл бөлім тек сәйкес рөлдегі қолданушыларға арналған.",
    },
    "ru": {
        "site_title": "Ailaer",
        "site_name": "Ailaer",
        "nav_home": "Главная",
        "nav_gallery": "Галерея",
        "nav_services": "Услуги",
        "nav_reviews": "Отзывы",
        "nav_contact": "Контакты",
        "nav_order": "Бронь",
        "nav_login": "Войти",
        "nav_register": "Регистрация",
        "nav_logout": "Выйти",
        "nav_dashboard": "Кабинет",
        "language": "Язык",
        "hero_kicker": "Свадьбы, портреты, семья и события",
        "hero_title": "Превращаю важные моменты в естественные и профессиональные кадры.",
        "hero_text": "Минималистичный стиль, мягкий свет и живая репортажная съемка. Каждая фотосессия планируется заранее и передается в готовой онлайн-галерее.",
        "hero_cta": "Забронировать съемку",
        "hero_secondary": "Смотреть галерею",
        "hero_stat_1": "Проектов",
        "hero_stat_2": "Направления",
        "hero_stat_3": "Передача",
        "hero_stat_1_value": "120+",
        "hero_stat_2_value": "4",
        "hero_stat_3_value": "7 дней",
        "about_title": "О фотографе",
        "about_text": "Я помогаю сохранить искренние эмоции, близость семьи и атмосферу важных дней. В работе ценю чистую композицию, естественный цвет и репортаж, который остается рядом с реальной историей.",
        "about_point_1": "Moodboard и маршрут до съемки",
        "about_point_2": "Профессиональная цветокоррекция и авторская ретушь",
        "about_point_3": "Удобная передача через онлайн-галерею",
        "gallery_preview_title": "Галерея",
        "gallery_preview_text": "Избранные кадры для Wedding, Portrait, Family и Event съемок.",
        "view_all": "Смотреть все",
        "services_title": "Услуги",
        "services_text": "Каждый пакет адаптируется под цель съемки, локацию и объем готовых материалов.",
        "service_wedding": "Wedding Photography",
        "service_wedding_text": "Свадебный день, love story, церемония и вечерний репортаж.",
        "service_portrait": "Portrait Photography",
        "service_portrait_text": "Личный бренд, lifestyle-портреты и студийные образы.",
        "service_family": "Family Photography",
        "service_family_text": "Семейная прогулка, теплые домашние кадры и детская съемка.",
        "service_event": "Event Photography",
        "service_event_text": "Конференции, дни рождения, корпоративы и культурные события.",
        "reviews_title": "Отзывы клиентов",
        "review_1": "Кадры получились очень естественными. На съемке было спокойно и комфортно.",
        "review_1_author": "Айгерим, wedding shoot",
        "review_2": "Портреты для LinkedIn и портфолио получились именно в нужной стилистике.",
        "review_2_author": "Арман, portrait session",
        "review_3": "Семейная съемка прошла легко, дети не стеснялись камеры.",
        "review_3_author": "Дана, family session",
        "contact_title": "Контакты",
        "contact_text": "Укажите дату, тип съемки и желаемый стиль. Я предложу подходящий пакет.",
        "contact_phone": "Телефон",
        "contact_email": "Email",
        "contact_location": "Город",
        "footer_text": "Современное портфолио фотографа и университетский проект.",
        "gallery_title": "Фотогалерея",
        "gallery_text": "Избранные фотосерии: свадьбы, портреты, семья и события.",
        "filter_all": "Все",
        "filter_wedding": "Wedding",
        "filter_portrait": "Portrait",
        "filter_family": "Family",
        "filter_event": "Event",
        "album_empty": "В этом альбоме пока нет фотографий.",
        "search_title": "Результаты поиска",
        "search_label": "Поиск",
        "no_results": "Ничего не найдено.",
        "login_title": "Вход",
        "register_title": "Создать аккаунт",
        "username": "Имя пользователя",
        "email": "Email",
        "password": "Пароль",
        "role": "Роль",
        "submit_login": "Войти",
        "submit_register": "Зарегистрироваться",
        "have_account": "Уже есть аккаунт?",
        "need_account": "Нужен аккаунт?",
        "invalid_login": "Неверный email или пароль.",
        "login_success": "Добро пожаловать!",
        "logout_success": "Вы вышли из системы.",
        "register_success": "Регистрация прошла успешно. Теперь можно войти.",
        "duplicate_user": "Этот email или username уже зарегистрирован.",
        "order_title": "Забронировать фотосессию",
        "order_text": "Оставьте имя и тип съемки.",
        "customer_name": "Ваше имя",
        "service_type": "Тип съемки",
        "send_order": "Отправить заявку",
        "review_title": "Оставить отзыв",
        "review_text": "Напишите впечатления о съемке.",
        "author": "Ваше имя",
        "review_body": "Ваш отзыв",
        "rating": "Оценка",
        "send_review": "Отправить",
        "open_photo": "Открыть фото",
        "close": "Закрыть",
        "dashboard_title": "Ролевой кабинет",
        "dashboard_text": "Этот раздел доступен только пользователям с подходящей ролью.",
    },
    "en": {
        "site_title": "Ailaer",
        "site_name": "Ailaer",
        "nav_home": "Home",
        "nav_gallery": "Gallery",
        "nav_services": "Services",
        "nav_reviews": "Reviews",
        "nav_contact": "Contact",
        "nav_order": "Book",
        "nav_login": "Login",
        "nav_register": "Register",
        "nav_logout": "Logout",
        "nav_dashboard": "Dashboard",
        "language": "Language",
        "hero_kicker": "Wedding, portrait, family and event photography",
        "hero_title": "Turning meaningful moments into natural, polished photographs.",
        "hero_text": "Minimal style, soft light, and emotional storytelling. Every session is planned in advance and delivered as a curated online gallery.",
        "hero_cta": "Book a session",
        "hero_secondary": "View gallery",
        "hero_stat_1": "Projects",
        "hero_stat_2": "Genres",
        "hero_stat_3": "Delivery",
        "hero_stat_1_value": "120+",
        "hero_stat_2_value": "4",
        "hero_stat_3_value": "7 days",
        "about_title": "About the photographer",
        "about_text": "I help preserve honest emotion, family closeness, and the atmosphere of important days. My work favors clean composition, natural color, and documentary images that stay close to the real story.",
        "about_point_1": "Moodboard and location plan before the shoot",
        "about_point_2": "Professional color editing and signature retouching",
        "about_point_3": "Easy delivery through an online gallery",
        "gallery_preview_title": "Gallery",
        "gallery_preview_text": "Selected frames for Wedding, Portrait, Family, and Event sessions.",
        "view_all": "View all",
        "services_title": "Services",
        "services_text": "Each package adapts to the session goal, location, and final gallery size.",
        "service_wedding": "Wedding Photography",
        "service_wedding_text": "Wedding day, love story, ceremony, and evening reportage.",
        "service_portrait": "Portrait Photography",
        "service_portrait_text": "Personal brand, lifestyle portraits, and studio looks.",
        "service_family": "Family Photography",
        "service_family_text": "Family walks, cozy home stories, and children photography.",
        "service_event": "Event Photography",
        "service_event_text": "Conferences, birthdays, corporate events, and cultural programs.",
        "reviews_title": "Client reviews",
        "review_1": "The photos feel so natural. The session was calm and comfortable.",
        "review_1_author": "Aigerim, wedding shoot",
        "review_2": "My portraits for LinkedIn and portfolio were delivered in exactly the right style.",
        "review_2_author": "Arman, portrait session",
        "review_3": "The family session felt easy, and the children were relaxed in front of the camera.",
        "review_3_author": "Dana, family session",
        "contact_title": "Contact",
        "contact_text": "Send the date, session type, and preferred style. I will suggest the best package.",
        "contact_phone": "Phone",
        "contact_email": "Email",
        "contact_location": "City",
        "footer_text": "Modern photographer portfolio and university project.",
        "gallery_title": "Photo gallery",
        "gallery_text": "Selected photo stories: weddings, portraits, family sessions, and events.",
        "filter_all": "All",
        "filter_wedding": "Wedding",
        "filter_portrait": "Portrait",
        "filter_family": "Family",
        "filter_event": "Event",
        "album_empty": "This album does not have photos yet.",
        "search_title": "Search results",
        "search_label": "Search",
        "no_results": "No results found.",
        "login_title": "Login",
        "register_title": "Create account",
        "username": "Username",
        "email": "Email",
        "password": "Password",
        "role": "Role",
        "submit_login": "Login",
        "submit_register": "Register",
        "have_account": "Already have an account?",
        "need_account": "Need an account?",
        "invalid_login": "Email or password is incorrect.",
        "login_success": "Welcome back!",
        "logout_success": "You have been logged out.",
        "register_success": "Registration completed. You can log in now.",
        "duplicate_user": "This email or username is already registered.",
        "order_title": "Book a photoshoot",
        "order_text": "Leave your name and session type.",
        "customer_name": "Your name",
        "service_type": "Session type",
        "send_order": "Send request",
        "review_title": "Leave a review",
        "review_text": "Tell us about your session experience.",
        "author": "Your name",
        "review_body": "Your review",
        "rating": "Rating",
        "send_review": "Submit",
        "open_photo": "Open photo",
        "close": "Close",
        "dashboard_title": "Role dashboard",
        "dashboard_text": "This section is available only to users with the matching role.",
    },
}


TRANSLATIONS["kk"].update({
    "hero_title": "Ailaer",
    "gallery_text": "Таңдаулы фотосериялар: той, портрет, отбасы және іс-шара кадрлары.",
    "profile_title": "Жеке профиль",
    "profile_text": "Өтінімдеріңізді, пікірлеріңізді және аккаунт деректерін осы жерден көре аласыз.",
    "my_orders": "Менің өтінімдерім",
    "my_reviews": "Менің пікірлерім",
    "admin_panel": "Әкімші панелі",
    "manager_panel": "Менеджер панелі",
    "employee_panel": "Қызметкер панелі",
    "moderator_panel": "Модератор панелі",
    "users": "Пайдаланушылар",
    "system_logs": "Жүйелік жазбалар",
    "orders": "Өтінімдер",
    "reviews": "Пікірлер",
    "customer": "Клиент",
    "status": "Статус",
    "date": "Күні",
    "actions": "Әрекеттер",
    "save": "Сақтау",
    "delete": "Жою",
    "approve": "Бекіту",
    "complete": "Аяқтау",
    "notes": "Қосымша ақпарат",
    "no_data": "Әзірге дерек жоқ.",
    "access_denied": "Қолжетімділік шектелген",
    "access_denied_text": "Бұл бетке кіру үшін сәйкес рөл қажет.",
    "order_created": "Өтінім сәтті жіберілді.",
    "review_created": "Пікір модерацияға жіберілді.",
    "role_updated": "Рөл жаңартылды.",
    "user_deleted": "Пайдаланушы жойылды.",
    "cannot_delete_self": "Өзіңізді жоя алмайсыз.",
    "order_updated": "Өтінім статусы жаңартылды.",
    "review_approved": "Пікір бекітілді.",
    "review_deleted": "Пікір жойылды.",
    "admin_hint": "Пайдаланушылардың рөлдерін өзгертіп, жүйелік жазбаларды бақылай аласыз.",
    "manager_hint": "Клиент өтінімдерін өңдеп, жұмыс статусын өзгертіңіз.",
    "employee_hint": "Өңдеуге берілген фотосессияларды қарап, аяқталғанын белгілеңіз.",
    "moderator_hint": "Клиент пікірлерін тексеріп, жариялауға бекітіңіз.",
})

TRANSLATIONS["ru"].update({
    "hero_title": "Ailaer",
    "gallery_text": "Избранные фотосерии: свадьбы, портреты, семья и события.",
    "profile_title": "Личный профиль",
    "profile_text": "Здесь можно посмотреть заявки, отзывы и данные аккаунта.",
    "my_orders": "Мои заявки",
    "my_reviews": "Мои отзывы",
    "admin_panel": "Панель администратора",
    "manager_panel": "Панель менеджера",
    "employee_panel": "Панель сотрудника",
    "moderator_panel": "Панель модератора",
    "users": "Пользователи",
    "system_logs": "Системные записи",
    "orders": "Заявки",
    "reviews": "Отзывы",
    "customer": "Клиент",
    "status": "Статус",
    "date": "Дата",
    "actions": "Действия",
    "save": "Сохранить",
    "delete": "Удалить",
    "approve": "Одобрить",
    "complete": "Завершить",
    "notes": "Дополнительная информация",
    "no_data": "Данных пока нет.",
    "access_denied": "Доступ ограничен",
    "access_denied_text": "Для этой страницы нужна подходящая роль.",
    "order_created": "Заявка успешно отправлена.",
    "review_created": "Отзыв отправлен на модерацию.",
    "role_updated": "Роль обновлена.",
    "user_deleted": "Пользователь удален.",
    "cannot_delete_self": "Нельзя удалить самого себя.",
    "order_updated": "Статус заявки обновлен.",
    "review_approved": "Отзыв одобрен.",
    "review_deleted": "Отзыв удален.",
    "admin_hint": "Изменяйте роли пользователей и контролируйте системные записи.",
    "manager_hint": "Обрабатывайте заявки клиентов и меняйте рабочий статус.",
    "employee_hint": "Просматривайте назначенные фотосессии и отмечайте завершение.",
    "moderator_hint": "Проверяйте отзывы клиентов и одобряйте публикацию.",
})

TRANSLATIONS["en"].update({
    "hero_title": "Ailaer",
    "gallery_text": "Selected photo stories: weddings, portraits, family sessions, and events.",
    "profile_title": "Profile",
    "profile_text": "View your requests, reviews, and account details here.",
    "my_orders": "My requests",
    "my_reviews": "My reviews",
    "admin_panel": "Admin panel",
    "manager_panel": "Manager panel",
    "employee_panel": "Employee panel",
    "moderator_panel": "Moderator panel",
    "users": "Users",
    "system_logs": "System logs",
    "orders": "Requests",
    "reviews": "Reviews",
    "customer": "Client",
    "status": "Status",
    "date": "Date",
    "actions": "Actions",
    "save": "Save",
    "delete": "Delete",
    "approve": "Approve",
    "complete": "Complete",
    "notes": "Notes",
    "no_data": "No data yet.",
    "access_denied": "Access denied",
    "access_denied_text": "This page requires the matching role.",
    "order_created": "Request sent successfully.",
    "review_created": "Review sent for moderation.",
    "role_updated": "Role updated.",
    "user_deleted": "User deleted.",
    "cannot_delete_self": "You cannot delete yourself.",
    "order_updated": "Request status updated.",
    "review_approved": "Review approved.",
    "review_deleted": "Review deleted.",
    "admin_hint": "Change user roles and monitor system activity.",
    "manager_hint": "Process client requests and update work status.",
    "employee_hint": "View assigned sessions and mark completed work.",
    "moderator_hint": "Review client feedback and approve publication.",
})

for translations in TRANSLATIONS.values():
    translations.update({
        "review_created": "Your review has been sent for moderation",
        "photo_required": "Photo title and image file are required.",
        "invalid_image_type": "Only PNG, JPG, JPEG, and WEBP images are allowed.",
        "photo_added": "Photo added successfully.",
        "photo_deleted": "Photo deleted successfully.",
    })

TRANSLATIONS["kk"].update({
    "content_management": "Контентті басқару",
    "review_moderation": "Пікірлерді модерациялау",
    "review_moderation_text": "Клиент пікірлері сайтта шықпас бұрын тексеріледі.",
    "open_review_moderation": "Пікірлерді ашу",
    "pending_reviews": "Күтіп тұрған пікірлер",
    "pending_reviews_count": "күтіп тұрған пікір",
    "recent_reviews": "Соңғы пікірлер",
    "pending_status": "күтілуде",
    "approved_status": "мақұлданды",
    "author_label": "Автор",
    "text_label": "Мәтін",
    "photos_label": "Фотолар",
    "manage_photos": "Фотоларды басқару",
    "manage_photos_text": "Галереяға жаңа жұмыстар қосыңыз немесе қажет емес фотоларды өшіріңіз.",
    "all_photos": "Барлық фотолар",
    "add_photo": "Фото қосу",
    "add_photo_text": "Ailaer галереясына жаңа сурет жүктеу.",
    "photo_title": "Фото атауы",
    "category": "Категория",
    "description": "Сипаттама",
    "image_file": "Сурет файлы",
    "album": "Альбом",
    "no_album": "Альбомсыз",
    "price": "Баға",
    "shoot_date": "Түсірілім күні",
    "upload_photo": "Фото жүктеу",
    "delete_photo_confirm": "Бұл фото өшірілсін бе?",
    "review_created": "Пікіріңіз модерацияға жіберілді",
    "photo_required": "Фото атауы мен сурет файлы міндетті.",
    "invalid_image_type": "Тек PNG, JPG, JPEG және WEBP суреттері қабылданады.",
    "photo_added": "Фото сәтті қосылды.",
    "photo_deleted": "Фото сәтті өшірілді.",
})

TRANSLATIONS["ru"].update({
    "content_management": "Управление контентом",
    "review_moderation": "Модерация отзывов",
    "review_moderation_text": "Отзывы клиентов проверяются перед публикацией на сайте.",
    "open_review_moderation": "Открыть модерацию",
    "pending_reviews": "Отзывы на проверке",
    "pending_reviews_count": "отзывов на проверке",
    "recent_reviews": "Последние отзывы",
    "pending_status": "ожидает",
    "approved_status": "одобрен",
    "author_label": "Автор",
    "text_label": "Текст",
    "photos_label": "Фотографии",
    "manage_photos": "Управление фото",
    "manage_photos_text": "Добавляйте новые работы в галерею или удаляйте устаревшие фото.",
    "all_photos": "Все фотографии",
    "add_photo": "Добавить фото",
    "add_photo_text": "Загрузите новое изображение в галерею Ailaer.",
    "photo_title": "Название фото",
    "category": "Категория",
    "description": "Описание",
    "image_file": "Файл изображения",
    "album": "Альбом",
    "no_album": "Без альбома",
    "price": "Цена",
    "shoot_date": "Дата съемки",
    "upload_photo": "Загрузить фото",
    "delete_photo_confirm": "Удалить это фото?",
    "review_created": "Ваш отзыв отправлен на модерацию",
    "photo_required": "Название фото и файл изображения обязательны.",
    "invalid_image_type": "Разрешены только изображения PNG, JPG, JPEG и WEBP.",
    "photo_added": "Фото успешно добавлено.",
    "photo_deleted": "Фото успешно удалено.",
})

TRANSLATIONS["en"].update({
    "content_management": "Content Management",
    "review_moderation": "Review Moderation",
    "review_moderation_text": "Client reviews are checked before they appear on the public website.",
    "open_review_moderation": "Open Review Moderation",
    "pending_reviews": "Pending Reviews",
    "pending_reviews_count": "pending reviews",
    "recent_reviews": "Recent Reviews",
    "pending_status": "pending",
    "approved_status": "approved",
    "author_label": "Author",
    "text_label": "Text",
    "photos_label": "Photos",
    "manage_photos": "Manage Photos",
    "manage_photos_text": "Add new work to the gallery or remove outdated photos.",
    "all_photos": "All Photos",
    "add_photo": "Add Photo",
    "add_photo_text": "Upload a new image to the Ailaer gallery.",
    "photo_title": "Photo title",
    "category": "Category",
    "description": "Description",
    "image_file": "Image file",
    "album": "Album",
    "no_album": "No album",
    "price": "Price",
    "shoot_date": "Shoot date",
    "upload_photo": "Upload Photo",
    "delete_photo_confirm": "Delete this photo?",
})


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "portfolio-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = "static/uploads"

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_global_template_data():
        current_lang = session.get("lang", "kk")
        if current_lang not in SUPPORTED_LANGUAGES:
            current_lang = "kk"

        def t(key):
            return TRANSLATIONS.get(current_lang, {}).get(
                key,
                TRANSLATIONS["en"].get(key, key),
            )

        def dashboard_endpoint(user):
            if getattr(user, "role", None) in STAFF_DASHBOARD_ROLES:
                return f"{user.role}.dashboard"
            return "auth.profile"

        return {
            "current_lang": current_lang,
            "dashboard_endpoint": dashboard_endpoint,
            "languages": SUPPORTED_LANGUAGES,
            "t": t,
        }

    @app.route("/")
    def home():
        approved_reviews = Review.query.filter_by(approved=True).order_by(
            Review.created_at.desc()
        ).limit(6).all()
        return render_template("index.html", approved_reviews=approved_reviews)

    @app.route("/set-language/<lang_code>")
    def set_language(lang_code):
        if lang_code in SUPPORTED_LANGUAGES:
            session["lang"] = lang_code
        return redirect(request.referrer or url_for("home"))

    @app.errorhandler(403)
    def forbidden(_error):
        return render_template("403.html"), 403

    from admin.routes import admin_bp
    from api.routes import api_bp
    from auth.routes import auth_bp
    from employee.routes import employee_bp
    from gallery.routes import gallery_bp
    from manager.routes import manager_bp
    from moderator.routes import moderator_bp
    from orders.routes import orders_bp
    from reviews.routes import reviews_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(gallery_bp, url_prefix="/gallery")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(reviews_bp, url_prefix="/reviews")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(manager_bp, url_prefix="/manager")
    app.register_blueprint(employee_bp, url_prefix="/employee")
    app.register_blueprint(moderator_bp, url_prefix="/moderator")

    with app.app_context():
        db.create_all()
        ensure_database_schema()
        ensure_default_admin()
        ensure_default_photos()

    return app


def ensure_database_schema():
    sqlite_columns = {
        "order": {
            "customer_email": "VARCHAR(120)",
            "notes": "TEXT",
            "user_id": "INTEGER",
        },
        "review": {
            "user_id": "INTEGER",
            "created_at": "DATETIME",
            "approved": "BOOLEAN DEFAULT 0",
        },
        "photo": {
            "category": "VARCHAR(50) DEFAULT 'Wedding'",
            "description": "TEXT",
            "price": "FLOAT",
            "shoot_date": "DATE",
            "created_at": "DATETIME",
        },
    }

    for table_name, required_columns in sqlite_columns.items():
        existing_columns = {
            row[1]
            for row in db.session.execute(text(f"PRAGMA table_info('{table_name}')"))
        }
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                db.session.execute(
                    text(f'ALTER TABLE "{table_name}" ADD COLUMN {column_name} {column_type}')
                )

    db.session.execute(
        text("UPDATE photo SET category = 'Wedding' WHERE category IS NULL OR category = ''")
    )
    db.session.commit()


def ensure_default_admin():
    admin = User.query.filter_by(email="Ailaer@studio.com").first()

    if not admin:
        admin = User(
            username="admin",
            email="Ailaer@studio.com",
            role="admin",
        )
        db.session.add(admin)

    admin.username = "admin"
    admin.email = "Ailaer@studio.com"
    admin.password = generate_password_hash("admins19")
    admin.role = "admin"
    db.session.commit()


def ensure_default_photos():
    if Photo.query.first():
        return

    defaults = [
        ("Wedding Vertical", "Wedding", "uploads/wedding-vertical.png"),
        ("Wedding Horizontal", "Wedding", "uploads/wedding-horizontal.png"),
        ("Full Portrait", "Portrait", "uploads/full-portrait.png"),
        ("3x4 Portrait", "Portrait", "uploads/3x4-portrait.png"),
        ("Family", "Family", "uploads/family.png"),
        ("Family Horizontal", "Family", "uploads/family-horizontal.png"),
        ("Event", "Event", "uploads/event.png"),
        ("Event Horizontal", "Event", "uploads/event-horizontal.png"),
    ]

    for title, category, image_path in defaults:
        absolute_path = os.path.join(current_app.static_folder, image_path)
        if os.path.exists(absolute_path):
            db.session.add(
                Photo(
                    title=title,
                    category=category,
                    image_path=image_path,
                    description=f"{category} photography",
                )
            )

    db.session.commit()


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=8000)
