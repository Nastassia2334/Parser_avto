import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
import json
import time
from headers import headers1

list_bmw = []


# отвечает за сбор информации со страницы
async def cars(session, page):
    url = "https://cars.av.by/bmw/x6"
    headers = headers1
    url_page = f"https://cars.av.by/filter?brands[0][brand]=8&brands[0][model]=1946&page={page}"
    # отправляем запрос на страницу
    async with session.get(url_page, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "lxml")
        cars_list = soup.find_all("div", class_="listing-item")
        for car in cars_list:
            name_car = car.find("a", class_="listing-item__link").text
            link_car = url + car.find("a", class_="listing-item__link").get("href")
            car_params_year = car.find("div", class_="listing-item__params").find("div").text.replace(' ', ' ')
            car_params_transmission = car.find("div", class_="listing-item__params").find_next().find_next().text.replace(' ', ' ')
            car_params_mileage = car.find("div", class_="listing-item__params").find_next().find_next().find_next()
            for mileage in car_params_mileage:
                mileage_encode = mileage.text.encode('ascii', errors='ignore')
                mileage_decode = mileage_encode.decode('UTF-8')
                car_params_mileage = str(mileage_decode) + ' км'
            price_rub = car.find("div", class_="listing-item__prices").find_next()
            for price in price_rub:
                price_encode = price.text.encode('ascii', errors='ignore')
                price_decode = price_encode.decode('UTF-8')
                price_rub = str(int(price_decode[:price_decode.index('.')])) + ' руб'
            price_usd = car.find("div", class_="listing-item__prices").find_next().find_next()
            for price in price_usd:
                price_encode = price.text.encode('ascii', errors='ignore')
                price_decode = price_encode.decode('UTF-8')
                price_usd = price_decode
            local = car.find("div", class_="listing-item__location").next_element.text
            try:
                description = car.find("div", class_="listing-item__message").string.replace('\n', '')
            except AttributeError:
                description = "описание отсутствует"
            date_ = car.find("div", class_="listing-item__date").next_element.text
            list_bmw.append(
                {
                    'название': name_car,
                    'ссылка': link_car,
                    'год выпуска': car_params_year,
                    'параметры': car_params_transmission,
                    'пробег': car_params_mileage,
                    'цена rub': price_rub,
                    'цена usb': price_usd,
                    'место нахождения': local,
                    'описание': description,
                    'дата размещения объявления': date_
                }
            )
        time.sleep(2)
    print(f'обработано {page} страниц')


# в асинхронной функции создаем список машин
async def list_creation():
    url = "https://cars.av.by/bmw/x6"
    headers = headers1
    list_cars = []
    # создаем клиент сессию которая позволяет повторно использовать открытое соединение
    async with aiohttp.ClientSession() as session:
        response = await session.get(url=url, headers=headers)

        # цикл по страницам сайта
        for page in range(1, 10):
            # создаем задачу с помощью Creat_task
            info_car = asyncio.create_task(cars(session, page))
            list_cars.append(info_car)

        # функция asyncio.gather позволяет рассматривать группу объектов,
        # допускающих ожидание, как один такой объект
        await asyncio.gather(*list_cars)


# выводим результат
def main():
    asyncio.run(list_creation())
    print(len(list_bmw))

    with open('dict_list_async.json', 'w', encoding='utf-8') as file:
        json.dump(list_bmw, file, indent=4, ensure_ascii=False)

    with open('bmw_x6_async.csv', 'w', encoding='utf-16') as file:
        writer_car = csv.writer(file)
        writer_car.writerow(
            ("название",
             'ссылка',
             'год выпуска',
             'параметры',
             'пробег',
             'цена',
             'цена usb',
             'место нахождения',
             'описание',
             'дата размещения объявления')
        )
    for car in list_bmw:
        with open('bmw_x6_async.csv', 'a', encoding='utf-16', newline='') as file:
            writer_car = csv.writer(file)
            writer_car.writerow(
                (car['название'],
                 car['ссылка'],
                 car['год выпуска'],
                 car['параметры'],
                 car['пробег'],
                 car['цена rub'],
                 car['цена usb'],
                 car['место нахождения'],
                 car['описание'],
                 car['дата размещения объявления'])
            )


if __name__ == '__main__':
    main()
