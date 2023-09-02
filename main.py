#sistema que controle la entrada y salida a un parqueo e histolial de los vehiculos que ingresan y salen del parqueoimport psycopg2
import psycopg2
import psycopg2.extras
import datetime

#
conn = psycopg2.connect(
    host="localhost",
    dbname="postgres",
    user="postgres",
    password="12345",
    port="5432"
)
cur =   conn.cursor()

#creador de tablas
cur.execute("""CREATE TABLE IF NOT EXISTS autos(
            id SERIAL PRIMARY KEY,
            marca VARCHAR(255),
            color  VARCHAR(255),
            hora_ingreso TIMESTAMP,
            hora_salida TIMESTAMP,
            hora_total INTERVAL
            );""")

cur.execute("""CREATE TABLE IF NOT EXISTS historial(
            id SERIAL PRIMARY KEY,
            id_auto INT,
            marca VARCHAR(255),
            color  VARCHAR(255),
            hora_ingreso TIMESTAMP,
            hora_salida TIMESTAMP,
            hora_total INTERVAL
            );""")


def get_current_datetime():
    return datetime.datetime.now()

#sistemas de entrada de autos
hora_salida = None
hora_total = None
def ingreso_de_autos():
    marca = input("Ingrese marca del auto: ")
    color = input("Ingrese color del auto: ")
    hora_ingreso = get_current_datetime().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute(
        "INSERT INTO autos (marca, color, hora_ingreso) VALUES (%s, %s, %s) RETURNING id", 
        (marca, color, hora_ingreso)
        )
    id_auto = cur.fetchone()[0]
    conn.commit()

    print("Auto ingresado con ID:", id_auto)
    cur.execute(
        "INSERT INTO historial (id_auto, marca, color, hora_ingreso, hora_salida, hora_total) VALUES (%s, %s, %s, %s, %s, %s)", 
        (id_auto, marca, color, hora_ingreso, hora_salida, hora_total)
        )
    conn.commit()

#sistema de salida de autos
def salida_de_autos():
    autos = []
    cur.execute("SELECT id, marca, color FROM autos")
    autos = cur.fetchall()
    print("Autos en el parqueo:")
    for auto in autos:
        print( "ID:", auto[0], "\tMarca:", auto[1], "\tColor:", auto[2])

    id_auto = int(input("Ingrese id del auto: "))
    hora_salida = get_current_datetime().strftime("%Y-%m-%d %H:%M:%S")
   

    cur.execute(
        "UPDATE historial SET hora_salida = %s WHERE id = %s", 
        (hora_salida, id_auto)
        )
    conn.commit()

    cur.execute("SELECT hora_ingreso, hora_salida FROM historial WHERE id = %s", (id_auto,))
    fila = cur.fetchone()
    if fila[0] and fila[1]:
        tiempo = fila[1] - fila[0]
        print("Tiempo estacionado:", tiempo)
        cur.execute("UPDATE historial SET hora_total = %s WHERE id = %s", (tiempo, id_auto))
        conn.commit()
    else:
        print("El auto no ha salido")
    
    cur.execute("DELETE FROM autos WHERE id = %s", (id_auto,))
    conn.commit()
    

#sistema de informes
def informes():
    def autos_estacionados():
        cur.execute("SELECT * FROM autos")
        autos = cur.fetchall()
        print("Autos estacionados:")
        for auto in autos:
            print()
            print("ID:", auto[0], "\tMarca:", auto[1], "\tColor:", auto[2], "\tHora de ingreso:", auto[3])
            print()

    def historial():
        cur.execute("SELECT * FROM historial")
        historial = cur.fetchall()
        print("Historial de autos:")
        for auto in historial:
            print()
            print("ID:", auto[0], "\tMarca:", auto[2], "\tColor:", auto[3], "\tHora de ingreso:", auto[4], "\tHora de salida:", auto[5], "\tTiempo total:", auto[6])
            print()

    


    while True:
        print("1. Autos estacionados")
        print("2. Historial de autos")
        print("3. Salir")
        opcion = int(input("Ingrese una opcion: "))

        if opcion == 1:
            autos_estacionados()
        elif opcion == 2:
            historial()
        elif opcion == 3:
            break
        else:
            print("Opcion incorrecta")

def menu():
    while True:
        print("1. Ingreso de autos")
        print("2. Salida de autos")
        print("3. Reporte de autos")
        print("4. Salir")
        opcion = int(input("Ingrese una opcion: "))

        if opcion == 1:
            ingreso_de_autos()
        elif opcion == 2:
            salida_de_autos()
        elif opcion == 3:
            informes()
        elif opcion == 4:
            break
        else:
            print("Opcion incorrecta")
menu()

conn.commit()
cur.close()
conn.close()                