from django.contrib import admin


class IngredientFilterAdmin(admin.SimpleListFilter):
    title = 'Ингредиенты'
    parameter_name = 'ингредиенты_категории'

    def lookups(self, request, model_admin):
        pattern = 'абвгдеёжзийклмнопрстуфхцчшщэюя'
        return [(i, i) for i in pattern]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(name__startswith=self.value())
        return queryset
