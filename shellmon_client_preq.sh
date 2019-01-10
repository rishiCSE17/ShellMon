# this script is only ment for raspberry  pi 3

echo 'updating repository...'
	sudo apt -y update > /dev/null
echo 'repo update done!'

echo 'preparing...'
	sudo apt -y install figlet > /dev/null 
	figlet ShellMon - by - Saptarshi Ghosh
echo 'press any key to continue...'
	read x 
echo 'Installing python...'
	echo 'python3...'
		sudo apt -y install python3  > /dev/null
	echo 'done!'
	
	echo 'pip3'
		sudo apt -y install python3-pip > /dev/null
	echo 'done!'
	
	echo 'tkinter3'
		sudo apt -y install python3-tk > /dev/null
	echo 'done'
echo 'Python installation done!'

echo 'Updating pip3...'
	sudo pip3 install --upgrade pip
echo 'pip update done!'

echo 'Installing python libraries for shellmon'

	echo 'matplotlib...'
		sudo pip3 install matplotlib > /dev/null
	echo 'done!'

	echo 'drawnow...' 
		sudo pip3 install drawnow > /dev/null
	echo 'done!'

	echo 'psutil...'
		sudo pip3 install psutil  > /dev/null
	echo 'done!'
	
	echo 'pymysql...'
		sudo pip3 install pymysql  > /dev/null
	echo 'done!'
echo 'libraries installation done! '