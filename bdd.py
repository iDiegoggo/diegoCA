import sqlite3
import os

# ruta del archivo index.txt generado por openssl
ruta_index = "/home/dgarcia/diegoCA/index.txt"

# ruta donde guardamos la base de datos
ruta_db = "/home/dgarcia/diegoCA/database/certificados.db"

# si no existe el directorio para la base de datos, lo creamos
os.makedirs(os.path.dirname(ruta_db), exist_ok=True)

# conectamos con la base de datos (si no existe se crea)
conn = sqlite3.connect(ruta_db)
cursor = conn.cursor()

# borramos todo lo que hay en las tablas antes de insertar datos nuevos
cursor.execute("DROP TABLE IF EXISTS revocaciones;")
cursor.execute("DROP TABLE IF EXISTS certificados;")

# volvemos a crear las tablas vacías
cursor.execute("""
CREATE TABLE certificados (
    numero_serie TEXT PRIMARY KEY,
    nombre_comun TEXT,
    sujeto TEXT,
    emisor TEXT,
    estado TEXT
);
""")

cursor.execute("""
CREATE TABLE revocaciones (
    numero_serie TEXT PRIMARY KEY,
    fecha_revocacion TEXT,
    FOREIGN KEY(numero_serie) REFERENCES certificados(numero_serie)
);
""")

# función para extraer el CN del sujeto
def extraer_cn(sujeto):
    for parte in sujeto.split("/"):
        if parte.startswith("CN="):
            return parte[3:]
    return "desconocido"

# procesamos el archivo index.txt
with open(ruta_index, "r") as f:
    for linea in f:
        partes = linea.strip().split("\t")
        if len(partes) < 6:
            continue  # línea mal formada

        estado_raw = partes[0]
        fecha_expiracion = partes[1]
        fecha_revocacion = partes[2] if estado_raw == "R" else None
        numero_serie = partes[3]
        sujeto = partes[5]
        emisor = "diegoCA"  # valor fijo
        nombre_comun = extraer_cn(sujeto)

        # traducimos estado
        estado = {
            "V": "valido",
            "R": "revocado",
            "E": "expirado"
        }.get(estado_raw, "desconocido")

        # insertamos en certificados
        cursor.execute("""
            INSERT OR REPLACE INTO certificados (numero_serie, nombre_comun, sujeto, emisor, estado)
            VALUES (?, ?, ?, ?, ?)
        """, (numero_serie, nombre_comun, sujeto, emisor, estado))

        # si está revocado, insertamos también en revocaciones
        if estado == "revocado" and fecha_revocacion:
            cursor.execute("""
                INSERT OR REPLACE INTO revocaciones (numero_serie, fecha_revocacion)
                VALUES (?, ?)
            """, (numero_serie, fecha_revocacion))

# guardamos y cerramos
conn.commit()
conn.close()
print("Base de datos actualizada con éxito.")
