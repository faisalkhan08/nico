# from django.contrib import admin
# from django.http import HttpResponse
#
# from accounts.models import Users
# from django.urls import path, include
# import csv
# from django.shortcuts import render, redirect
# from django import forms
# # Register your models here.
#
#
# class ExportCsvMixin:
#     def export_as_csv(self, request, queryset):
#         meta = self.model._meta
#         field_names = [field.name for field in meta.fields]
#         response = HttpResponse(content_type='text/csv')
#         response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
#         writer = csv.writer(response)
#         writer.writerow(field_names)
#         for obj in queryset:
#             row = writer.writerow([getattr(obj, field) for field in field_names])
#         return response
#     export_as_csv.short_description = "Export Selected"
#
#
# class CsvImportForm(forms.Form):
#     csv_file = forms.FileField()
#
#
# @admin.register(Users)
# class HeroAdmin(admin.ModelAdmin, ExportCsvMixin):
#     change_list_template = "change_list.html"
#     search_fields = ('firstname', 'email')
#
#     def get_urls(self):
#         urls = super().get_urls()
#         my_urls = [
#             path('import-csv/', self.import_csv),
#         ]
#         return my_urls + urls
#
#     def import_csv(self, request):
#         if request.method == "POST":
#             csv_file = request.FILES["csv_file"]
#             reader = csv.reader(csv_file)
#             # Create Hero objects from passed in data
#             # ...
#             self.message_user(request, "Your csv file has been imported")
#             return redirect("..")
#         form = CsvImportForm()
#         payload = {"form": form}
#         return render(
#             request, "csv_form.html", payload
#         )
#
#
#
#
