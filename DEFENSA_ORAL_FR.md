# Guide pour la soutenance orale — Contrôle qualité (QuantumTech Precision)

Pour chaque thème du programme de **Structures de données et programmation** : **où** il se trouve dans le code (fichier → classe → méthode) et **pourquoi** il a été utilisé à cet endroit. À la fin : les erreurs qu'on peut provoquer en direct, les cas limites et les questions les plus probables. Le détail technique complet se trouve dans le [README](README.md) (en espagnol).

> Les noms de classes, de méthodes et les messages sont en espagnol, comme dans le code. Vocabulaire : *lote* = lot, *muestra* = échantillon, *defecto* = défaut, *gravedad* = gravité, *equipo* = instrument, *profesional* = inspecteur, *reporte* = rapport d'écart, *procedimiento* = procédure.

---

## 1. Le système en une minute

**Problème :** QuantumTech utilisait des instruments périmés, clôturait des lots incomplets et émettait des rapports qui n'expliquaient pas le rejet. **Solution :** un système qui valide tout avant d'inspecter et décide la conformité avec des règles fixes.

**Flux :** enregistrer (lot → échantillons dans une **file**) → valider (certification, instrument, état) → évaluer (chaque procédure à sa façon : **polymorphisme**) → clôturer (CONFORME / NO_CONFORME, historique dans une **pile**, rapport si non conforme) → décider le lot (rejeté au-delà de 5 %) → traiter les rapports du plus grave au moins grave (**tas**).

| Classe | Rôle | Méthodes clés |
|---|---|---|
| `Muestra` | Sous-ensemble du lot ; la seule classe qui change son propre état | `iniciar_inspeccion`, `agregar_defecto`, `cerrar` |
| `Lote` | Lot de production ; décide approuvé ou rejeté | `crear_muestra`, `decidir`, `porcentaje_no_conforme` |
| `Inspeccion` | Réunit échantillon, inspecteur, instrument, procédure et date ; **valide tout avant de commencer** | `__init__`, `ejecutar`, `cerrar` |
| `Procedimiento` (abstraite) | Contrat d'évaluation ; deux sous-classes aux critères différents | `evaluar` |
| `Defecto` | Écart immuable ; sous-classes visuelle et dimensionnelle | `es_critico`, `copia`, `__lt__` |
| `Reporte` | Trace immuable d'un échantillon non conforme | `gravedad_maxima`, `defectos_por_gravedad`, `to_dict` |
| `Empresa` | Point d'entrée : enregistre tout, interroge et sérialise | `crear_registrar_*`, `lanzar_inspeccion`, `listar_*` |
| `ArbolAVL` / `ColaPrioridad` | Index par date et ordre de traitement | `buscar`, `buscar_rango` / `insertar`, `extraer_maximo` |

---

## 2. Les thèmes du programme dans le projet

### Unité 1 — En Python, tout est objet
| Sous-thème | Où | Pourquoi là |
|---|---|---|
| `isinstance` | `Profesional.agregar_certificacion`, `Nodo.set_siguiente`, `Inspeccion.ejecutar` (défauts étrangers), `Empresa.cargar` | Vérifier le **type** de l'objet avant de l'accepter protège les règles (par exemple, qu'un fichier chargé soit vraiment une `Empresa`) |
| `is` vs `==` | `main.py` section 6 : `cargada is not empresa` ; les tests utilisent `is` avec la file | Distinguer **identité** (le même objet) et **égalité** (même contenu) : ce que pickle charge est un autre objet au même contenu |
| `type(e).__name__` | `intentar` dans `main.py`, `App._ejecutar` dans `front/clase_app.py`, `ejecutar_opcion` dans `consola.py` | Montrer à l'utilisateur quel type d'erreur s'est produit |

### Unité 2 — Types de données
| Sous-thème | Où | Pourquoi là |
|---|---|---|
| Immuables : **tuples** | `Muestra.defectos`, `Lote.muestras`, `Reporte.defectos`, `Pila.historial()` | On renvoie des tuples pour que personne ne modifie l'état interne de l'extérieur (encapsulation) |
| Mutables : listes et dictionnaires | Listes internes (`Muestra._defectos`), registre d'`Empresa` | À l'intérieur de l'objet, il faut pouvoir ajouter des éléments |
| Chaînes | `validar_texto` (`isalpha`), `validar_nombre_tecnico` (`isalnum`), `ListaEnlazada.__str__` (`join`), f-strings dans tous les messages | Valider les noms (« Ana 2 » n'est pas un nom ; « ISO 9001 » est un nom technique valide) et construire des messages clairs |
| Copie superficielle | `Profesional.certificaciones` renvoie `dict(...)` | Une copie du dictionnaire : la modifier ne change pas l'inspecteur |
| Copie d'objets | `Reporte` garde `copia()` de chaque défaut | Le rapport ne dépend pas des objets d'origine |

### Unité 3 — Bibliothèques et modules
**Modules et paquets propres :** `classes/` (le domaine), `front/` et `front/paginas/` (l'interface, un module par page) ; `interfaz.py` se contente d'importer `App` et de l'ouvrir.

**Bibliothèques :** `datetime` (`date`, `timedelta` : étalonnages, certifications, échéances) · `uuid` (identifiants uniques, règle 1) · `abc` (classe abstraite) · `json` et `pickle` (sérialisation) · `random` (simulateur avec graine) · `functools.reduce` · `os` (supprimer le fichier temporaire dans `main.py`) · `tkinter` (interface graphique) · `pytest` (500 tests).

### Unité 4 — Fonctions
| Sous-thème | Où | Pourquoi là |
|---|---|---|
| Paramètres par défaut | `Cola(tipo=None, maxsize=None)`, `Simulador(semilla=None)`, `cola_atencion_reportes(desde=None, hasta=None)` | Le cas courant marche sans arguments ; les cas particuliers sont explicites |
| `*args` | `Empresa.crear_registrar_muestras(lote, *cantidades)` | Créer plusieurs échantillons en un appel et vérifier le total **avant** de créer (s'ils n'entrent pas tous, aucun n'est créé) |
| `**kwargs` | `crear_registrar_procedimiento(tipo, **kwargs)`, `listar_*(**filtros)`, `CalidadError(**detalles)`, `simular_lote(..., **opciones)` | Chaque procédure a ses propres paramètres (`unidad_medida`) ; les filtres se choisissent à l'appel |
| Dépaquetage | `crear_registrar_muestras(lote, *[50] * 20)`, `Reporte(**datos)`, `Clase(**datos)` dans `from_dict` | Passer une liste comme arguments séparés et un dictionnaire comme arguments nommés |
| Fonctions comme valeurs | `intentar(descripcion, donde, accion)` dans `main.py` reçoit une `lambda` ; `key=` dans `sorted` | Réutiliser le même `try/except` pour les 25 erreurs |
| `lambda`, `map`, `filter` | `Lote.porcentaje_no_conforme`, `evaluar()` des deux procédures, `Empresa._filtrar`, `Empresa.reportes` | Transformer et sélectionner des collections sans boucles explicites |
| `reduce` | `Reporte.gravedad_maxima` | Accumuler la gravité maximale en parcourant les défauts un par un |
| `sorted` | `Profesional.certificaciones_vigentes` (`key=lambda c: c.fecha_fin`), `Reporte.defectos_por_gravedad` (utilise `__lt__`) | Trier sans modifier la collection d'origine |
| `any`, `all`, `sum`, `max` | `Muestra.tiene_critico` (`any`), `Lote.todas_cerradas` (`all`), `Muestra.suma_gravedades` (`sum`) | Des règles métier en une ligne : « l'un est critique », « tous clôturés » |
| `zip`, `enumerate` | `main.py` (comparer rapports d'origine et chargés), `consola.elegir_de_lista` (liste numérotée) | Parcourir deux collections en parallèle ; numéroter des options |
| Générateurs (`yield`) | `ListaEnlazada.__iter__` | Parcourir les nœuds un par un sans copier ; d'où le fonctionnement avec `for`, `map` et `filter` |

### Unité 5 — Exceptions
| Sous-thème | Où | Pourquoi là |
|---|---|---|
| `raise` | Validations de tous les constructeurs ; `Inspeccion.__init__` | Rejeter **avant** de changer l'état : un objet invalide n'est pas créé, l'échantillon ne change pas |
| Exceptions propres et hiérarchie | `excepciones.py` : `CalidadError` → 7 sous-classes | Un seul `except CalidadError` les capture toutes ; chaque sous-classe dit quelle règle a échoué |
| Données en plus (`**detalles`) | `CalidadError.detalles` (cas 2a de `main.py`) | Joindre à l'erreur les données qui l'ont causée |
| `try/except ... as e` et ordre | `consola.ejecutar_opcion` (`CalidadError`, puis `OSError`), `App._ejecutar` (`front/clase_app.py`) | Capturer d'abord les erreurs du système, ensuite les erreurs de fichier |
| Propagation | Levée dans `Lote.decidir`, capturée dans l'interface | Le domaine détecte le problème ; l'interface décide comment l'afficher |
| `raise ... from e` | `Empresa.cargar`, `Empresa.cargar_reportes_json`, `ArbolAVL.insertar` | Convertir des erreurs Python (pickle, JSON, `TypeError`) en erreurs du système sans perdre la cause |
| `finally` | `main.py`, cas 6a | Supprimer **toujours** le fichier temporaire, erreur ou pas |
| Non utilisé | `try/else` | Pas nécessaire : le code « sans erreur » va dans le `try` |

### Unité 6 — Programmation orientée objet
| Sous-thème | Où | Pourquoi là |
|---|---|---|
| Encapsulation | Attributs `_x` avec `@property` dans toutes les classes ; `Defecto` et `Reporte` sans setters | L'état ne change que par des méthodes qui valident (exigé par l'énoncé) |
| Getters et setters | `Nodo` et `NodoAVL` (`get_dato`, `set_siguiente` avec validation) | Le setter valide avant de chaîner |
| Attributs de classe et constantes | `Lote.ESTADOS_FINALES`, `Equipo.DIAS_VALIDEZ_CALIBRACION`, `Empresa.CLASES_POR_CATEGORIA`, `Procedimiento.CLASE_DEFECTO`, `Simulador.DEFECTOS_VISUALES` | Une valeur partagée écrite à un seul endroit (les 182 jours) |
| `@staticmethod` / `@classmethod` | `Defecto.from_dict`, `Reporte.from_dict`, `Empresa.cargar_reportes_json` / `Empresa.cargar` | Créer des objets à partir de données sans objet préalable ; `cargar` utilise `cls` pour vérifier le type |
| Héritage simple | `Procedimiento` → `ProcedimientoVisual` / `ProcedimientoDimensional` ; `Defecto` → `DefectoVisual` / `DefectoDimensional` | Règle « est un » : une procédure visuelle **est une** procédure |
| Héritage multiniveau | `Exception` → `CalidadError` → `DatosInvalidosError` (et les autres) | Capturer par niveau : toutes les erreurs du système ou une en particulier |
| `super()` | `ProcedimientoVisual.__init__`, `DefectoDimensional.__init__` et `to_dict` | Réutiliser le code du parent et ajouter le sien |
| Héritage multiple et MRO | `App` (`front/clase_app.py`) hérite de `PaginaPanel`, `PaginaRegistro`, `PaginaInspeccion`, `PaginaLotes`, `PaginaReportes` et `Archivos`. MRO : `App → PaginaPanel → … → Archivos → object` | Patron *mixin* : chaque page apporte ses méthodes et `App` les réunit dans une seule fenêtre, au lieu d'un fichier de 1400 lignes. Aucune page ne répète un nom de méthode, donc le MRO ne crée pas d'ambiguïté. Ce n'est pas un « est un » strict : l'héritage sert à réunir des comportements. Le domaine n'utilise pas l'héritage multiple |
| Classe abstraite | `Procedimiento(ABC)` avec `@abstractmethod evaluar` | On ne peut pas créer une procédure générique (cas 1e) |
| Polymorphisme | `evaluar()`, `copia()`, `to_dict()` | L'inspection appelle `evaluar()` sans savoir de quelle procédure il s'agit |
| Méthodes spéciales | `__len__` et `__iter__` (`ListaEnlazada`, `Pila`, `Cola`, `ArbolAVL`), `__contains__` (`muestra in lote`), `__lt__` (`Defecto`), `__bool__` (`ColaPrioridad` : `while cola:`), `__str__`, `__repr__` | Nos classes fonctionnent avec `len`, `for`, `in`, `<`, `sorted` et `while` |
| Composition | Lot–Échantillon (le lot les crée), Échantillon–Pile, Lot–File, Pile/File–ListeChaînée | La partie n'existe pas sans le tout |
| Agrégation | Inspecteur–Certification | La certification est créée à l'extérieur puis ajoutée |
| Association | `Inspeccion` avec échantillon, inspecteur, instrument et procédure | Elle les utilise, mais chacun existe indépendamment |

### Unité 7 — Structures de données
| Structure | Où | Pourquoi là |
|---|---|---|
| Dictionnaires | Registre d'`Empresa` (`{catégorie: {id: objet}}`), `Lote._muestras`, certifications de l'inspecteur, `conteo_por_tipo` (avec `.get`), `to_dict()` | Recherche par identifiant en O(1) ; comptage par type |
| Tuples | Retours immuables ; priorités du tas `(gravité max, somme)` | Les tuples se comparent élément par élément : la gravité max décide d'abord |
| Liste chaînée | `Nodo`, `ListaEnlazada` (un seul type de donnée par liste) | Base de la pile et de la file, comme en cours |
| Pile (LIFO) | Historique des états de `Muestra` : `peek()` est l'état actuel | Le dernier état est celui qui compte, et l'historique complet va dans le rapport |
| File (FIFO) | Échantillons en attente de `Lote` ; `ArbolAVL.niveles()` (parcours en largeur) | Inspecter dans l'ordre d'arrivée |
| Arbre AVL | `Empresa` : instruments par date d'étalonnage, rapports par date, lots par production ; `Lote` : défauts par gravité | Les dates arrivent dans l'ordre : un arbre non équilibré deviendrait une liste. Il couvre les exercices de la classe 11 : `minimo`, `maximo`, `buscar` et `insertar` récursifs, et `entre(a, b)` (notre `buscar_rango`). Contrairement à l'ABR du cours, une clé répétée n'est pas ignorée : elle est stockée dans le même nœud, car beaucoup de défauts ont la même gravité |
| Tas (file de priorité) | `Empresa.cola_atencion_reportes()` | Traiter d'abord le plus grave, pas le premier arrivé |
| Ensembles | Pas encore vus en cours | Quand ils seront vus : `__eq__` et `__hash__` par identifiant dans les entités |
| Vecteurs et matrices | Non utilisés | Le domaine n'a pas de données en grille |

### Unité 8 — Récursivité
Comme vu en cours, la récursivité est une **technique** (pas une structure de données), et une récursion correcte remplit **3 conditions** : un **cas de base** résolu directement, un **cas récursif** qui applique la même fonction à un problème plus petit, et une **progression** (chaque appel se rapproche du cas de base). Elle a une **phase de descente** (les appels descendent) et une **phase de remontée** (les appels en attente se résolvent dans l'ordre inverse).

| Sous-thème | Où | Pourquoi là |
|---|---|---|
| Cas de base et cas récursif | Toutes les opérations d'`ArbolAVL` (`_insertar_rec`, `_buscar_rec`, `_buscar_rango_rec`, `_eliminar_rec`, parcours) | Chaque sous-arbre est un arbre : le cas de base est `None` (ou trouver la clé) |
| Phase de remontée | `ArbolAVL._balancear`, appelé au retour de chaque appel | À la remontée, on met à jour les hauteurs et on fait les rotations : la récursion parcourt le chemin de bas en haut sans le stocker à la main |
| Progression | Chaque appel descend d'un niveau (`nodo.get_izquierdo()` ou `get_derecho()`) | Le sous-arbre rétrécit à chaque appel jusqu'à atteindre `None` |
| Récursivité vs itération | `ListaEnlazada` : `buscar` / `buscar_recursivo`, `len` / `longitud_recursiva` (`main.py` 5.1) | Comparer les deux approches sur la même structure |
| Critère d'utilisation et limite | Récursivité dans l'arbre (structure **hiérarchique**) ; versions itératives dans la liste (processus **linéaire**) | C'est le critère du cours. De plus, une très longue liste provoquerait `RecursionError` ; dans l'AVL la profondeur est log n |

### Unité 9 — Graphiques (Matplotlib)
Non utilisé. L'énoncé exclut les cartes de contrôle, et le tableau de bord de l'interface (`front/paginas/panel.py`, avec les fonctions de `front/visualizaciones.py`) dessine ses graphiques à la main sur un `Canvas` tkinter, sans bibliothèque supplémentaire.

### Unités 10 et 11 — Recherche, tri et complexité
| Sous-thème | Où | Complexité |
|---|---|---|
| Recherche séquentielle | `ListaEnlazada.buscar` | O(n) |
| Recherche dans un arbre équilibré (équivalente à la dichotomie) | `ArbolAVL.buscar` et `buscar_rango` | O(log n) garanti |
| Recherche par clé dans un dictionnaire | `Lote.__contains__`, `Empresa.obtener_lote` | O(1) |
| Tri | `sorted` (`Reporte`, `Profesional`), parcours infixe de l'AVL, extraction successive du tas | L'AVL renvoie les données déjà triées |
| Algorithmes manuels (bulles, rapide, fusion) | Non implémentés | Ils n'apportent rien au domaine ; `sorted` et les structures trient déjà |

### Matériel complémentaire du cours — Sérialisation
| Format | Ce qu'il enregistre | Pourquoi |
|---|---|---|
| JSON (`Empresa.exportar_reportes_json` / `cargar_reportes_json`) | Les rapports d'écart | Lisible et indépendant de Python. Enregistré avec `to_dict()` + `json.dump`, chargé avec `Clase(**data)` ; `UUID`, `date` et les enums deviennent du texte |
| pickle (`Empresa.guardar` / `Empresa.cargar`) | L'entreprise complète, avec ses relations | Enregistre directement nos propres objets, pour reprendre le travail. Ne charger que ses propres fichiers |

---

## 3. Récursivité, AVL et tas, expliqués simplement

**Arbre AVL.** Un arbre de recherche (les plus petits à gauche, les plus grands à droite) maintenu équilibré : à chaque nœud, `hauteur(gauche) − hauteur(droite)` doit valoir −1, 0 ou 1. Si cela vaut 2 ou −2, on fait une **rotation** :

```
Insérer 10, 20, 30 (chargé à droite)  →  rotation à gauche

10                        20
  \                      /  \
   20          →       10    30
     \
      30
```

Les 4 cas : gauche-gauche (rotation à droite), droite-droite (rotation à gauche), gauche-droite et droite-gauche (deux rotations). Dans `main.py` 5.2, 15 clés triées laissent l'AVL à une **hauteur de 4** ; sans équilibrage, la hauteur serait de 15.

**Récursivité.** `_buscar_rec(nodo, clave)` : si `nodo` vaut `None`, la clé n'y est pas (cas de base) ; si la clé correspond, on l'a trouvée (cas de base) ; sinon, on cherche seulement dans la moitié gauche ou droite (cas récursif).

**Tas (max-heap).** Un arbre complet stocké dans une liste : `padre(i) = (i−1)//2`, `hijo_izq(i) = 2i+1`, `hijo_der(i) = 2i+2`. Le maximum est toujours à l'indice 0. À l'insertion, l'élément **monte** tant qu'il est plus grand que son parent ; à l'extraction, le dernier passe à la racine et **descend** par le plus grand enfant. Les deux opérations sont en O(log n).

---

## 4. Erreurs qu'on peut provoquer en direct

**Où elles sont capturées :** dans `main.py`, dans la fonction `intentar` ; dans l'interface graphique, dans `App._ejecutar` (`front/clase_app.py` : affiche une fenêtre avec le nom de l'exception) ; dans `consola.py`, dans `ejecutar_opcion` (affiche `[X] NomDeLErreur: message`). Dans tous les cas, le programme continue.

**Pourquoi l'état ne change pas :** chaque validation a lieu **avant** de modifier quoi que ce soit. Si elle échoue, l'exception est levée et rien n'est modifié.

| Cas dans `main.py` | Ce qu'on tente | Exception | Levée dans |
|---|---|---|---|
| 1a / 4b | Échantillon qui dépasse le lot (4b : plusieurs à la fois → aucun n'est créé) | `TransicionIlegalError` | `Lote.crear_muestra` / `Empresa.crear_registrar_muestras` |
| 1b | Lot de quantité 0 | `DatosInvalidosError` | `validar_cantidad` |
| 1c | Certification qui se termine avant de commencer | `DatosInvalidosError` | `validar_rango_fechas` |
| 1d | Inspecteur nommé « Ana 2 » | `DatosInvalidosError` | `validar_texto` |
| 1e | `Procedimiento(...)` générique | `TypeError` (de Python) | `ABC`, à cause de `@abstractmethod evaluar` |
| 2a / 2b | Sans certification / certification expirée | `CertificacionNoVigenteError` | `Inspeccion.__init__` |
| 2c / 2e | Instrument étalonné il y a 183 jours / après l'inspection | `EquipoNoAptoError` | `Inspeccion.__init__` (`Equipo.esta_calibrado`) |
| 2d | Instrument d'une autre catégorie | `EquipoNoAptoError` | `Inspeccion.__init__` (`Equipo.es_compatible`) |
| 2f | La certification et l'instrument échouent : seule la première erreur sort | `CertificacionNoVigenteError` | `Inspeccion.__init__` (ordre : date, état, certification, catégorie, étalonnage) |
| 2g | Date écrite comme texte | `DatosInvalidosError` | `Inspeccion.__init__` |
| 3a | Réinspecter un échantillon clôturé | `TransicionIlegalError` | `Inspeccion.__init__` |
| 3b | Exécuter une inspection clôturée | `InspeccionInvalidaError` | `Inspeccion.ejecutar` |
| 3c | Ajouter un défaut à un échantillon clôturé | `TransicionIlegalError` | `Muestra.agregar_defecto` |
| 3d / 4a | Décider un lot incomplet / le décider une seconde fois | `TransicionIlegalError` | `Lote.decidir` |
| 3e | Inspection suivante avec la file vide | `EstructuraVaciaError` | `Empresa.lanzar_siguiente_inspeccion` |
| 4c | Gravité 6 | `DatosInvalidosError` | `validar_rango_entero` |
| 4d | Défaut dimensionnel dans la tolérance | `DatosInvalidosError` | `DefectoDimensional.__init__` |
| 5a / 5b | Extraire d'un tas vide / ajouter à une file pleine | `EstructuraVaciaError` / `EstructuraLlenaError` | `ColaPrioridad.extraer_maximo` / `Cola.put` |
| 6a | Charger un fichier qui n'est pas une entreprise | `DatosInvalidosError` | `Empresa.cargar` (avec `raise ... from e`) |
| 8a | Filtrer par un attribut inexistant | `DatosInvalidosError` | `Empresa._filtrar` |

**Pour les montrer dans l'interface** (`py interfaz.py`) : bouton *Datos de ejemplo*, puis inspecter avec Carlos (sans certification), choisir l'instrument périmé, décider un lot avec des échantillons en attente, ou créer plus d'échantillons que ce qui rentre.

**Code minimal (vérifié) à exécuter en direct :**
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
carlos = empresa.crear_registrar_profesional("Carlos")            # sans certification
equipo = empresa.crear_registrar_equipo("Visual", date(2025, 6, 1))
proc = empresa.crear_registrar_procedimiento(
    ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida="ISO")  # **kwargs

try:                                     # Carlos n'a pas la certification
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

## 5. Cas limites

| Cas | Règle | Résultat |
|---|---|---|
| Étalonné il y a **182** jours | Les bornes sont incluses | Valide (le cas 2c utilise 183 ; le lot 2 utilise un instrument de 182 jours) |
| Étalonné il y a **183** jours ou dans le futur | `0 <= jours <= 182` | `EquipoNoAptoError` |
| Certification le premier ou le dernier jour | `fecha_inicio <= date <= fecha_fin` | Valide (Bruno, lot 2 de `main.py`) |
| Somme des gravités **égale** à la limite | Non conforme seulement si elle la **dépasse** | CONFORME |
| Un défaut de gravité 5 | Un seul défaut critique suffit | NO_CONFORME même si la somme est faible |
| Lot avec **exactement 5 %** de non-conformes | Rejeté seulement au-**delà** de 5 % | APROBADO (1 sur 20) ; 2 sur 20 = 10 % → RECHAZADO |
| Échantillons qui ne rentrent pas tous | Le total est vérifié avant de créer | Aucun n'est créé |

**Graines du simulateur** (lot de 20 échantillons, probabilité de défaut 0,15, limite 5) : graine **5** → 5 % → APROBADO ; graine **1** → 10 % → RECHAZADO. Commande vérifiée :
```bash
py -c "from datetime import date; from classes.empresa import Empresa; from classes.certificacion import Certificacion; from classes.proc_visual import ProcedimientoVisual; from classes.simulador import Simulador; e = Empresa(); l = e.crear_registrar_lote('Bulones', 200); e.crear_registrar_muestras(l, *[10] * 20); a = e.crear_registrar_profesional('Ana'); a.agregar_certificacion(Certificacion('ISO', date(2025, 1, 1), date(2025, 12, 31))); q = e.crear_registrar_equipo('Visual', date(2025, 6, 1)); p = e.crear_registrar_procedimiento(ProcedimientoVisual, limite_gravedad_acumulada=5, certificacion_requerida='ISO'); Simulador(5).simular_lote(e, l, a, q, p, date(2025, 6, 15), prob_defecto=0.15); print('Semilla 5:', l.porcentaje_no_conforme(), '% ->', l.decidir().value)"
```

---

## 6. Changement contrôlé (extensions que le cours peut demander)

**Réinspection autorisée.** Ajouter un état `REINSPECCION_AUTORIZADA` dans `EstadoMuestra` ; dans `Muestra`, garder une liste d'inspections au lieu d'une seule et permettre `iniciar_inspeccion()` depuis cet état ; dans `Inspeccion.__init__`, accepter cet état en plus de `PENDIENTE`. `Lote` ne change pas : il décide déjà avec l'état actuel (le sommet de la pile).

**Échantillonnage selon la sévérité (normal, renforcé, réduit).** Une énumération `NivelSeveridad` et un attribut dans `Lote` ; les 5 % de `Lote.decidir()` dépendent du niveau (par exemple 2 % en renforcé). `Empresa` pourrait changer le niveau selon les derniers lots rejetés.

**Étalonnage par heures d'utilisation.** Dans `Equipo`, des attributs `horas_uso` et `limite_horas` et une méthode `registrar_uso(horas)` ; `esta_calibrado(fecha)` exige en plus `horas_uso <= limite_horas` ; `Inspeccion.cerrar()` enregistre les heures utilisées. L'index AVL par date ne change pas.

---

## 7. Questions probables

- **Où tout est-il validé avant l'inspection ?** Dans `Inspeccion.__init__`, dans cet ordre : date, état de l'échantillon, certification, catégorie de l'instrument et étalonnage. En cas d'échec, l'échantillon reste `PENDIENTE`.
- **Pourquoi `Procedimiento` est-elle abstraite ?** Une procédure générique ne sait pas évaluer : chaque sous-classe définit son critère dans `evaluar()`. Python refuse de l'instancier (cas 1e).
- **Comment garantit-on qu'un rapport ne change pas ?** Il garde un tuple de copies des défauts et n'a pas de setters.
- **Pourquoi une pile pour l'historique ?** L'état actuel est le dernier empilé (`peek()`), et l'historique complet reste pour le rapport.
- **Pourquoi une file pour les échantillons ?** Ils sont inspectés dans l'ordre de création (FIFO).
- **Pourquoi un AVL et pas un dictionnaire ?** Le dictionnaire cherche une clé exacte mais ne gère ni les intervalles ni l'ordre (« instruments qui expirent avant X »). Et pas un arbre simple, car les dates arrivent triées et le transformeraient en liste.
- **Pourquoi un tas pour les rapports ?** Il faut traiter d'abord le plus grave, pas le premier arrivé ; le tas donne le maximum en O(1) et l'extraire coûte O(log n).
- **Pourquoi JSON et pickle ?** JSON pour les rapports, que tout le monde doit pouvoir lire ; pickle pour reprendre l'entreprise complète avec ses objets et ses relations.
- **Où est la récursivité ?** Dans toutes les opérations de l'AVL et dans les versions récursives de la liste chaînée (comparées aux versions itératives dans `main.py` 5.1). Elle remplit les 3 conditions : cas de base (`None` ou la clé trouvée), cas récursif (un sous-arbre) et progression (chaque appel descend d'un niveau).
- **Pourquoi `App` hérite-t-elle de 6 classes ?** C'est de l'héritage multiple avec le patron *mixin* : chaque page de `front/paginas/` apporte ses méthodes et `App` les réunit. Aucune page ne répète un nom, donc le MRO n'a pas d'ambiguïté.
- **Comment l'IA a-t-elle été utilisée ?** C'est documenté dans le README (section 10) : ce qui a été généré, quelles erreurs elle a aidé à détecter et comment nous l'avons relu.
