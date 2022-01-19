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
colorama.init()

passwordchange = "password.change.own"
logout = "logout"
adminpanel = "admin.panel"
admincheckperm = "admin.checkperm"
adminaddstaff = "admin.addStaff"
adminmanagedataown = "admin.manageData.own"
adminmanagedataother = "admin.manageData.other"