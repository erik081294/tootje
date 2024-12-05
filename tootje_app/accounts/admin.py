from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, PaymentHistory

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_car_owner')
    
    def get_is_car_owner(self, obj):
        return obj.profile.is_car_owner
    get_is_car_owner.short_description = 'Car Owner'
    get_is_car_owner.boolean = True

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']
    search_fields = ['user__username']

class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'date']
    list_filter = ['user', 'date']
    search_fields = ['user__username', 'description']

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PaymentHistory, PaymentHistoryAdmin)
