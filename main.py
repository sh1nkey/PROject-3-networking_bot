# -----------------------------------------------------------
# the main program for the bot to work
#
# 2022 Alexey Kudelko, Moscow, Russia
#
# email: flexivanov237@gmail.com
# -----------------------------------------------------------


import os
import pathlib
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from config import vk_token, reminder_txt_dir
from func_container import create_people, change_data_table, show_table, create_table, create_timers, create_dft, Reminder

vk_session = vk_api.VkApi(token=vk_token)
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)


def sending_message_func(id, text):
    vk_session.method("messages.send", {"user_id": id, "message": text, "random_id": 0})


change_list = []
tne = ''
running = 0

while 1:
    try:
        for event in longpool.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg = event.text.lower()
                    id = event.user_id
                    if msg == "привет":
                        sending_message_func(id,
                                             "Давай сразу к делу. Инструкция:\n (Команды писать без квадратных скобочек)\n\n-создать "
                                             "таблицу, "
                                             "в которой будут размещаться данные:\n[!создатьтаблицу]\n\n"
                                             "-чтобы посмотреть содержание таблицы, надо ввести ее название, которое состоит из "
                                             "8-ми символов: [idsmHkPk]\n\n-чтобы добавить человека, надо написать эту команду, "
                                             "например: [создать ddldfdls Иван_Иванович 2000-01-13 Село_Иваново корововед "
                                             "увлекается_аниме 14] \ \nИз ограничений разве что строгое расположение пробелов: "
                                             "их ставить только между категориями. Внутри категории использовать  \ нижнее "
                                             "подчеркивание (_). Вот кстати категории: [номер имя_фамилия дата_рождения город "
                                             "специальность увлечения срок напоминания]\n\n-Чтобы задать ячейку, в которой вам "
                                             "нужно что-то изменить, пишем: [изменить название_таблицы категория "
                                             "порядковый_номер_человека].' \ 'Например:[изменить qwerTyui Имя 2]\n\nЧтобы "
                                             "поменять данные в этой ячейке пишем: [на то_на_что_меняем]. Например: [на "
                                             "Андрей]' \ '\n\n-чтобы заставить программу напоминать вам о том, чтобы время от "
                                             "времени писать определенным людям, то пишем: [отсчет "
                                             "название_таблички]. Например: [отсчет qwertyUi]\nНе беспокойтесь, если вы "
                                             "обновите свою таблицу, то и список тоже обновится :) ")
                    elif msg == "!создатьтаблицу":
                        sending_message_func(id, "таблица готова!\n ее имя:" + create_table())
                    elif len(msg) == 8:
                        sending_message_func(id, "Вот содержание таблицы {}\n:".format(msg))
                        full = list(show_table(msg))
                        sd = ''
                        for _ in range(0, len(full)):
                            n = list(show_table(msg)[_].values())
                            print(n)
                            sd += '\n' + "[" + str(n[0]) + ']' + " " + "[" + str(n[1]) + ']' + " " + "[" + str(
                                n[2]) + ']' + " " + "[" + str(n[3]) + ']' + \
                                  " " + "[" + str(n[4]) + ']' + " " + "[" + str(n[5]) + ']' + " " + "[" + str(n[6]) + ']' + '\n'
                        sending_message_func(id, sd)


                    elif msg[0] == 'и':
                        table_name = msg[9:17]
                        tne = msg[9:17]
                        change_list.append(table_name)
                        idshnik = 0
                        what_change = msg[18:-2]
                        change_list.append(what_change)
                        if msg[-2] == ' ':
                            idshnik = int(msg[-1])
                        else:
                            idshnik = int(str(msg[-2] + '' + msg[-1]))
                        change_list.append(idshnik)
                        sending_message_func(id, "Хорошо, на что вы хотите изменить? ")
                        if len(change_list) > 3:
                            change_list.clear()

                    elif msg[0:2] == "на":
                        to_what = msg[3:]
                        change_data_table(change_list[0], change_list[1], change_list[2], to_what)
                        sending_message_func(id, "Изменено успешно! ")
                        change_list.clear()

                        checking_path = pathlib.Path(reminder_txt_dir + '/{}.txt'.format('Napominalka-' + str(id)))
                        if os.path.exists(checking_path):
                            running = 1

                    elif msg[0] == 'о' or running == 1:  # создать и запустить отсчет, отсчет обновиться автоматом, если таблицу
                        # изменить
                        tname = msg[7:]
                        if running == 1:
                            tname = tne
                        retu = create_dft(tname)
                        par_3 = create_timers(retu[0], retu[1])
                        print('PAR_3', par_3)
                        rem = Reminder(par_3[0], par_3[1], par_3[2], str(id))
                        rem.append_totxt()
                        if running == 0:
                            sending_message_func(id, 'список создан!')
                        elif running == 1:
                            running = 0

                    elif msg[0] == 'с':  # с - создать, добавляет человека в таблицу
                        space_list = []
                        d = -1
                        for i in msg:
                            d += 1
                            if i == " ":
                                space_list.append(d)
                            if len(space_list) == 7:
                                break
                        table_name = msg[space_list[0]:space_list[1]]
                        name_surname = msg[space_list[1]:space_list[2]]
                        date = msg[space_list[2]:space_list[3]]
                        place = msg[space_list[3]:space_list[4]]
                        occupation = msg[space_list[4]:space_list[5]]
                        hobby = msg[space_list[5]:space_list[6]]
                        if msg[-2] == ' ':
                            reminder_term = msg[-1]
                        else:
                            reminder_term = int(str(msg[-2] + '' + msg[-1]))
                        print('dannie:', table_name, name_surname, date, place, occupation, hobby, reminder_term)
                        create_people(table_name, name_surname, date, place, occupation, hobby, reminder_term)

                        sending_message_func(id, "Готово! ")

                    # elif msg[0] == 'у':
                    #     tname = msg[8:16]
                    #     if msg[-2] == ' ':
                    #         del_name = int(msg[-1])
                    #     else:
                    #         del_name = int(msg[-2] + '' + msg[-1])
                    #     print(type(del_name))
                    #     print(del_name)
                    #     delete_people(tname, del_name)
                    #     sending_message_func(id, "человек удален ")
                    '''
                    функция
                    на
                    доработке
                    '''

    except:
        pass
