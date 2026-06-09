# routes/ventas.py
# Rutas para el registro de nuevas ventas

from flask import Blueprint, request, redirect, url_for, session, flash
from models.database import get_db
from utils.decorators import requiere_login
from datetime import datetime, timedelta

ventas_bp = Blueprint("ventas", __name__)

OFFSET_COLOMBIA = timedelta(hours=5)

CLIENTE_ANONIMO_ID   = "C000"
CLIENTE_ANONIMO_NOMBRE = "cliente anónimo"


def _asegurar_cliente_anonimo(conn):
    """Crea el cliente anónimo si no existe."""
    existe = conn.execute("SELECT id FROM clientes WHERE id = ?", (CLIENTE_ANONIMO_ID,)).fetchone()
    if not existe:
        conn.execute(
            "INSERT OR IGNORE INTO clientes (id, nombre, edad, cedula, direccion, telefono) VALUES (?,?,?,?,?,?)",
            (CLIENTE_ANONIMO_ID, CLIENTE_ANONIMO_NOMBRE, 0, 0, "—", "—"),
        )
        conn.commit()


@ventas_bp.route("/nueva", methods=["POST"])
@requiere_login
def nueva_venta():
    juego_id  = int(request.form["juego_id"])
    cliente_id = request.form.get("cliente_id", "").strip()
    cantidad  = int(request.form.get("cantidad", 1))

    conn = get_db()

    # Si no se seleccionó cliente, usar el anónimo
    if not cliente_id:
        _asegurar_cliente_anonimo(conn)
        cliente_id = CLIENTE_ANONIMO_ID

    juego   = conn.execute("SELECT * FROM juegos WHERE id = ?", (juego_id,)).fetchone()
    cliente = conn.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,)).fetchone()

    if not juego or not cliente:
        flash("Juego o cliente no válido.", "error")
        conn.close()
        return redirect(url_for("juegos.catalogo"))

    if juego["stock"] < cantidad:
        flash(f"Stock insuficiente. Disponible: {juego['stock']}", "error")
        conn.close()
        return redirect(url_for("juegos.detalle", juego_id=juego_id))

    total = juego["precio"] * cantidad
    fecha_colombia = (datetime.utcnow() - OFFSET_COLOMBIA).strftime("%Y-%m-%d %H:%M:%S")

    conn.execute(
        """
        INSERT INTO ventas
            (cliente_id, cliente_nombre, juego_id, juego_nombre,
             cantidad, precio_unitario, total, vendedor, fecha)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            cliente["id"], cliente["nombre"],
            juego["id"], juego["title"],
            cantidad, juego["precio"], total,
            session["empleado_nombre"],
            fecha_colombia,
        ),
    )
    conn.execute("UPDATE juegos SET stock = stock - ? WHERE id = ?", (cantidad, juego_id))
    conn.commit()
    conn.close()

    etiqueta = "anónimo" if cliente_id == CLIENTE_ANONIMO_ID else cliente["nombre"]
    flash(f"Venta registrada — {etiqueta} — Total: ${total:,.2f}", "success")
    return redirect(url_for("juegos.detalle", juego_id=juego_id))
