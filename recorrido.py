"""
Guía de referencia — recorrido sobre la red de dependencias.

Este archivo NO es importado por la consulta de impacto (`impacto.py`).
La panadería ya puede consultar disponibilidad e impacto de punta a punta
sin este módulo. Aquí queda el contrato y un ejemplo de algoritmo para
quien vaya a especializar o sustituir solo la forma de caminar el grafo.

Contrato sugerido
-----------------
Función: recorrer_red(grafo, id_inicio) -> list[str]

Debe:
  1. Partir del elemento que se supone no disponible.
  2. Seguir la regla de negocio: si lo requerido cayó, quien lo requiere
     también queda no operable (caminar EN CONTRA de aristas REQUIERE).
  3. Devolver ids sin duplicados; el primero es siempre id_inicio.
  4. Usar un orden comprensible (por capas, por descubrimiento, etc.).

Dirección del grafo
-------------------
  origen REQUIERE destino
  producto → insumo → proveedor

Ejemplo: PRD-PAN → INS-HARINA → PRV-MATERIAPRIMA
  "Para producir pan necesito harina; la harina la trae ese proveedor."

Cómo conectarlo más adelante (opcional)
--------------------------------------
En impacto.py existe `_recorrido_externo`. Si se asigna una función con
la firma de arriba, la consulta de impacto usará ese caminar en lugar
del interno. Ejemplo:

    import impacto
    import recorrido
    impacto._recorrido_externo = recorrido.recorrer_red

Mientras no se asigne nada, el producto sigue funcionando igual.

Consumo desde la interfaz
-------------------------
La interfaz no debe llamar este módulo. Debe usar:

    GET /impacto/{elemento_id}

y resaltar en pantalla los campos `visitados` / `afectados`.
"""

from __future__ import annotations

from models import Grafo


def recorrer_red(grafo: Grafo, id_inicio: str) -> list[str]:
    """
    Ejemplo de recorrido propio (referencia).

    Propagación por punto fijo sobre la lista de aristas:
      - bolsa inicial = {id_inicio}
      - si destino está caído y origen no, el origen también cae
      - repetir hasta que no entre nadie nuevo

    Quien especialice el recorrido puede reemplazar este cuerpo
    (BFS, DFS, cola, etc.) respetando el contrato del módulo.
    """
    visitados: list[str] = [id_inicio]
    en_bolsa = {id_inicio}
    cambio = True

    while cambio:
        cambio = False
        for arista in grafo.aristas:
            if arista.destino in en_bolsa and arista.origen not in en_bolsa:
                en_bolsa.add(arista.origen)
                visitados.append(arista.origen)
                cambio = True

    return visitados
