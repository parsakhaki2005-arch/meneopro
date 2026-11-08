from django import forms
from menus.models import MenuCategory, MenuItem

PERSIAN_LABELS = {
    "name": "نام",
    "description": "توضیحات",
    "image": "تصویر",
    "is_active": "فعال بودن",
    "sort_order": "ترتیب نمایش",
    "category": "دستهبندی",
    "ingredients": "مواد تشکیلدهنده",
    "price": "قیمت",
    "discount_price": "قیمت با تخفیف",
    "is_available": "موجود برای سفارش",
    "is_featured": "نمایش بهعنوان پیشنهاد ویه",
    "prep_time_minutes": "زمان آمادهسازی (دقیقه)",
    "prep_time": "زمان آمادهسازی",
    "calories": "کالری",
    "currency": "واحد پول",
    "primary_color": "رنگ اصلی منو",
    "show_prices": "نمایش قیمتها",
    "show_unavailable_items": "نمایش محصولات ناموجود",
    "allow_online_orders": "فعال بودن سفارش آنلاین",
}

HELP_TEXTS = {
    "ingredients": "مواد تشکیلدهنده را بهصورت متن ساده وارد کنید. در صورت استفاده از JSON ساختار معتبر باشد.",
    "sort_order": "عدد کمتر باعث نمایش زودتر در منو میشود.",
    "discount_price": "در صورت نداشتن تخفیف این فیلد را خالی بگذارید.",
    "image": "تصویر واضح و باکیفیت انتخاب کنید.",
}

def style_form_fields(form):
    for name, field in form.fields.items():
        field.label = PERSIAN_LABELS.get(name, field.label or name)
        field.help_text = HELP_TEXTS.get(name, field.help_text or "")

        widget = field.widget
        css = "form-control"
        if isinstance(widget, forms.CheckboxInput):
            css = "form-check-input"
        elif isinstance(widget, forms.Select):
            css = "form-select"

        widget.attrs["class"] = (widget.attrs.get("class", "") + " " + css).strip()
        widget.attrs.setdefault("dir", "rtl")

        if isinstance(widget, forms.Textarea):
            widget.attrs.setdefault("rows", 4)
            widget.attrs.setdefault("placeholder", "توضیحات را وارد کنید...")

        if isinstance(widget, forms.FileInput):
            widget.attrs["accept"] = "image/*"

class CategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = [
            name for name in (
                "name", "description", "image", "is_active", "sort_order"
            )
            if name in [f.name for f in MenuCategory._meta.fields]
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_form_fields(self)

class ItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = [
            name for name in (
                "category", "name", "description", "ingredients",
                "price", "discount_price", "image", "is_available",
                "is_featured", "is_active", "prep_time_minutes",
                "prep_time", "calories", "sort_order"
            )
            if name in [f.name for f in MenuItem._meta.fields]
        ]

    def __init__(self, *args, restaurant=None, **kwargs):
        super().__init__(*args, **kwargs)

        if restaurant and "category" in self.fields:
            self.fields["category"].queryset = MenuCategory.objects.filter(
                restaurant=restaurant
            )

        style_form_fields(self)
