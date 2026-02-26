from werkzeug.security import generate_password_hash
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '6SK_@mtP!cT7MeI4', 
    'database': 'registrohorasss'
}

def fix_passwords():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 1. Obtener todos los usuarios
    cursor.execute("SELECT id_usuario, password_hash FROM usuarios")
    usuarios = cursor.fetchall()

    print(f"Procesando {len(usuarios)} usuarios...")

    for user in usuarios:
        pass_actual = user['password_hash']
        
        # 2. Verificar si ya es un hash (los hashes de Werkzeug suelen empezar con 'scrypt' o 'pbkdf2')
        if not pass_actual.startswith(('scrypt:', 'pbkdf2:')):
            # Es texto plano, hay que hashearlo
            nuevo_hash = generate_password_hash(pass_actual)
            
            # 3. Actualizar en la base de datos
            cursor.execute(
                "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s",
                (nuevo_hash, user['id_usuario'])
            )
            print(f"Usuario ID {user['id_usuario']} actualizado.")

    conn.commit()
    cursor.close()
    conn.close()
    print("¡Listo! Todas las contraseñas han sido hasheadas.")

if __name__ == "__main__":
    fix_passwords()