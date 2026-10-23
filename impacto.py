"""
Consulta de disponibilidad e impacto sobre la red de abastecimiento.

Propósito de producto
---------------------
Cuando un proveedor, un insumo o un producto deja de estar disponible,
producción necesita saber qué más de la panadería queda comprometido.
Esta capa responde esa pregunta de negocio sin depender de otros módulos
de recorrido: trae su propia propagación sobre el grafo.

Modelo de dependencias
----------------------
Cada arista se interpreta: origen REQUIERE destino
  producto → insumo → proveedor

La falla se propaga en sentido contrario a la flecha:
  si lo requerido no está, quien lo requiere tampoco puede operar.

API HTTP
--------
GET /impacto/{elemento_id}

Contrato de respuesta (`ImpactoResponse`):
  - inexistente       → el id no está en el catálogo
  - sin_dependencias  → existe, pero nadie más queda comprometido
  - afecta_cadena     → hay elementos alcanzados en la red

Punto de extensión (opcional)
-----------------------------
Si más adelante se quiere sustituir solo la forma de caminar el grafo,
asignar una función a `_recorrido_externo` con la firma:

    (grafo: Grafo, id_inicio: str) -> list[str]

Esa función debe devolver los ids visitados (el primero = id_inicio).
Mientras `_recorrido_externo` sea None, se usa la propagación interna.
Ver `recorrido.py` como guía de referencia para ese contrato.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Optional

from models import Grafo, ImpactoResponse, Nodo, NodoImpactado

# Extensión opcional: no se importa ningún módulo externo de recorrido.
# Si se asigna una función aquí, reemplaza solo el caminar del grafo.
_recorrido_externo: Optional[Callable[[Grafo, str], list[str]]] = None


def _a_nodo_impactado(nodo: Nodo) -> NodoImpactado:
    return NodoImpactado(id=nodo.id, nombre=nodo.nombre, capa=nodo.capa)


def _buscar(grafo: Grafo, elemento_id: str) -> Nodo | None:
    for nodo in grafo.nodos:
        if nodo.id == elemento_id:
            return nodo
    return None


def _propagar_indisponibilidad(grafo: Grafo, id_inicio: str) -> list[str]:
    """
    Propaga la indisponibilidad sobre la red.

    Empieza en id_inicio y, mientras haya novedades, marca como no
    operables a quienes REQUIEREN algo que ya quedó indisponible
    (recorre en contra de las aristas).
    """
    visitados: list[str] = [id_inicio]
    caidos = {id_inicio}
    cambio = True

    while cambio:
        cambio = False
        for arista in grafo.aristas:
            if arista.destino in caidos and arista.origen not in caidos:
                caidos.add(arista.origen)
                visitados.append(arista.origen)
                cambio = True

    return visitados


def _ids_alcanzados(grafo: Grafo, elemento_id: str) -> list[str]:
    if _recorrido_externo is not None:
        return _recorrido_externo(grafo, elemento_id)
    return _propagar_indisponibilidad(grafo, elemento_id)


def consultar_impacto(grafo: Grafo, elemento_id: str) -> ImpactoResponse:
    """
    Simula que `elemento_id` no está disponible y reporta el impacto
    sobre la cadena de abastecimiento de la panadería.
    """
    origen = _buscar(grafo, elemento_id)

    if origen is None:
        return ImpactoResponse(
            origen=None,
            caso="inexistente",
            mensaje=f"No existe el elemento '{elemento_id}' en el catálogo.",
            visitados=[],
            afectados=[],
        )

    ids_visitados = _ids_alcanzados(grafo, elemento_id)

    nodos_por_id = {nodo.id: nodo for nodo in grafo.nodos}
    visitados: list[NodoImpactado] = []
    for vid in ids_visitados:
        nodo = nodos_por_id.get(vid)
        if nodo is not None:
            visitados.append(_a_nodo_impactado(nodo))

    afectados = [n for n in visitados if n.id != elemento_id]

    if not afectados:
        return ImpactoResponse(
            origen=_a_nodo_impactado(origen),
            caso="sin_dependencias",
            mensaje=(
                f"'{origen.nombre}' ({origen.id}) está en el catálogo, pero "
                "ningún otro elemento de la red depende de él: su "
                "indisponibilidad no compromete la producción."
            ),
            visitados=visitados,
            afectados=[],
        )

    return ImpactoResponse(
        origen=_a_nodo_impactado(origen),
        caso="afecta_cadena",
        mensaje=(
            f"Si '{origen.nombre}' ({origen.id}) no está disponible, "
            f"quedan comprometidos {len(afectados)} elemento(s) de la red."
        ),
        visitados=visitados,
        afectados=afectados,
    )


def simular_indisponibilidad(grafo: Grafo, elemento_id: str) -> ImpactoResponse:
    """Alias de negocio: consultar impacto = simular indisponibilidad."""
    return consultar_impacto(grafo, elemento_id)
