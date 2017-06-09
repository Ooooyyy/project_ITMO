# -*- coding: utf-8 -*-
from selenium import webdriver
import csv
import json
import requests

class Bot:
    def __init__(self, url):
        self.driver = webdriver.Firefox()
        #self.get_call(call)
        #self.driver.implicitly_wait(10)
        self.get_urls(url)
        #self.get_page_data()
        

    def write_csv(self, data):
        with open('avito_m.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow( (data['header'],
                              data['price'],
                              data['location'],
                              data['phone']) )

    
    def get_urls(self, url):
        self.driver.get(url)
        urls = self.driver.find_elements_by_xpath('*//a[@class="item-link"]')
        for i in range(10):
            urls[i].click()
            self.driver.implicitly_wait(10000000000000)
            self.get_page_data()
            self.driver.back()
            urls = self.driver.find_elements_by_xpath('*//a[@class="item-link"]')
        self.driver.quit()   


    def get_call(self, call):
        self.driver.get('https://m.avito.ru/sankt-peterburg')
        call = self.driver.find_elements_by_tag_name('input')[2].send_keys(call)
        button = self.driver.find_element_by_xpath('//button[@class="control-self control-self-button button button-solid button-blue button-large"]')
        button.click()

    
    def get_page_data(self):
        #self.driver.get('https://m.avito.ru/sankt-peterburg/telefony/moschnyy_smartfon_htc_one_mini_2_16_rst_original_1040311785')
        header = self.driver.find_element_by_xpath('//header[@class="single-item-header b-with-padding"]').text
        
        price = self.driver.find_element_by_class_name('info-price').text
        
        location = self.driver.find_element_by_xpath('//span[@class="avito-address-text"]').text.split(',')[-1].strip()
        
        element = self.driver.find_elements_by_class_name("clearfix")
        button = element[1].find_element_by_tag_name("a")
        #self.driver.implicitly_wait(1000000000000000)
        button.click()
        #self.driver.implicitly_wait(1000000000000000)
        
        phone = button.find_element_by_xpath('//span[@class="button-text"]').text
        i = 0
        # while phone[0] != 8 and i < 3:
        #     phone = button.find_element_by_xpath('//span[@class="button-text"]').text
        #     i += 1
        if phone[0] != 8:
            phone = button.find_element_by_xpath('//span[@class="button-text"]').text
            if phone[0] != 8:
                phone = button.find_element_by_xpath('//span[@class="button-text"]').text

        phone = phone.replace(' ','')
        phone = phone.replace('-','')
        phone = "7" + phone[1:]

        if sms_sending == 1:
            send = send_sms(phone, text)
        data = {'header': header,
                'price': price,
                'location': location,
                'phone': phone}
        self.write_csv(data)




 
def send_sms(phones, text, total_price=1):
    login = 'Ooooyyy'       # Логин в smsc
    password = '2b5xtb'     # Пароль в smsc
    sender = 'SMSC.RU'    # Имя отправителя
    # Возможные ошибки
    errors = {
        1: 'Ошибка в параметрах.',
        2: 'Неверный логин или пароль.',
        3: 'Недостаточно средств на счете Клиента.',
        4: 'IP-адрес временно заблокирован из-за частых ошибок в запросах. Подробнее',
        5: 'Неверный формат даты.',
        6: 'Сообщение запрещено (по тексту или по имени отправителя).',
        7: 'Неверный формат номера телефона.',
        8: 'Сообщение на указанный номер не может быть доставлено.',
        9: 'Отправка более одного одинакового запроса на передачу SMS-сообщения либо более пяти одинаковых запросов на получение стоимости сообщения в течение минуты. '
    }
    # Отправка запроса
    url = "http://smsc.ru/sys/send.php?login=%s&psw=%s&phones=%s&mes=%s&cost=%d&sender=%s&fmt=3" % (login, password, phones, text, total_price, sender)
    answer = json.loads(requests.get(url).text)
    if 'error_code' in answer:
        # Возникла ошибка
        return errors[answer['error_code']]
    else:
        if total_price == 1:
            # Не отправлять, узнать только цену
            print('цена рассылки: %s' % (answer['cost']))
        else:
            # СМС отправлен, ответ сервера
            return answer
 
# # Рассылка на несколько номеров
# phones = ('711111111', '722222222', '7333333333333')
# text = 'текст для письма!'
# for number in phones:
#     send = send_sms(number, text)
#     if 'cnt' in send:
#         print 'На номер %s, сообщение отправлено успешно!' % number
#         time.sleep(30) # Засыпаем передачу на 30 сек - ограничение...
#     else:
#         print send
#         print 'Ошибка...'


if __name__ == '__main__':
    call = str(input('Введите поисковой запрос: '))
    url = "https://m.avito.ru/sankt-peterburg?p=1&bt=1&q={}".format(call)
    sms_sending = int(input('Введите 1 для смс рассылки: '))
    if sms_sending == 1:
        text = str(input('Введите текст сообщения: '))
    b = Bot(url)