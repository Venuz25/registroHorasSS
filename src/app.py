from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '6SK_@mtP!cT7MeI4', 
    'database': 'registrohorasss'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM usuarios WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        if check_password_hash(user['password_hash'], password): 
            return jsonify({
                "status": "success",
                "message": "Login exitoso",
                "rol": user['rol'],
                "id_usuario": user['id_usuario']
            }), 200
        else:
            return jsonify({"status": "error", "message": "Contraseña incorrecta"}), 401
    else:
        return jsonify({"status": "error", "message": "Usuario no encontrado"}), 404

@app.route('/registro_alumno', methods=['POST'])
def registro_alumno():
    data = request.json
    
    email = data.get('email')
    password = data.get('password')
    nombre = data.get('nombre_completo')
    num_servicio = data.get('num_servicio')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')

    conn = get_db_connection()
    cursor = conn.cursor()

    try:        
        cursor.execute("SELECT id_usuario FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Este correo electrónico ya está registrado."}), 409

        cursor.execute("SELECT id_alumno FROM alumnos WHERE num_servicio = %s", (num_servicio,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Este Número de Servicio ya se encuentra registrado."}), 409

        cursor.execute("SELECT id_alumno FROM alumnos WHERE nombre_completo = %s", (nombre,))
        if cursor.fetchone():
            return jsonify({"status": "error", "message": "Ya existe un alumno registrado con ese nombre exacto."}), 409

        password_hash = generate_password_hash(password)
        query_user = "INSERT INTO usuarios (email, password_hash, rol) VALUES (%s, %s, 'alumno')"
        cursor.execute(query_user, (email, password_hash))
        id_usuario_generado = cursor.lastrowid

        query_alumno = """
            INSERT INTO alumnos (id_usuario, nombre_completo, num_servicio, fecha_inicio, fecha_termino)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query_alumno, (id_usuario_generado, nombre, num_servicio, fecha_inicio, fecha_fin))

        conn.commit()
        return jsonify({"status": "success", "message": "Alumno registrado correctamente"}), 201

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "message": f"Error de base de datos: {err}"}), 500
    
    finally:
        cursor.close()
        conn.close()

@app.route('/datos_alumno/<int:id_usuario>', methods=['GET'])
def datos_alumno(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT a.id_alumno, a.nombre_completo, a.fecha_inicio, a.fecha_termino,
               v.horas_totales_acumuladas, v.dias_asistidos
        FROM alumnos a
        LEFT JOIN vista_progreso_alumnos v ON a.id_alumno = v.id_alumno
        WHERE a.id_usuario = %s
    """
    cursor.execute(query, (id_usuario,))
    alumno = cursor.fetchone()
    
    if alumno:
        alumno['fecha_inicio'] = str(alumno['fecha_inicio'])
        alumno['fecha_termino'] = str(alumno['fecha_termino'])
        
        cursor.execute("SELECT * FROM bitacora_horas WHERE id_alumno = %s", (alumno['id_alumno'],))
        registros = cursor.fetchall()
        
        for reg in registros:
            reg['fecha_actividad'] = str(reg['fecha_actividad'])
            reg['horas'] = float(reg['horas']) 

        alumno['registros'] = registros
    
    cursor.close()
    conn.close()
    
    if alumno:
        return jsonify({"status": "success", "data": alumno}), 200
    else:
        return jsonify({"status": "error", "message": "Alumno no encontrado"}), 404

@app.route('/guardar_dia', methods=['POST'])
def guardar_dia():
    data = request.json
    id_alumno = data.get('id_alumno')
    fecha = data.get('fecha')
    tipo = data.get('tipo_dia')
    horas = data.get('horas', 0)
    descripcion = data.get('descripcion', '')

    if tipo != 'habil':
        horas = 0

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO bitacora_horas (id_alumno, fecha_actividad, horas, descripcion, tipo_dia)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            horas = VALUES(horas),
            descripcion = VALUES(descripcion),
            tipo_dia = VALUES(tipo_dia),
            fecha_captura = NOW()
        """
        cursor.execute(query, (id_alumno, fecha, horas, descripcion, tipo))
        conn.commit()
        return jsonify({"status": "success", "message": "Día guardado"}), 200

    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"status": "error", "message": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/lista_alumnos', methods=['GET'])
def admin_lista_alumnos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) as total FROM alumnos WHERE activo = 1")
        res_conteo = cursor.fetchone()
        conteo = res_conteo['total'] if res_conteo else 0

        query = """
            SELECT a.id_alumno, a.nombre_completo, a.num_servicio, 
                   a.fecha_inicio, a.fecha_termino, a.activo,
                   v.horas_totales_acumuladas, v.dias_asistidos
            FROM alumnos a
            LEFT JOIN vista_progreso_alumnos v ON a.id_alumno = v.id_alumno
            ORDER BY a.fecha_termino ASC
        """
        cursor.execute(query)
        alumnos = cursor.fetchall()

        for alu in alumnos:
            alu['fecha_inicio'] = str(alu['fecha_inicio'])
            alu['fecha_termino'] = str(alu['fecha_termino'])
            
            if alu.get('horas_totales_acumuladas') is None:
                alu['horas_totales_acumuladas'] = 0.0
            else:
                alu['horas_totales_acumuladas'] = float(alu['horas_totales_acumuladas'])

            if alu.get('dias_asistidos') is None:
                alu['dias_asistidos'] = 0

        return jsonify({"status": "success", "activos": conteo, "alumnos": alumnos}), 200

    except Exception as e:
        print(f"ERROR LISTA: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/detalle_alumno/<int:id_alumno>', methods=['GET'])
def admin_detalle_alumno(id_alumno):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        query = "SELECT * FROM bitacora_horas WHERE id_alumno = %s ORDER BY fecha_actividad DESC"
        cursor.execute(query, (id_alumno,))
        registros = cursor.fetchall()

        for reg in registros:
            reg['fecha_actividad'] = str(reg['fecha_actividad'])
            if reg.get('horas') is None: reg['horas'] = 0.0
            else: reg['horas'] = float(reg['horas'])

        return jsonify({"status": "success", "registros": registros}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/cambiar_estado', methods=['POST'])
def cambiar_estado():
    data = request.json
    id_alumno = data.get('id_alumno')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query = "UPDATE alumnos SET activo = NOT activo WHERE id_alumno = %s"
        cursor.execute(query, (id_alumno,))
        conn.commit()
        
        return jsonify({"status": "success", "message": "Estado actualizado"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)