#!/bin/bash

echo "Enter Language(En or Zh-Tw)"
read lang

if [ $lang = "En" ]
then
	echo "Select a step:(Please Enter the Name of the Step.)"
	echo "1.install : Install the dependencies."
	echo "2.batch : Start the program."
	read step

	if [ $step = "install" ]
	then
		echo "Start Installing the dependencies..."

		python3 -m pip install -r requirements.txt
	elif [ $step = "batch" ]
	then
		echo "Entering the program..."

		python3 batch.py

	else
		echo "Please Enter a effective step."
		return
	fi

elif [ $lang = "Zh-Tw" ]
then
	echo "請選擇一個動作：（請輸入該步驟的「名稱」）"
	echo "1.install : 安裝依賴項（如果已經安裝則不須再次安裝）。"
	echo "2.batch : 運行程式。"
	read step

	if [ $step = "install" ]
	then
		echo "開始安裝依賴項..."

		python3 -m pip install -r requirements.txt
	elif [ $step = "batch" ]
	then
		echo "開始執行程式..."

		python3 batch.py

	else
		echo "請輸入一個有效的動作。"
		return

	fi

else
	echo "Please Enter a effective language."


fi