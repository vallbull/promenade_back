import csv
from test import get_dist
import time
from geopy.distance import geodesic
from geopy.point import Point
import requests

API_KEY = '9fe10d95-b359-4cff-b6c4-d1c47b8e3744'
d = {}


def get_coords(address):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={API_KEY}&geocode={address}&format=json"
    response = requests.get(url).json()
    res = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()
    res = float(res[0]), float(res[1])
    return res


def get_dist(address1, address2):
    # координаты точек
    if address1 in d:
        point1 = d[address1]
    else:
        point1 = get_coords(address1)
        d[address1] = point1
    time.sleep(0.1)
    if address2 in d:
        point2 = d[address2]
    else:
        point2 = get_coords(address2)
        d[address2] = point2

    # расчет расстояния между точками
    distance = geodesic(point1, point2).meters
    return distance


addresses = [0]

with open('addresses.txt', 'r') as file:
    # Читаем строки из файла построчно
    for line in file:
        addresses.append(line.strip())

routes = []

for a1 in addresses:
    pre_routes = []
    for a2 in addresses:
        if a1 == 0 and a2 != 0:
            pre_routes.append("Краснодар, " + str(a2))
        elif a2 == 0 and a1 != 0:
            pre_routes.append("Краснодар, " + str(a1))
        else:
            pre_routes.append(0)
    routes.append(pre_routes)

for i in range(1, len(addresses)):
    for j in range(1, len(addresses)):
        if j > i:
            try:
                dist = get_dist(routes[0][j], routes[i][0])
                routes[i][j] = dist
                routes[j][i] = dist
            except:
                print("err", i, j)
        else:
            continue


filename = 'output.csv'
with open(filename, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=';')
    csvwriter.writerows(routes)

print(f'Массив успешно записан в файл {filename}')
