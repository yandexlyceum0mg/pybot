from requests import get
from pygame.image import load, save
from pygame.transform import scale
from os import remove
from cfg import g_api_key, w_api_key


def svg_to_png(img: bytes):
    f = open('tmp/svg.svg', 'wb')
    f.write(img)
    f.close()
    save(scale(load('tmp/svg.svg'), (72, 72)),
         'tmp/png.png')  # преобразовать в больший размер нужно, чтобы в телеге было не совсем размыто
    f = open('tmp/png.png', 'rb')
    img = f.read()
    f.close()
    remove('tmp/svg.svg')
    remove('tmp/png.png')
    return img


async def weather(text, outtext, outphoto, retry_send):
    res = []
    res.append(text)
    res_geo = get('https://geocode-maps.yandex.ru/1.x',
                  params={'geocode': text, 'apikey': g_api_key, 'format': 'json'}).json()
    coords = res_geo['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split()
    res_weather = get('https://api.weather.yandex.ru/v2/forecast', params={'lat': coords[1], 'lon': coords[0]},
                      headers={'X-Yandex-API-Key': w_api_key}).json()
    c = 0
    while True:
        try:
            c += 1
            await outphoto(svg_to_png(
                get(f'https://yastatic.net/weather/i/icons/funky/dark/{res_weather["fact"]["icon"]}.svg').content))
        except:
            if c == retry_send:
                raise
            break
        else:
            break

    res.append(f'Температура: {res_weather["fact"]["temp"]}°C')
    res.append(f'Ощущается как: {res_weather["fact"]["feels_like"]}°C')
    conditions = 'clear — ясно.partly-cloudy — малооблачно.cloudy — облачно с прояснениями.overcast — пасмурно.dri' \
                 'zzle — морось.light-rain — небольшой дождь.rain — дождь.moderate-rain — умеренно сильный дождь.heav' \
                 'y-rain — сильный дождь.continuous-heavy-rain — длительный сильный дождь.showers — ливень.wet-snow ' \
                 '— дождь со снегом.light-snow — небольшой снег.snow — снег.snow-showers — снегопад.hail — град.thun' \
                 'derstorm — гроза.thunderstorm-with-rain — дождь с грозой.thunderstorm-with-hail — гроза с градом'
    conditions = {i.split(' — ')[0]: i.split(' — ')[1] for i in conditions.split('.')}
    res.append(conditions[res_weather['fact']['condition']])
    wnd = {'nw': 'северо-западный', 'n': 'северный', 'ne': 'северо-восточный', 'e': 'восточный', 'se': 'юго-восточный',
           's': 'южный', 'sw': 'юго-западный', 'w': 'западный', 'c': 'отсутствует'}
    w = wnd[res_weather["fact"]["wind_dir"]]
    if w != 'штиль':
        w = w.capitalize() + ' ветер' + f', {res_weather["fact"]["wind_speed"]}м/с'
        res.append(w)
    else:
        res.append('штиль (ветер отсутствует)')

    res.append(f'Порывы ветра до: {res_weather["fact"]["wind_gust"]}м/с')
    res.append(f'Влажность: {res_weather["fact"]["humidity"]}%')

    prec = {i.split(' — ')[0]: i.split(' — ')[1] for i in
            '0 — отсутствуют.1 — дождь.2 — дождь со снегом.3 — снег.4 — град'.split('.')}
    res.append(f'Осадки: {prec[str(res_weather["fact"]["prec_type"])]}')
    cns = {i.split(' — ')[0]: i.split(' — ')[1] for i in
           '0 — ясно . 0.25 — малооблачно . 0.5 — облачно с прояснениями . 0.75 —' \
           ' облачно с прояснениями . 1 — пасмурно'.split(
               ' . ')}
    res.append(f'Облачость: {cns[str(res_weather["fact"]["cloudness"])]}')
    res.append(
        f'Атмосферное давление: {res_weather["fact"]["pressure_mm"]} мм.рт'
        f'.ст. ({res_weather["fact"]["pressure_pa"]}Па)')
    if 'phenom' in res_weather["fact"].keys():
        phn = {i.split(' — ')[0]: i.split(' — ')[1] for i in
               'fog — туман.mist — дымка.smoke — смог.dust — пыль.dust-suspension — пылевая взвесь.' \
               'duststorm — пыльная буря.thunderstorm-with-duststorm — пыльная буря с грозой.drifting-sno' \
               'w — слабая метель.blowing-snow — метель.ice-pellets — ледяная крупа.freezing-rain — ледяной дож' \
               'дь.tornado — торнадо.volcanic-ash — вулканический пепел'.split(
                   '.')}
        res.append(f'{res_weather["fact"]["phenom_condition"]}')
        c = 0
        while True:
            try:
                c += 1
                await outphoto(svg_to_png(
                    get(f'https://yastatic.net/weather/i/icons/funky/dark/{res_weather["fact"]["phenom_icon"]}.svg').content))
            except:
                if c == retry_send:
                    raise
                break
            else:
                break
    c = 0
    while True:
        try:
            c += 1
            await outtext('\n'.join(res))
        except:
            if c == retry_send:
                raise
            break
        else:
            break
