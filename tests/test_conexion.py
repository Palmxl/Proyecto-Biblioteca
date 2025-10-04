from gestor_almacenamiento.gestor_db import GestorBD

bd = GestorBD()
print("Conexión exitosa con la BD")

print("\n--- Prueba préstamo ---")
print(bd.prestar_libro("789", "hammer"))

print("\n--- Prueba renovación ---")
print(bd.renovar_libro("789", "hammer"))

print("\n--- Prueba devolución ---")
print(bd.devolver_libro("789", "hammer"))

bd.close()
print("\nConexión cerrada correctamente")
