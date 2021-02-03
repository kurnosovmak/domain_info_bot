import config
import logging

import whois

import datetime

import OpenSSL
import ssl, socket

from aiogram import Bot, Dispatcher, executor, types



# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)


# Команда активации подписки
@dp.message_handler()
async def main(message: types.Message):
    createddata = getInfo(message.text)
    if(not createddata):
        return await message.answer('This domain('+message.text+') is not using')

    if (isinstance(createddata.creation_date, list)):
        creation_date = createddata.creation_date[0]
    else:
        creation_date = createddata.creation_date

    if (isinstance(createddata.expiration_date, list)):
        expiration_days = createddata.expiration_date[0] - datetime.datetime.now()
    else:
        expiration_days = createddata.expiration_date - datetime.datetime.now()

    sslser = get_certificate(message.text)
    if (sslser != False):
        sslser = (sslser - datetime.datetime.now())

    rezult = res(message.text,creation_date,expiration_days,sslser)

    await message.answer(rezult)



def res(domain,creation_date,expiration_days,sslser):
    # expiration_days = createddata.expiration_date[0]-datetime.datetime.now()


    answer = 'Домен - ' + domain + '\n' \
             + 'Дата создания - ' + str(creation_date) + '\n' \
             + 'Дней до продления - ' + str(expiration_days.days) + '\n'
    if (sslser != False):
        answer += 'Наличие SSL сертификата - ДА\n' \
                  + 'Дней до продления SSL сертификата - ' + str(sslser.days) + '\n'
    else:
        answer += 'Наличие SSL сертификата - НЕТ\n'
    return answer



def getInfo(domain):
    try:
        w = whois.whois(domain)
        # print('Hello World')
        # print(domain)

    except Exception:
        # print('Hello World')
        return False

    else:
        # print(w)
        if(w.domain_name):
            return (w)
        return False


def get_certificate(host, port=443):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=host,
        )
        # 3 second timeout because Lambda has runtime limitations
        conn.settimeout(3.0)
        conn.connect((host, port))
        ssl_info = conn.getpeercert()

        # parse the str+ing from the certificate into a Python datetime object
        res = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
        # print('\n  ' + str(res) + '  \n')
        return res
    except ssl.SSLCertVerificationError:
        return False



# запускаем лонг поллинг
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)