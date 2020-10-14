import csv
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.admin import AdminSite

from .models import User, Account, Broker, Symbol, Order, Deal, Deposit, Withdraw


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


class Accounts(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'user', 'symbol', 'balance')
    actions = ["export_as_csv"]


class Brokers(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name',)
    actions = ["export_as_csv"]


class Symbols(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'commission', 'min_transaction', 'deals_commission')
    actions = ["export_as_csv"]


class Orders(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'limit_from', 'limit_to', 'rate', 'type', 'symbol', 'user', 'is_deleted', 'is_active', 'is_active')
    list_filter = ('type', 'symbol')
    actions = ["export_as_csv"]


class Deals(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'rate', 'status', 'rate', 'amount_crypto', 'amount_currency', 'commission', 'created_at', 'closed_at', 'buyer', 'seller', 'symbol')
    list_filter = ('status', 'symbol')
    actions = ["export_as_csv"]


class Deposits(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'tx_hash', 'created_at', 'confirmed_at', 'amount', 'symbol', 'user')
    list_filter = ('symbol', 'user')
    actions = ["export_as_csv"]


class Withdraws(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'tx_hash', 'address', 'created_at', 'confirmed_at', 'amount', 'symbol', 'user', 'commission_service', 'commission_blockchain')
    list_filter = ('symbol', 'user')
    actions = ["export_as_csv"]


admin_site.register(User, Users)
admin_site.register(Account, Accounts)
admin_site.register(Broker, Brokers)
admin_site.register(Symbol, Symbols)
admin_site.register(Order, Orders)
admin_site.register(Deal, Deals)
admin_site.register(Deposit, Deposits)
admin_site.register(Withdraw, Withdraws)
