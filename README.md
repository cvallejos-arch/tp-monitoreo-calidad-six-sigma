# Sistema de Monitoreo de Calidad Industrial

Trabajo práctico de **Estructuras de Datos y Programación (ITBA)**. La consigna completa está en [ConsignaTP.md](ConsignaTP.md).

**QuantumTech Precision** fabrica componentes en lotes. Hoy registra mediciones, calibraciones y defectos en documentos separados, y eso le permite usar equipos vencidos, cerrar lotes incompletos y emitir reportes que no explican el rechazo. Este prototipo coordina las inspecciones y decide la conformidad de muestras y lotes aplicando umbrales fijos: no hace estadística Six Sigma.

---

## 1. Cómo ejecutarlo

Desde la carpeta del proyecto:

```bash
py main.py            # simulación completa por consola
py -m pytest -q       # 330 tests
```

`main.py` recorre el flujo completo y además provoca a propósito cada error del sistema, para mostrar dónde y por qué se rechaza cada operación:

- **Lote 1 (Tornillos):** 1000 unidades con 20 muestras. Se inspeccionan en el orden de la cola y el lote sale **APROBADO** con exactamente 5 % no conforme (la regla rechaza solo si se supera el 5 %).
- **Lote 2 (Arandelas):** 4 muestras que muestran las reglas de cierre: suma de gravedades igual al límite → `CONFORME`; suma mayor al límite → `NO_CONFORME`; un defecto crítico → `NO_CONFORME`; sin defectos → `CONFORME`. Con 50 % no conforme, el lote sale **RECHAZADO**.

**Casos de error que se demuestran:**

| Caso | Qué se intenta | Excepción |
|---|---|---|
| 1a | Crear una muestra que supera la cantidad fabricada del lote | `TransicionIlegalError` |
| 1b | Crear un lote con cantidad 0 | `DatosInvalidosError` |
| 4a | Instanciar `Procedimiento` (clase abstracta) | `TypeError` (de Python) |
| 5a | Inspeccionar con un profesional sin la certificación requerida | `CertificacionNoVigenteError` |
| 5b | Inspeccionar con una certificación vencida | `CertificacionNoVigenteError` |
| 5c | Inspeccionar con un equipo calibrado hace 183 días (el de 182 se acepta) | `EquipoNoAptoError` |
| 5d | Inspeccionar con un equipo de otra categoría | `EquipoNoAptoError` |
| 5e | Fallan la certificación y el equipo a la vez: sale solo el primero, por el orden de validación | `CertificacionNoVigenteError` |
| 5f | Crear una observación con gravedad 6 | `DatosInvalidosError` |
| 6a | Inspeccionar de nuevo una muestra ya cerrada | `TransicionIlegalError` |
| 6b / 6c | Ejecutar o cerrar una inspección ya cerrada | `InspeccionInvalidaError` |
| 6d | Agregar un defecto a una muestra cerrada | `TransicionIlegalError` |
| 6e | Decidir un lote con muestras pendientes | `TransicionIlegalError` |
| 7 | Pedir la siguiente inspección con la cola vacía | `EstructuraVaciaError` |
| 9 | Decidir de nuevo un lote ya decidido | `TransicionIlegalError` |
| 11 | Filtrar por un atributo que no existe | `DatosInvalidosError` |

En todos los rechazos de la sección 5, la muestra queda en `PENDIENTE`: las validaciones se hacen en el constructor de `Inspeccion` antes de cambiar el estado.

---

## 2. Flujo de una inspección

1. **Registro:** `Empresa` crea el lote, y el lote crea sus muestras y las pone en una **cola** de pendientes. También se registran profesionales con sus certificaciones, equipos con su fecha de calibración y procedimientos.
2. **Validación previa:** al crear una `Inspeccion` se controla que la muestra esté `PENDIENTE`, que el profesional tenga la certificación vigente, y que el equipo sea compatible y esté calibrado. Si algo falla, se lanza una excepción y la muestra no cambia.
3. **Ejecución:** el procedimiento transforma las observaciones en defectos con su propio criterio (polimorfismo). La inspección verifica que esos defectos sean del tipo que corresponde al procedimiento.
4. **Cierre:** la muestra queda `CONFORME` o `NO_CONFORME`. Si es no conforme, genera un `Reporte` con una copia fija de sus defectos. Cada cambio de estado se guarda en una **pila** (el historial).
5. **Decisión:** cuando todas las muestras están cerradas, el lote queda `APROBADO` o `RECHAZADO`, y esa decisión no se puede cambiar.

---

## 3. Clases y relaciones (en orden de importancia)

**Muestra** (`muestra.py`): un subconjunto del lote. Es la única clase que cambia su propio estado.
- **Atributos:** `id`, `cantidad`, `lote_id`, `estado` (el tope de la pila), `historial_estados`, `defectos` (tupla), `reporte`.
- **Métodos:** `iniciar_inspeccion()`, `agregar_defecto()`, `cerrar(limite)`, `suma_gravedades()` y `tiene_critico()`.
- **Relaciones:** pertenece a un **Lote**, que la crea (composición). Tiene una **Pila** de `EstadoMuestra` (composición), guarda **Defectos**, crea su **Reporte** y conoce la **Inspección** que la evalúa.

**Lote** (`lote.py`): una partida de componentes. Decide si se aprueba o se rechaza.
- **Atributos:** `id`, `nombre_componentes`, `cantidad_fabricada`, `estado`, `muestras` y la constante `ESTADOS_FINALES`.
- **Métodos:**
  - `crear_muestra(cantidad)`: controla que no se supere la cantidad fabricada;
  - `siguiente_muestra_pendiente()` y `pendientes_en_orden()`;
  - `decidir()`, `porcentaje_no_conforme()` y `todas_cerradas()`;
  - `total_defectos_criticos()` y `conteo_por_tipo()`.
- **Relaciones:** contiene sus **Muestras** en un diccionario `{id: muestra}` y una **Cola** de pendientes (composición).

**Inspeccion** (`inspeccion.py`): une la muestra, el profesional, el equipo, el procedimiento y la fecha.
- **Qué hace:** en el constructor valida todos los requisitos antes de empezar. Después guarda ese contexto, que no se puede modificar.
- **Métodos:** `ejecutar(observaciones)` y `cerrar()`.
- **Relaciones:** se asocia con **Muestra**, **Profesional**, **Equipo** y **Procedimiento**.

**Procedimiento** (`procedimiento.py`): clase **abstracta** (`ABC`) que define el contrato de toda inspección.
- **Atributos:** `limite_gravedad_acumulada`, `categoria_equipo_requerida`, `certificacion_requerida` y `CLASE_DEFECTO`.
- **Método abstracto:** `evaluar(observaciones)`.
- **ProcedimientoVisual** (`proc_visual.py`): hereda de `Procedimiento`. Recibe `ObservacionVisual` y produce `DefectoVisual`.
- **ProcedimientoDimensional** (`proc_dimensional.py`): hereda de `Procedimiento`. Recibe `ObservacionDimensional`, calcula la gravedad según cuánto se pasa la medida de la tolerancia (`_calcular_gravedad`) y produce `DefectoDimensional`.

**Defecto** (`defecto.py`): una desviación observada. Es inmutable: tiene getters y no tiene setters.
- **Atributos:** `tipo`, `descripcion` y `gravedad` (de 1 a 5). Métodos: `es_critico()` y `copia()`.
- **DefectoVisual:** hereda de `Defecto` con el tipo fijo en `"VISUAL"`.
- **DefectoDimensional:** hereda de `Defecto` y además guarda `valor_medido`, `tolerancia_min`, `tolerancia_max` y `unidad`. Si el valor medido está dentro del rango, lanza error, porque no sería un defecto.

**Reporte** (`reporte.py`): el respaldo de una muestra no conforme.
- **Atributos:** `muestra_id`, `lote_id`, `profesional_id`, `fecha`, `defectos` (tupla de copias) e `historial_estados`.
- Lo crea la **Muestra** al cerrarse como no conforme. No se puede modificar.

**Profesional** (`profesional.py`): quien ejecuta la inspección.
- **Atributos:** `id`, `nombre` y `certificaciones` (diccionario `{nombre: Certificacion}`).
- **Métodos:** `agregar_certificacion()`, `tiene_certificacion_vigente(nombre, fecha)` y `certificaciones_vigentes(fecha)`.

**Certificacion** (`certificacion.py`): `nombre`, `fecha_inicio` y `fecha_fin`. El método `es_vigente(fecha)` cuenta los dos extremos como válidos. Cada **Profesional** guarda las suyas (agregación).

**Equipo** (`equipo.py`): un instrumento de medición.
- **Atributos:** `id`, `categoria` y `fecha_calibracion`.
- **Métodos:** `esta_calibrado(fecha)`, que acepta hasta 182 días contando los dos extremos, y `es_compatible(categoria)`.

**Observaciones** (`observacion_visual.py` y `observacion_dimensional.py`): los datos de entrada de cada procedimiento.
- **Visual:** `descripcion`, `defecto_detectado` y `gravedad`.
- **Dimensional:** `valor_medido`, `tolerancia_min` y `tolerancia_max`. También calcula `desviacion` y `tolerancia`.

**Empresa** (`empresa.py`): el punto de entrada del dominio. Guarda todo en un registro de diccionarios por categoría.
- **Registro y lanzamiento:**
  - `crear_registrar_*()` para cada entidad;
  - `crear_registrar_procedimiento(tipo, **kwargs)`;
  - `lanzar_inspeccion()`;
  - `lanzar_siguiente_inspeccion(lote, ...)`, que toma la muestra del frente de la cola del lote.
- **Consultas:** `listar_lotes()`, `listar_muestras()` y `listar_inspecciones()` aceptan filtros `**kwargs`. `resumen()` da la cantidad de cada categoría.

**Estructuras de datos propias:**
- **Nodo** (`nodo.py`): guarda un `dato` y la referencia `siguiente`.
- **ListaEnlazada** (`lista_enlazada.py`): lista simple con `inicio`, `fin` y tamaño. Todos sus datos son de un mismo tipo. Implementa `__len__` y `__iter__` (con `yield`), así que funciona con `for`, `map`, `filter` y `sum`.
- **Pila** (`pila.py`, LIFO) y **Cola** (`cola.py`, FIFO): usan una `ListaEnlazada` por dentro. La pila tiene `push`, `pop`, `peek`, `isEmpty` y `size`. La cola tiene `put`, `get`, `front`, `qsize`, `empty` y `full`, y acepta un `maxsize` opcional.

**Soporte:**
- **`EstadoMuestra` y `EstadoLote`:** enums con los estados posibles.
- **`validacion.py`:** funciones de validación reutilizables, entre ellas `validar_texto`, que acepta solo letras, y `validar_nombre_tecnico`, que admite números y `- . /` (por ejemplo, "ISO 9001").
- **`excepciones.py`:** jerarquía de excepciones propias con base `CalidadError`, que acepta `**detalles`. Incluye `DatosInvalidosError`, `EquipoNoAptoError`, `CertificacionNoVigenteError`, `TransicionIlegalError`, `InspeccionInvalidaError`, `EstructuraVaciaError` y `EstructuraLlenaError`.

---

## 4. Reglas de negocio: dónde se cumplen

| # | Regla | Dónde | Tests |
|---|---|---|---|
| 1 | Ids únicos y no vacíos; cantidades enteras positivas | `uuid4` en cada constructor; `validar_cantidad` | `test_reglas_consigna`, `test_validacion` |
| 2 | La muestra pertenece a un solo lote, no se puede mover y no supera la cantidad fabricada | `Lote.crear_muestra`; `lote_id` solo tiene getter | `test_lote` |
| 3 | Gravedad entre 1 y 5; datos del defecto coherentes con su procedimiento | `validar_gravedad`; `DefectoVisual` y `DefectoDimensional`; `CLASE_DEFECTO` | `test_defecto`, `test_reglas_consigna` |
| 4 | Calibración válida hasta 182 días, contando los extremos | `Equipo.esta_calibrado` | `test_equipo` |
| 5 | Certificación vigente, contando los extremos; si falta, la muestra no cambia | `Certificacion.es_vigente`; validación en `Inspeccion.__init__` | `test_certificacion`, `test_inspeccion` |
| 6 | Solo una muestra `PENDIENTE` inicia, una sola inspección por muestra, con requisitos fijos | `Inspeccion.__init__`; `Muestra.asignar_inspeccion` | `test_inspeccion` |
| 7 | Evaluación polimórfica, sin defectos ajenos | `evaluar()` en cada subclase; control en `Inspeccion.ejecutar` | `test_procedimiento`, `test_reglas_consigna` |
| 8 | No conforme si hay un crítico o si la suma supera el límite | `Muestra.cerrar` | `test_muestra` |
| 9 | Una muestra cerrada no se puede modificar ni reinspeccionar | `Muestra.agregar_defecto`; `defectos` es una tupla | `test_muestra`, `test_inspeccion` |
| 10 | Un único reporte con copia inmutable, solo si es no conforme | `Muestra.cerrar` → `Reporte` | `test_reporte` |
| 11 | El lote se decide solo si todas sus muestras están cerradas; rechazado si supera el 5 %; decisión final | `Lote.decidir` | `test_lote`, `test_estado_lote` |
| 12 | Las consultas solo miran muestras cerradas y no tienen efectos | `_muestras_cerradas`, `total_defectos_criticos`, `conteo_por_tipo` | `test_lote` |

---

## 5. Decisiones de diseño

- **¿Cómo reciben los procedimientos observaciones distintas sin exponer la muestra?** Cada procedimiento recibe sus propios objetos de observación (`ObservacionVisual` u `ObservacionDimensional`) y devuelve una lista de defectos. Nunca toca la muestra: es la `Inspeccion` la que agrega los defectos.
- **¿Quién valida todo antes de iniciar?** El constructor de `Inspeccion`. Si una validación falla, se lanza la excepción **antes** de cambiar el estado, así que la muestra queda intacta.
- **¿Cómo se mantiene fijo el contexto?** La inspección guarda la muestra, el profesional, el equipo, el procedimiento y la fecha en atributos privados con solo getters. El procedimiento tampoco tiene setters, así que sus requisitos no pueden cambiar a mitad de la ejecución.
- **¿La conformidad se guarda o se calcula?** Se calcula a partir de los defectos en el momento del cierre y se guarda como estado final. No hay contradicción posible, porque después del cierre no se pueden agregar defectos.
- **¿Cómo se copia el reporte de forma estable?** `Reporte` guarda una tupla con `copia()` de cada defecto. Cada subclase redefine `copia()` para conservar sus datos propios.
- **¿Dónde se decide el lote?** En `Lote.decidir()`, que solo mira el estado de las muestras. No sabe qué procedimiento usó cada una, así que agregar un procedimiento nuevo no afecta la decisión.

---

## 6. Conceptos de la materia aplicados

| Concepto | Dónde se aplica |
|---|---|
| **POO y encapsulamiento** | Atributos privados (`_x`) con `@property`; ningún estado se cambia directamente desde afuera |
| **Herencia y polimorfismo** | `Procedimiento` → `ProcedimientoVisual` / `ProcedimientoDimensional` (mismo `evaluar()`, distinto criterio); `Defecto` → `DefectoVisual` / `DefectoDimensional`; `CalidadError` → excepciones propias |
| **Clase abstracta** | `Procedimiento(ABC)` con `@abstractmethod evaluar` |
| **Composición, agregación y asociación** | Lote–Muestra y Muestra–Pila (composición); Profesional–Certificación (agregación); Inspección con sus 4 componentes (asociación) |
| **Atributos de clase y constantes** | `Lote.ESTADOS_FINALES`, `Empresa.CLASES_POR_CATEGORIA`, `CLASE_DEFECTO`, `TIPO` |
| **Métodos mágicos** | `__repr__`, `__str__`, `__len__` y `__iter__` en `ListaEnlazada`, `Pila` y `Cola` |
| **Excepciones propias** | Jerarquía con base `CalidadError` y `**detalles`; `try/except` en `main.py` |
| **`lambda`, `map`, `filter`, `all`, `any`, `sum`** | `Lote` (porcentaje, críticos, cerradas), `evaluar()` de ambos procedimientos, `Empresa._filtrar`, `Muestra.suma_gravedades`, `Reporte` (copias), `validar_nombre_tecnico` |
| **Diccionarios** | Registro de `Empresa` (`{categoría: {id: objeto}}`) recorrido con `.items()`; `Lote._muestras`; certificaciones de `Profesional`; `conteo_por_tipo` con `.get()` |
| **`*args` / `**kwargs`** | `crear_registrar_procedimiento(tipo, **kwargs)`, filtros `listar_*(**filtros)`, `CalidadError(**detalles)` |
| **Tuplas** | Retornos inmutables: `defectos`, `muestras`, `historial_estados`, `pendientes_en_orden()` |
| **Nodos y lista enlazada** | `Nodo` y `ListaEnlazada` (simple, con `inicio`/`fin`), con un solo tipo de dato por lista |
| **Pila (LIFO)** | Historial de estados de cada `Muestra`: el `peek()` es el estado actual |
| **Cola (FIFO)** | Muestras pendientes del `Lote`: se inspeccionan en orden de creación |
| **Generadores (`yield`)** | `ListaEnlazada.__iter__` recorre los nodos sin copiarlos |
| **Fechas** | `date` y `timedelta` en calibraciones, certificaciones e inspecciones |
| **Tests con pytest** | 297 tests, con fixtures (`conftest.py`), `parametrize` y `monkeypatch` |

---

## 7. Uso de IA

El modelo de dominio, las clases base y los tests iniciales los construimos nosotros. Después usamos Claude (Claude Code) para revisar el código y aplicar los conceptos teóricos en los lugares que correspondía. Los cambios más importantes en los que ayudó:

**Detección de errores**
- Un commit dejó `Muestra` usando `self._estado`, un atributo que ya no existía, y eso hacía fallar 33 tests. Ese mismo commit había deshecho mejoras anteriores en `Lote`. Se identificó la causa y se corrigió.
- `Nodo.set_dato` comparaba el tipo del dato nuevo con `type(self)` en lugar de `type(self.dato)`, así que siempre fallaba.
- `Reporte` no aceptaba el historial de estados que `Muestra` le pasaba.
- `Inspeccion.cerrar()` marcaba la inspección como cerrada antes de cerrar la muestra: si el cierre fallaba, el estado quedaba inconsistente.
- `validar_texto` rechazaba nombres reales como "ISO 9001" o "Tornillos M8". Se agregó `validar_nombre_tecnico`.
- Un filtro mal escrito en `Empresa` (por ejemplo `estdo=`) devolvía una lista vacía sin avisar. Ahora lanza `DatosInvalidosError`.

**Dónde aplicar los conceptos teóricos**
- Reemplazar bucles por `map`, `filter` y `lambda` en `Lote`, en los procedimientos, en `Empresa` y en `main.py`, sin usar `map` solo para provocar efectos.
- Dónde usar la pila y la cola dentro del dominio: el historial de estados de la muestra y la cola de pendientes del lote. Adaptar sus métodos a los nombres de la cátedra.
- Agregar `__len__` y `__iter__` a la lista enlazada para que funcione con `for`, `map` y `filter`.
- Convertir `Procedimiento` en clase abstracta y crear subclases de `Defecto` para cumplir la regla 3.
- Agregar tests para las pruebas mínimas de la consigna que todavía no estaban cubiertas, por ejemplo los identificadores únicos.

Todo el código generado lo revisamos, lo probamos con `pytest` y lo podemos explicar.
