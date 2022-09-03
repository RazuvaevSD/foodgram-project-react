import io

from django.db import IntegrityError
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response


def add_object(serializer, data, context):
    """Добавление объекта."""
    try:
        serializer = serializer(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
    except IntegrityError as ie:
        return Response({'errors': f'{ie}'},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'errors': f'{e}'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def del_object(model, filters):
    """Удаление объекта."""
    obj = get_object_or_404(model, **filters)
    try:
        obj.delete()
    except IntegrityError as ie:
        return Response({'errors': f'{ie}'},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'errors': f'{e}'},
                        status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_204_NO_CONTENT)


def generate_pdf_shopping_cart(queryset):
    """Генерация файла с ингредиентами."""
    buffer = io.BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
    page.setFont('FreeSans', 12)
    # задаем позицию заголовка от левого нижнего угла
    position_y = 800
    position_x = 250
    page.drawString(position_x, position_y, 'Список покупок.')
    if not queryset:
        position_y -= 100  # отступаем от заголовка
        page.drawString(position_x, position_y,
                        'Нет ингредиентов для покупок!')
    else:
        # задаем координаты для первой строки списка
        position_x = 50  # на вскидуку отступаем от края листа
        position_y -= 30  # отступаем от заголовка
        for ingredient in queryset:
            position_y -= 15  # отступаем от предыдущей строки
            page.drawString(position_x, position_y,
                            f'* {ingredient["name"]}: '
                            f'{ingredient["amount"]}'
                            f'{ingredient["measure"]}')
    page.showPage()
    page.save()
    buffer.seek(0)
    return buffer
