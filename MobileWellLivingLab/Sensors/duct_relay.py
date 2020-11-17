import RPi.GPIO as GPIO
import time
import datetime

GPIO.setmode(GPIO.BCM)
# pin 4 did not work
# Set Pins that will be used
pinlist = [2,3,27,17]

# pin 2 is relay 1
# pin 3 is relay 2
# pin 17 is relay 3
# pin 27 is relay 4



# Loop and set state to high
for i in pinlist:
	GPIO.setup(i,GPIO.OUT)
	GPIO.output(i,GPIO.HIGH)

try:
	while True:
		
		print('Loop Starts: Ball Valve Open / pinch valve closed')
		time.sleep(10);
		GPIO.output(17,GPIO.LOW)
		pin2Val = GPIO.input(2)
		pin3Val = GPIO.input(3)
#		data = whatever values for 2,3,17 and push to store + timestamp
		#self.log.info('Begin Duct Switch: Ball Open / Opening  Pinch Valve')
		time.sleep(5);
		GPIO.output(2,GPIO.HIGH) 
		GPIO.output(3,GPIO.LOW)
		
##    Open to close ball valve switch
		print('Begin Ball Valve Switch: Ball changing/ Pinch open')
		time.sleep(5);
		GPIO.output(17, GPIO.HIGH)
		print('End Switch: Ball Closed / Pinch closed')
		time.sleep(5);
		GPIO.output(17, GPIO.LOW)
		print('Begin Duct Switch: Ball Open / Opening Pinch')
		time.sleep(5);
		GPIO.output(2,GPIO.LOW)
		GPIO.output(3,GPIO.HIGH)
##     Closed to Open
		print('Begin Ball Switch: Ball Changing / Pinch Open')
		time.sleep(5);
		GPIO.output(17, GPIO.HIGH)
		print('End Switch: Ball Closed / Pinch Closed')
		time.sleep(5);
		print('End loop')


except KeyboardInterrupt:
	print('Quitter')
	GPIO.cleanup()

