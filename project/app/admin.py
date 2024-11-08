from django.contrib import admin
from django.utils.html import format_html
from . import models

@admin.register(models.Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 's3_file_link', 's3_text_link')
    list_display_links = ('id', 'name')

    def s3_file_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            models.Document.s3_file_link(obj.id),
            'Download File',
        )

    def s3_text_link(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            models.Document.s3_text_link(obj.id),
            'Download Text',
        )

    s3_file_link.short_description = 'File Link'
    s3_text_link.short_description = 'Text Link'
