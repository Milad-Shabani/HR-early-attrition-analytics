<div dir="rtl">

# تحلیل خروج زودهنگام کارکنان (Early Attrition Analytics)

این پروژه نرخ **خروج زودهنگام** را درست (با در نظر گرفتن ناقص‌بودن مشاهده‌ی استخدام‌های اخیر) محاسبه می‌کند و در پایان یک
**گزارش HTML مستقل و دوزبانه** (فارسی راست‌به‌چپ و انگلیسی) می‌سازد؛ بدون هیچ درخواست بیرونی.

**نمایش زنده:** <https://milad-shabani.github.io/early-attrition-analytics/> ·
[گزارش فارسی](docs/early_attrition_fa.html) · [English README](README.md)

> **داده‌ی ساختگی:** داده‌ی نمونه را [`synth.py`](src/attrition/synth.py) برای یک شرکت **فرضی** می‌سازد. هیچ داده‌ی واقعی،
> شرکت واقعی یا آزمون استخدامی واقعی در کار نیست و اندازه‌ی اثرها را خود مولد داده تعیین کرده است.

## چه می‌کند

1. **KPI:** نرخ خروج ۱۲ ماهه فقط روی کوهورت کامل (هر نفر ۱۲ ماه کامل دیده شده) با بازه اطمینان Wilson؛ نرخ خام هم برای نمایش سوگیری می‌آید.
2. **وضعیت کلی:** منحنی تجمعی Kaplan–Meier، دلایل خروج و سهم خروج اختیاری.
3. **مقایسه گروه‌ها:** نرخ و بازه اطمینان هر گروه؛ فقط وقتی رنگی می‌شود که بازه‌اش از نرخ کل جدا باشد.
4. **عوامل مرتبط:** رگرسیون Logistic با ترجمه به زبان ساده («برابر شانس خروج») و نمودار ستونی.
5. **Insights:** انباشت عوامل ریسک (۰، ۱، ۲ یا بیشتر).
6. **اقدام‌ها:** اولویت بر اساس «خروج اضافه»، شروع از کدام گروه‌ها، مسئول و هدف سناریویی.

## شروع سریع

```bash
git clone https://github.com/Milad-Shabani/early-attrition-analytics.git
cd early-attrition-analytics
pip install -e ".[dev]"
python -m attrition build      # data/synthetic_hires.csv و گزارش‌ها در docs/
python -m pytest -q
```

برای داده‌ی خودت: `python -m attrition build --csv my_hires.csv --obs-end 2026-06-30 --out my_reports` (ستون‌ها در [README انگلیسی](README.md#use-your-own-data)).

## ساختار

`src/attrition/` (داده، آمار، گزارش، ترجمه‌ها) · `tests/` · `docs/` (گزارش‌ها و [methodology.md](docs/methodology.md)) · `.github/` (CI و Pages) · `publish.sh` / `publish.bat`.

## مجوز

[MIT](LICENSE) © ۲۰۲۶ میلاد شعبانی

</div>
