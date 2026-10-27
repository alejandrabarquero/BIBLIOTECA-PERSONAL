#Biblioteca personal 
#Versión 3
from flask import Flask, jsonify, request, render_template
from datetime import date
import json
import os

app = Flask(__name__)

ARCHIVO = "libros.json"
ESTADOS = {"Empezado", "En proceso", "Terminado", "No empezado"}

# Claves viejas -> claves nuevas (para migrar libros.json existente)
CLAVES_ANTIGUAS = {
    "nombredelLibro": "nombre",
    "nombredelAutor": "autor",
    "cantidadePaginas": "paginas",
    "laCategoria": "estado",
}

def aEntero(valor):
    """Convierte a entero >= 0. Devuelve None si no es válido."""
    try:
        return max(0, int(valor or 0))
    except (ValueError, TypeError):
        return None
def ajustarEstado(libro):
    """Sube el estado según el avance. Nunca lo baja."""
    total = aEntero(libro.get("paginas")) or 0
    leidas = aEntero(libro.get("leidas")) or 0
    if total and leidas >= total:
        libro["estado"] = "Terminado"
    elif leidas > 0 and libro["estado"] == "No empezado":
        libro["estado"] = "En proceso"


def migrar(lista):
    for libro in lista:
        for vieja, nueva in CLAVES_ANTIGUAS.items():
            if vieja in libro:
                libro[nueva] = libro.pop(vieja)
        libro.setdefault("favorito", False)
        libro.setdefault("leidas", 0)
    return lista

def cargarArchivo():
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return migrar(json.load(f))
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        respaldo = ARCHIVO + ".danado"
        os.replace(ARCHIVO, respaldo)
        print(f"Advertencia: {ARCHIVO} estaba dañado. Copia en {respaldo}.")
        return []

def guardarArchivo():
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(libros, f, ensure_ascii=False, indent=4)

libros = cargarArchivo()

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/api/libros", methods=["GET"])
def listar():
    resultado = [{**libro, "indice": i} for i, libro in enumerate(libros)]
    estado = request.args.get("estado")
    if estado:
        resultado = [l for l in resultado if l.get("estado") == estado]
    return jsonify(resultado)

@app.route("/api/libros", methods=["POST"])
def agregar():
    datos = request.get_json(silent=True) or {}   # no revienta si no llega JSON

    nombre = str(datos.get("nombre", "")).strip()
    autor = str(datos.get("autor", "")).strip()
    paginas = str(datos.get("paginas", "")).strip()
    estado = datos.get("estado")
    leidas = aEntero(datos.get("leidas"))

    if not nombre or not autor:
        return jsonify({"error": "Nombre y autor son obligatorios"}), 400
    if estado not in ESTADOS:
        return jsonify({"error": "Estado inválido"}), 400
    if leidas is None:
        return jsonify({"error": "Páginas leídas debe ser un número"}), 400


    libro = {
        "nombre": nombre,
        "autor": autor,
        "paginas": paginas,
        "estado": estado,
        "fecha": date.today().isoformat(),   # para "+N este mes"
    }
    ajustarEstado()
    libros.append(libro)
    guardarArchivo()
    return jsonify({**libro, "indice": len(libros) - 1}), 201

@app.route("/api/libros/<int:indice>", methods=["PUT"])
def actualizar(indice):
    if not 0 <= indice < len(libros):
        return jsonify({"error": "Libro no encontrado"}), 404

    datos = request.get_json(silent=True) or {}
    libro = libros[indice]

    for clave in ("nombre", "autor", "paginas"):
        if clave in datos:
            libro[clave] = str(datos[clave]).strip()
    if "estado" in datos:
        if datos["estado"] not in ESTADOS:
            return jsonify({"error": "Estado inválido"}), 400
        libro["estado"] = datos["estado"]
    if "leidas" in datos:
        leidas = aEntero(datos["leidas"])
        if leidas is None:
            return jsonify({"error": "Páginas leídas debe ser un número"}), 400
        libro["leidas"] = leidas
    if "favorito" in datos:
        libro["favorito"] = bool(datos["favorito"])
    ajustarEstado()
    guardarArchivo()
    return jsonify(libro)

@app.route("/api/libros/<int:indice>", methods=["DELETE"])
def eliminar(indice):
    if not 0 <= indice < len(libros):
        return jsonify({"error": "Libro no encontrado"}), 404
    eliminado = libros.pop(indice)
    guardarArchivo()
    return jsonify(eliminado)

if __name__ == "__main__":
    app.run(debug=True)