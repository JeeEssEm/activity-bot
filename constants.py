from dtos import StreamType

LEGEND = f'''
├Лекция: {StreamType.lecture.value}
├Семинар: {StreamType.seminar.value}
├Практические занятия: {StreamType.practice.value}
╰Научно-исследовательский семинар: {StreamType.science_seminar.value}
'''

NAVIGATOR = (f'🗺️Навигатор по типам:{LEGEND}\n'
             f'📚<b>Твои дисциплины для отслеживания</b>')
