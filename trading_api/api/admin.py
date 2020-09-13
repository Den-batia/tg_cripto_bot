import csv
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import User, Account


class MyAdminSite(AdminSite):
    site_header = 'Админ страница'


admin_site = MyAdminSite(name='Админ')


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Экспортировать"


class Users(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'telegram_id', 'nickname', 'is_admin', 'is_verify')
    actions = ["export_as_csv"]


admin_site.register(User, Users)
