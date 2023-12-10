from django.http import JsonResponse
from django.views.generic import TemplateView

from movies.utils import *


# Create your views here.

class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def autocomplete(request, model):
    if 'term' in request.GET:
        term = request.GET.get('term').upper()
        if model == 'user':
            field_name = 'userId'
            table_name = 'user'
        elif model == 'movie':
            field_name = 'productId'
            table_name = 'movie'
        else:
            return JsonResponse([])

        with connection.cursor() as cursor:
            cursor.execute(f'SELECT "{field_name}" FROM revies_movies.{table_name} WHERE "{field_name}" LIKE %s',
                           [f'{term}%'])
            result = cursor.fetchall()
        suggestions = [item[0] for item in result][:10]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([])



def consultar_registros(request):
    try:
        fecha_inicio = request.POST.get("fechaInicio", "")
        fecha_fin = request.POST.get("fechaFin", "")
        product_id = request.POST.get("pelicula", "")
        user_id = request.POST.get("usuario", "")

        top_10_mejores = obtener_top_scores(fecha_inicio, fecha_fin, product_id, user_id, "mejores")
        top_10_peores = obtener_top_scores(fecha_inicio, fecha_fin, product_id, user_id, "peores")
        primeros_200 = obtener_primeros_200(fecha_inicio, fecha_fin, product_id, user_id)
        max_min_avg_scores = calcular_max_min_avg_scores(fecha_inicio, fecha_fin, product_id, user_id)
        cantidad_usuarios = calcular_cantidad_usuarios(fecha_inicio, fecha_fin, product_id, user_id)
        visualizaciones = visualization(fecha_inicio, fecha_fin, product_id, user_id)
        return JsonResponse({
            "top_10_mejores": top_10_mejores,
            "top_10_peores": top_10_peores,
            "primeros_200": primeros_200,
            "max_min_avg_scores": max_min_avg_scores,
            "cantidad_usuarios": cantidad_usuarios,
            "visualizaciones": visualizaciones
        })

    except Exception as error:
        return JsonResponse({"error": str(error)})
