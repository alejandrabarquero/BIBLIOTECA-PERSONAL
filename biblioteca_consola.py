#Código "ORIGINAL" de la biblioteca personal 


#Bibliote/librería - Versión 2
from flask import Flask, jsonify, rquest, render_template
import json
import os

app = Flask(__name__)

ARCHIVO = "libros.json"
ESTADOS = {"1" : "Empezado",
            "2" : "En proceso", 
            "3": "Terminado", 
            "4":"No empezado"}
libros = []

def cargarArchivo():
    try: 
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        respaldo = ARCHIVO + ".danado"
        os.replace(ARCHIVO, respaldo)
        print(f"Advertencia: {ARCHIVO} estaba dañado. Se guardó una copia en {respaldo} y se empezará con una lista vacía.")
        return []

def guardarArchivo():

    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(libros , f, ensure_ascii=False, indent=4)

libros = cargarArchivo()

def agregarInfo():
    nombreLibro = input("Digite el nombre del libro: ").strip().lower()
    nombreAutor = input("Digite el nombre del autor del libro: ").strip().lower()
    cantidadPaginas = input("Digite la cantidad de páginas del libro: ").strip()
    for clave, nombre in ESTADOS.items():
        print(f"{clave}. {nombre}")
    estado = input("Seleccione el estado actual: ")
    if estado not in ESTADOS: 
        print("Opción Inválida, no se guardó la información.")
        return
    categoria = ESTADOS[estado]
    libro = {"nombredelLibro": nombreLibro.lower(),
            "nombredelAutor": nombreAutor.lower(), 
            "cantidadePaginas": cantidadPaginas, 
            "laCategoria": categoria}
    libros.append(libro)
    guardarArchivo() 
    print("¡Información guardada!") 

def categoria():

    print("\n-----Categoria-----")
    print("\n¿Cuál categoría desea ver?")
    for clave, nombre in ESTADOS.items():
        print(f"{clave}.{nombre}")
    print("5. Salir")
    opcionCategoria = input("Digite la opción que desea: ")

    if opcionCategoria == "5":
        print("----- ¡Adiós! ------")
        return
    if opcionCategoria not in ESTADOS:
        print("Opción inválida")
        return

    estado = ESTADOS[opcionCategoria]
    print(f"\n----- {estado} -----")
    librosFiltrados = [l for l in libros if l["laCategoria"] == estado]
    if not librosFiltrados: 
        print("No hay libros en esta categoría.")
        return
    for numero, libro in enumerate(librosFiltrados, start=1):
        print(f"{numero}.{libro["nombredelLibro"]}")
                

def consultarLibros():
    print("\n-----Libros Guardados:----- ")
    if not libros: 
        print("No hay libros guardados.")
    else:
        for numero, libro in enumerate(libros, start=1):
            print(f"{numero}.{libro["nombredelLibro"]}")
        print("\n*****************************")

#busqueda parcial usando enumerate/while
def buscarLibroporNombre(nombre):
    indice = 0 #empieza en el primer libro
    nombre = nombre.strip().lower()
    #mientras todavía queden libros por revisar y el libro que sale no es el que busco
    while indice < len(libros) and libros[indice]["nombredelLibro"].strip().lower() != nombre.lower():
        #entonces pasa al siguiente libro
        indice +=1
        #retorna el libro si se encuentra y sino retorna -1 que significa no encontrado
    return indice if indice < len(libros) else -1  

def eliminarLibros():
    if not libros:
        print("NO hay libros guardados")
        return

    print("\n-----Libros Guardados:----- ")
    for numero, libro in enumerate(libros, start=1):
        print(f"{numero}. {libro["nombredelLibro"]}")

    print("\n*****************************")
    print("\n----- Eliminar Libro -----")
    print("1. Eliminar")
    print("2. Salir")
    opcion = input("Digite la opción que desee: ")

    if opcion == "1":
        buscarLibro = input("Digite el número del libro que desea eliminar: ").strip()
        if not buscarLibro.isdigit() or not (1 <= int(buscarLibro) <= len(libros)):
            print("----- Número inválido -----")
            return
        libroEncontrado = libros.pop(int(buscarLibro)-1)
        guardarArchivo()
        print(f"----- Libro '{libroEncontrado['nombredelLibro']}' eliminado -----")
    elif opcion == "2":
        print("------ Adiós -----")
    else:
        print("Opción Inválida")
   

def actualizarInfoLibro():
   
    if not libros:
        print("NO hay libros guardados")
        return

    consultarLibros()
    libroActualizado = input("Digite el número del libro que desea actualizar: ").strip()
    if not libroActualizado.isdigit() or not (1 <= int(libroActualizado) <= len(libros)):
        print("\n----- Número inválido -----")
        return
    libro = libros[int(libroActualizado) -1]

    print("\n-----¿Qué desea actualizar?-----")
    print("1. Nombre")
    print("2. Autor")
    print("3. Cantidad de páginas")
    print("4. Estado")
    option = input("Digite el número de la opción que desea: ")

    if option == "1":
        libro["nombredelLibro"] = input("Digite nuevo nombre: ").strip().lower()
    elif option == "2":
        libro["nombredelAutor"] = input("Digite el nuevo autor: ").strip().lower()
    elif option == "3":
        libro["cantidadePaginas"] = input("Digite la cantidad de páginas del libro: ").strip()
    elif option == "4":
        for clave, nombre in ESTADOS.items():
            print(f"{clave}. {nombre}")
        estadoActualizado = input("Digite el nuevo estado del libro: ").strip()
        if estadoActualizado not in ESTADOS:
            print("\n-----Opción inválida -----")
            return
        libro["laCategoria"] = ESTADOS[estadoActualizado]
    else:
        print("\n-----Opción inválida, ¡vuelve a intentarlo!-----")
        return
    
    guardarArchivo()
    print("\n----- Actualización guardada -----")



def menu_principal():
    while True: 
        print("\n----- Menú Principal ----- ")
        print("1. Añadir libro")
        print("2. Ver clasificaciones de libros ")
        print("3. Consultar Libros ")
        print("4. Eliminar Libros")
        print("5. Actualizar información guardada ")
        print("6. Salir")

        opcion = input("Digite el número de la opción que desee: ")
        if opcion == "1":
               agregarInfo()
        elif opcion == "2":
                categoria()
        elif opcion == "3":
            consultarLibros()
        elif opcion == "4":
            eliminarLibros()
        elif opcion == "5":
           actualizarInfoLibro()
        elif opcion == "6": 
            print("¡Adiós!")
            break
        else:
            print("Opción inválida, intente de nuevo.")

libros = cargarArchivo()       
menu_principal()
         
