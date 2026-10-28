# ⚡ Antigravity Token Tracker (`agy-token-tracker`)

پلاگین رسمی پایش و مانیتورینگ مصرف توکن برای **Google Antigravity**.

این پلاگین آمار دقیق توکن‌های ورودی (`input_tokens`)، توکن‌های خروجی (`output_tokens`) و توکن‌های خوانده شده از کش (`cache_read_tokens`) را از لاگ‌های محلی Antigravity استخراج کرده و در قالب ویجت‌های تعاملی چت و پنل نوار کناری (Auxiliary Pane) نمایش می‌دهد.

---

## 🚀 ویژگی‌ها

- **نمایش مصرف گفتگوی جاری**: محاسبه تعداد دورها (Turns)، نسبت مصرف ورودی/خروجی و درصد کش با کارت گرافیکی مدرن.
- **گزارش جامع تمام گفتگوها**:
  - نمودار افقی پرمصرف‌ترین گفتگوها (Top Conversations Chart).
  - جدول قابل سورت بر اساس تمام ستون‌ها (عنوان، تعداد دور، توکن ورودی، خروجی، مجموع، کش).
  - استخراج عنوان واقعی گفتگو از پرامپت‌ها در کنار شناسه (Conversation ID).
  - فیلتر و جستجوی آنی.
- **داشبورد مستقل نوار کناری (Sidecar Web UI)**: اجرا در پنل جانبی برنامه با آپدیت خودکار هر ۵ ثانیه.
- **بروزرسانی خودکار (Self-Update)**: امکان آپدیت مستقیم پلاگین به آخرین نسخه توسط خود ایجنت یا با یک دستور.

---

## 📦 نصب و راه‌اندازی

### نصب سریع با Git (توصیه‌شده):

```bash
git clone https://github.com/maa3x/agy-token-tracker.git ~/.gemini/config/plugins/token-tracker
agy plugin enable token-tracker
```

یا اگر از قبل زیپ کرده‌اید:
```bash
unzip token-tracker.zip -d ~/.gemini/config/plugins/
agy plugin enable token-tracker
```

---

## 🛠 دستورات (Slash Commands)

در محیط چت Antigravity می‌توانید از دستورات زیر استفاده کنید:

| دستور | عملکرد |
| :--- | :--- |
| `/tokens` | نمایش وضعیت مصرف توکن در همین گفتگو با ویجت گرافیکی زنده |
| `/tokens-all` | تولید گزارش تصویری تمام گفتگوها با چارت و جدول قابل سورت |
| `/tokens-update` | آپدیت مستقیم پلاگین از ریپوزیتوری گیت‌هاب به آخرین نسخه |

---

## 🔄 راهنمای بروزرسانی پلاگین

### روش ۱: از طریق ایجنت (دستور در چت)
به ایجنت بگویید:
```text
/tokens-update
```
یا
```text
پلاگین token-tracker رو به آخرین نسخه آپدیت کن
```
ایجنت با فراخوانی اسکیل `token-tracker` اسکریپت `scripts/update.sh` را اجرا کرده و کدها را به صورت `git pull` بروزرسانی می‌کند.

### روش ۲: از طریق ترمینال
```bash
bash ~/.gemini/config/plugins/token-tracker/scripts/update.sh
```

### روش ۳: بروزرسانی خودکار در شروع هر سشن (با Hook اختیاری)
اگر می‌خواهید در شروع هر گفتگو پلاگین خودش خودکار چک کند، کافیست فایل `hooks.json` را در ریشه پلاگین قرار دهید:

```json
{
  "token-tracker-autoupdate": {
    "SessionStart": [
      {
        "type": "command",
        "command": "./scripts/update.sh"
      }
    ]
  }
}
```

---

## 📁 ساختار پوشه پلاگین

```text
~/.gemini/config/plugins/token-tracker/
├── plugin.json                    # مانیفست پلاگین
├── README.md                      # راهنمای کامل
├── scripts/
│   ├── get_tokens.py              # اسکریپت پارس و استخراج لاگ‌ها
│   ├── generate_report.py         # تولید گزارش تعاملی مستقل تمام گفتگوها
│   └── update.sh                  # اسکریپت بروزرسانی ریپوزیتوری
├── skills/
│   └── token-tracker/
│       └── SKILL.md               # تعریف اسکیل چت و اسلش کامندها
└── sidecars/
    └── dashboard/
        ├── sidecar.json           # ثبت پنل وب در Auxiliary Pane
        ├── server.py              # وب‌سرور داخلی سبک
        └── index.html             # رابط کاربری وب داشبورد
```

---

## 📄 لایسنس
MIT
