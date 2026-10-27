# Guía Rápida para la Defensa Oral — TP Monitoreo de Calidad Six Sigma

> **QuantumTech Precision** — Documento de soporte para la mesa de evaluación.  
> Diseñado para responder en segundos: tablas, códigos mínimos y referencias exactas del código.

---

## 1. Flujo Feliz Básico (Código Mínimo para Mostrar al Profesor)

```python
from datetime import date
from classes.empresa import Empresa
from classes.proc_visual import ProcedimientoVisual
from classes.observacion_visual import ObservacionVisual

# 1. Crear empresa y lote (capacidad 100)
emp = Empresa()
lote = emp.crear_registrar_lote("Ejes", 100)

# 2. Crear muestra (toma 20 del lote y se encola automáticamente)
m = emp.crear_registrar_muestra(20, lote)

# 3. Profesional con certificación vigente
prof = emp.crear_registrar_profesional("Ana")
cert = emp.crear_registrar_certificacion(prof, "ISO-Visual", date(2025, 1, 1), date(2025, 12, 31))

# 4. Equipo calibrado (hoy = 15/06/2025, calibrado 01/06/2025 -> 14 días)
eq = emp.crear_registrar_equipo("Visual", date(2025, 6, 1))

# 5. Procedimiento (límite gravedad 5, requiere equipo 'Visual' y cert 'ISO-Visual')
proc = emp.crear_registrar_procedimiento(ProcedimientoVisual, 5, "Visual", "ISO-Visual")

# 6. Lanzar inspección (desencola o toma la muestra PENDIENTE -> EN_INSPECCION)
insp = emp.lanzar_siguiente_inspeccion(lote, prof, eq, proc, date(2025, 6, 15))

# 7. Ejecutar y Cerrar (sin defectos -> CONFORME)
insp.ejecutar([ObservacionVisual("Superficie limpia", False)])
insp.cerrar()

# 8. Decidir lote (0% no conformes <= 5% -> APROBADO)
print(lote.decidir().value)  # 'Aprobado'
```

---

## 2. Catálogo de Errores para Demostrar (Preguntas y Respuestas)

### Dónde se capturan los errores en cada interfaz:
* **En `main.py`:** Bloques `try / except <ErrorEspecifico> as e:` en cada sección demostrativa.
* **En `menu.py` (GUI):** Método centralizado `_ejecutar(self, accion)` (línea 158) que hace `except (CalidadError, OSError) as e:` y abre una ventana modal `messagebox.showerror(type(e).__name__, str(e))`. La app nunca se cuelga.
* **En `consola.py`:** Función `ejecutar_opcion(empresa, opcion)` (línea 416) que hace `except CalidadError as e:` y `except OSError as e:`, imprime `[X] <TipoError>: <mensaje>` y devuelve la empresa intacta.

---

### Tabla Maestra de Errores del Sistema

| # | Error a Provocar | Código Mínimo | En `menu.py` / `consola.py` | Excepción | Clase y Método donde se lanza (`raise`) | ¿Por qué el estado no cambia? (Fail-Fast) |
|---|---|---|---|---|---|---|
| **1** | **Muestra excede capacidad del lote** | `lote = emp.crear_registrar_lote("X", 100)`<br>`emp.crear_registrar_muestra(101, lote)` | Pestaña *Registro* -> Crear Muestra con cantidad mayor a la fabricada del lote. | `TransicionIlegalError` | `Lote.crear_muestra`<br>(`classes/lote.py`) | Se calcula `capacidad_usada + cantidad > cantidad_fabricada` antes de instanciar `Muestra` o tocar la cola. |
| **2** | **Cantidad 0 o negativa** | `emp.crear_registrar_lote("X", 0)`<br>o `lote.crear_muestra(-5)` | Ingresar `0` o `-1` en cantidad de lote o muestra. | `DatosInvalidosError` | `validar_cantidad`<br>(`classes/validacion.py`) | Función pura que valida `isinstance(int)` y `cantidad > 0` antes de asignar atributos. |
| **3** | **Gravedad fuera de 1 a 5** | `ObservacionVisual("Raya", True, 6)`<br>o `Defecto("Visual", "X", 0)` | Pestaña *Inspección* -> Ejecutar -> ingresar gravedad `0` o `6`. | `DatosInvalidosError` | `validar_rango_entero` / `validar_gravedad`<br>(`classes/validacion.py`) | Se valida `1 <= gravedad <= 5` en el constructor de la observación/defecto antes de evaluarse. |
| **4a** | **Profesional sin certificación requerida** | Profesional sin cert `ISO-Visual` asignado a procedimiento que la exige. | Elegir en Pestaña *Inspección* a un profesional sin la certificación requerida. | `CertificacionNoVigenteError` | `Inspeccion.__init__`<br>(`classes/inspeccion.py`) | Se valida `profesional.tiene_certificacion_vigente()` **antes** de llamar a `muestra.iniciar_inspeccion()`. La muestra sigue `PENDIENTE`. |
| **4b** | **Certificación vencida** | Certificación con `fecha_fin < fecha_inspeccion`. | Profesional con cert vencida al día de la inspección. | `CertificacionNoVigenteError` | `Inspeccion.__init__`<br>(`classes/inspeccion.py`) | `Certificacion.es_vigente(fecha)` devuelve `False`. Falla en pre-condición; la muestra no pasa a `EN_INSPECCION`. |
| **5a** | **Equipo vencido (183 días)** | `eq = Equipo("Visual", date(2025,1,1))` e inspeccionar el `2025-07-03` (183 días). | Seleccionar equipo calibrado hace más de 182 días. | `EquipoNoAptoError` | `Inspeccion.__init__`<br>(`classes/inspeccion.py`) | `equipo.esta_calibrado(fecha)` retorna `(dias <= 182)`. Se aborta el constructor de `Inspeccion`; estado de muestra intacto. |
| **5b** | **Equipo de categoría incompatible** | Procedimiento pide `"Visual"` y se le pasa equipo `"Dimensional"`. | Seleccionar equipo cuya categoría no coincida con el procedimiento. | `EquipoNoAptoError` | `Inspeccion.__init__`<br>(`classes/inspeccion.py`) | `equipo.es_compatible(req)` evalúa igualdad de string antes de iniciar inspección. Muestra sigue `PENDIENTE`. |
| **6** | **Reinspeccionar una muestra** | `emp.lanzar_inspeccion(muestra_cerrada, ...)` | Intentar lanzar inspección seleccionando una muestra ya cerrada (`CONFORME` / `NO_CONFORME`). | `TransicionIlegalError` | `Inspeccion.__init__`<br>(`classes/inspeccion.py`) | Valida `muestra.estado == EstadoMuestra.PENDIENTE`. Si es final o ya está en curso, se rechaza de inmediato. |
| **7** | **Agregar defecto a muestra cerrada** | `muestra_cerrada.agregar_defecto(defecto)` | Operación interna inviable por interfaz porque las inspecciones cerradas se bloquean. | `TransicionIlegalError` | `Muestra.agregar_defecto`<br>(`classes/muestra.py`) | Verifica estrictamente `self.estado == EstadoMuestra.EN_INSPECCION`. Si está cerrada, la lista interna es intocable. |
| **8a** | **Ejecutar inspección cerrada** | `insp.cerrar()`<br>`insp.ejecutar([obs])` | Pulsar botón "Ejecutar" sobre una inspección que ya fue cerrada. | `InspeccionInvalidaError` | `Inspeccion.ejecutar`<br>(`classes/inspeccion.py`) | El flag booleano `self._cerrada` se comprueba en la primera línea del método. No evalúa ni agrega defectos. |
| **8b** | **Cerrar inspección dos veces** | `insp.cerrar()`<br>`insp.cerrar()` | Pulsar botón "Cerrar" sobre una inspección ya cerrada. | `InspeccionInvalidaError` | `Inspeccion.cerrar`<br>(`classes/inspeccion.py`) | Comprueba `if self._cerrada: raise...` antes de intentar cerrar la muestra. |
| **9a** | **Decidir lote incompleto** | Lote con 1 muestra cerrada y 1 pendiente -> `lote.decidir()` | Pestaña *Lotes* -> "Decidir Lote" cuando aún hay muestras en estado `PENDIENTE` o `EN_INSPECCION`. | `TransicionIlegalError` | `Lote.decidir`<br>(`classes/lote.py`) | Evalúa `not self.todas_cerradas()`. El atributo `self._estado` sigue en `EN_PRODUCCION`. |
| **9b** | **Decidir lote dos veces** | `lote.decidir()`<br>`lote.decidir()` | Pulsar "Decidir Lote" en un lote ya `APROBADO` o `RECHAZADO`. | `TransicionIlegalError` | `Lote.decidir`<br>(`classes/lote.py`) | Evalúa `self._estado != EstadoLote.EN_PRODUCCION`. Las decisiones son terminales e inmutables. |
| **9c** | **Decidir lote sin muestras** | `lote = emp.crear_registrar_lote("X", 10)`<br>`lote.decidir()` | "Decidir Lote" sobre un lote recién creado sin muestras. | `TransicionIlegalError` | `Lote.decidir`<br>(`classes/lote.py`) | Evalúa `not self._muestras`. Requiere al menos una muestra inspeccionada y cerrada. |
| **10** | **Cola vacía** | `emp.lanzar_siguiente_inspeccion(lote, ...)` sin muestras pendientes. | Pulsar "Siguiente Inspección" cuando el lote ya no tiene muestras en cola. | `EstructuraVaciaError` | `Empresa.lanzar_siguiente_inspeccion`<br>(o `Cola.get` / `front`) | `lote.siguiente_muestra_pendiente()` retorna `None`. Empresa verifica y lanza excepción sin modificar nada. |
| **11** | **Filtro con atributo inexistente** | `emp.listar_lotes(estadoo="APROBADO")` | Intentar buscar con clave de filtro errónea por código. | `DatosInvalidosError` | `Empresa._filtrar`<br>(`classes/empresa.py`) | Hace introspección con `hasattr(clase, attr)` sobre la clase del registro antes de ejecutar el `filter()`. |
| **12a**| **JSON de reportes inválido / corrupto** | `Empresa.cargar_reportes_json("archivo_corrupto.json")` | Pestaña *Archivo* -> Cargar Reportes JSON -> elegir archivo con sintaxis rota o sin formato de lista. | `DatosInvalidosError` | `Empresa.cargar_reportes_json`<br>(`classes/empresa.py`) | Atrapa `json.JSONDecodeError`, valida que sea `list`, y atrapa `KeyError/TypeError` de `Reporte.from_dict`. |
| **12b**| **Pickle inválido / archivo no-Empresa** | `Empresa.cargar("archivo.bin")` con contenido basura o clase distinta. | Pestaña *Archivo* -> Cargar Empresa (pickle) -> archivo no binario o dañado. | `DatosInvalidosError` | `Empresa.cargar`<br>(`classes/empresa.py`) | Atrapa `pickle.UnpicklingError` / `EOFError` y valida `isinstance(empresa, cls)`. Ningún estado se sobrescribe. |

---

## 3. Casos Límite y Reglas de Negocio Críticas

| Caso Límite | Regla de la Consigna | Condición en el Código | Resultado |
|---|---|---|---|
| **Calibración a 182 días** | 6 meses = 182 días exactos. Los extremos son inclusivos. | `0 <= (fecha_insp - fecha_calib).days <= 182` | **VÁLIDO** (apto para inspeccionar). |
| **Calibración a 183 días** | 1 día más que el límite máximo. | `(fecha_insp - fecha_calib).days == 183` | **INVÁLIDO** -> Lanza `EquipoNoAptoError`. |
| **Certificación en día de inicio o fin** | Vigencia con extremos inclusivos. | `fecha_inicio <= fecha_insp <= fecha_fin` | **VIGENTE** (tanto el primer día como el último son válidos). |
| **Suma de gravedades = Límite** | Solo es no conforme si **supera** el límite. | `suma_gravedades > limite_gravedad` | **CONFORME** (ej. límite 5, suma 5 -> Conforme; suma 6 -> No Conforme). |
| **Defecto crítico (gravedad 5)** | Basta un solo crítico, sin importar el límite de suma acumulada. | `tiene_critico() or suma > limite` | **NO CONFORME** inmediata (incluso si la suma acumulada fuese menor). |
| **Porcentaje lote exactamente 5%** | Se rechaza si **supera** el 5% (estrictamente mayor). | `porcentaje_no_conforme() > 5` | **APROBADO** (ej. 1 de 20 = 5.0% -> APROBADO; 2 de 20 = 10.0% -> RECHAZADO). Sin redondeos. |

---

## 4. Cambio Controlado (Posibles Extensiones de la Consigna)

> En caso de que el profesor pregunte cómo extender el sistema sin romper la arquitectura existente:

### Extensión 1: Reinspección Autorizada
* **Qué permitir:** Que una muestra `NO_CONFORME` pueda ser reinspeccionada si cuenta con una autorización/orden de retrabajo.
* **Clases y métodos a modificar:**
  1. `classes/estado_muestra.py`: Agregar estado intermedio `REINSPECCION_SOLICITADA` o permitir retorno controlado.
  2. `classes/muestra.py`:
     - Modificar `_inspeccion` para almacenar una lista o historial de inspecciones (`_inspecciones`).
     - Modificar `iniciar_inspeccion()`: permitir transición si está en `REINSPECCION_SOLICITADA`.
     - Modificar `cerrar()`: conservar el histórico de reportes anteriores o marcar el reporte previo como "subsanado".
  3. `classes/inspeccion.py`:
     - En `__init__`: relajar la condición `muestra.estado == EstadoMuestra.PENDIENTE` para aceptar también muestras autorizadas para reensayo.
  4. `classes/lote.py`:
     - En `decidir()` y `porcentaje_no_conforme()`: consultar siempre el **estado más reciente** (tope de la pila LIFO `_historial`), garantizando que la muestra compute con su veredicto final.

### Extensión 2: Muestreo por Severidad (Normal, Riguroso, Atenuado - ISO 2859)
* **Qué permitir:** Cambiar la cantidad de muestras requeridas y el umbral de rechazo del lote según el historial de calidad de la fábrica.
* **Clases y métodos a modificar:**
  1. Nuevo Enum `NivelSeveridad` (`NORMAL`, `RIGUROSO`, `ATENUADO`).
  2. `classes/lote.py`:
     - Agregar atributo `_severidad`.
     - Método `calcular_muestras_requeridas()`: determina el tamaño del muestreo según tamaño del lote y nivel de severidad.
     - Modificar `decidir()`: el umbral de rechazo deja de ser una constante fija del 5% y pasa a ser dinámico (ej. Riguroso: rechazo si > 2% o al 1er crítico; Atenuado: rechazo si > 10%).
  3. `classes/empresa.py`:
     - Mantener contador de lotes aprobados/rechazados consecutivos.
     - Implementar *switching rules* (ej. 2 de 5 lotes rechazados -> pasar a muestreo Riguroso; 10 aprobados seguidos -> pasar a Atenuado).

### Extensión 3: Calibraciones por Horas de Uso
* **Qué permitir:** Los equipos pierden calibración por antigüedad (días) O por horas acumuladas de uso en inspecciones.
* **Clases y métodos a modificar:**
  1. `classes/equipo.py`:
     - Nuevos atributos: `_horas_acumuladas` (entero/float >= 0) y `_limite_horas_calibracion` (ej. 500 hs).
     - Nuevo método `registrar_uso(horas)`: incrementa el contador de horas.
     - Modificar `esta_calibrado(fecha, horas_estimadas=0)`: retorna `True` si `(0 <= dias <= 182)` **Y** `(horas_acumuladas + horas_estimadas <= limite_horas)`.
     - Método `recalibrar(fecha)`: actualiza fecha y reinicia `horas_acumuladas = 0`.
  2. `classes/inspeccion.py`:
     - Recibir duración de la inspección o derivarla del procedimiento.
     - En `Inspeccion.cerrar()`: llamar a `self._equipo.registrar_uso(duracion)`.

---

## 5. Semillas para Demostrar (`classes/simulador.py`)

Para mostrar en vivo la repetibilidad y el criterio del 5% con datos pseudoaleatorios deterministas:

* **Parámetros:** Lote de **20 muestras**, probabilidad de defecto **0.15**, límite de gravedad **5** (procedimiento visual).
* **Semilla 5:** Produce exactamente **1 muestra no conforme de 20** = **5.0 %**.  
  $\rightarrow$ Como 5 % no es estrictamente mayor a 5 %, el lote resulta **`Aprobado`**.
* **Semilla 1:** Produce **2 muestras no conformes de 20** = **10.0 %**.  
  $\rightarrow$ Como 10 % supera el 5 %, el lote resulta **`Rechazado`**.

### Código de consola de una línea para ejecutar en la defensa:
```bash
py -c "from classes.empresa import Empresa; from classes.simulador import Simulador; from classes.proc_visual import ProcedimientoVisual; from datetime import date; emp = Empresa(); l5 = emp.crear_registrar_lote('B5', 200); [emp.crear_registrar_muestra(10, l5) for _ in range(20)]; p = emp.crear_registrar_profesional('Ana'); emp.crear_registrar_certificacion(p, 'ISO', date(2025,1,1), date(2025,12,31)); eq = emp.crear_registrar_equipo('Visual', date(2025,6,1)); pr = emp.crear_registrar_procedimiento(ProcedimientoVisual, 5, 'Visual', 'ISO'); Simulador(5).simular_lote(emp, l5, p, eq, pr, date(2025,6,15), prob_defecto=0.15); print('Semilla 5:', l5.porcentaje_no_conforme(), '% ->', l5.decidir().value)"
```
*(Salida directa: `Semilla 5: 5.0 % -> Aprobado`)*

---

## 6. Recursividad y Árboles Binarios de Búsqueda (Unidades 7 y 8 EDP)

En caso de que el profesor pregunte cómo y dónde se aplican la recursividad y los árboles:

1. **Recursividad en `ListaEnlazada` (Unidad 7):**
   - Métodos: `longitud_recursiva()`, `buscar_recursivo(valor)`, `contar_recursivo(valor)`, `a_lista_recursiva()` e `invertir_recursivo()`.
   - Patrón: método público wrapper que delega en una función recursiva pura sobre nodos con **caso base** (nodo es `None` o último nodo) y **caso recursivo** (llamada con `nodo.get_siguiente()`).

2. **Árbol Binario de Búsqueda (ABB / BST - Unidad 8):**
   - Clases: [`NodoArbol`](file:///c:/Users/TRONCHETTI/GIT/EDP/PROJECT/tp-monitoreo-calidad-six-sigma/classes/nodo_arbol.py) y [`ArbolBinarioBusqueda`](file:///c:/Users/TRONCHETTI/GIT/EDP/PROJECT/tp-monitoreo-calidad-six-sigma/classes/arbol_binario.py).
   - Operaciones 100 % recursivas: `insertar(dato, clave)`, `buscar(clave)`, `contiene(clave)`, `altura()`, `minimo()`, `maximo()`, `eliminar(clave)` (3 casos clásicos, con sucesor in-order) y recorridos (`recorrido_in_orden()`, `recorrido_pre_orden()`, `recorrido_post_orden()`).
   - **Aplicación al dominio:**
     - `Lote.arbol_defectos_por_gravedad()`: indexa defectos por gravedad (1 a 5). Permite búsqueda $O(\log n)$ de defectos críticos (`arbol.buscar_todos(5)`).
     - `Lote.arbol_muestras_por_cantidad()`: indexa muestras por tamaño de piezas.
     - `Empresa.arbol_lotes_por_produccion()`: indexa lotes por cantidad fabricada para ordenarlos y consultarlos por volumen.
