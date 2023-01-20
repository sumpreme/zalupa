# -*- coding: utf-8 -*-
import time
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import telebot
from telebot import types
import pymysql
from threading import Thread

# ------------------ config ----------------------------
host = "31.31.196.38"
user = "u1721556_admin"
password = "Lapik2022."
bd_name = "u1721556_telegrambot"

token = '5884481081:AAEXlp06j9K6Rq0r_HkuX0PL89Hwac52MjI'
bot = telebot.TeleBot(token)
# -------------------------------------------------------

urlList = ['https://yaponomaniya.com/assorty', 'https://yaponomaniya.com/kombo', 'https://yaponomaniya.com/rolly/gorjachie_rolly', 'https://yaponomaniya.com/pitstsy']
productListMore = []*len(urlList)

def ThreadBot():
    productFocusId = 0
    productIndex = 0
    orderAddress = ''
    orderPhone = ''
    productsList = ''
    @bot.message_handler(commands=['start'])
    def start_message(message):
      photo = open('img1.jpg', 'rb')
      markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
      btn1 = types.KeyboardButton("🍕🍟Сделать заказ🍰🍣")
      btn2 = types.KeyboardButton("🛒Корзина🛒")
      btn3 = types.KeyboardButton("❗️Информация❗️")
      btn4 = types.KeyboardButton("☎️Контакты☎️")
      markup.add(btn1, btn2, btn3, btn4)
      bot.send_message(message.chat.id,"<strong>🍕🍰🍣Привет🍣🍰🍕</strong>", reply_markup=markup, parse_mode='html')
      bot.send_message(message.chat.id,"<strong>🍕Хотите заказать роллы в Кирове?🍕</strong> \n Ассортимент на любой вкус. Япономания угодит вкусу даже самого взыскательного гурмана.", parse_mode='html')
      bot.send_photo(message.chat.id, photo)
      try:
        connection = pymysql.connect(
            host=host,
            port=3306,
            user=user,
            password=password,
            database=bd_name,
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `users` WHERE `id` = '{message.chat.id}'")
                result1 = cursor.fetchall()
                if result1 == ():
                  with connection.cursor() as cursor:
                      cursor.execute("INSERT INTO `users` (`id`, `name`, `addres`, `phone`) VALUES (%s,%s,%s,%s)",
                                  (message.chat.id, message.from_user.first_name, '', ''))
                      connection.commit()
        finally:
            connection.close()
      except Exception as ex:
        print(ex)

    def CheckPhoneAddres(message):
        try:
          connection = pymysql.connect(
              host=host,
              port=3306,
              user=user,
              password=password,
              database=bd_name,
          )
          try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `users` WHERE `id` = '{message.chat.id}'")
                phAd = cursor.fetchone()
                if phAd[3] == "":
                    sendPhone(message)
                else:
                    bot.send_message(message.chat.id, "Ваша заявка успешно отправлена, мененджер перезвонить вам в течении 5 минут по номеру: " + phAd[3], parse_mode='html')
                    DeleteCart(message)

          finally:
              connection.close()
        except Exception as ex:
            print(ex)

    def OpenCart(message):
        try:
          connection = pymysql.connect(
              host=host,
              port=3306,
              user=user,
              password=password,
              database=bd_name,
          )
          try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT `id`, `productId`, `name`, `price`, `qty` FROM `cart` WHERE `userId` = '{message.chat.id}'")
                carts = cursor.fetchall()
                if carts == ():
                    bot.send_message(message.chat.id, "Корзина пуста")
                    return
                msg = ""
                total = 0
                for cart in carts:
                    msg += f"{cart[2]} ({cart[3]}руб.) - {cart[4]}шт. - {cart[3] * cart[4]}руб.\n"
                    total += cart[3] * cart[4]
                global productsList
                productsList = msg
                msg += f"<b>Итого: {total}руб.</b>"
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
                markup.add(types.KeyboardButton("✅Заказать✅"), types.KeyboardButton("❌Очистить корзину❌"), types.KeyboardButton("⬅Назад⬅"))
                bot.send_message(message.chat.id, msg, parse_mode="html", reply_markup=markup)
                bot.register_next_step_handler(message, OpenCartNextHandler)
          finally:
              connection.close()
        except Exception as ex:
            print(ex)

    def OpenCartNextHandler(message):
        if message.text == "✅Заказать✅":
            CheckPhoneAddres(message)
            #Back(message)
        elif message.text == "❌Очистить корзину❌":
            DeleteCart(message)
        elif message.text == "⬅Назад⬅":
            Back(message)

    def OrderAddCart(message, adress, phone, productsList):
        print("давай закажем уже")
        print(adress, phone, productsList)

    def DeleteCart(message):
        try:
          connection = pymysql.connect(
              host=host,
              port=3306,
              user=user,
              password=password,
              database=bd_name,
          )
          try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM `cart` WHERE `userId` = '{message.chat.id}'")
                connection.commit()
                bot.send_message(message.chat.id, "Корзина очищена")
                Back(message)
          finally:
              connection.close()
        except Exception as ex:
            print(ex)
    def OrderSend(message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🍣Сеты🍣")
        btn2 = types.KeyboardButton("🍕🍟Комбо🍕🍟")
        btn3 = types.KeyboardButton("🥢Роллы🥢")
        btn4 = types.KeyboardButton("🍕Пицца🍕")
        btn5 = types.KeyboardButton("⬅Назад⬅")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.chat.id, text="Выберите категорию", reply_markup=markup, parse_mode='html')
        bot.register_next_step_handler(message, OrderSendHandler)
    def InputProduct(message, id, productListMore):
        global productFocusId, productIndex
        if productIndex >= len(productListMore):
            productIndex = 0
        index = productIndex
        productFocusId = productListMore[id][index][0]
        bot.send_photo(message.chat.id, photo=productListMore[id][index][3])
        bot.send_message(message.chat.id, text=f"<em>"+productListMore[id][index][1]+"</em>\n<strong>"+productListMore[id][index][2] + "р</strong>", parse_mode='html')
    def sendPhone(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
        back = types.KeyboardButton("⬅Назад⬅")
        keyboard.add(button_phone, back)
        bot.send_message(message.chat.id, text="Укажите контактный телефон", reply_markup=keyboard, parse_mode='html')
    def Sets(message):
        global productListMore
        markupSets = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🍣Ещё🍣")
        btn2 = types.KeyboardButton("✅Заказать✅")
        btn3 = types.KeyboardButton("⬅Назад⬅")
        markupSets.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Сеты", reply_markup=markupSets)
        InputProduct(message, 0, productListMore)
        bot.register_next_step_handler(message, SetsHandler)
    def Combo(message):
        global productListMore
        markupCombo = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🍕🍟Ещё🍕🍟")
        btn2 = types.KeyboardButton("✅Заказать✅")
        btn3 = types.KeyboardButton("⬅Назад⬅")
        markupCombo.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Комбо", reply_markup=markupCombo)
        InputProduct(message, 1, productListMore)
        bot.register_next_step_handler(message, ComboHandler)
    def Rolls(message):
        global productListMore
        markupRolls = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🥢Ещё🥢")
        btn2 = types.KeyboardButton("✅Заказать✅")
        btn3 = types.KeyboardButton("⬅Назад⬅")
        markupRolls.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Роллы", reply_markup=markupRolls)
        InputProduct(message, 2, productListMore)
        bot.register_next_step_handler(message, RollsHandler)
    def Pizza(message):
        global productListMore
        markupPizza = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🍕Ещё🍕")
        btn2 = types.KeyboardButton("✅Заказать✅")
        btn3 = types.KeyboardButton("⬅Назад⬅")
        markupPizza.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Пицца", reply_markup=markupPizza)
        InputProduct(message, 3, productListMore)
        bot.register_next_step_handler(message, PizzaHandler)
    def Order(message, index, number):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("❌Отмена❌"))
        markup.add(types.KeyboardButton("-"), types.KeyboardButton(str(number)), types.KeyboardButton("+"))
        markup.add(types.KeyboardButton("✅Заказать✅"))
        bot.send_message(message.chat.id, f"Количество {number}шт.", reply_markup=markup)
        bot.register_next_step_handler(message, lambda m: OrderNextHandler(m, index, number))
    def OrderNextHandler(message, index, number):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        buttonList = ["🍣Ещё🍣", "🍕🍟Ещё🍕🍟", "🥢Ещё🥢", "🍕Ещё🍕"]
        textList = ["🍣Сеты🍣", "🍕🍟Комбо🍕🍟", "🥢Роллы🥢", "🍕Пицца🍕"]
        nextHandlerList = [SetsHandler, ComboHandler, RollsHandler, PizzaHandler]
        btn2 = types.KeyboardButton("✅Заказать✅")
        btn3 = types.KeyboardButton("⬅Назад⬅")
        markup.add(buttonList[index], btn2, btn3)
        if message.text == "❌Отмена❌":
            bot.send_message(message.chat.id, textList[index], reply_markup=markup)
            bot.register_next_step_handler(message, nextHandlerList[index])
            InputProduct(message, index, productListMore)
        elif message.text == "-":
            if number != 1:
                number -= 1
            Order(message, index, number)
        elif message.text == "+":
            number += 1
            Order(message, index, number)
        elif message.text == "✅Заказать✅":
            OrderAdd(message, index, number)
            bot.send_message(message.chat.id, textList[index], reply_markup=markup)
            bot.register_next_step_handler(message, nextHandlerList[index])
        else:
            bot.register_next_step_handler(message, OrderNextHandler)
    def OrderAdd(message, index, qty):
        try:
          connection = pymysql.connect(
              host=host,
              port=3306,
              user=user,
              password=password,
              database=bd_name,
          )
          try:
            with connection.cursor() as cursor:
                productList = productListMore[index][productIndex]
                cursor.execute("INSERT INTO `cart` (`userId`, `productId`, `name`, `price`, `qty`) VALUES (%s,%s,%s,%s,%s)",
                            (message.chat.id, productList[0], productList[1], int(productList[2]), qty))
                connection.commit()
                bot.send_message(message.chat.id, f"В корзину добавлен продукт: <b>{productList[1]} в количестве {qty}шт. на сумму {int(productList[2]) * qty}руб.</b>", parse_mode="html")
          finally:
              connection.close()
        except Exception as ex:
            print(ex)
    def Back(message):
        photo = open('img1.jpg', 'rb')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = types.KeyboardButton("🍕🍟Сделать заказ🍰🍣")
        btn2 = types.KeyboardButton("🛒Корзина🛒")
        btn3 = types.KeyboardButton("❗️Информация❗️")
        btn4 = types.KeyboardButton("☎️Контакты☎️")
        markup.add(btn1, btn2, btn3, btn4)

        bot.send_photo(message.chat.id, photo, caption="Главное меню", reply_markup=markup)
    @bot.message_handler(content_types=['text'])
    def func(message):
        def InfoSend():
            photo2 = open('img2.webp', 'rb')
            bot.send_message(message.chat.id, text="<em><strong>🍕Хотите заказать роллы в Кирове?🍕</strong> \n Тогда вы точно столкнулись с непростым выбором и большим количеством предложений. Как сделать правильный выбор, и на что обратить внимание? Мы вам поможем! \n <strong>1.</strong>Ассортимент на любой вкус. Доставка еды (Киров) должна удивить разнообразием роллов и пиццы. Япономания угодит вкусу даже самого взыскательного гурмана. \n <strong>2.</strong>Быстрая доставка. Заказывая доставку роллов и пиццы в Кирове, хочется получить еду как можно быстрее. Наши курьеры вовремя и бережно привезут ваш заказ в любую точку города. \n <strong>3.</strong>Профессиональные повара. В первую очередь еда должна быть вкусной. В Япономании для вас готовит команда профессионалов своего дела.</em>", parse_mode='html')
            bot.send_message(message.chat.id, text="<em><strong>Роллы Киров доставка — это Япономания! Порадуйте себя и сделайте заказ прямо сейчас.</strong></em>", parse_mode='html')
        def ContactsSend():
            #photo3 = open('/Users/user/Desktop/хакатон/logo2.png', 'rb')
            #bot.send_photo(message.chat.id, photo3)
            bot.send_message(message.chat.id, text=f"<em><strong>🍕Контакты🍕</strong>\n🍣г. Киров, ул. Спасская, 17 / Ленина, 82\n🍣г. Киров, ул. Московская, 185а\n🍣г. Киров, Октябрьский пр-т, 19\n🍣г. Киров, Коминтерновская пл.1Б (ТЦ Клён, левое крыло)\n🍣г. Кирово-Чепецк, ул.Фестивальная, 5\n🍣г. Кирово-Чепецк, ул. Володарского, 9\n🍣г. Кирово-Чепецк, пр-т России, 34 (ТЦ ""Россия"", 2 этаж)\n🍣<strong>Телефон: +7 (8332) 735-166</strong>\n🍣<strong>Прием заказов: 10:00 — 23:00</strong></em>",parse_mode='html')
            bot.send_venue(message.chat.id, latitude = 58.60250752290142, longitude = 49.681341311816595, address="г. Киров, ул. Спасская, 17 / Ленина, 82", title="🍣г. Киров, ул. Спасская, 17 / Ленина, 82")
            bot.send_venue(message.chat.id, latitude = 58.60320882122029, longitude = 49.59145272715841, address="г. Киров, ул. Московская, 185а", title="🍣г. Киров, ул. Московская, 185а")
            bot.send_venue(message.chat.id, latitude = 58.63737481025416, longitude = 49.62389591366625, address="г. Киров, Октябрьский пр-т, 19", title="🍣г. Киров, Октябрьский пр-т, 19")
            bot.send_venue(message.chat.id, latitude = 58.644245195202636, longitude = 49.722704327160265, address="г. Киров, Коминтерновская пл.1Б (ТЦ Клён, левое крыло)", title="🍣г. Киров, Коминтерновская пл.1Б (ТЦ Клён, левое крыло)")
            bot.send_venue(message.chat.id, latitude = 58.54348646660314, longitude = 50.05261375599123, address="г. Кирово-Чепецк, ул.Фестивальная, 5", title="🍣г. Кирово-Чепецк, ул.Фестивальная, 5")
            bot.send_venue(message.chat.id, latitude = 58.531380191736666, longitude = 50.03653399831977, address="г. Кирово-Чепецк, ул. Володарского, 9", title="🍣г. Кирово-Чепецк, ул. Володарского, 9")
            bot.send_venue(message.chat.id, latitude = 58.544120772700374, longitude = 50.044049936396846, address="г. Кирово-Чепецк, пр-т России, 34 (ТЦ Россия, 2 этаж)", title="🍣г. Кирово-Чепецк, пр-т России, 34 (ТЦ Россия, 2 этаж)")

        if(message.text == "🍕🍟Сделать заказ🍰🍣"):
            OrderSend(message)
        elif(message.text == "❗️Информация❗️"):
            InfoSend()
        elif(message.text == "☎️Контакты☎️"):
            ContactsSend()
        elif (message.text == "🛒Корзина🛒"):
            OpenCart(message)

        elif(message.text == "⬅Назад⬅"):
            Back(message)
    def OrderSendHandler(message):
        global productIndex
        if message.text == "🍣Сеты🍣":
            productIndex = 0
            Sets(message)
        elif (message.text == "🍕🍟Комбо🍕🍟"):
            productIndex = 0
            Combo(message)
        elif (message.text == "🥢Роллы🥢"):
            productIndex = 0
            Rolls(message)
        elif (message.text == "🍕Пицца🍕"):
            productIndex = 0
            Pizza(message)
        elif (message.text == "⬅Назад⬅"):
            Back(message)
    def SetsHandler(message):
        global productIndex
        if (message.text == "🍣Ещё🍣"):
            productIndex += 1
            InputProduct(message, 0, productListMore)
            bot.register_next_step_handler(message, SetsHandler)
        elif (message.text == "✅Заказать✅"):
            Order(message, 0, 1)
        elif (message.text == "⬅Назад⬅"):
            OrderSend(message)
    def ComboHandler(message):
        global productIndex
        if(message.text == "🍕🍟Ещё🍕🍟"):
            productIndex += 1
            InputProduct(message, 1, productListMore)
            bot.register_next_step_handler(message, ComboHandler)
        elif (message.text == "✅Заказать✅"):
            Order(message, 1, 1)
        elif (message.text == "⬅Назад⬅"):
            OrderSend(message)
    def RollsHandler(message):
        global productIndex
        if (message.text == "🥢Ещё🥢"):
            productIndex += 1
            InputProduct(message, 2, productListMore)
            bot.register_next_step_handler(message, RollsHandler)
        elif (message.text == "✅Заказать✅"):
            Order(message, 2, 1)
        elif (message.text == "⬅Назад⬅"):
            OrderSend(message)
    def PizzaHandler(message):
        global productIndex
        if (message.text == "🍕Ещё🍕"):
            productIndex += 1
            InputProduct(message, 3, productListMore)
            bot.register_next_step_handler(message, PizzaHandler)
        elif (message.text == "✅Заказать✅"):
            Order(message, 3, 1)
        elif (message.text == "⬅Назад⬅"):
            OrderSend(message)


    bot.polling(none_stop=True)

def ThreadParser():
    def ParserProducts(catalogID, urlList):
        productId = 0
        productCatalogId = 0
        productsList = []
        productCatalogId = catalogID
        r = requests.get(urlList[catalogID])
        soup = bs(r.text, "html.parser")
        productsItems = soup.find_all('li', class_='product-item')
        for productItem in productsItems:
            productList = []
            productId = productItem['id'].replace('dish-', '')
            productList.append(productId)
            priductTitel = productItem.find_all('div', class_='product-title')
            for titel in priductTitel:
                productList.append(titel.div.text)
                priductPrice = productItem.find_all('div', class_='price-text-wrap')
                for price in priductPrice:
                    cleanPrice = price.span.text.replace(' ₽', '')
                    productList.append(cleanPrice.replace('\xa0', ' '))
                    priductImage = productItem.find_all('img', class_='product-img')
                    for image in priductImage:
                        productList.append("https://yaponomaniya.com" + image['src'])
                        productList.append(productCatalogId)
            productsList.append(productList)
        return productsList
    while True:
        global productListMore, urlList

        productListMoreDuble = []
        for i in range(len(urlList)):
            productListMoreDuble.append(ParserProducts(i, urlList))

        productListMore = productListMoreDuble.copy()
        time.sleep(30)
@bot.message_handler(content_types=['contact']) 
def contact(message):
    if message.contact is not None: 
        try:
          connection = pymysql.connect(
              host=host,
              port=3306,
              user=user,
              password=password,
              database=bd_name,
          )
          try:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE `users` SET `phone` = %s WHERE `id` = %s",
                 (message.contact.phone_number, message.chat.id)),
                connection.commit()
                bot.send_message(message.chat.id, "Номер телефона успешно добавлен") 
                bot.send_message(message.chat.id, "Ваша заявка успешно отправлена, мененджер перезвонить вам в течении 5 минут по номеру: " + phAd[3], parse_mode='html')
                DeleteCart(message)
          finally:
              connection.close()
        except Exception as ex:
            print(ex)
    
threadPars = Thread(target=ThreadParser).start()
threadBot = Thread(target=ThreadBot).start()