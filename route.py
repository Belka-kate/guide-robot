#for launching u need to call function get_route_details(api, start_point, last_point)
# the result is str which is suitable for arduino code

import requests
from math import sqrt
import math

def get_route_details(api_key, point_a, point_b):
    # Форматирование координат для waypoints
    waypoints = f"{point_a[1]},{point_a[0]}|{point_b[1]},{point_b[0]}"

    # URL для получения маршрута
    url = f'https://api.routing.yandex.net/v2/route?waypoints={waypoints}&apikey={api_key}&mode=walking'

    try:
        # Отправка GET-запроса
        response = requests.get(url)
        response.raise_for_status()  # Поднимет исключение для ошибок HTTP

        # Обработка успешного ответа
        data = response.json()
        print(data)
        if 'route' in data and 'legs' in data['route'] and len(data['route']['legs']) > 0:
            legs = data['route']['legs']
            polyline_points = []
            for leg in legs:
                if 'steps' in leg:
                    for step in leg['steps']:
                        if 'polyline' in step and 'points' in step['polyline']:
                            polyline_points.extend(step['polyline']['points'])
            route = construct_route(polyline_points)
            return route
        else:
            print("Маршрут не найден.")


    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP ошибка: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Ошибка запроса: {req_err}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def calculate_distance(polyline_points):
    length_route = []
    for i_point_1 in range(0, len(polyline_points)-1):
        lat1, lon1 = math.radians(polyline_points[i_point_1][0]), math.radians(polyline_points[i_point_1][1])
        lat2, lon2 = math.radians(polyline_points[i_point_1+1][0]), math.radians(polyline_points[i_point_1+1][1])
        R = 6371000

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        distance = R * c * 1000
        length_route.append('%.2f'%distance)
    return length_route

def calculate_turn_angle(point1, point2, point3):
    AB = (point2[1] - point1[1], point2[0] - point1[0])  # (lon, lat)
    BC = (point3[1] - point2[1], point3[0] - point2[0])  # (lon, lat)
    dot_product = AB[0] * BC[0] + AB[1] * BC[1]

    length_AB = math.sqrt(AB[0] ** 2 + AB[1] ** 2)
    length_BC = math.sqrt(BC[0] ** 2 + BC[1] ** 2)
    cos_theta = dot_product / (length_AB * length_BC)
    angle_rad = math.acos(cos_theta)

    angle_deg = math.degrees(angle_rad)
    return '%.2f'%angle_deg

def construct_route(polyline_points):
    length_route = calculate_distance(polyline_points)
    route = "0 " + str(length_route[0]) + " "
    for i in range(1, len(polyline_points)-1):
        angel = calculate_turn_angle(polyline_points[i-1], polyline_points[i], polyline_points[i+1])
        route += str(angel) + " " + str(length_route[i]) + " "
    route += "0"
    return route
api_key = 'e8ba2603-9003-491a-82b9-726a443d1b7e'  # Замените на ваш реальный API-ключ
point_a = (56.828345, 60.647565)  # Координаты первой точки (например, Москва)
point_b = (56.817326, 60.639254)  # Координаты второй точки (например, другая точка в Москве)

route = get_route_details(api_key, point_a, point_b)
print(route)