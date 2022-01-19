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

mysql_host = "localhost"
mysql_login = "FSSS_admin"
mysql_password = "FSSS_password_b900cdbb70563a810"
mysql_db = "FSSS"