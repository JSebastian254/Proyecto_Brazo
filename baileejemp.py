from machine import Pin, PWM
import utime
import random

# Configura los pines GPIO conectados a los servos
pin_servo1 = Pin(0)  # Pin para el primer servo
pin_servo2 = Pin(28)  # Pin para el segundo servo

# Crea instancias de PWM con una frecuencia de 50 Hz (20 ms) para ambos servos
s1 = PWM(pin_servo1)
s2 = PWM(pin_servo2)
s1.freq(50)
s2.freq(50)

# Define los valores de duty máximos y mínimos
duty_max = 8388
duty_min = 2097

# Función para mapear el ángulo a valores de duty
def map_angle_to_duty(angle):
    return int(duty_min + (duty_max - duty_min) * (angle / 180))

# Función para mover los servos suavemente
def move_servos_smoothly(servo1, servo2, current_angle1, target_angle1, current_angle2, target_angle2, duration):
    steps = 100
    step_duration = duration // steps  # Asegura que sea un número entero
    
    for i in range(steps + 1):
        ratio = i / steps
        intermediate_angle1 = current_angle1 * (1 - ratio) + target_angle1 * ratio
        intermediate_angle2 = current_angle2 * (1 - ratio) + target_angle2 * ratio
        
        duty_value1 = map_angle_to_duty(intermediate_angle1)
        duty_value2 = map_angle_to_duty(intermediate_angle2)
        
        servo1.duty_u16(duty_value1)
        servo2.duty_u16(duty_value2)
        
        utime.sleep_ms(step_duration)

# Función para establecer los ángulos iniciales de los servos
def set_initial_angles():
    initial_angle1 = 90
    initial_angle2 = 0
    s1.duty_u16(map_angle_to_duty(initial_angle1))
    s2.duty_u16(map_angle_to_duty(initial_angle2))
    return initial_angle1, initial_angle2

# Función para generar un ángulo aleatorio para un servo con restricciones
def generate_random_angle():
    return random.randint(0, 180)

# Función para realizar el baile del robot con restricciones
def dance_robot(duration):
    initial_angle1, initial_angle2 = set_initial_angles()
    current_angle1 = initial_angle1
    current_angle2 = initial_angle2
    
    start_time = utime.time()
    end_time = start_time + duration
    
    while utime.time() < end_time:
        angle1 = generate_random_angle()
        angle2 = generate_random_angle()
        
        # Aplicar restricciones durante el baile
        if angle2 == 0:
            if angle1 > 135:
                angle1 = 135
            elif angle1 == 0:
                angle1 = random.randint(30, 135)
            elif angle1 <= 30:
                angle1 = 30
        elif angle2 == 180 and angle1 > 150:
            angle1 = 150
        elif angle1 == 180 and (angle2 < 35 or angle2 > 165):
            angle2 = random.randint(35, 165)
        
        # Ajuste de ángulos para el segundo servo
        adjusted_angle2 = 180 - angle2
        
        move_servos_smoothly(s1, s2, current_angle1, angle1, current_angle2, adjusted_angle2, 1000)
        
        current_angle1 = angle1
        current_angle2 = adjusted_angle2
        
        utime.sleep(0.5)
    
    # Restablecer los ángulos finales después del baile
    move_servos_smoothly(s1, s2, current_angle1, 90, current_angle2, 180, 3000)  # Ajuste para que el segundo servo termine en 180
    s1.duty_u16(map_angle_to_duty(90))
    s2.duty_u16(map_angle_to_duty(0))

# Estado inicial de los servos (suponiendo que empiezan en 90 y 0 grados)
current_angle1 = 90
current_angle2 = 0

continuar = True 

while continuar:
    angle_input1 = input("Digite el valor del ángulo del primer servo (0-180) o 'baile' para iniciar el baile: ")
    if angle_input1.lower() == "baile":
        dance_robot(10)
        print("El baile del robot ha terminado.")
    elif angle_input1.lower() == "fin":
        continuar = False
        s1.deinit()
        s2.deinit()
        print("Fin del programa")
    else:
        angle_input2 = input("Digite el valor del ángulo del segundo servo (0-180): ")
        if angle_input2.lower() == "fin":
            continuar = False
            s1.deinit()
            s2.deinit()
            print("Fin del programa")
        else:
            try:
                angle1 = int(angle_input1)
                angle2 = int(angle_input2)
                if angle1 < 0 or angle1 > 180 or angle2 < 0 or angle2 > 180:
                    print("Por favor, ingrese ángulos entre 0 y 180.")
                else:
                    # Aplicación de restricciones adicionales
                    if angle2 == 0:
                        if angle1 > 135:
                            print("El ángulo de Servo 1 no puede ser mayor a 135 cuando Servo 2 es 0.")
                        elif angle1 == 0:
                            print("El ángulo de Servo 1 no puede ser 0 cuando Servo 2 es 0.")
                        elif angle1 <= 30:
                            print("El ángulo de Servo 1 debe ser mayor a 30 cuando Servo 2 es 0.")
                        else:
                            # Ajuste de ángulos para el segundo servo
                            target_angle2 = 180 - angle2

                            move_servos_smoothly(s1, s2, current_angle1, angle1, current_angle2, target_angle2, 3000)  # 3000 milisegundos = 3 segundos
                            current_angle1 = angle1
                            current_angle2 = target_angle2
                            print("Ángulos establecidos: Servo 1 =", angle1, "grados, Servo 2 =", angle2, "grados")
                    elif angle2 == 180 and angle1 > 150:
                        print("El ángulo de Servo 1 no puede ser mayor a 150 cuando Servo 2 es 180.")
                    elif angle1 == 180 and (angle2 < 35 or angle2 > 165):
                        print("El ángulo de Servo 2 debe estar entre 35 y 165 cuando Servo 1 es 180.")
                    else:
                        # Ajuste de ángulos para el segundo servo
                        target_angle2 = 180 - angle2

                        move_servos_smoothly(s1, s2, current_angle1, angle1, current_angle2, target_angle2, 3000)  # 3000 milisegundos = 3 segundos
                        current_angle1 = angle1
                        current_angle2 = target_angle2
                        print("Ángulos establecidos: Servo 1 =", angle1, "grados, Servo 2 =", angle2, "grados")
            except ValueError:
                print("Por favor, ingrese números válidos o 'fin' para terminar.")

                print("Por favor, ingrese números válidos o 'fin' para terminar.")
