from django.db import connection
from datetime import datetime


def construir_where_clause(fecha_inicio, fecha_fin, product_id, user_id):
    where_clause = " WHERE 1=1"
    query_params = []

    if fecha_inicio:
        date_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        where_clause += " AND \"time\" >= %s AND year >= %s"
        query_params.extend([fecha_inicio, date_obj.year])

    if fecha_fin:
        date_obj = datetime.strptime(fecha_fin, "%Y-%m-%d")
        where_clause += " AND \"time\" <= %s AND year <= %s"
        query_params.extend([fecha_fin, date_obj.year])

    if product_id:
        where_clause += " AND \"productId\" = %s"
        query_params.append(product_id)

    if user_id:
        where_clause += " AND \"userId\" = %s"
        query_params.append(user_id)

    return where_clause, query_params


def ejecutar_consulta_simple(sql_query, params):
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        return cursor.fetchone()


def ejecutar_consulta(sql_query, params):
    with connection.cursor() as cursor:
        cursor.execute(sql_query, params)
        registros = cursor.fetchall()
        return [dict(zip([column[0] for column in cursor.description], row)) for row in registros]


def obtener_top_scores(fecha_inicio, fecha_fin, product_id, user_id, top_type="mejores"):
    order_by = "DESC" if top_type == "mejores" else "ASC"
    where_clause, params = construir_where_clause(fecha_inicio, fecha_fin, product_id, user_id)
    final_query = f"SELECT * FROM revies_movies.review_partitioned{where_clause} ORDER BY score {order_by} LIMIT 10"
    return ejecutar_consulta(final_query, params)


def obtener_primeros_200(fecha_inicio, fecha_fin, product_id, user_id):
    where_clause, params = construir_where_clause(fecha_inicio, fecha_fin, product_id, user_id)
    final_query = f"SELECT * FROM revies_movies.review_partitioned{where_clause} LIMIT 200"
    return ejecutar_consulta(final_query, params)


def calcular_max_min_avg_scores(fecha_inicio, fecha_fin, product_id, user_id):
    where_clause, params = construir_where_clause(fecha_inicio, fecha_fin, product_id, user_id)
    final_query = f"SELECT MAX(score), MIN(score), AVG(score) FROM revies_movies.review_partitioned{where_clause}"
    return ejecutar_consulta_simple(final_query, params)


def calcular_cantidad_usuarios(fecha_inicio, fecha_fin, product_id, user_id):
    if user_id:
        return 1
    else:
        where_clause, params = construir_where_clause(fecha_inicio, fecha_fin, product_id, None)
        final_query = f"SELECT COUNT(DISTINCT \"userId\") FROM revies_movies.review_partitioned{where_clause}"
        return ejecutar_consulta_simple(final_query, params)[0]


def visualization(fecha_inicio, fecha_fin, user_id, product_id):

    where_clause, params = construir_where_clause(fecha_inicio, fecha_fin, product_id, user_id)
    final_query = f"""SELECT
            DATE("time") as fecha,
            AVG(score) as promedio_score,
            AVG(CAST(SPLIT_PART(helpfulness, '/', 1) AS FLOAT) / NULLIF(CAST(SPLIT_PART(helpfulness, '/', 2) AS FLOAT), 0)) as promedio_helpfulness
        FROM
            revies_movies.review_partitioned
            {where_clause} 
            GROUP BY DATE("time") """
    return ejecutar_consulta(final_query, params)
