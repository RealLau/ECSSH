tell application "Terminal"
	set currentTab to do script ("ssh user@host")
	delay 3
	do script ("123456") in currentTab
end tell