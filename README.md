# Sistema de Monitoreo de Calidad Industrial

Trabajo práctico de **Estructuras de Datos y Programación (ITBA)**. La consigna completa está en [ConsignaTP.md](ConsignaTP.md).

**QuantumTech Precision** fabrica componentes en lotes. Hoy registra mediciones, calibraciones y defectos en documentos separados, y eso le permite usar equipos vencidos, cerrar lotes incompletos y emitir reportes que no explican el rechazo. Este prototipo coordina las inspecciones y decide la conformidad de muestras y lotes aplicando umbrales fijos: no hace estadística Six Sigma.

**Guías para el oral** (cada tema del programa, dónde está en el código y por qué): [español](DEFENSA_ORAL_ES.md) · [English](DEFENSA_ORAL_EN.md) · [français](DEFENSA_ORAL_FR.md).

---

## 1. Cómo ejecutarlo

Desde la carpeta del proyecto:

```bash
py interfaz.py        # interfaz gráfica (ventana con panel de control)
py consola.py         # el mismo uso interactivo, por consola con input()
py main.py            # demo guionada: recorre todo el sistema y provoca cada error
py -m pytest -q       # 521 tests
```

**Para probar rápido:** en la interfaz gráfica (botón **Datos de ejemplo**) o en `consola.py` (opción **12**) se cargan lotes, profesionales con y sin certificación, equipos al día, por vencer y vencidos, y los dos procedimientos. Desde ahí se pueden provocar los errores en vivo: inspeccionar con Carlos (sin certificación), usar el equipo vencido o decidir un lote con muestras pendientes.

**Resultados fijos de `main.py`:** lote 1 con exactamente 5 % no conforme → **APROBADO** (se rechaza solo si se *supera* el 5 %); lote 2 con 50 % → **RECHAZADO**; simulación con semilla 5 → 5 % **APROBADO** y semilla 1 → 10 % **RECHAZADO**.

---

## 2. Estructura del repositorio

| Archivo / carpeta | Qué contiene |
|---|---|
| `classes/` | **El dominio:** todas las clases y sus reglas. No usa `input`, `print` ni azar. |
| `classes/simulador.py` | Generador de observaciones al azar con semilla (lo usan las tres interfaces). |
| `interfaz.py` | Punto de entrada de la interfaz gráfica (tkinter): crea la ventana `App`. |
| `front/` | La interfaz gráfica, separada en módulos: `clase_app.py` (ventana principal), `paginas/` (una clase por página), `estilos.py`, `herramientas.py` y `visualizaciones.py`. |
| `consola.py` | Interfaz por consola (`input()`). |
| `main.py` | Demo guionada por consola. |
| `tests/` | 521 tests con pytest: uno o más archivos por clase, más reglas de la consigna, índices, serialización, simulador y consola. |
| `DEFENSA_ORAL_*.md` | Guías para el oral en español, inglés y francés. |

Las tres interfaces están **separadas del dominio**, como pide la consigna: solo llaman a métodos públicos (nunca a atributos privados como `empresa._registros`), y las reglas se validan siempre dentro del dominio.

---

## 3. Interfaces

**`interfaz.py` + `front/`: interfaz gráfica (5 páginas, barra lateral)**
- **Organización:** `interfaz.py` solo crea la ventana. `front/clase_app.py` define `App`, que hereda los métodos de una clase por página (`front/paginas/`: `PaginaPanel`, `PaginaRegistro`, `PaginaInspeccion`, `PaginaLotes`, `PaginaReportes` y `Archivos`). `front/estilos.py` tiene los colores y fuentes; `front/herramientas.py`, funciones auxiliares (lectura de datos, tarjetas, botones); `front/visualizaciones.py`, los gráficos.
- **Panel:** indicadores (lotes, avance, % no conforme, gravedad promedio, críticos, reportes) y gráficos dibujados a mano en un `Canvas`: estado de las muestras, defectos por gravedad (con el árbol AVL), % no conforme por lote, inspecciones por profesional, calibración de equipos (ordenados con el AVL: el que vence primero, arriba) y últimas inspecciones.
- **Registro:** lotes, muestras, profesionales, certificaciones, equipos y procedimientos.
- **Inspección:** elegir lote y muestra (o *Tomar la siguiente de la cola*), profesional, equipo, procedimiento y fecha; cargar observaciones a mano o *Observaciones al azar*; *Inspeccionar muestra*; *Simulación aleatoria del lote*.
- **Lotes:** tabla de lotes, muestras del lote con su historial (pila) y *Decidir lote seleccionado*.
- **Reportes:** en **orden de atención** (columna *Turno*, cola de prioridad: el más grave primero), con **filtro por fechas** (árbol AVL) y *Exportar a JSON*.
- Barra lateral: *Datos de ejemplo*, *Guardar empresa* y *Cargar empresa* (pickle).
- **Errores:** pasan todos por `App._ejecutar` (`front/clase_app.py`), que captura `CalidadError` y `OSError` y los muestra en una ventana con el nombre de la excepción. El programa sigue funcionando.

**`consola.py`: menú por consola (15 opciones)**
- Registro, inspección (a mano o al azar), ver y decidir lotes, reportes, pickle/JSON, datos de ejemplo, simulación aleatoria, **alertas de calibración** (opción 14) y **reportes por fecha en orden de atención** (opción 15).
- Las funciones de entrada (`pedir_entero`, `pedir_fecha`, `elegir_de_lista`, etc.) **vuelven a preguntar** hasta que el dato sea válido, y las observaciones se piden **antes** de lanzar la inspección, para que una muestra nunca quede a medias en `EN_INSPECCION`.
- Un único `except CalidadError` en `ejecutar_opcion` muestra cualquier error del sistema; también se capturan `OSError` y `Ctrl+C`.

**`main.py`: demo guionada en 8 secciones, con 25 rechazos provocados.** Cada rechazo pasa por la función `intentar`, que imprime la excepción, el mensaje y **dónde se lanza**.

| Sección | Qué muestra | Casos de error |
|---|---|---|
| 1. Registro | Lote con 20 muestras (`*args`), profesionales, equipos de 100, 180, **182** y **183** días y uno calibrado en el futuro, procedimientos | 1a muestra que excede el lote · 1b cantidad 0 · 1c certificación con fechas invertidas · 1d nombre "Ana 2" · 1e instanciar la clase abstracta |
| 2. Validaciones | Todo lo que `Inspeccion.__init__` controla antes de empezar | 2a sin certificación · 2b certificación vencida · 2c equipo de 183 días · 2d categoría incompatible · 2e calibración posterior a la inspección · 2f dos fallas a la vez · 2g fecha como texto |
| 3. Inspecciones | Muestra 0 crítica (reporte, pila), muestras 1 a 18 por la cola, muestra 19 dimensional | 3a reinspeccionar · 3b ejecutar una inspección cerrada · 3c defecto en muestra cerrada · 3d decidir lote incompleto · 3e cola vacía |
| 4. Cierre y decisión | Lote 1 al 5 % → APROBADO; lote 2 con suma = límite, suma > límite, crítico y sin defectos → RECHAZADO; certificación que vence ese día y equipo de 182 días aceptados | 4a decidir otra vez · 4b muestras que no entran (no se crea ninguna) · 4c gravedad 6 · 4d defecto dimensional dentro de tolerancia |
| 5. Estructuras | Recursión vs iteración, AVL (altura, rotaciones, equipos y reportes por fecha), cola de prioridad, cola con `maxsize`, conjuntos (comparar lotes con `&`, `^` y `-`) | 5a heap vacío · 5b cola llena |
| 6. Serialización | Reportes a JSON y empresa completa con pickle; lo cargado es otro objeto pero la misma entidad (`==` por id) | 6a cargar un archivo que no es una empresa (con `finally`) |
| 7. Simulación | Semillas 5 y 1, reproducibilidad | — |
| 8. Resumen | Reportes con defectos ordenados, filtros `**kwargs`, registro | 8a filtro inexistente |

---

## 4. Flujo de una inspección

1. **Registro:** `Empresa` crea el lote, y el lote crea sus muestras y las pone en una **cola** de pendientes. También se registran profesionales con certificaciones, equipos (que entran a un **árbol AVL** ordenado por fecha de calibración) y procedimientos.
2. **Validación previa:** al crear una `Inspeccion` se controla que la muestra esté `PENDIENTE`, que el profesional tenga la certificación vigente y que el equipo sea compatible y esté calibrado. Si algo falla, se lanza una excepción y la muestra no cambia.
3. **Ejecución:** el procedimiento transforma las observaciones en defectos con su propio criterio (polimorfismo). La inspección verifica que los defectos sean del tipo que corresponde al procedimiento.
4. **Cierre:** la muestra queda `CONFORME` o `NO_CONFORME`. Si es no conforme, genera un `Reporte` con una copia fija de sus defectos. Cada cambio de estado se guarda en una **pila** (el historial).
5. **Decisión:** cuando todas las muestras están cerradas, el lote queda `APROBADO` o `RECHAZADO`, y esa decisión no se puede cambiar.
6. **Atención:** los reportes se atienden del más grave al menos grave con una **cola de prioridad** (heap).

---

## 5. Clases y relaciones (en orden de importancia)

**Muestra** (`muestra.py`): un subconjunto del lote; la única clase que cambia su propio estado.
- **Atributos:** `id`, `cantidad`, `lote_id`, `estado` (el tope de la pila), `historial_estados`, `defectos` (tupla), `reporte`.
- **Métodos:** `iniciar_inspeccion()`, `agregar_defecto()`, `cerrar(limite)`, `suma_gravedades()`, `tiene_critico()`.
- **Relaciones:** la crea su **Lote** (composición); tiene una **Pila** de estados (composición); crea su **Reporte**; conoce su **Inspección**.

**Lote** (`lote.py`): una partida de componentes; decide si se aprueba.
- **Atributos:** `id`, `nombre_componentes`, `cantidad_fabricada`, `estado`, `muestras`, `capacidad_libre` y la constante `ESTADOS_FINALES`.
- **Métodos:** `crear_muestra(cantidad)`, `siguiente_muestra_pendiente()`, `pendientes_en_orden()`, `decidir()`, `porcentaje_no_conforme()`, `todas_cerradas()`, `total_defectos_criticos()`, `conteo_por_tipo()`, `tipos_de_defecto()` (un `set`), `tipos_en_comun(otro)` (`&`), `tipos_exclusivos(otro)` (`^`), `arbol_muestras_por_cantidad()`, `arbol_defectos_por_gravedad()`; `muestra in lote` (`__contains__`).
- **Relaciones:** guarda sus **Muestras** en un diccionario `{id: muestra}` y una **Cola** de pendientes (composición).

**Inspeccion** (`inspeccion.py`): une muestra, profesional, equipo, procedimiento y fecha. Valida todo en el constructor y después guarda ese contexto sin setters. Métodos: `ejecutar(observaciones)` y `cerrar()`.

**Procedimiento** (`procedimiento.py`): clase **abstracta** (`ABC`) con `limite_gravedad_acumulada`, `categoria_equipo_requerida`, `certificacion_requerida`, `CLASE_DEFECTO` y el método abstracto `evaluar(observaciones)`.
- **ProcedimientoVisual** (`proc_visual.py`): recibe `ObservacionVisual` y produce `DefectoVisual`.
- **ProcedimientoDimensional** (`proc_dimensional.py`): agrega `unidad_medida`, calcula la gravedad según cuánto se pasa la medida (`_calcular_gravedad`) y produce `DefectoDimensional`.

**Defecto** (`defecto.py`): inmutable (solo getters). `tipo`, `descripcion`, `gravedad` (1 a 5); `es_critico()`, `copia()`, `to_dict()`, `from_dict()`; se compara por gravedad con `<` (`__lt__`).
- **DefectoVisual:** tipo fijo `"VISUAL"`.
- **DefectoDimensional:** además guarda `valor_medido`, `tolerancia_min`, `tolerancia_max` y `unidad`; rechaza una medida dentro del rango.

**Reporte** (`reporte.py`): respaldo de una muestra no conforme. `muestra_id`, `lote_id`, `profesional_id`, `fecha`, `defectos` (tupla de copias), `historial_estados`, `gravedad_maxima` (con `reduce`), `suma_gravedades`, `defectos_por_gravedad()` (con `sorted`), `to_dict()`, `from_dict()`.

**Profesional** (`profesional.py`): `nombre` y `certificaciones` (diccionario `{nombre: Certificacion}`); `agregar_certificacion()`, `tiene_certificacion_vigente(nombre, fecha)`, `certificaciones_vigentes(fecha)` (ordenadas por vencimiento).

**Certificacion** (`certificacion.py`): `nombre`, `fecha_inicio`, `fecha_fin`; `es_vigente(fecha)` con los extremos incluidos.

**Equipo** (`equipo.py`): `categoria`, `fecha_calibracion`, `fecha_vencimiento` y la constante `DIAS_VALIDEZ_CALIBRACION = 182`; `esta_calibrado(fecha)` y `es_compatible(categoria)`.

**Observaciones** (`observacion_visual.py`, `observacion_dimensional.py`): los datos de entrada de cada procedimiento.

**Empresa** (`empresa.py`): el punto de entrada del dominio; guarda todo en un registro de diccionarios por categoría.
- **Registro:** `crear_registrar_*()`, `crear_registrar_muestras(lote, *cantidades)` y `crear_registrar_procedimiento(tipo, **kwargs)`; `lanzar_inspeccion()` y `lanzar_siguiente_inspeccion(lote, ...)` (toma la muestra del frente de la cola).
- **Consultas:** `listar_lotes()`, `listar_muestras()`, `listar_inspecciones()`, `listar_profesionales()`, `listar_equipos()`, `listar_procedimientos()` (todas con filtros `**kwargs`, por medio de `_filtrar`), `obtener_lote(id)`, `obtener_muestra(id)`, `reportes()` y `resumen()`.
- **Índices AVL:** `equipos_por_calibracion()`, `equipos_vencidos_al(fecha)`, `equipos_que_vencen_entre(desde, hasta)`, `equipo_que_vence_primero(fecha)` (el árbol de equipos se mantiene al día al registrar cada uno), `reportes_entre(desde, hasta)`, `arbol_reportes_por_fecha()` y `arbol_lotes_por_produccion()`.
- **Cola de prioridad:** `cola_atencion_reportes(desde=None, hasta=None)`.
- **Conjuntos:** `profesionales_de_lote(lote)`, `equipos_de_lote(lote)`, `profesionales_en_comun(a, b)` (`&`) y `profesionales_solo_en(a, b)` (`-`).
- **Serialización:** `exportar_reportes_json(ruta)`, `cargar_reportes_json(ruta)`, `guardar(ruta)` y `cargar(ruta)`.

**Simulador** (`simulador.py`): genera casos al azar con un generador propio, `random.Random(semilla)`: `observaciones_visuales`, `observaciones_dimensionales`, `observaciones_para` y `simular_lote`. No es parte del dominio.

**Estructuras de datos propias:**
- **Nodo** y **ListaEnlazada** (`nodo.py`, `lista_enlazada.py`): lista simple con un solo tipo de dato, `__len__` y `__iter__` (con `yield`), y versiones recursivas de sus operaciones (`longitud_recursiva`, `buscar_recursivo`, `contar_recursivo`, `a_lista_recursiva`, `invertir_recursivo`).
- **Pila** (`pila.py`, LIFO: `push`, `pop`, `peek`, `isEmpty`, `size`) y **Cola** (`cola.py`, FIFO: `put`, `get`, `front`, `qsize`, `empty`, `full`, `maxsize` opcional), sobre una `ListaEnlazada`.
- **NodoAVL** y **ArbolAVL** (`nodo_avl.py`, `arbol_avl.py`): árbol de búsqueda que se rebalancea con rotaciones; operaciones recursivas (`insertar`, `buscar`, `buscar_rango`, `eliminar`, `minimo`, `maximo`, recorridos) y `niveles()` (BFS con nuestra `Cola`). Claves repetidas en el mismo nodo.
- **ColaPrioridad** (`cola_prioridad.py`): max-heap en una lista (`padre`, `hijo_izq`, `hijo_der`, `_subir`, `_bajar`, `insertar`, `extraer_maximo`, `ver_maximo`), con desempate por orden de llegada.

**Entidad** (`entidad.py`): clase base de `Lote`, `Muestra`, `Profesional`, `Equipo`, `Procedimiento`, `Inspeccion` y `Reporte`. Define `__eq__` (mismo tipo y mismo `id`) y `__hash__` (`hash(id)`), así una entidad cargada con pickle o JSON es igual a la original y las entidades se pueden guardar en un `set`. `Defecto` no la hereda: no tiene id, y dos defectos con los mismos datos son dos defectos distintos.

**Soporte:** `EstadoMuestra` y `EstadoLote` (enums), `validacion.py` (funciones de validación reutilizables) y `excepciones.py` (jerarquía con base `CalidadError` y `**detalles`: `DatosInvalidosError`, `EquipoNoAptoError`, `CertificacionNoVigenteError`, `TransicionIlegalError`, `InspeccionInvalidaError`, `EstructuraVaciaError`, `EstructuraLlenaError`).

---

## 6. Reglas de negocio: dónde se cumplen

| # | Regla | Dónde | Tests |
|---|---|---|---|
| 1 | Ids únicos y no vacíos; cantidades enteras positivas | `uuid4` en cada constructor; `validar_cantidad` | `test_reglas_consigna`, `test_validacion` |
| 2 | La muestra pertenece a un solo lote, no se puede mover y no supera la cantidad fabricada | `Lote.crear_muestra`, `Empresa.crear_registrar_muestras`; `lote_id` solo tiene getter | `test_lote`, `test_empresa` |
| 3 | Gravedad entre 1 y 5; datos del defecto coherentes con su procedimiento | `validar_gravedad`; `DefectoVisual` y `DefectoDimensional`; `CLASE_DEFECTO` | `test_defecto`, `test_reglas_consigna` |
| 4 | Calibración válida hasta 182 días, contando los extremos | `Equipo.esta_calibrado` | `test_equipo`, `test_indices_por_fecha` |
| 5 | Certificación vigente con los extremos incluidos; si falta, la muestra no cambia | `Certificacion.es_vigente`; `Inspeccion.__init__` | `test_certificacion`, `test_inspeccion` |
| 6 | Solo una muestra `PENDIENTE` inicia, una sola inspección por muestra, con requisitos fijos | `Inspeccion.__init__`; `Muestra.asignar_inspeccion` | `test_inspeccion` |
| 7 | Evaluación polimórfica, sin defectos ajenos | `evaluar()` en cada subclase; control en `Inspeccion.ejecutar` | `test_procedimiento`, `test_reglas_consigna` |
| 8 | No conforme si hay un crítico o si la suma supera el límite | `Muestra.cerrar` | `test_muestra` |
| 9 | Una muestra cerrada no se puede modificar ni reinspeccionar | `Muestra.agregar_defecto`; `defectos` es una tupla | `test_muestra`, `test_inspeccion` |
| 10 | Un único reporte con copia inmutable, solo si es no conforme | `Muestra.cerrar` → `Reporte` | `test_reporte` |
| 11 | El lote se decide solo con todas sus muestras cerradas; rechazado si supera el 5 %; decisión final | `Lote.decidir` | `test_lote`, `test_estados` |
| 12 | Las consultas solo miran muestras cerradas y no tienen efectos | `_muestras_cerradas`, `total_defectos_criticos`, `conteo_por_tipo` | `test_lote` |

---

## 7. Decisiones de diseño

- **¿Cómo reciben los procedimientos observaciones distintas sin exponer la muestra?** Cada procedimiento recibe sus propios objetos de observación y devuelve una lista de defectos. Nunca toca la muestra: es la `Inspeccion` la que agrega los defectos.
- **¿Quién valida todo antes de iniciar?** El constructor de `Inspeccion`. Si una validación falla, la excepción se lanza **antes** de cambiar el estado.
- **¿Cómo se mantiene fijo el contexto?** La inspección guarda sus componentes en atributos privados con solo getters, y el procedimiento no tiene setters.
- **¿La conformidad se guarda o se calcula?** Se calcula a partir de los defectos al cerrar y se guarda como estado final; después del cierre no se pueden agregar defectos, así que no puede haber contradicción.
- **¿Cómo se copia el reporte?** `Reporte` guarda una tupla con `copia()` de cada defecto; cada subclase redefine `copia()` para conservar sus datos propios.
- **¿Dónde se decide el lote?** En `Lote.decidir()`, que solo mira el estado de las muestras; agregar un procedimiento nuevo no la afecta.
- **¿Por qué un AVL y no un árbol de búsqueda común?** Las fechas de calibración y de reportes llegan en orden, que es el peor caso de un árbol sin balance (queda como una lista y buscar es O(n)). El AVL se rebalancea con rotaciones y garantiza O(log n). El índice de equipos se mantiene al día porque los equipos siempre se crean por `Empresa`; el de reportes se arma al consultar, porque los reportes los crea la `Muestra` al cerrarse.
- **¿Por qué una cola de prioridad para los reportes?** Hay que atender primero al más grave, no al que llegó antes. La prioridad es la tupla (gravedad máxima, suma de gravedades) y los empates salen por orden de llegada.
- **¿Dónde va el azar?** Solo en `Simulador`, nunca en el dominio; los tests usan semillas fijas.
- **¿Cuándo dos entidades son iguales?** Cuando tienen el mismo id (clase base `Entidad`). Si se define `__eq__`, Python anula el `__hash__` heredado, así que se definen los dos juntos y sobre el id, que es inmutable. Así `set(reportes) == set(reportes_cargados_del_json)` y una empresa cargada con pickle sigue reconociendo sus objetos. `Defecto` queda fuera a propósito: compararlo por valor fusionaría defectos distintos en un `set`.
- **¿Por qué `App` hereda de 6 clases (herencia múltiple)?** Cada página de la interfaz es una clase con sus propios métodos (patrón *mixin*), y `App` los combina en una sola ventana. Así cada página está en su archivo, en lugar de un único archivo de 1400 líneas. Las páginas no repiten nombres de métodos, así que el MRO (`App → PaginaPanel → … → Archivos → object`) no genera ambigüedades. No es una relación "es un" en sentido estricto: se usa la herencia para reunir comportamiento.

---

## 8. Extensiones (fuera de lo que pide la consigna)

La consigna deja **fuera de alcance la interfaz gráfica y la persistencia**. Las sumamos para aplicar temas de la materia, sin cambiar ninguna regla:
- **Serialización:** JSON para los reportes (legible, no depende de Python: `to_dict()` + `json.dump`, y `Clase(**data)` al cargar) y pickle para la empresa completa (retomar el trabajo donde quedó).
- **Interfaces interactivas:** `interfaz.py` con `front/` (ventana) y `consola.py` (`input()`).
- **Simulación aleatoria con semilla**, para generar y repetir casos.
- **Índices AVL y cola de prioridad**, para consultas por fecha y orden de atención.

---

## 9. Conceptos de la materia aplicados

Resumen; el detalle de cada tema y subtema del programa, con el archivo, la clase, el método y el porqué, está en las guías [`DEFENSA_ORAL_ES.md`](DEFENSA_ORAL_ES.md) (y sus versiones en inglés y francés).

| Unidad del programa | Dónde se aplica (ejemplos) |
|---|---|
| 1-2. Objetos y tipos de datos | `isinstance`, `is` frente a `==` (lo cargado con pickle no es el mismo objeto pero sí la misma entidad); tuplas para devolver datos inmutables; listas, diccionarios y strings (`isalpha`, `join`, f-strings) |
| 3. Bibliotecas y módulos | Módulos y paquetes propios (`classes/`, `front/`, `front/paginas/`); `datetime`, `uuid`, `abc`, `json`, `pickle`, `random`, `functools`, `os`, `tkinter`, `pytest` |
| 4. Funciones | `lambda`, `map`, `filter`, `reduce`, `zip`, `sorted(key=...)`, `any`/`all`, `*args`, `**kwargs`, funciones como valores (`intentar` en `main.py`), `yield` |
| 5. Excepciones | Jerarquía propia con base `CalidadError`, `raise ... from e`, `try/except/finally` |
| 6. POO | Encapsulamiento con `@property`, herencia simple, multinivel y múltiple (`App` en `front/clase_app.py` hereda de las 6 clases de página; `Procedimiento(Entidad, ABC)`), polimorfismo, clase abstracta (`ABC`), `@staticmethod`/`@classmethod`, métodos mágicos (`__eq__`, `__hash__`, `__len__`, `__iter__`, `__contains__`, `__lt__`, `__bool__`, `__repr__`, `__str__`), composición y agregación |
| 7. Estructuras de datos | Listas enlazadas, pila, cola, árbol AVL, heap, diccionarios, tuplas, conjuntos (`set` con `&`, `^`, `-`, `update` y entidades hashables) |
| 8. Recursividad | Todas las operaciones del AVL; versiones recursivas de `ListaEnlazada` frente a las iterativas |
| 10-11. Búsqueda y complejidad | Búsqueda secuencial (lista enlazada) frente a búsqueda en el AVL O(log n); heap O(log n) |

---

## 10. Uso de IA

El modelo de dominio, las clases base y los tests iniciales los construimos nosotros. Después usamos Claude (Claude Code) para revisar el código y aplicar los conceptos teóricos en los lugares que correspondía.

**Qué se generó con IA:** con Claude, a partir de nuestras indicaciones, se generaron:
- la interfaz gráfica (`interfaz.py` y `front/`) y el menú por consola (`consola.py`);
- el `Simulador` (`classes/simulador.py`);
- la serialización con JSON y pickle;
- `Nodo`, `ListaEnlazada`, el árbol AVL, la cola de prioridad y los conjuntos (`Entidad` y las operaciones con `set`);
- buena parte de los tests nuevos;
- la reorganización de `main.py`, este README y las guías `DEFENSA_ORAL`.

Después los revisamos, los adaptamos al resto del sistema y los probamos con `pytest`.

**Detección de errores**
- Un commit dejó `Muestra` usando `self._estado`, un atributo que ya no existía, y eso hacía fallar 33 tests; ese mismo commit había deshecho mejoras en `Lote`.
- `Nodo.set_dato` comparaba el tipo del dato nuevo con `type(self)` en lugar de `type(self.dato)`.
- `Reporte` no aceptaba el historial de estados que `Muestra` le pasaba.
- `Inspeccion.cerrar()` marcaba la inspección como cerrada antes de cerrar la muestra.
- `validar_texto` rechazaba nombres reales como "ISO 9001"; se agregó `validar_nombre_tecnico`.
- Un filtro mal escrito en `Empresa` devolvía una lista vacía sin avisar; `listar_equipos(categoria=...)` lanzaba `TypeError` porque el parámetro de `_filtrar` se llamaba igual que el atributo.
- En la primera versión del menú, escribir mal un dato después de iniciar una inspección dejaba la muestra trabada en `EN_INSPECCION`.
- En la interfaz: crear muestras que no entraban dejaba creadas solo algunas; se podía inspeccionar sin observaciones; al fallar la exportación se mostraba "None"; dos profesionales con el mismo nombre no se distinguían.
- El árbol binario de búsqueda inicial se degeneraba en una lista con claves repetidas u ordenadas; se reemplazó por un AVL.
- Al cargar un reporte desde JSON, su id volvía como texto en lugar de `UUID`: con `__eq__` por id, el reporte cargado no habría sido igual al original. Se convierte al reconstruirlo.
- La guía de defensa anterior tenía ejemplos de código que fallaban (métodos inexistentes y argumentos mal pasados); se rehízo verificando cada ejemplo.

**Dónde aplicar los conceptos teóricos**
- Reemplazar bucles por `map`, `filter` y `lambda`, sin usar `map` solo para provocar efectos.
- Usar la pila y la cola en el dominio (historial de estados y muestras pendientes), con los nombres de la cátedra.
- Elegir el AVL para consultas por fecha y el heap para el orden de atención.
- Sumar usos naturales de temas que faltaban: `*args`, `__contains__`, `__lt__` con `sorted`, `reduce`, `finally`, y `__eq__` con `__hash__` para usar entidades en conjuntos.
- Elegir qué guardar con JSON y qué con pickle; ubicar el azar en un `Simulador` con semilla.
- Agregar tests para las pruebas mínimas de la consigna y quitar tests repetidos o sin uso.

Todo el código generado lo revisamos, lo probamos con `pytest` y lo podemos explicar.
