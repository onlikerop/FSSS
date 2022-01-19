@echo off

set "inext=.ui"

(
for /f "delims=^" %%i in ('dir /B *%inext%') do (
	python -m PyQt5.uic.pyuic -x %%i -o "%%i.py"
	echo %%i
	echo %inext%
 )
)|| (PAUSE)

exit/b