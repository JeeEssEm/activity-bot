from dtos import StreamType

LEGEND = f'''
├Лекция: {StreamType.lecture.value}
├Семинар: {StreamType.seminar.value}
├Практические занятия: {StreamType.practice.value}
╰Научно-исследовательский семинар: {StreamType.science_seminar.value}
'''

NAVIGATOR = (f'🗺️Навигатор по типам:{LEGEND}\n'
             f'📚<b>Твои дисциплины для отслеживания</b>')

GOOD_STICKERS = [
    'CAACAgIAAxkBAAEOXZNoC9J_LBntRUJ8lAacC2UlUW3r6gACUkAAAiIPsEhMkRJv6qSvbzYE',  # супер гуд
    'CAACAgIAAxkBAAEOXZ1oC9LhbFx5Pay9a_DRg_z_yfUNeQAC5jAAAvudaEp_11QAAZfgDgY2BA',  # хорош
    'CAACAgIAAxkBAAEOXZ9oC9L0bZfftW4Jgsh4WoPIaHQuuwACxDIAAq1PaUp-vbvj-AHpSjYE',  # хорош
    'CAACAgIAAxkBAAEOXaFoC9MEX6con4z5hnPgR3RYRYG-GgAC_TgAAmh6aEpwXUUOOmlrbDYE',  # хорош
    'CAACAgIAAxkBAAEOXaNoC9Md1fbfRJx_PDiGVaM74-15jQAClC4AApDlaUpgW0z6Xopa6zYE'  # хорош
]

BAD_STICKERS = [
    'CAACAgIAAxkBAAEOXZVoC9KTm7FGTpfoaBLVpFS5DJlKoAAC1zoAAj16uUhH1_o1cmKVITYE',  # это печально
    'CAACAgIAAxkBAAEOXZdoC9Kj0kGXWg9vuY28T4VA-T2x4gAC3UoAAm0KGUgXMpZ0zcWjEzYE',  # нихуя
    'CAACAgIAAxkBAAEOXZloC9K4vMfNGYtUDzN0q0k2XGpXQgACRUUAAgW2GUh7XyI9OgvjwjYE',  # все мы виноваты

]

NEUTRAL_STICKERS = [
    'CAACAgIAAxkBAAEOXZtoC9LNgSgJR_J6mJ07DhEYzuP2ugACimwAApMkiUlpH5TXuFYgmzYE',  # не рыпаемся
    'CAACAgIAAxkBAAEOXadoC9N4MriUVrjy5CI7iVMGiz8WZAACQW8AAr1eiUkT2YeCvEIPvjYE',  # копим элик
]
