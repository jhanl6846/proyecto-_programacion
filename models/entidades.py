# models/entidades.py
from werkzeug.security import generate_password_hash, check_password_hash


def hashear_contrasena(contrasena_plana: str) -> str:
    """Genera un hash seguro (scrypt) de la contraseña en texto plano.
    Usar esta función antes de guardar cualquier contraseña en la BD."""
    return generate_password_hash(contrasena_plana)


class Empleado:
    """Superclase Base que mapea la tabla 'empleados'"""
    def __init__(self, id_emp, nombre, rango, contrasena, edad, cedula, direccion, telefono):
        self.id = id_emp
        self.nombre = nombre
        self.rango = rango
        self._contrasena_hash = contrasena  # Siempre es el hash almacenado en BD
        self.edad = edad
        self.cedula = cedula
        self.direccion = direccion
        self.telefono = telefono

    @classmethod
    def desde_fila_db(cls, fila):
        """Crea un objeto Empleado a partir de una fila de la base de datos."""
        if not fila:
            return None
        return cls(
            id_emp=fila["id"], nombre=fila["nombre"], rango=fila["rango"],
            contrasena=fila["contrasena"], edad=fila["edad"], cedula=fila["cedula"],
            direccion=fila["direccion"], telefono=fila["telefono"]
        )

    def verificar_contrasena(self, contrasena_ingresada: str) -> bool:
        """Compara la contraseña ingresada contra el hash almacenado en BD."""
        return check_password_hash(self._contrasena_hash, contrasena_ingresada)

    def obtener_permisos(self):
        return ["ver_catalogo"]


# HERENCIA: Administrador y Vendedor heredan de Empleado
class Administrador(Empleado):
    def obtener_permisos(self):  # POLIMORFISMO
        return ["ver_catalogo", "gestionar_empleados", "aplicar_descuentos", "ver_ventas_globales"]

class Vendedor(Empleado):
    def obtener_permisos(self):  # POLIMORFISMO
        return ["ver_catalogo", "registrar_cliente", "registrar_venta"]


class Juego:
    """Clase que mapea la tabla 'juegos'"""
    def __init__(
        self,
        id_juego,
        title,
        precio,
        calificacion,
        stock,
        genre,
        platform,
        publisher,
        developer,
        release_date,
        short_description,
        thumbnail,
        game_url,
    ):
        self.id = id_juego
        self.title = title
        self.precio = precio
        self.calificacion = calificacion
        self.stock = stock
        self.genre = genre
        self.platform = platform
        self.publisher = publisher
        self.developer = developer
        self.release_date = release_date
        self.short_description = short_description
        self.thumbnail = thumbnail
        self.game_url = game_url

    @classmethod
    def desde_fila_db(cls, fila):
        if not fila:
            return None
        return cls(
            id_juego=fila["id"], title=fila["title"], precio=fila["precio"],
            calificacion=fila["calificacion"], stock=fila["stock"], genre=fila["genre"],
            platform=fila["platform"], publisher=fila["publisher"],
            developer=fila["developer"], release_date=fila["release_date"],
            short_description=fila["short_description"], thumbnail=fila["thumbnail"],
            game_url=fila["game_url"]
        )

    def reducir_stock(self, cantidad):
        """Lógica de negocio: Modifica el atributo stock si hay suficiente"""
        if self.stock >= cantidad:
            self.stock -= cantidad
            return True
        return False


class Cliente:
    """Clase que mapea la tabla 'clientes'"""
    def __init__(self, id_cliente, nombre, edad, cedula, direccion, telefono):
        self.id = id_cliente
        self.nombre = nombre
        self.edad = edad
        self.cedula = cedula
        self.direccion = direccion
        self.telefono = telefono

    @classmethod
    def desde_fila_db(cls, fila):
        if not fila:
            return None
        return cls(
            id_cliente=fila["id"], nombre=fila["nombre"], edad=fila["edad"],
            cedula=fila["cedula"], direccion=fila["direccion"], telefono=fila["telefono"]
        )
