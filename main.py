
import rp2
import network
import ubinascii
import machine
import urequests as requests
import time
import socket
import ure
from machine import Timer
import math


tim = None

mot0dir0 = machine.PWM(machine.Pin(16, machine.Pin.OUT))
mot0dir1 = machine.PWM(machine.Pin(17, machine.Pin.OUT))
mot1dir0 = machine.PWM(machine.Pin(18, machine.Pin.OUT))
mot1dir1 = machine.PWM(machine.Pin(19 , machine.Pin.OUT))
mot0dir0.freq(1000)
mot0dir1.freq(1000)
mot1dir0.freq(1000)
mot1dir1.freq(1000)
#k=1
#mot0dir0.duty_u16(0)
#mot0dir1.duty_u16(0)
#mot1dir0.duty_u16(0)
#mot1dir1.duty_u16(0)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Other things to query
# print(wlan.config('channel'))
# print(wlan.config('essid'))
# print(wlan.config('txpower'))

# Load login data from different file for safety reasons
ssid = "Ejemplo"
pw = "123456789"

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Define blinking function for onboard LED to indicate error codes    
def blink_onboard_led(num_blinks):
    led = machine.Pin('LED', machine.Pin.OUT)
    for i in range(num_blinks):
        led.on()
        time.sleep(.2)
        led.off()
        time.sleep(.2)
    
# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()
blink_onboard_led(wlan_status)

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed ',wlan_status)
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    
# Function to load in html page    
def get_html(html_name):
    with open(html_name, 'r') as file:
        html = file.read()
        
    return html



def findall_1(pattern, text):
    matches = []
    start = 0

    while True:
        match = re.search(pattern, text[start:])
        if match is None:
            break

        matches.append(match.group(0))
        start += match.end()

    return matches


# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]


s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

s.bind(addr)

s.listen(1)

print('Listening on', addr)
led = machine.Pin('LED', machine.Pin.OUT)







def next_command(timer):
    global angle_LOGO_deg, P0, P1, t, comandos
    #commands=comandos
    print('comandos',comandos)
    
    if comandos != [] :
        tiem,m1,m2=comandos.pop(0)
        set_PWMs(mot0dir1,mot0dir0,m1)
        set_PWMs(mot1dir0,mot1dir1,m2)
        tim = Timer(period=abs(tiem), mode=Timer.ONE_SHOT, callback=next_command)
    else:
        set_PWMs(mot0dir1,mot0dir0,0)
        set_PWMs(mot1dir0,mot1dir1,0)
        tim.deinit()
        tim=None
        
        
        
        
        
 
def set_PWMs(mot_dir0,mot_dir1,x_value):
    print(mot_dir0,mot_dir1,x_value)
    if x_value<0:
        mot_dir0.duty_u16(-x_value)
        mot_dir1.duty_u16(0)
    elif x_value>0:
        mot_dir0.duty_u16(0)
        mot_dir1.duty_u16(x_value)
    else:
        mot_dir0.duty_u16(0)
        mot_dir1.duty_u16(0)



    
    

comandos=[]
# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        led.on()
       
        print('Client connected from', addr)
        r = cl.recv(1024)
        
        r = str(r)
        print(r[:30])
        # Utilizar expresiones regulares para encontrar los valores de x e y
        match = ure.search(r'\?x=(-?\d+)&y=(-?\d+)', r)
        

        if match:
            x_value = int(match.group(1))
            y_value = int(match.group(2))

            print(f'Valor de x: {x_value}')
            print(f'Valor de y: {y_value}')
            
            set_PWMs(mot0dir1,mot0dir0,x_value)
            set_PWMs(mot1dir0,mot1dir1,y_value)

            if tim:
                tim.deinit()
                tim=None
            
        else:
            print('No se encontraron valores de x e y en la cadena de la solicitud HTTP.')

        match = ure.search(r'command=([^\s]+)', r)
        if match:
            input_string= match.group(1)
            matches = []
            start = 0   
            
            while True:
                match = ure.search(r'([+-]?\d+)_?', input_string[start:])
                if match is None:
                    break

                matches.append(int(match.group(1)))
                start += match.end()

            # Build the list of lists
            result = [matches[i:i+3] for i in range(0, len(matches), 3)]
 
 
            comandos += result#ure.finditer(r'([+-]?\d+)([+-]?\d+)([+-]?\d+)_?', match.group(1))
            #match.group(1).split('_')
            # triplas = re.findall(r'([+-]?\d+)([+-]?\d+)([+-]?\d+)_?', cadena)
            if not tim:
                next_command(None)
                #tim=Timer(period=5000, mode=Timer.ONE_SHOT, callback=lambda t:print(1))


        else:
            print('No se encontraron comandos en la cadena de la solicitud HTTP.')
            
        response = get_html('flecha.html')
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send(response)
        cl.close()
        #print(r[:20])
        #time.sleep(.2)
        led.off()
        #time.sleep(.2)
    except OSError as e:
        cl.close()
        print('Connection closed')

# Make GET request
#request = requests.get('http://www.google.com')
#print(request.content)
#request.close().