# routes/vendedor.py
# Rutas del panel del vendedor: dashboard y gestión de clientes

import random
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.database import get_db
from utils.decorators import requiere_login

vendedor_bp = Blueprint("vendedor", __name__)

CLIENTE_ANONIMO_ID = "C000"


def _siguiente_cliente_id(conn):
    max_id = conn.execute(
        "SELECT MAX(CAST(SUBSTR(id, 2) AS INTEGER)) FROM clientes WHERE id != ?",
        (CLIENTE_ANONIMO_ID,),
    ).fetchone()[0]
    return f"C{(max_id or 0) + 1:03}"


@vendedor_bp.route("/")
@requiere_login
def dashboard():
    """
    Mostrar el panel principal del vendedor con sus estadísticas.
    ---
    tags:
      - Vendedor
    responses:
      200:
        description: Página HTML del dashboard del vendedor con totales de juegos, clientes y sus ventas.
      302:
        description: Redirección al login si no hay sesión activa.
    """
    conn = get_db()
    stats = {
        "total_juegos":   conn.execute("SELECT COUNT(*) FROM juegos").fetchone()[0],
        "total_clientes": conn.execute(
            "SELECT COUNT(*) FROM clientes WHERE id != ?",
            (CLIENTE_ANONIMO_ID,),
        ).fetchone()[0],
        "mis_ventas":     conn.execute(
            "SELECT COUNT(*) FROM ventas WHERE vendedor = ?",
            (session["empleado_nombre"],),
        ).fetchone()[0],
    }
    conn.close()
    return render_template("vendedor/dashboard.html", **stats)


@vendedor_bp.route("/ventas")
@requiere_login
def mis_ventas():
    conn = get_db()
    ventas = conn.execute(
        "SELECT * FROM ventas WHERE vendedor = ? ORDER BY fecha DESC",
        (session["empleado_nombre"],),
    ).fetchall()
    conn.close()
    return render_template("admin/ventas.html", ventas=ventas)


@vendedor_bp.route("/clientes")
@requiere_login
def lista_clientes():
    """
    Listar todos los clientes registrados (vista vendedor).
    ---
    tags:
      - Vendedor
    responses:
      200:
        description: Página HTML con la lista de clientes.
      302:
        description: Redirección al login si no hay sesión activa.
    """
    conn = get_db()
    clientes = conn.execute(
        "SELECT * FROM clientes WHERE id != ?",
        (CLIENTE_ANONIMO_ID,),
    ).fetchall()
    conn.close()
    return render_template("vendedor/clientes.html", clientes=clientes)


@vendedor_bp.route("/clientes/nuevo", methods=["GET", "POST"])
@requiere_login
def nuevo_cliente():
    """
    Mostrar formulario o registrar un nuevo cliente desde el panel vendedor.
    ---
    tags:
      - Vendedor
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: nombre
        in: formData
        type: string
        required: true
        description: Nombre completo del cliente.
      - name: edad
        in: formData
        type: integer
        required: true
        description: Edad del cliente.
      - name: cedula
        in: formData
        type: integer
        required: true
        description: Número de cédula (único).
      - name: direccion
        in: formData
        type: string
        required: false
        description: Dirección (se genera aleatoriamente si se omite).
      - name: telefono
        in: formData
        type: string
        required: false
        description: Teléfono (se genera aleatoriamente si se omite).
    responses:
      200:
        description: Página HTML del formulario de creación.
      302:
        description: Redirección a la lista de clientes tras crear correctamente.
    """
    if request.method == "POST":
        conn = get_db()
        nuevo_id = _siguiente_cliente_id(conn)
        try:
            conn.execute(
                """
                INSERT INTO clientes (id, nombre, edad, cedula, direccion, telefono)
                VALUES (?,?,?,?,?,?)
                """,
                (
                    nuevo_id,
                    request.form["nombre"].lower(),
                    int(request.form["edad"]),
                    int(request.form["cedula"]),
                    request.form.get("direccion") or
                        f"carrera {random.randint(1, 100)} # {random.randint(1, 100)}-{random.randint(1, 100)}",
                    request.form.get("telefono") or
                        str(random.randint(3_000_000_000, 3_999_999_999)),
                ),
            )
            conn.commit()
            flash(f"Cliente {nuevo_id} registrado con éxito.", "success")
        except Exception as e:
            flash(f"Error: {e}", "error")
        finally:
            conn.close()
        return redirect(url_for("vendedor.lista_clientes"))

    return render_template("vendedor/nuevo_cliente.html")
