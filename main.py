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
from PyQt5 import QtCore, QtGui, QtWidgets;
from PyQt5.QtCore import *;
from PyQt5.QtWidgets import *;
from PyQt5.QtGui import *;
colorama.init();

#Импорт собственных модулей
import data_vars as dv #Данные для БД
import permissions as permission #Список прмишенсов

import GUI_adminpanel as GUI_ap #Импорт интерфейса админпанели.
import GUI_adminpanel_adduser as GUI_apadduser #Импорт добавление нового сотрудника в админпанели.


os.system("cls")
print("=======================================================================")
print("================   Program: FSSS                      =================")
print("================   Coder: FSSS coder                  =================")
print("================   Availability: Private using only   =================")
print("=======================================================================")

salt = ".GRE4g436%^65er4435234$^#%^$hgtr3"

		#Функции
def log(logtype, ip, hddserial, login, log): #Логгирование действий
	try:
		cursor.execute("INSERT INTO `logs` (`type`, `ip`, `hddserial`, `login`, `log`) VALUES (%s, %s, %s, %s, %s)", (str(logtype), str(ip), str(hddserial), str(login), str(log)))
	except MySQLdb.Error:
		print(colored("Не возможно отправить лог действий! Обратитесь к системному администратору", 'red'));
		sys.exit(2003);

	conn.commit()
	return 0;

def passhash(password, salt): #Вывод хеша пароля
	return hashlib.sha256((password + salt).encode('utf-8')).hexdigest();

#Статусы аккаунта
def acc_status1(User_Data): #Действия при статуксе 1
	return 0

def acc_status2(User_Data): #Действия при статуксе 2
	print (colored("Действие Вашей учётной записи приостановлено!", 'red') + " Обратитесь к руководителю своего отдела или в Административный отдел.");
	contin = getpass.getpass("Нажмите Enter для закрытия программы.");
	sys.exit(0)

def acc_status3(User_Data): #Действия при статуксе 3
	print ("Ваш пароль устарел, или системный админстратор советует Вам его сменить.")
	changepassword(User_Data)

	cursor.execute("UPDATE `Users` SET `status` = 1 WHERE `login` = '" + User_Data['login'] + "'")
	conn.commit()
	log('2', IP, str(DriveID), User_Data['login'], "Статус был изменён на '1'.")	

def acc_status4(User_Data): #Действия при статуксе 4
	cursor.execute("SELECT `reason` FROM `bans` WHERE `userid` = '" + str(userid) + "'")
	ban_reason = cursor.fetchone()
	if ban_reason != None:
		ban_reason = ban_reason[0]
	print(colored("Ваш аккаунт заблокирован!", 'red') + "\nПричина блокировки: '" + str(ban_reason) + "'.\nЕсли Вы считаете, что это произошло по ошибке, обратитесь к руководителю своего отдела или в Административный отдел.")
	contin = getpass.getpass("Нажмите Enter для закрытия программы.");
	sys.exit(0)

def acc_unknownstatus(User_Data): #Действия при неопределённом статусе
	print(colored("Статус Вашего аккаунта не установлен!", 'red') + "\nОбратитесь к руководителю своего отдела или в Административный отдел.")
	contin = getpass.getpass("Нажмите Enter для закрытия программы.");
	sys.exit(0)
def acc_status_switch(User_Data): #Выборка действий по статусу аккаунта
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
#

#Свич команд/проверка групп и прав.

def checkperm(User_Data,perm): #Проверка права у пользователя (включая личные права, права его группы и права наследуемых ею групп)
	
	inheritance = ""
	all_perms = list()
	query = "SELECT `permission` from `Permissions` WHERE (`type` = 1 AND `targetid` = " + str(User_Data['id']) + ")" #	" OR (`type` = 0 AND `targetid` = " + groupid + ")"
	cursor.execute("SELECT `groupid` FROM `Users` WHERE `id` = %s", (str(User_Data['id'])))
	
	groupid = cursor.fetchone()
	if groupid != None:
		groupid = groupid[0]
		
	query += " OR (`type` = 0 AND `targetid` = " + str(groupid) + ")"
	
	while groupid != 0:
		cursor.execute("SELECT `inheritance` FROM `Groups` WHERE `id` = %s", (str(groupid)))
		groupid = cursor.fetchone()
		if groupid != None:
			groupid = groupid[0]
		
		if groupid > 0:
			query += " OR (`type` = 0 AND `targetid` = " + str(groupid) + ")"
	
	cursor.execute(query)
	fetch = cursor.fetchall()
	i = 0
	for i in range (len(fetch)):
		all_perms.append(fetch[i][0])
	
	
	realperms = list()
	fullperm = list()
	fullperm = perm.split(".")
	for j in range(len(fullperm)):
		if j != 0:
			newperm = newperm + "." + fullperm[j]
		else:
			newperm = fullperm[j]
		realperms.append(newperm)
		
	access = False
	for j in range(len(realperms)):
		if realperms[j] in all_perms:
			access = True
	return(access)

def commandswitch(command, User_Data): #Выбор действия при вводе команды
	log(1, User_Data['ip'], User_Data['hddserial'], User_Data['login'], "Введена команда: '" + command + "'.")
	if (command == "changepassword" or command == "changepass" or command == "passwd" or command == "chngpass") and checkperm(User_Data, permission.passwordchange):
		#
		changepassword(User_Data)
		#
	elif (command == "logout" or command == "exit" or command == "quit" or command == "off" or command == "stop" or command == "shoutdown") and checkperm(User_Data, permission.logout):
		#
		logout(User_Data)
		#
	elif (command == "admpanel" or command == "adminpanel" or command == "sudo adm") and checkperm(User_Data, permission.adminpanel):
		#
		adminpanel(User_Data)
		#
	elif (command == "checkperm" or command == "checkpermission") and checkperm(User_Data, permission.admincheckperm):
		#
		admincheckperm(User_Data)
		#
	elif (command == "addstaff" or command == "checkpermission") and checkperm(User_Data, permission.adminaddstaff):
		#
		addstaff(User_Data)
		#
	else:
		#
		print (colored("Данная команда не найдена, либо у Вас нет прав на её выполнение!", 'red'))
		log(1, User_Data['ip'], User_Data['hddserial'], User_Data['login'], "Команда не выполнена!")	
		return 0
		#
	
	log(1, User_Data['ip'], User_Data['hddserial'], User_Data['login'], "Команда выполнена успешно!")		
#

#Функции самих команд
def changepassword(User_Data): #Смена пароля
	newpass = "\0-\0"; newpass_check = "---\0-\0\'"

	cursor.execute("SELECT `password` FROM `Users` WHERE `login` = '" + str(User_Data['login']) + "'")
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

	cursor.execute("UPDATE `Users` SET `password` = '" + newpass + "' WHERE `login` = '" + str(User_Data['login']) + "'")
	conn.commit()
	log('2', IP, str(DriveID), User_Data['login'], "Пароль был изменён с '" + old_pass + "' на '" + newpass + "'.")
	
def logout(User_Data): #Выход...
	sys.exit(0)
	
def adminpanel(User_Data): #Открытие админ-панели (Дальше слабонервным не смотреть!)
	
	class GUI_win(GUI_ap.QtWidgets.QMainWindow): #Так надо!
		
		def __init__(self, parent=None): #Инициализация
			GUI_ap.QtWidgets.QWidget.__init__(self, parent)
			self.ui = GUI_ap.Ui_MainWindow()
			self.ui.setupUi(self)
			self.setWindowTitle("Панель администрирования ФСГБ || " + str(User_Data['login']))
			
			self.ui.search_btn.clicked.connect(self.search_btn_clicked)
			self.ui.dataedit_btn.clicked.connect(self.dataedit_btn_clicked)
			self.ui.search_edit.returnPressed.connect(self.ui.search_btn.click)
			self.ui.dataedit_btn.clicked.connect(self.dataedit_btn_clicked)
			self.ui.dataedit_btn_confirm.clicked.connect(self.dataedit_btn_confirm_clicked)
			self.ui.dataedit_btn_cancel.clicked.connect(self.dataedit_btn_cancel_clicked)
			self.ui.addstaff_btn.clicked.connect(self.addstaff_btn_clicked)
			
			if (checkperm(User_Data, permission.adminaddstaff)):
				self.ui.addstaff_btn.setEnabled(True)
			else:
				self.ui.addstaff_btn.setDisabled(True)
			
		def getTargetData(self, search_query): #Получаем данные сотрдуника, по запросу search_query (id, серия и номер дока, либо ФИО)
			if len(search_query) == 2:
				cursor.execute("SELECT * FROM `User_Data` WHERE `docs_serie` = %s AND `docs_number` = %s", (search_query[0], search_query[1]))
			elif len(search_query) == 3:
				cursor.execute("SELECT * FROM `User_Data` WHERE `second_name` = %s AND `name` = %s AND `middle_name` = %s", (search_query[0], search_query[1], search_query[2]))
			elif len(search_query) == 1:
				cursor.execute("SELECT * FROM `User_Data` WHERE `userid` = %s", (search_query[0]))
		
			column_data = cursor.fetchall()
		
			if column_data != ():
				cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'User_Data'")
				fetch = cursor.fetchall()
				column_names = []
				i = 0
				for i in range (len(fetch)):
					column_names.append(fetch[i][0])			
		
				i = 0
				Target_Data = dict()			
				for i in range(len(column_names)):
					Target_Data[column_names[i]] = column_data[0][i]

			else:
				GUI_win.messagebox(self, "Сотрудников с заданными данными не найдено!")
				return {}
				
					
			return Target_Data
		def DataUpdate(self, Target_Data): #Обновляем данные, которые видим на экране на те, которые в БД (из Target_Data, а их уже из бд. (По-факту, можно передать Target_Data какой захотим, но это будет, когда я запилю создание сотрудника))
			if Target_Data != {}:
				_translate = QtCore.QCoreApplication.translate
				self.ui.photo.setPixmap(QtGui.QPixmap("C:\Server\OSPanel\domains\FSSS.RU\photos\\" + Target_Data['photo']))
				self.ui.label_secondname.setText(_translate("MainWindow", str(Target_Data['second_name'])))
				self.ui.label_name.setText(_translate("MainWindow", str(Target_Data['name'])))
				self.ui.label_middlename.setText(_translate("MainWindow", str(Target_Data['middle_name'])))
				self.ui.label_rank.setText(_translate("MainWindow", str(Target_Data['rank'])))
				
				self.ui.label_department.clear()
				
				cursor.execute("SELECT `name` FROM `Departments`")
				departmentslist = cursor.fetchall()
				i = 0
				for i in range (len(departmentslist)):
					self.ui.label_department.addItem(departmentslist[i][0])
				cursor.execute("SELECT `name` FROM `Departments` WHERE `id` = '" + str(Target_Data['departmentid']) + "'")
				
				depid = cursor.fetchone()[0]
				
				self.ui.label_department.setCurrentIndex(Target_Data['departmentid']-1)
				self.ui.label_department_RO.setText(_translate("MainWindow", depid))
				self.ui.label_post.setText(_translate("MainWindow", str(Target_Data['post'])))
				self.ui.label_docsSerie.setText(_translate("MainWindow", str(Target_Data['docs_serie']).zfill(4)))
				self.ui.label_docsNumber.setText(_translate("MainWindow", str(Target_Data['docs_number']).zfill(16)))
				self.ui.label_docsDate.setText(_translate("MainWindow", str(Target_Data['docs_date'])))
				self.ui.label_adoptdate.setText(_translate("MainWindow", str(Target_Data['adoption_date'])))
				self.ui.label_salary.setText(_translate("MainWindow", str(Target_Data['salary'])))
				self.ui.label_checksum.setText(_translate("MainWindow", str(Target_Data['check_sum'])))
				self.ui.label_id.setText(_translate("MainWindow", str(Target_Data['userid'])))
				
	
				self.ui.label_secondname.setReadOnly(True)
				self.ui.label_name.setReadOnly(True)
				self.ui.label_middlename.setReadOnly(True)
				self.ui.label_rank.setReadOnly(True)
				self.ui.label_department_RO.setVisible(True)
				self.ui.label_department.setDisabled(True)
				self.ui.label_post.setReadOnly(True)
				self.ui.label_adoptdate.setReadOnly(True)
				self.ui.label_docsSerie.setReadOnly(True)
				self.ui.label_docsNumber.setReadOnly(True)
				self.ui.label_docsDate.setReadOnly(True)
				self.ui.label_salary.setReadOnly(True)
				self.ui.dataedit_btn_confirm.setDisabled(True)
				self.ui.dataedit_btn_cancel.setDisabled(True)
				
				if (checkperm(User_Data, permission.adminmanagedataown) and User_Data['id'] == Target_Data['userid']) or (checkperm(User_Data, permission.adminmanagedataother) and User_Data['id'] != Target_Data['userid']):
					self.ui.dataedit_btn.setEnabled(True)
				else:
					self.ui.dataedit_btn.setDisabled(True)
				
				if (checkperm(User_Data, permission.adminaddstaff)):
					self.ui.addstaff_btn.setEnabled(True)
				else:
					self.ui.addstaff_btn.setDisabled(True)
			
		def search_btn_clicked(self): #Действие при клике на кнпку поика
			search_query = str(self.ui.search_edit.text()).split(" ", 3)
			
			Target_Data = GUI_win.getTargetData(self, search_query)
			GUI_win.DataUpdate(self, Target_Data)
			
				
			
		def dataedit_btn_clicked(self): #Кнопку изменения данных
			Target_Data = GUI_win.getTargetData(self,str(self.ui.label_id.text()))
			self.ui.label_secondname.setReadOnly(False)
			self.ui.label_name.setReadOnly(False)
			self.ui.label_middlename.setReadOnly(False)
			self.ui.label_rank.setReadOnly(False)
			self.ui.label_department_RO.setVisible(False)
			self.ui.label_department.setEnabled(True)
			self.ui.label_department.setCurrentIndex(Target_Data['departmentid']-1)
			self.ui.label_post.setReadOnly(False)
			self.ui.label_adoptdate.setReadOnly(False)
			self.ui.label_docsSerie.setReadOnly(False)
			self.ui.label_docsNumber.setReadOnly(False)
			self.ui.label_docsDate.setReadOnly(False)
			self.ui.label_salary.setReadOnly(False)
			self.ui.dataedit_btn.setDisabled(True)
			self.ui.dataedit_btn_confirm.setEnabled(True)
			self.ui.dataedit_btn_cancel.setEnabled(True)
			
		def dataedit_btn_confirm_clicked(self): #Кнопку подтверждения изменений
			search_query = str(self.ui.label_id.text())
			Target_Data = GUI_win.getTargetData(self, search_query)
			
			datalog = "Изменены данные у сотрудника '" + str(Target_Data['second_name']) + " " + str(Target_Data['name']) + " " + str(Target_Data['middle_name']) + "' (User ID: '" + str(Target_Data['userid']) + "')\nБыло:\n\""
			
			datalog += "\n" + str(Target_Data) + "\n\"\nСтало:\n\""
			
			NewData = dict()
			
			NewData['id'] = Target_Data['id']
			NewData['userid'] = str(self.ui.label_id.text())
			NewData['second_name'] = str(self.ui.label_secondname.text())
			NewData['name'] = str(self.ui.label_name.text())
			NewData['middle_name'] = str(self.ui.label_middlename.text())
			NewData['phone'] = Target_Data['phone']
			NewData['departmentid'] =  str(self.ui.label_department.currentIndex() + 1)
			NewData['post'] = str(self.ui.label_post.text())
			NewData['rank'] = str(self.ui.label_rank.text())
			NewData['docs_serie'] = str(self.ui.label_docsSerie.text())
			NewData['docs_number'] = str(self.ui.label_docsNumber.text())
			NewData['docs_date'] = str(self.ui.label_docsDate.text())
			NewData['adoption_date'] = str(self.ui.label_adoptdate.text())
			NewData['salary'] = str(self.ui.label_salary.text())
			check_data = NewData['userid'] + NewData['second_name'] + "-9Hhwrf" + NewData['docs_number'] + NewData['departmentid'] + NewData['docs_serie'] + "\\Jsercheck-"
			NewData['check_sum'] = passhash(check_data, ".check_sum_salt.dev//0")
			NewData['photo'] = str(NewData['id']) + ".jpg"
			

			datalog += "\n" + str(NewData)
			datalog += "\n\""
			
			conn.commit()
			
			try:
				cursor.execute("""UPDATE `User_Data` SET `photo` = %s, `second_name` = %s, `name` = %s, `middle_name` = %s, `phone` = %s, `departmentid` = %s, `post` = %s, `rank` = %s, `docs_serie` = %s, `docs_number` = %s, `docs_date` = %s, `adoption_date` = %s, `salary` = %s, `check_sum` = %s WHERE `id` = %s""",
					       (str(NewData['photo']), str(NewData['second_name']), str(NewData['name']), str(NewData['middle_name']), NewData['phone'], NewData['departmentid'], str(NewData['post']), str(NewData['rank']), NewData['docs_serie'], NewData['docs_number'], str(NewData['docs_date']), str(NewData['adoption_date']), NewData['salary'], str(NewData['check_sum']), NewData['id']))
			except MySQLdb.Error:
				print(colored("Не возможно сохранить изменения или отправить лог действий! Обратитесь к системному администратору", 'red'));
				app.quit()
			else:
				log('3', User_Data['ip'], User_Data['hddserial'], User_Data['login'], datalog)
				conn.commit()
				GUI_win.messagebox(self, "Данные успешно обновлены!")
			
			search_query = str(NewData['id'])
			Target_Data = GUI_win.getTargetData(self, search_query)				
			GUI_win.DataUpdate(self, Target_Data)
				
			
		def dataedit_btn_cancel_clicked(self): #Кнопку отмены изменений
			search_query = str(self.ui.label_id.text())
			
			Target_Data = GUI_win.getTargetData(self, search_query)
			GUI_win.DataUpdate(self, Target_Data)
			
		def addstaff_btn_clicked(self, User_Data = User_Data): #Кнопку добавления сотрудника
			
			print("addstaff_btn_clicked!")
			addstaff(User_Data)

			

		def messagebox(self, body, title="Информация"): #Вывод диалоговых окон с информацией
			dialog = QMessageBox(QMessageBox.Information, title, body)
			dialog.exec_()
			
	if __name__ == "__main__": #Проверка на то, что это основная запущенная программа (так надо)
		app = QtWidgets.QApplication(sys.argv)
		window = GUI_win()
		window.show()
		app.exec_()
def addstaff (User_Data):
	
	class GUI_win(QtWidgets.QMainWindow): #Так надо!
		
		def __init__(self, parent=None): #Инициализация
			QtWidgets.QWidget.__init__(self, parent)
			self.ui = GUI_apadduser.Ui_MainWindow()
			self.ui.setupUi(self)
			self.setWindowTitle("Панель администрирования ФСГБ || " + str(User_Data['login']))

			

		def messagebox(self, body, title="Информация"): #Вывод диалоговых окон с информацией
			dialog = QMessageBox(QMessageBox.Information, title, body)
			dialog.exec_()
			
	if __name__ == "__main__": #Проверка на то, что это основная запущенная программа (так надо)
		app = QtWidgets.QApplication(sys.argv)
		window = GUI_win()
		window.show()
		app.exec_()
			
def admincheckperm(User_Data):
	nextcheck = ""
	while (nextcheck != "-exit"):
		nextcheck = input("Введите право для проверки (\"-exit\" прерывает команду):")
		if nextcheck !="-exit":
			print (checkperm(User_Data, nextcheck))
		#

E_password = ""
realpassword = "-\0-"
E_login = ""
DriveID = list()

		#Узнаём данные машины#
#Серийник ЖД
c = wmi.WMI()
for item in c.Win32_PhysicalMedia():
	DriveID.append(str(item.serialnumber).strip())

#IP
IP = urllib.request.urlopen('http://ident.me').read().decode('utf8')

		##



#Подключаемся к БД
try:
	conn = MySQLdb.connect(dv.mysql_host, dv.mysql_login, dv.mysql_password, dv.mysql_db, charset='utf8', init_command='SET NAMES UTF8')
	cursor = conn.cursor()
except MySQLdb.Error:
	print(colored("Не возможно подключиться к базе данных! Проверьте интернет-соединение!", 'red'));
	sys.exit(2002);

cursor.execute("SELECT DATE_FORMAT(`datetime`, \"%Y-%m-%d\") FROM `logs` WHERE `hddserial` = \"" + str(DriveID) + "\" AND `ip` = '" + IP + "' ORDER BY `datetime` DESC")

cursorfetch = cursor.fetchone()

if cursorfetch != None:
	last_connection_date = str(datetime.datetime.date(datetime.datetime.strptime(str(cursorfetch[0]), "%Y-%m-%d")))
	current_date = str(datetime.datetime.date(datetime.datetime.now()))
	if last_connection_date != current_date:
		log('-1', IP, str(DriveID), "", "Соединение установлено!")
else:
	log('-1', IP, str(DriveID), "", "Соединение установлено!")
#

while realpassword != E_password or acc_status == 0:
	E_login = input("Введите логин: ")
	E_password = passhash(getpass.getpass("Введите пароль: "), salt)

	cursor.execute("SELECT `password` FROM `Users` WHERE `login` = '" + E_login + "'")
	realpassword = cursor.fetchone()
	if realpassword != None:
		realpassword = realpassword[0]
	cursor.execute("SELECT `status` FROM `Users` WHERE `login` = '" + E_login + "'")
	acc_status = cursor.fetchone()
	if acc_status != None:
		acc_status = acc_status[0]

	if realpassword != E_password:
		print (colored("Неверный логин или пароль!",'red'))
		log('0', IP, str(DriveID), "", "Ошибка при входе. Попытка войти с логином '" + E_login + "' и паролем (хеш) '" + E_password + "'.")
	elif acc_status == 0:
		print (colored("Неверный логин или пароль!",'red'))
		log('0', IP, str(DriveID), "", "Ошибка при входе. Попытка войти с логином '" + E_login + "' и паролем (хеш) '" + E_password + "'.")

		#После успешной авторизации

#Узнаём id пользователя под которым сидим.
cursor.execute("SELECT `id` FROM `Users` WHERE `login` = '" + E_login + "'")
userid = cursor.fetchone()
if userid != None:
	userid = userid[0]
#

#Создаём словарь с данными пользователя
User_Data = dict()
User_Data['id'] = userid
User_Data['login'] = E_login
User_Data['password'] = E_password
User_Data['ip'] = IP
User_Data['hddserial'] = str(DriveID)
#

log('0', IP, str(DriveID), User_Data['login'], "Успешный вход!")

acc_status_switch(acc_status)
while True:
	commandswitch(input("Введите команду: "),User_Data)
	
sys.exit(2004);