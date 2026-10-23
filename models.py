from typing import Literal, Optional, List
from pydantic import BaseModel, Field

Capa = Literal["producto", "insumo", "proveedor"]


class Nodo(BaseModel):
    id: str
    nombre: str
    capa: Capa
    categoria: Optional[str] = None


class Arista(BaseModel):
    id: str
    origen: str   
    destino: str  
    tipo: Literal["REQUIERE"]


class Grafo(BaseModel):
    nodos: List[Nodo]
    aristas: List[Arista]

class ProveedorCreate(BaseModel):
    id: str
    nombre: str
    categoria: Optional[str] = None


class InsumoCreate(BaseModel):
    id: str
    nombre: str
    categoria: Optional[str] = None
    proveedor_id: str


class ProductoCreate(BaseModel):
    id: str
    nombre: str
    categoria: Optional[str] = None
    insumo_ids: List[str] = Field(min_length=1)


# --- Disponibilidad e impacto sobre la red de abastecimiento ---

CasoImpacto = Literal[
    "inexistente",
    "sin_dependencias",
    "afecta_cadena",
]


class NodoImpactado(BaseModel):
    """Elemento de la red alcanzado al simular una indisponibilidad."""

    id: str
    nombre: str
    capa: Capa


class ImpactoResponse(BaseModel):
    """
    Resultado de preguntar: si este elemento no está disponible,
    ¿qué queda comprometido en la panadería?

    - origen: elemento consultado (None si el id no existe).
    - caso: inexistente | sin_dependencias | afecta_cadena
    - visitados: elementos alcanzados en orden (incluye el origen).
    - afectados: visitados sin el origen (cadena comprometida).
    """

    origen: Optional[NodoImpactado] = None
    caso: CasoImpacto
    mensaje: str
    visitados: List[NodoImpactado] = []
    afectados: List[NodoImpactado] = []