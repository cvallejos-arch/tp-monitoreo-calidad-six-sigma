# Oral defense guide — Quality Monitoring (QuantumTech Precision)

For each topic of the **Data Structures and Programming** syllabus: **where** it is in the code (file → class → method) and **why** it was used there. At the end: the errors that can be triggered live, the edge cases and the most likely questions. The full technical detail is in the [README](README.md) (in Spanish).

> Class, method and message names are in Spanish, as in the code. Key terms: *lote* = batch, *muestra* = sample, *defecto* = defect, *gravedad* = severity, *equipo* = instrument, *profesional* = inspector, *reporte* = deviation report, *procedimiento* = procedure.

---

## 1. The system in one minute

**Problem:** QuantumTech used expired instruments, closed incomplete batches and issued reports that did not explain the rejection. **Solution:** a system that validates everything before inspecting and decides conformity with fixed rules.

**Flow:** register (batch → samples in a **queue**) → validate (certification, instrument, state) → evaluate (each procedure in its own way: **polymorphism**) → close (CONFORME / NO_CONFORME, history in a **stack**, report if non-conforming) → decide the batch (rejected if above 5 %) → handle reports from most to least severe (**heap**).

| Class | Purpose | Key methods |
|---|---|---|
| `Muestra` | Subset of the batch; the only class that changes its own state | `iniciar_inspeccion`, `agregar_defecto`, `cerrar` |
| `Lote` | Production batch; decides approved or rejected | `crear_muestra`, `decidir`, `porcentaje_no_conforme` |
| `Inspeccion` | Joins sample, inspector, instrument, procedure and date; **validates everything before starting** | `__init__`, `ejecutar`, `cerrar` |
| `Procedimiento` (abstract) | Evaluation contract; two subclasses with different criteria | `evaluar` |
| `Defecto` | Immutable deviation; visual and dimensional subclasses | `es_critico`, `copia`, `__lt__` |
| `Reporte` | Immutable record of a non-conforming sample | `gravedad_maxima`, `defectos_por_gravedad`, `to_dict` |
| `Empresa` | Entry point: registers everything, queries and serializes | `crear_registrar_*`, `lanzar_inspeccion`, `listar_*` |
| `ArbolAVL` / `ColaPrioridad` | Date indexes and handling order | `buscar`, `buscar_rango` / `insertar`, `extraer_maximo` |

---

## 2. Syllabus topics in the project

### Unit 1 — Everything in Python is an object
| Subtopic | Where | Why there |
|---|---|---|
| `isinstance` | `Profesional.agregar_certificacion`, `Nodo.set_siguiente`, `Inspeccion.ejecutar` (foreign defects), `Empresa.cargar` | Checking the object's **type** before accepting it protects the rules (e.g. that a loaded file really is an `Empresa`) |
| `is` vs `==` | `main.py` section 6: `cargada is not empresa`; tests use `is` with the queue | Distinguish **identity** (same object) from **equality** (same content): what pickle loads is a different object with the same content |
| `type(e).__name__` | `intentar` in `main.py`, `_ejecutar` in `menu.py`, `ejecutar_opcion` in `consola.py` | Show the user which kind of error happened |

### Unit 2 — Data types
| Subtopic | Where | Why there |
|---|---|---|
| Immutable: **tuples** | `Muestra.defectos`, `Lote.muestras`, `Reporte.defectos`, `Pila.historial()` | Tuples are returned so nobody can modify the internal state from outside (encapsulation) |
| Mutable: lists and dicts | Internal lists (`Muestra._defectos`), the `Empresa` registry | Inside the object we need to add elements |
| Strings | `validar_texto` (`isalpha`), `validar_nombre_tecnico` (`isalnum`), `ListaEnlazada.__str__` (`join`), f-strings in every message | Validate names ("Ana 2" is not a name; "ISO 9001" is a valid technical name) and build clear messages |
| Shallow copy | `Profesional.certificaciones` returns `dict(...)` | A copy of the dict: changing it does not change the inspector |
| Object copies | `Reporte` stores `copia()` of each defect | The report does not depend on the original objects |

### Unit 3 — Libraries
`datetime` (`date`, `timedelta`: calibrations, certifications, expiry) · `uuid` (unique ids, rule 1) · `abc` (abstract class) · `json` and `pickle` (serialization) · `random` (seeded simulator) · `functools.reduce` · `os` (delete the temporary file in `main.py`) · `tkinter` (GUI) · `pytest` (500 tests).

### Unit 4 — Functions
| Subtopic | Where | Why there |
|---|---|---|
| Default parameters | `Cola(tipo=None, maxsize=None)`, `Simulador(semilla=None)`, `cola_atencion_reportes(desde=None, hasta=None)` | The common case works without arguments; special cases are explicit |
| `*args` | `Empresa.crear_registrar_muestras(lote, *cantidades)` | Create several samples in one call and check the total **before** creating (if they don't all fit, none is created) |
| `**kwargs` | `crear_registrar_procedimiento(tipo, **kwargs)`, `listar_*(**filtros)`, `CalidadError(**detalles)`, `simular_lote(..., **opciones)` | Each procedure has its own parameters (`unidad_medida`); filters are chosen when calling |
| Unpacking | `crear_registrar_muestras(lote, *[50] * 20)`, `Reporte(**datos)`, `Clase(**datos)` in `from_dict` | Pass a list as separate arguments and a dict as keyword arguments |
| Functions as values | `intentar(descripcion, donde, accion)` in `main.py` receives a `lambda`; `key=` in `sorted` | Reuse the same `try/except` for the 25 errors |
| `lambda`, `map`, `filter` | `Lote.porcentaje_no_conforme`, both procedures' `evaluar()`, `Empresa._filtrar`, `Empresa.reportes` | Transform and select collections without explicit loops |
| `reduce` | `Reporte.gravedad_maxima` | Accumulate the highest severity, one defect at a time |
| `sorted` | `Profesional.certificaciones_vigentes` (`key=lambda c: c.fecha_fin`), `Reporte.defectos_por_gravedad` (uses `__lt__`) | Sort without modifying the original collection |
| `any`, `all`, `sum`, `max` | `Muestra.tiene_critico` (`any`), `Lote.todas_cerradas` (`all`), `Muestra.suma_gravedades` (`sum`) | Business rules in one line: "any is critical", "all closed" |
| `zip`, `enumerate` | `main.py` (compare original and loaded reports), `consola.elegir_de_lista` (numbered list) | Walk two collections in parallel; number options |
| Generators (`yield`) | `ListaEnlazada.__iter__` | Walk the nodes one by one without copying; that's why it works with `for`, `map` and `filter` |

### Unit 5 — Exceptions
| Subtopic | Where | Why there |
|---|---|---|
| `raise` | Validations in every constructor; `Inspeccion.__init__` | Reject **before** changing the state: an invalid object is not created, the sample does not change |
| Custom exceptions and hierarchy | `excepciones.py`: `CalidadError` → 7 subclasses | One `except CalidadError` catches them all; each subclass says which rule failed |
| Extra data (`**detalles`) | `CalidadError.detalles` (case 2a of `main.py`) | Attach the data that caused the error |
| `try/except ... as e` and order | `consola.ejecutar_opcion` (`CalidadError`, then `OSError`), `menu._ejecutar` | Catch the system's errors first, then file errors |
| Propagation | Raised in `Lote.decidir`, caught in the interface | The domain detects the problem; the interface decides how to show it |
| `raise ... from e` | `Empresa.cargar`, `Empresa.cargar_reportes_json`, `ArbolAVL.insertar` | Turn Python errors (pickle, JSON, `TypeError`) into system errors without losing the cause |
| `finally` | `main.py`, case 6a | **Always** delete the temporary file, error or not |
| Not used | `try/else` | Not needed: the "no error" code goes inside the `try` |

### Unit 6 — Object-oriented programming
| Subtopic | Where | Why there |
|---|---|---|
| Encapsulation | `_x` attributes with `@property` in every class; `Defecto` and `Reporte` have no setters | State only changes through methods that validate (required by the assignment) |
| Getters and setters | `Nodo` and `NodoAVL` (`get_dato`, `set_siguiente` with validation) | The setter validates before linking |
| Class attributes and constants | `Lote.ESTADOS_FINALES`, `Equipo.DIAS_VALIDEZ_CALIBRACION`, `Empresa.CLASES_POR_CATEGORIA`, `Procedimiento.CLASE_DEFECTO`, `Simulador.DEFECTOS_VISUALES` | A shared value written in one place (the 182 days) |
| `@staticmethod` / `@classmethod` | `Defecto.from_dict`, `Reporte.from_dict`, `Empresa.cargar_reportes_json` / `Empresa.cargar` | Build objects from data without having an object first; `cargar` uses `cls` to check the type |
| Single inheritance | `Procedimiento` → `ProcedimientoVisual` / `ProcedimientoDimensional`; `Defecto` → `DefectoVisual` / `DefectoDimensional` | "Is a" rule: a visual procedure **is a** procedure |
| Multilevel inheritance | `Exception` → `CalidadError` → `DatosInvalidosError` (and the others) | Catch by level: all system errors or a specific one |
| `super()` | `ProcedimientoVisual.__init__`, `DefectoDimensional.__init__` and `to_dict` | Reuse the parent's code and add our own |
| Multiple inheritance / MRO | Not used | No domain class "is" two things at once |
| Abstract class | `Procedimiento(ABC)` with `@abstractmethod evaluar` | A generic procedure cannot be created (case 1e) |
| Polymorphism | `evaluar()`, `copia()`, `to_dict()` | The inspection calls `evaluar()` without knowing which procedure it is |
| Magic methods | `__len__` and `__iter__` (`ListaEnlazada`, `Pila`, `Cola`, `ArbolAVL`), `__contains__` (`muestra in lote`), `__lt__` (`Defecto`), `__bool__` (`ColaPrioridad`: `while cola:`), `__str__`, `__repr__` | Our classes work with `len`, `for`, `in`, `<`, `sorted` and `while` |
| Composition | Batch–Sample (the batch creates them), Sample–Stack, Batch–Queue, Stack/Queue–LinkedList | The part does not exist without the whole |
| Aggregation | Inspector–Certification | The certification is created outside and added |
| Association | `Inspeccion` with sample, inspector, instrument and procedure | It uses them, but each exists on its own |

### Unit 7 — Data structures
| Structure | Where | Why there |
|---|---|---|
| Dictionaries | `Empresa` registry (`{category: {id: object}}`), `Lote._muestras`, inspector certifications, `conteo_por_tipo` (with `.get`), `to_dict()` | O(1) lookup by id; counting by type |
| Tuples | Immutable returns; heap priorities `(max severity, sum)` | Tuples compare element by element: max severity decides first |
| Linked list | `Nodo`, `ListaEnlazada` (one data type per list) | Base of the stack and the queue, as taught in class |
| Stack (LIFO) | `Muestra` state history: `peek()` is the current state | The last state is what matters, and the full history goes into the report |
| Queue (FIFO) | `Lote` pending samples; `ArbolAVL.niveles()` (BFS traversal) | Inspect in arrival order |
| AVL tree | `Empresa`: instruments by calibration date, reports by date, batches by production; `Lote`: defects by severity | Dates arrive in order: an unbalanced tree would become a list |
| Heap (priority queue) | `Empresa.cola_atencion_reportes()` | Handle the most severe first, not the one that arrived first |
| Sets | Not taught yet | When taught: `__eq__` and `__hash__` by id in the entities |
| Vectors and matrices | Not used | The domain has no grid-shaped data |

### Unit 8 — Recursion
| Subtopic | Where | Why there |
|---|---|---|
| Base case and recursive case | Every `ArbolAVL` operation (`_insertar_rec`, `_buscar_rec`, `_buscar_rango_rec`, `_eliminar_rec`, traversals) | Each subtree is a tree: the base case is `None` (or finding the key) |
| Rebalancing on the way back | `ArbolAVL._balancear`, called after each recursive call returns | Recursion walks the path bottom-up without storing it by hand |
| Recursion vs iteration | `ListaEnlazada`: `buscar` / `buscar_recursivo`, `len` / `longitud_recursiva` (`main.py` 5.1) | Compare both approaches on the same structure |
| Limit | A very long list (thousands of nodes) would raise `RecursionError` in the recursive versions | That's why the list uses the iterative ones; in the AVL the depth is log n |

### Unit 9 — Plotting (Matplotlib)
Not used. The assignment excludes control charts, and the `menu.py` dashboard draws its charts by hand on a tkinter `Canvas`, with no extra libraries.

### Units 10 and 11 — Searching, sorting and complexity
| Subtopic | Where | Complexity |
|---|---|---|
| Sequential search | `ListaEnlazada.buscar` | O(n) |
| Balanced-tree search (equivalent to binary search) | `ArbolAVL.buscar` and `buscar_rango` | O(log n) guaranteed |
| Dictionary lookup | `Lote.__contains__`, `Empresa.obtener_lote` | O(1) |
| Sorting | `sorted` (`Reporte`, `Profesional`), AVL in-order traversal, successive heap extraction | The AVL returns the data already sorted |
| Manual algorithms (bubble, quick, merge) | Not implemented | They add nothing to the domain; `sorted` and the structures already sort |

### Extra course material — Serialization
| Format | What it stores | Why |
|---|---|---|
| JSON (`Empresa.exportar_reportes_json` / `cargar_reportes_json`) | Deviation reports | Human-readable, not Python-specific. Saved with `to_dict()` + `json.dump`, loaded with `Clase(**data)`; `UUID`, `date` and enums become text |
| pickle (`Empresa.guardar` / `Empresa.cargar`) | The whole company, with its relations | Stores our own objects directly, to resume work. Only load your own files |

---

## 3. Recursion, AVL and heap, explained simply

**AVL tree.** A search tree (smaller to the left, larger to the right) kept balanced: at every node, `height(left) − height(right)` must be −1, 0 or 1. If it is 2 or −2, it **rotates**:

```
Insert 10, 20, 30 (right-heavy)  →  left rotation

10                        20
  \                      /  \
   20          →       10    30
     \
      30
```

The 4 cases: left-left (rotate right), right-right (rotate left), left-right and right-left (two rotations). In `main.py` 5.2, 15 sorted keys leave the AVL at **height 4**; without balancing it would be height 15.

**Recursion.** `_buscar_rec(nodo, clave)`: if `nodo` is `None`, the key is not there (base case); if the key matches, found (base case); otherwise search only the left or the right half (recursive case).

**Heap (max-heap).** A complete tree stored in a list: `padre(i) = (i−1)//2`, `hijo_izq(i) = 2i+1`, `hijo_der(i) = 2i+2`. The maximum is always at index 0. On insert, the element **moves up** while it is larger than its parent; on extract, the last element goes to the root and **moves down** through the larger child. Both are O(log n).

---

## 4. Errors that can be triggered live

**Where they are caught:** in `main.py`, in the `intentar` function; in `menu.py`, in `_ejecutar` (shows a window with the exception name); in `consola.py`, in `ejecutar_opcion` (prints `[X] ErrorName: message`). In every case the program keeps running.

**Why the state does not change:** every validation happens **before** modifying anything. If it fails, the exception is raised and nothing is changed.

| Case in `main.py` | What is attempted | Exception | Raised in |
|---|---|---|---|
| 1a / 4b | Sample exceeding the batch (4b: several at once → none is created) | `TransicionIlegalError` | `Lote.crear_muestra` / `Empresa.crear_registrar_muestras` |
| 1b | Batch with quantity 0 | `DatosInvalidosError` | `validar_cantidad` |
| 1c | Certification that ends before it starts | `DatosInvalidosError` | `validar_rango_fechas` |
| 1d | Inspector named "Ana 2" | `DatosInvalidosError` | `validar_texto` |
| 1e | Generic `Procedimiento(...)` | `TypeError` (Python's) | `ABC`, because of `@abstractmethod evaluar` |
| 2a / 2b | No certification / expired certification | `CertificacionNoVigenteError` | `Inspeccion.__init__` |
| 2c / 2e | Instrument calibrated 183 days ago / after the inspection | `EquipoNoAptoError` | `Inspeccion.__init__` (`Equipo.esta_calibrado`) |
| 2d | Instrument of another category | `EquipoNoAptoError` | `Inspeccion.__init__` (`Equipo.es_compatible`) |
| 2f | Certification and instrument both fail: the first one is reported | `CertificacionNoVigenteError` | `Inspeccion.__init__` (order: date, state, certification, category, calibration) |
| 2g | Date given as text | `DatosInvalidosError` | `Inspeccion.__init__` |
| 3a | Re-inspect a closed sample | `TransicionIlegalError` | `Inspeccion.__init__` |
| 3b | Run a closed inspection | `InspeccionInvalidaError` | `Inspeccion.ejecutar` |
| 3c | Add a defect to a closed sample | `TransicionIlegalError` | `Muestra.agregar_defecto` |
| 3d / 4a | Decide an incomplete batch / decide it again | `TransicionIlegalError` | `Lote.decidir` |
| 3e | Next inspection with an empty queue | `EstructuraVaciaError` | `Empresa.lanzar_siguiente_inspeccion` |
| 4c | Severity 6 | `DatosInvalidosError` | `validar_rango_entero` |
| 4d | Dimensional defect within tolerance | `DatosInvalidosError` | `DefectoDimensional.__init__` |
| 5a / 5b | Extract from an empty heap / add to a full queue | `EstructuraVaciaError` / `EstructuraLlenaError` | `ColaPrioridad.extraer_maximo` / `Cola.put` |
| 6a | Load a file that is not a company | `DatosInvalidosError` | `Empresa.cargar` (with `raise ... from e`) |
| 8a | Filter by a non-existent attribute | `DatosInvalidosError` | `Empresa._filtrar` |

**To show them in the GUI:** *Datos de ejemplo* button, then inspect with Carlos (no certification), pick the expired instrument, decide a batch with pending samples, or create more samples than fit.

**Minimal (verified) code to run live:**
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
carlos = empresa.crear_registrar_profesional("Carlos")            # no certifications
equipo = empresa.crear_registrar_equipo("Visual", date(2025, 6, 1))
proc = empresa.crear_registrar_procedimiento(
    ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")  # **kwargs

try:                                     # Carlos lacks the certification
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

## 5. Edge cases

| Case | Rule | Result |
|---|---|---|
| Calibrated **182** days ago | Both ends included | Valid (case 2c uses 183; batch 2 uses a 182-day instrument) |
| Calibrated **183** days ago or in the future | `0 <= days <= 182` | `EquipoNoAptoError` |
| Certification on its first or last day | `fecha_inicio <= date <= fecha_fin` | Valid (Bruno, batch 2 in `main.py`) |
| Sum of severities **equal** to the limit | Non-conforming only if it **exceeds** it | CONFORME |
| One defect of severity 5 | One critical defect is enough | NO_CONFORME even if the sum is low |
| Batch with **exactly 5 %** non-conforming | Rejected only if it **exceeds** 5 % | APROBADO (1 of 20); 2 of 20 = 10 % → RECHAZADO |
| Samples that don't all fit | The total is checked before creating | None is created |

**Simulator seeds** (batch of 20 samples, defect probability 0.15, limit 5): seed **5** → 5 % → APROBADO; seed **1** → 10 % → RECHAZADO. Verified command:
```bash
py -c "from datetime import date; from classes.empresa import Empresa; from classes.certificacion import Certificacion; from classes.proc_visual import ProcedimientoVisual; from classes.simulador import Simulador; e = Empresa(); l = e.crear_registrar_lote('Bulones', 200); e.crear_registrar_muestras(l, *[10] * 20); a = e.crear_registrar_profesional('Ana'); a.agregar_certificacion(Certificacion('ISO', date(2025, 1, 1), date(2025, 12, 31))); q = e.crear_registrar_equipo('Visual', date(2025, 6, 1)); p = e.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida='ISO'); Simulador(5).simular_lote(e, l, a, q, p, date(2025, 6, 15), prob_defecto=0.15); print('Semilla 5:', l.porcentaje_no_conforme(), '% ->', l.decidir().value)"
```

---

## 6. Controlled change (extensions the course may ask for)

**Authorized re-inspection.** Add a `REINSPECCION_AUTORIZADA` state to `EstadoMuestra`; in `Muestra`, keep a list of inspections instead of one and allow `iniciar_inspeccion()` from that state; in `Inspeccion.__init__`, accept that state besides `PENDIENTE`. `Lote` does not change: it already decides with the current state (top of the stack).

**Severity-based sampling (normal, tightened, reduced).** A `NivelSeveridad` enum and an attribute in `Lote`; the 5 % in `Lote.decidir()` depends on the level (e.g. 2 % when tightened). `Empresa` could change the level based on the latest rejected batches.

**Calibration by hours of use.** In `Equipo`, `horas_uso` and `limite_horas` attributes and a `registrar_uso(horas)` method; `esta_calibrado(fecha)` also requires `horas_uso <= limite_horas`; `Inspeccion.cerrar()` records the hours used. The date-based AVL index does not change.

---

## 7. Likely questions

- **Where is everything validated before inspecting?** In `Inspeccion.__init__`, in this order: date, sample state, certification, instrument category and calibration. If anything fails, the sample stays `PENDIENTE`.
- **Why is `Procedimiento` abstract?** A generic procedure doesn't know how to evaluate: each subclass defines its criterion in `evaluar()`. Python won't instantiate it (case 1e).
- **How is a report guaranteed not to change?** It stores a tuple with copies of the defects and has no setters.
- **Why a stack for the history?** The current state is the last one pushed (`peek()`), and the full history stays for the report.
- **Why a queue for the samples?** They are inspected in the order they were created (FIFO).
- **Why an AVL and not a dict?** A dict looks up exact keys but can't do ranges or order ("instruments expiring before X"). And not a plain tree, because dates arrive sorted and would degrade it into a list.
- **Why a heap for the reports?** The most severe must be handled first, not the first to arrive; the heap gives the maximum in O(1) and extracting it costs O(log n).
- **Why JSON and pickle?** JSON for the reports, which anyone must be able to read; pickle to resume the whole company with its objects and relations.
- **Where is the recursion?** In every AVL operation and in the recursive versions of the linked list (compared with the iterative ones in `main.py` 5.1).
- **How was AI used?** It is documented in the README (section 10): what was generated, which errors it helped detect and how we reviewed it.
