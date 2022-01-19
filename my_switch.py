# coding: utf8

from termcolor import colored;
import sys;
import os;
import colorama;
import hashlib;
import MySQLdb;
import getpass;
import wmi;
import urllib.request;
import datetime;
import time;
colorama.init();

#Импорт собственных модулей
import data_vars as dv

#Подключаемся к БД
try:
        conn = MySQLdb.connect(dv.mysql_host, dv.mysql_login, dv.mysql_password, dv.mysql_db, charset='utf8', init_command='SET NAMES UTF8')
        cursor = conn.cursor()
except MySQLdb.Error:
        print(colored("Не возможно подключиться к базе данных! Проверьте интернет-соединение!", 'red'));
        sys.exit(2002);
#

def acc_status1(acc_status):
        return 0

def acc_status2(acc_status):
        print (colored("Действие Вашей учётной записи приостановлено!", 'red') + " Обратитесь к руководителю своего отдела или в Административный отдел." + "\nВы всё ещё можете пользоваться своим терминалом, но Ваша группа была заменена на \"Сотрудник\".");
        cursor.execute("UPDATE `Users` SET `groupid` = 1 WHERE `login` = '" + E_login + "'")
        conn.commit()
        cursor.execute("UPDATE `Users` SET `status` = 1 WHERE `login` = '" + E_login + "'")
        conn.commit()        
        log('1', IP, str(DriveID), E_login, "Group changed becouse of accaunt's status 2.")
        contin = getpass.getpass("Нажмите Enter для продолжения.");
        os.system("cls")
        acc_status_switch(acc_status)

def acc_status3(acc_status):
        print ("Ваш пароль устарел, или системный админстратор советует Вам его сменить.")
        newpass = "\0-\0"; newpass_check = "---\0-\0\'"
    
        cursor.execute("SELECT `password` FROM `Users` WHERE `login` = '" + E_login + "'")
        old_pass = cursor.fetchone()
        if old_pass != None:
                old_pass = old_pass[0]	
    
        while newpass != newpass_check or newpass == old_pass:
                newpass = passhash(getpass.getpass("Введите новый пароль: "), salt)
                newpass_check = passhash(getpass.getpass("Повторите новый пароль: "), salt)
                if newpass != newpass_check:
                        print (colored("Пароли не совпадают!", 'red'))
                elif newpass == old_pass:
                        print (colored("Новый пароль совпадает со старым!", 'red'))
    
        cursor.execute("UPDATE `Users` SET `password` = " + newpass + " WHERE `login` = '" + E_login + "'")
            
    
        conn.commit()
        log('1', IP, str(DriveID), E_login, "Password was changed from '" + old_pass + "' to '" + newpass + "'.")

def acc_status4(acc_status):
        cursor.execute("SELECT `id` FROM `Users` WHERE `login` = '" + E_login + "'")
        userid = cursor.fetchone()
        if userid != None:
                userid = userid[0]
        cursor.execute("SELECT `reason` FROM `bans` WHERE `userid` = '" + str(userid) + "'")
        ban_reason = cursor.fetchone()
        if ban_reason != None:
                ban_reason = ban_reason[0]
        print(colored("Ваш аккаунт заблокирован!", 'red') + "\nПричина блокировки: '" + str(ban_reason) + "'.\nЕсли Вы считаете, что это произошло по ошибке, обратитесь к руководителю своего отдела или в Административный отдел.")
        contin = getpass.getpass("Нажмите Enter для закрытия программы.");
        sys.exit(0)

def acc_unknownstatus(acc_status):
        print(colored("Статус Вашего аккаунта не установлен!", 'red') + "\nОбратитесь к руководителю своего отдела или в Административный отдел.")
        contin = getpass.getpass("Нажмите Enter для закрытия программы.");
        sys.exit(0)
def acc_status_switch(acc_status):
        if acc_status == 2: #Проверка на статус аккаунта "приостановлен"
                acc_status2(acc_status)
        elif acc_status == 3: #Проверка на статус аккаунта "необходимо сменить пароль"
                acc_status3(acc_status)
        elif acc_status == 4: #Проверка на статус аккаунта "заблокирован"
                acc_status4(acc_status)
        elif acc_status == 1: #У аккаунта статус "активен" (как и должно быть по-умолчанию)
                acc_status1(acc_status)
        else: #У аккаунта неизвестный статус.
                acc_unknownstatus(acc_status)