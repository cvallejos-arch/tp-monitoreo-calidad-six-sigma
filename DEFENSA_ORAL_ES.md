# Guía para la defensa oral — Monitoreo de Calidad (QuantumTech Precision)

Para cada tema del programa de **Estructuras de Datos y Programación**: **dónde** está en el código (archivo → clase → método) y **por qué** se usó ahí. Al final, los errores que se pueden provocar en vivo, los casos límite y las preguntas más probables. El detalle técnico completo está en el [README](README.md).

---

## 1. El sistema en un minuto

**Problema:** QuantumTech usaba equipos vencidos, cerraba lotes incompletos y emitía reportes que no explicaban el rechazo. **Solución:** un sistema que valida todo antes de inspeccionar y decide la conformidad con reglas fijas.

**Flujo:** registrar (lote → muestras en una **cola**) → validar (certificación, equipo, estado) → evaluar (cada procedimiento a su manera: **polimorfismo**) → cerrar (CONFORME / NO_CONFORME, historial en una **pila**, reporte si es no conforme) → decidir el lote (rechazado si supera el 5 %) → atender reportes del más grave al menos grave (**heap**).

| Clase | Para qué está | Métodos clave |
|---|---|---|
| `Muestra` | Subconjunto del lote; la única que cambia su propio estado | `iniciar_inspeccion`, `agregar_defecto`, `cerrar` |
| `Lote` | Partida de componentes; decide aprobado o rechazado | `crear_muestra`, `decidir`, `porcentaje_no_conforme` |
| `Inspeccion` | Une muestra, profesional, equipo, procedimiento y fecha; **valida todo antes de empezar** | `__init__`, `ejecutar`, `cerrar` |
| `Procedimiento` (abstracta) | Contrato de evaluación; dos subclases con criterios distintos | `evaluar` |
| `Defecto` | Desviación inmutable; subclases visual y dimensional | `es_critico`, `copia`, `__lt__` |
| `Reporte` | Respaldo inmutable de una muestra no conforme | `gravedad_maxima`, `defectos_por_gravedad`, `to_dict` |
| `Empresa` | Punto de entrada: registra todo, consulta y serializa | `crear_registrar_*`, `lanzar_inspeccion`, `listar_*` |
| `ArbolAVL` / `ColaPrioridad` | Índices por fecha y orden de atención | `buscar`, `buscar_rango` / `insertar`, `extraer_maximo` |

---

## 2. Los temas del programa en el TP

### Unidad 1 — Todo en Python es un objeto
| Subtema | Dónde | Por qué ahí |
|---|---|---|
| `isinstance` | `Profesional.agregar_certificacion`, `Nodo.set_siguiente`, `Inspeccion.ejecutar` (defectos ajenos), `Empresa.cargar` | Verificar el **tipo** del objeto antes de aceptarlo protege las reglas (por ejemplo, que un archivo cargado sea de verdad una `Empresa`) |
| `is` vs `==` | `main.py` sección 6: la muestra cargada con pickle da `m0_cargada is m0` → `False` y `m0_cargada == m0` → `True` | Distinguir **identidad** (`is`: el mismo objeto en memoria) de **igualdad** (`==`): lo cargado es otro objeto, pero la misma entidad, porque `Entidad.__eq__` compara por id |
| `type(e).__name__` | `intentar` en `main.py`, `App._ejecutar` en `front/clase_app.py`, `ejecutar_opcion` en `consola.py` | Mostrar al usuario qué clase de error ocurrió |

### Unidad 2 — Tipos de datos
| Subtema | Dónde | Por qué ahí |
|---|---|---|
| Inmutables: **tuplas** | `Muestra.defectos`, `Lote.muestras`, `Reporte.defectos`, `Pila.historial()` | Se devuelven tuplas para que nadie modifique el estado interno desde afuera (encapsulamiento), como el ejemplo `Ciudad` de la clase 9 con `tuple(coordenadas)` |
| Mutables: listas y diccionarios | Listas internas (`Muestra._defectos`), registro de `Empresa` | Adentro del objeto se necesita poder agregar elementos |
| Strings | `validar_texto` (`isalpha`), `validar_nombre_tecnico` (`isalnum`), `ListaEnlazada.__str__` (`join`), f-strings en todos los mensajes | Validar nombres ("Ana 2" no es un nombre; "ISO 9001" sí es un nombre técnico) y armar mensajes claros |
| Copia superficial | `Profesional.certificaciones` devuelve `dict(...)` | Una copia del diccionario: modificarla no cambia al profesional |
| Copia de objetos | `Reporte` guarda `copia()` de cada defecto | El reporte no depende de los objetos originales |

### Unidad 3 — Bibliotecas y módulos
**Módulos y paquetes propios:** `classes/` (el dominio), `front/` y `front/paginas/` (la interfaz, un módulo por página); `interfaz.py` solo importa `App` y la abre.

**Bibliotecas:** `datetime` (`date`, `timedelta`: calibraciones, certificaciones, vencimientos) · `uuid` (ids únicos, regla 1) · `abc` (clase abstracta) · `json` y `pickle` (serialización) · `random` (simulador con semilla) · `functools.reduce` · `os` (borrar el archivo temporal en `main.py`) · `tkinter` (interfaz) · `pytest` (521 tests).

### Unidad 4 — Funciones
| Subtema | Dónde | Por qué ahí |
|---|---|---|
| Parámetros por defecto | `Cola(tipo=None, maxsize=None)`, `Simulador(semilla=None)`, `cola_atencion_reportes(desde=None, hasta=None)` | Lo más común funciona sin pasar nada; lo especial se pide explícitamente |
| `*args` | `Empresa.crear_registrar_muestras(lote, *cantidades)` | Crear varias muestras en una llamada y controlar el total **antes** de crear (si no entran todas, no se crea ninguna) |
| `**kwargs` | `crear_registrar_procedimiento(tipo, **kwargs)`, `listar_*(**filtros)`, `CalidadError(**detalles)`, `simular_lote(..., **opciones)` | Cada procedimiento tiene parámetros propios (`unidad_medida`); los filtros se eligen al llamar |
| Desempaquetado | `crear_registrar_muestras(lote, *[50] * 20)`, `Reporte(**datos)`, `Clase(**datos)` en `from_dict` | Pasar una lista como argumentos sueltos y un diccionario como argumentos con nombre |
| Funciones como valores | `intentar(descripcion, donde, accion)` en `main.py` recibe una `lambda`; `key=` en `sorted` | Reutilizar el mismo `try/except` para los 25 errores |
| `lambda`, `map`, `filter` | `Lote.porcentaje_no_conforme`, `evaluar()` de los dos procedimientos, `Empresa._filtrar`, `Empresa.reportes` | Transformar y seleccionar colecciones sin bucles explícitos |
| `reduce` | `Reporte.gravedad_maxima` | Acumular la mayor gravedad recorriendo los defectos de a uno |
| `sorted` | `Profesional.certificaciones_vigentes` (`key=lambda c: c.fecha_fin`), `Reporte.defectos_por_gravedad` (usa `__lt__`) | Ordenar sin modificar la colección original |
| `any`, `all`, `sum`, `max` | `Muestra.tiene_critico` (`any`), `Lote.todas_cerradas` (`all`), `Muestra.suma_gravedades` (`sum`) | Expresar reglas de negocio en una línea: "alguno es crítico", "todas cerradas" |
| `zip`, `enumerate` | `main.py` (comparar reportes originales y cargados), `consola.elegir_de_lista` (lista numerada) | Recorrer dos colecciones en paralelo; numerar opciones |
| Generadores (`yield`) | `ListaEnlazada.__iter__` | Recorrer los nodos de a uno sin copiar la lista; por eso funciona con `for`, `map` y `filter` |

### Unidad 5 — Excepciones
| Subtema | Dónde | Por qué ahí |
|---|---|---|
| `raise` | Validaciones de todos los constructores; `Inspeccion.__init__` | Rechazar **antes** de cambiar el estado: si algo es inválido, el objeto no se crea o la muestra no cambia |
| Excepciones propias y jerarquía | `excepciones.py`: `CalidadError` → 7 subclases | Un solo `except CalidadError` captura todas; cada subclase dice qué regla falló |
| Datos extra (`**detalles`) | `CalidadError.detalles` (caso 2a de `main.py`) | Adjuntar al error los datos que lo causaron |
| `try/except ... as e` y orden | `consola.ejecutar_opcion` (`CalidadError`, después `OSError`), `App._ejecutar` (`front/clase_app.py`) | Capturar primero lo específico del sistema y después los errores de archivo |
| Propagación | Se lanza en `Lote.decidir` y se captura en la interfaz | El dominio detecta el problema; la interfaz decide cómo mostrarlo |
| `raise ... from e` | `Empresa.cargar`, `Empresa.cargar_reportes_json`, `ArbolAVL.insertar` | Convertir errores de Python (pickle, JSON, `TypeError`) en errores del sistema sin perder la causa |
| `finally` | `main.py`, caso 6a | Borrar el archivo temporal **siempre**, haya error o no |
| No se usa | `try/else` | No hizo falta: el código "si no hubo error" va dentro del `try` |

### Unidad 6 — Programación orientada a objetos
| Subtema | Dónde | Por qué ahí |
|---|---|---|
| Encapsulamiento | Atributos `_x` con `@property` en todas las clases; `Defecto` y `Reporte` sin setters | El estado solo cambia por métodos que validan (la consigna lo exige) |
| Getters y setters | `Nodo` y `NodoAVL` (`get_dato`, `set_siguiente` con validación) | El setter valida antes de enlazar |
| Atributos de clase y constantes | `Lote.ESTADOS_FINALES`, `Equipo.DIAS_VALIDEZ_CALIBRACION`, `Empresa.CLASES_POR_CATEGORIA`, `Procedimiento.CLASE_DEFECTO`, `Simulador.DEFECTOS_VISUALES` | Un valor compartido escrito en un solo lugar (los 182 días) |
| `@staticmethod` / `@classmethod` | `Defecto.from_dict`, `Reporte.from_dict`, `Empresa.cargar_reportes_json` / `Empresa.cargar` | Crear objetos a partir de datos, sin tener un objeto antes; `cargar` usa `cls` para verificar el tipo |
| Herencia simple | `Procedimiento` → `ProcedimientoVisual` / `ProcedimientoDimensional`; `Defecto` → `DefectoVisual` / `DefectoDimensional` | Regla "es un": un procedimiento visual **es un** procedimiento |
| Herencia multinivel | `Exception` → `CalidadError` → `DatosInvalidosError` (y las demás) | Capturar por nivel: todas las del sistema o una en particular |
| `super()` | `ProcedimientoVisual.__init__`, `DefectoDimensional.__init__` y `to_dict` | Reutilizar lo del padre y agregar lo propio |
| Herencia múltiple y MRO | `App` (`front/clase_app.py`) hereda de `PaginaPanel`, `PaginaRegistro`, `PaginaInspeccion`, `PaginaLotes`, `PaginaReportes` y `Archivos`. MRO: `App → PaginaPanel → … → Archivos → object` | Patrón *mixin*: cada página aporta sus métodos y `App` los reúne en una ventana, en lugar de un archivo de 1400 líneas. Ninguna página repite nombres de métodos, así que el MRO no genera ambigüedades. No es un "es un" estricto: la herencia se usa para reunir comportamiento. En el dominio también: `Procedimiento(Entidad, ABC)` hereda la igualdad por id de `Entidad` y el contrato abstracto de `ABC` |
| Clase abstracta | `Procedimiento(ABC)` con `@abstractmethod evaluar` | No se puede crear un procedimiento genérico (caso 1e) |
| Polimorfismo | `evaluar()`, `copia()`, `to_dict()` | La inspección llama a `evaluar()` sin saber qué procedimiento es |
| Métodos mágicos | `__eq__` y `__hash__` (`Entidad`), `__len__` y `__iter__` (`ListaEnlazada`, `Pila`, `Cola`, `ArbolAVL`), `__contains__` (`muestra in lote`), `__lt__` (`Defecto`), `__bool__` (`ColaPrioridad`: `while cola:`), `__str__`, `__repr__` | Que nuestras clases funcionen con `==`, `set`, `len`, `for`, `in`, `<`, `sorted` y `while` |
| Composición | Lote–Muestra (el lote las crea), Muestra–Pila, Lote–Cola, Pila/Cola–ListaEnlazada | La parte no existe sin el todo |
| Agregación | Profesional–Certificación | La certificación se crea afuera y se agrega |
| Asociación | `Inspeccion` con muestra, profesional, equipo y procedimiento | Los usa, pero cada uno existe por su cuenta |

### Unidad 7 — Estructuras de datos
| Estructura | Dónde | Por qué ahí |
|---|---|---|
| Diccionarios | Registro de `Empresa` (`{categoría: {id: objeto}}`), `Lote._muestras`, certificaciones de `Profesional`, `conteo_por_tipo` (con `.get`), `to_dict()` | Búsqueda por id O(1); contar por tipo |
| Tuplas | Retornos inmutables; prioridades del heap `(gravedad máxima, suma)` | Las tuplas se comparan elemento a elemento: primero decide la gravedad máxima |
| Lista enlazada | `Nodo`, `ListaEnlazada` (un solo tipo de dato por lista) | Base de la pila y la cola, como en la cátedra |
| Pila (LIFO) | Historial de estados de `Muestra`: el `peek()` es el estado actual | El último estado es el que importa, y el historial completo va al reporte |
| Cola (FIFO) | Muestras pendientes de `Lote`; `ArbolAVL.niveles()` (recorrido BFS) | Inspeccionar en orden de llegada |
| Árbol AVL | `Empresa`: equipos por fecha de calibración, reportes por fecha, lotes por producción; `Lote`: defectos por gravedad | Las fechas llegan en orden: un árbol sin balance quedaría como una lista. Cubre los ejercicios de la clase 11: `minimo`, `maximo`, `buscar` e `insertar` recursivos y `entre(a, b)` (nuestro `buscar_rango`). A diferencia del ABB de la clase, una clave repetida no se descarta: se guarda en el mismo nodo, porque hay muchos defectos con la misma gravedad |
| Heap (cola de prioridad) | `Empresa.cola_atencion_reportes()` | Atender primero al más grave, no al que llegó antes |
| Conjuntos | `Lote.tipos_de_defecto()` (`set()` + `update`), `tipos_en_comun` (`&`), `tipos_exclusivos` (`^`); `Empresa.profesionales_de_lote`, `equipos_de_lote`, `profesionales_en_comun` (`&`), `profesionales_solo_en` (`-`); `main.py` 5.9 | Comparar lotes sin repetir elementos, como el ejercicio *Curso* de la clase 9 |
| Entidades hashables | Clase base `Entidad` (`entidad.py`): `__eq__` por tipo e id, `__hash__` = `hash(id)` | Si se define `__eq__`, Python anula el `__hash__`: se definen los dos sobre el id, que es inmutable (como el legajo del `Estudiante` de la clase). Por eso `set(reportes) == set(reportes_cargados_del_json)`. `Defecto` queda afuera: compararlo por valor fusionaría defectos distintos en un `set` |
| Vectores y matrices | No se usan | El dominio no tiene datos en forma de grilla |

### Unidad 8 — Recursividad
Como dice la cátedra, la recursividad es una **técnica** (no una estructura de datos), y una recursión correcta cumple **3 condiciones**: un **caso base** que se resuelve directo, un **caso recursivo** que usa la misma función sobre un problema más chico, y **progreso** (cada llamada se acerca al caso base). Tiene una **fase de ida** (las llamadas bajan) y una **fase de vuelta** (las llamadas pendientes se resuelven en orden inverso).

| Subtema | Dónde | Por qué ahí |
|---|---|---|
| Caso base y caso recursivo | Todas las operaciones de `ArbolAVL` (`_insertar_rec`, `_buscar_rec`, `_buscar_rango_rec`, `_eliminar_rec`, recorridos) | Cada subárbol es otro árbol: el caso base es `None` (o encontrar la clave) |
| Fase de vuelta | `ArbolAVL._balancear`, llamado al volver de cada llamada | En la vuelta se actualizan las alturas y se rota: la recursión recorre el camino de abajo hacia arriba sin guardarlo a mano |
| Progreso | Cada llamada baja un nivel (`nodo.get_izquierdo()` o `get_derecho()`) | El subárbol es más chico en cada llamada, hasta llegar a `None` |
| Recursión vs iteración | `ListaEnlazada`: `buscar` / `buscar_recursivo`, `len` / `longitud_recursiva` (`main.py` 5.1) | Comparar las dos formas sobre la misma estructura |
| Criterio de uso y límite | Recursión en el árbol (estructura **jerárquica**); en la lista, las versiones iterativas (proceso **lineal**) | Es el criterio de la cátedra. Además, una lista muy larga daría `RecursionError`; en el AVL la profundidad es log n |

### Unidad 9 — Gráficos (Matplotlib)
No se usa. La consigna excluye los gráficos de control, y el panel de la interfaz (`front/paginas/panel.py`, con las funciones de `front/visualizaciones.py`) dibuja sus gráficos a mano en un `Canvas` de tkinter, sin librerías extra.

### Unidades 10 y 11 — Búsqueda, ordenamiento y complejidad
| Subtema | Dónde | Complejidad |
|---|---|---|
| Búsqueda secuencial | `ListaEnlazada.buscar` | O(n) |
| Búsqueda en árbol balanceado (equivalente a la binaria) | `ArbolAVL.buscar` y `buscar_rango` | O(log n) garantizado |
| Búsqueda por clave en diccionario o conjunto (tabla hash) | `Lote.__contains__`, `Empresa.obtener_lote`, `Empresa._inspecciones_de_lote` (set de ids) | O(1) |
| Ordenamiento | `sorted` (`Reporte`, `Profesional`), recorrido in-orden del AVL, extracción sucesiva del heap | El AVL entrega los datos ya ordenados |
| Algoritmos manuales (bubble, quick, merge) | No se implementan | No aportan al dominio; `sorted` y las estructuras ya ordenan |

### Material extra de la cátedra — Serialización
| Formato | Qué guarda | Por qué |
|---|---|---|
| JSON (`Empresa.exportar_reportes_json` / `cargar_reportes_json`) | Los reportes de desviación | Legible y no depende de Python. Se guarda con `to_dict()` + `json.dump` y se carga con `Clase(**data)`; `UUID`, `date` y los enums se pasan a texto |
| pickle (`Empresa.guardar` / `Empresa.cargar`) | La empresa completa, con sus relaciones | Guarda objetos propios directamente, para retomar el trabajo. Solo debe cargar archivos propios |

---

## 3. Recursión, AVL y heap, explicados simple

**Árbol AVL.** Árbol de búsqueda (menores a la izquierda, mayores a la derecha) que se mantiene balanceado: en cada nodo, `altura(izquierdo) − altura(derecho)` tiene que ser −1, 0 o 1. Si da 2 o −2, se **rota**:

```
Insertar 10, 20, 30 (cargado a la derecha)  →  rotación a la izquierda

10                        20
  \                      /  \
   20          →       10    30
     \
      30
```

Los 4 casos: izquierda-izquierda (rotar a la derecha), derecha-derecha (rotar a la izquierda), izquierda-derecha y derecha-izquierda (dos rotaciones). En `main.py` 5.2, 15 claves ordenadas dejan el AVL con **altura 4**; sin balance quedarían con altura 15.

**Recursión.** `_buscar_rec(nodo, clave)`: si `nodo` es `None`, no está (caso base); si la clave coincide, la encontré (caso base); si no, busco solo en la mitad izquierda o en la derecha (caso recursivo).

**Heap (max-heap).** Un árbol completo guardado en una lista: `padre(i) = (i−1)//2`, `hijo_izq(i) = 2i+1`, `hijo_der(i) = 2i+2`. El máximo está siempre en el índice 0. Al insertar, el elemento **sube** mientras sea mayor que su padre; al extraer, el último pasa a la raíz y **baja** por el hijo mayor. Las dos operaciones son O(log n).

---

## 4. Errores que se pueden provocar en vivo

**Dónde se capturan:** en `main.py`, en la función `intentar`; en la interfaz gráfica, en `App._ejecutar` (`front/clase_app.py`: muestra una ventana con el nombre de la excepción); en `consola.py`, en `ejecutar_opcion` (imprime `[X] NombreDelError: mensaje`). En todos los casos el programa sigue funcionando.

**Por qué el estado no cambia:** toda validación se hace **antes** de modificar algo. Si falla, se lanza la excepción y no se llega a cambiar nada.

| Caso en `main.py` | Qué se intenta | Excepción | Dónde se lanza |
|---|---|---|---|
| 1a / 4b | Muestra que excede el lote (4b: varias juntas → no se crea ninguna) | `TransicionIlegalError` | `Lote.crear_muestra` / `Empresa.crear_registrar_muestras` |
| 1b | Lote con cantidad 0 | `DatosInvalidosError` | `validar_cantidad` |
| 1c | Certificación que termina antes de empezar | `DatosInvalidosError` | `validar_rango_fechas` |
| 1d | Profesional "Ana 2" | `DatosInvalidosError` | `validar_texto` |
| 1e | `Procedimiento(...)` genérico | `TypeError` (de Python) | `ABC`, por `@abstractmethod evaluar` |
| 2a / 2b | Sin certificación / certificación vencida | `CertificacionNoVigenteError` | `Inspeccion.__init__` |
| 2c / 2e | Equipo de 183 días / calibrado después de la inspección | `EquipoNoAptoError` | `Inspeccion.__init__` (`Equipo.esta_calibrado`) |
| 2d | Equipo de otra categoría | `EquipoNoAptoError` | `Inspeccion.__init__` (`Equipo.es_compatible`) |
| 2f | Fallan la certificación y el equipo: sale el primero | `CertificacionNoVigenteError` | `Inspeccion.__init__` (orden: fecha, estado, certificación, categoría, calibración) |
| 2g | Fecha como texto | `DatosInvalidosError` | `Inspeccion.__init__` |
| 3a | Reinspeccionar una muestra cerrada | `TransicionIlegalError` | `Inspeccion.__init__` |
| 3b | Ejecutar una inspección cerrada | `InspeccionInvalidaError` | `Inspeccion.ejecutar` |
| 3c | Defecto en una muestra cerrada | `TransicionIlegalError` | `Muestra.agregar_defecto` |
| 3d / 4a | Decidir un lote incompleto / decidirlo otra vez | `TransicionIlegalError` | `Lote.decidir` |
| 3e | Siguiente inspección con la cola vacía | `EstructuraVaciaError` | `Empresa.lanzar_siguiente_inspeccion` |
| 4c | Gravedad 6 | `DatosInvalidosError` | `validar_rango_entero` |
| 4d | Defecto dimensional dentro de la tolerancia | `DatosInvalidosError` | `DefectoDimensional.__init__` |
| 5a / 5b | Extraer del heap vacío / agregar a una cola llena | `EstructuraVaciaError` / `EstructuraLlenaError` | `ColaPrioridad.extraer_maximo` / `Cola.put` |
| 6a | Cargar un archivo que no es una empresa | `DatosInvalidosError` | `Empresa.cargar` (con `raise ... from e`) |
| 8a | Filtrar por un atributo que no existe | `DatosInvalidosError` | `Empresa._filtrar` |

**Para mostrarlos en la interfaz** (`py interfaz.py`): botón *Datos de ejemplo*, y después inspeccionar con Carlos (sin certificación), elegir el equipo vencido, decidir un lote con muestras pendientes, o crear más muestras de las que entran.

**Código mínimo (verificado) para hacer en vivo:**
```python
from datetime import date
from classes.empresa import Empresa
from classes.certificacion import Certificacion
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual
from classes.excepciones import CalidadError

empresa = Empresa()
lote = empresa.crear_registrar_lote("Ejes", 100)
m1, m2 = empresa.crear_registrar_muestras(lote, 20, 20)          # *args

ana = empresa.crear_registrar_profesional("Ana")
ana.agregar_certificacion(Certificacion("ISO", date(2025, 1, 1), date(2025, 12, 31)))
carlos = empresa.crear_registrar_profesional("Carlos")            # sin certificaciones
equipo = empresa.crear_registrar_equipo("Visual", date(2025, 6, 1))
proc = empresa.crear_registrar_procedimiento(
    ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")  # **kwargs

try:                                     # Carlos no tiene la certificación
    empresa.lanzar_inspeccion(m1, carlos, equipo, proc, date(2025, 6, 15))
except CalidadError as e:
    print(type(e).__name__, "->", m1.estado.value)       # CertificacionNoVigenteError -> PENDIENTE

insp = empresa.lanzar_siguiente_inspeccion(lote, ana, equipo, proc, date(2025, 6, 15))
insp.ejecutar([ObservacionVisual("Fisura", True, 5)])
insp.cerrar()
print(m1.estado.value, m1.reporte is not None)           # NO_CONFORME True

insp = empresa.lanzar_siguiente_inspeccion(lote, ana, equipo, proc, date(2025, 6, 15))
insp.ejecutar([ObservacionVisual("Sin defectos", False)])
insp.cerrar()
print(lote.porcentaje_no_conforme(), lote.decidir().value)   # 50.0 RECHAZADO
```

---

## 5. Casos límite

| Caso | Regla | Resultado |
|---|---|---|
| Calibración hace **182** días | Los extremos se incluyen | Válido (caso 2c usa 183; el lote 2 usa un equipo de 182) |
| Calibración hace **183** días o en el futuro | `0 <= días <= 182` | `EquipoNoAptoError` |
| Certificación el día que empieza o vence | `fecha_inicio <= fecha <= fecha_fin` | Vigente (Bruno, lote 2 de `main.py`) |
| Suma de gravedades **igual** al límite | No conforme solo si **supera** | CONFORME |
| Un defecto de gravedad 5 | Basta un crítico | NO_CONFORME aunque la suma sea baja |
| Lote con **exactamente 5 %** no conforme | Rechazado solo si **supera** el 5 % | APROBADO (1 de 20); 2 de 20 = 10 % → RECHAZADO |
| Muestras que no entran todas | Se controla el total antes de crear | No se crea ninguna |

**Semillas del simulador** (lote de 20 muestras, probabilidad de defecto 0.15, límite 5): semilla **5** → 5 % → APROBADO; semilla **1** → 10 % → RECHAZADO. Comando verificado:
```bash
py -c "from datetime import date; from classes.empresa import Empresa; from classes.certificacion import Certificacion; from classes.proc_visual import ProcedimientoVisual; from classes.simulador import Simulador; e = Empresa(); l = e.crear_registrar_lote('Bulones', 200); e.crear_registrar_muestras(l, *[10] * 20); a = e.crear_registrar_profesional('Ana'); a.agregar_certificacion(Certificacion('ISO', date(2025, 1, 1), date(2025, 12, 31))); q = e.crear_registrar_equipo('Visual', date(2025, 6, 1)); p = e.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida='ISO'); Simulador(5).simular_lote(e, l, a, q, p, date(2025, 6, 15), prob_defecto=0.15); print('Semilla 5:', l.porcentaje_no_conforme(), '% ->', l.decidir().value)"
```

---

## 6. Cambio controlado (extensiones que puede pedir la cátedra)

**Reinspección autorizada.** Agregar un estado `REINSPECCION_AUTORIZADA` en `EstadoMuestra`; en `Muestra`, guardar una lista de inspecciones en lugar de una sola y permitir `iniciar_inspeccion()` desde ese estado; en `Inspeccion.__init__`, aceptar ese estado además de `PENDIENTE`. `Lote` no cambia: ya decide con el estado actual (el tope de la pila).

**Muestreo por severidad (normal, riguroso, reducido).** Un enum `NivelSeveridad` y un atributo en `Lote`; el 5 % de `Lote.decidir()` pasa a depender del nivel (por ejemplo, 2 % en riguroso). `Empresa` podría cambiar el nivel según los últimos lotes rechazados.

**Calibración por horas de uso.** En `Equipo`, atributos `horas_uso` y `limite_horas`, y un método `registrar_uso(horas)`; `esta_calibrado(fecha)` exige además `horas_uso <= limite_horas`; `Inspeccion.cerrar()` registra las horas usadas. El índice AVL por fecha no cambia.

---

## 7. Preguntas probables

- **¿Dónde se valida todo antes de inspeccionar?** En `Inspeccion.__init__`, en este orden: fecha, estado de la muestra, certificación, categoría del equipo y calibración. Si algo falla, la muestra sigue `PENDIENTE`.
- **¿Por qué `Procedimiento` es abstracta?** Porque un procedimiento genérico no sabe evaluar: cada subclase define su criterio en `evaluar()`. Python no deja instanciarla (caso 1e).
- **¿Cómo se garantiza que un reporte no cambie?** Guarda una tupla con copias de los defectos y no tiene setters.
- **¿Por qué una pila para el historial?** El estado actual es el último que entró (`peek()`), y el historial completo queda para el reporte.
- **¿Por qué una cola para las muestras?** Se inspeccionan en el orden en que se crearon (FIFO).
- **¿Por qué un AVL y no un diccionario?** El diccionario busca por clave exacta, pero no sirve para rangos ni para orden ("equipos que vencen antes de X"). Y no un árbol común porque las fechas llegan ordenadas y lo degenerarían en una lista.
- **¿Por qué un heap para los reportes?** Hay que atender primero al más grave, no al que llegó antes; el heap da el máximo en O(1) y extraerlo cuesta O(log n).
- **¿Por qué JSON y pickle?** JSON para los reportes, que tiene que poder leer cualquier persona; pickle para retomar la empresa completa, con sus objetos y relaciones.
- **¿Dónde está la recursión?** En todas las operaciones del AVL y en las versiones recursivas de la lista enlazada (comparadas con las iterativas en `main.py` 5.1). Cumple las 3 condiciones: caso base (`None` o la clave encontrada), caso recursivo (un subárbol) y progreso (cada llamada baja un nivel).
- **¿Por qué `App` hereda de 6 clases?** Es herencia múltiple con el patrón *mixin*: cada página de `front/paginas/` aporta sus métodos y `App` los reúne. Ninguna página repite nombres, así que el MRO no tiene ambigüedades.
- **¿Por qué `__eq__` y `__hash__` juntos, y por id?** Si se define solo `__eq__`, Python anula el `__hash__` y el objeto ya no entra en un `set`. Se basan en el id porque nunca cambia, y así se cumple que `a == b` implica `hash(a) == hash(b)`. Sirve para reconocer una entidad cargada con pickle o JSON y para operar con conjuntos de profesionales o equipos.
- **¿Cómo se usó la IA?** Está documentado en el README (sección 10): qué se generó, qué errores ayudó a detectar y cómo lo revisamos.
