from django.contrib import admin
from .models import Profile, User, Payment

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')  # whatever
    list_filter = ('is_master',)
    search_fields = ('username',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet_address', 'telegram_id', )
    search_fields = ('user', 'wallet_address')

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Payment)