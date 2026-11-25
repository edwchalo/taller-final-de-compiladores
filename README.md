# MiniCompiler Web

Compilador web educativo para **MiniLang**, un lenguaje pequeño de asignaciones y expresiones aritméticas.

La aplicación permite escribir código fuente y observar, en orden, todas las fases de un compilador:

1. Análisis léxico
2. Análisis sintáctico
3. Análisis semántico
4. Generación de código intermedio
5. Optimización
6. Generación de código destino (ensamblador educativo)

---

## Descripción

MiniCompiler Web es un proyecto universitario pensado para **entender** cómo trabaja un compilador, no para generar código de una máquina real.

El usuario ingresa un programa MiniLang, pulsa **Compilar** y ve el resultado de cada fase en tarjetas independientes. Si ocurre un error, la interfaz indica la fase, muestra un mensaje claro y **no continúa** con las etapas siguientes.

---

## Objetivo

Diseñar e implementar un compilador didáctico, con frontend y backend separados, que:

- reconozca un lenguaje propio (MiniLang);
- respete precedencia de operadores y paréntesis;
- detecte variables no declaradas;
- genere código de tres direcciones;
- aplique optimizaciones básicas;
- traduzca el resultado a un ensamblador ficticio (MiniCPU).

---

## Arquitectura

El frontend y el backend se ejecutan por separado en la máquina local.

```text
Navegador (HTML/CSS/JS)
        |
        |  POST /api/compile  { "code": "..." }
        v
Flask (Python)  →  compiler.py
                     ├── lexer.py
                     ├── parser.py
                     ├── semantic.py
                     ├── intermediate.py
                     ├── optimizer.py
                     └── code_generator.py
```

- **Frontend:** interfaz tipo editor oscuro. Se sirve con un servidor HTTP estático (puerto 8080).
- **Backend:** API REST con Flask (puerto 5000).
- **CORS:** habilitado para que el navegador pueda llamar al API desde otro origen.

Endpoint principal:

```http
POST /api/compile
Content-Type: application/json

{
  "code": "a = 10\nb = 5\nresultado = (a + b) * 2"
}
```

Otros endpoints:

- `GET /` — estado del servicio
- `GET /api/health` — comprobación rápida

---

## MiniLang

MiniLang es un lenguaje de un solo tipo de instrucción: la **asignación**.

Soporta:

- identificadores (`a`, `resultado`, `total`);
- números enteros y decimales (`10`, `3.14`);
- operadores `+`, `-`, `*`, `/`, `=`;
- paréntesis.

Ejemplos válidos:

```text
x = 10
y = 20
resultado = x + y
total = (x + y) * 2
```

Una variable se **declara** al asignarle un valor. Debe existir antes de usarse a la derecha de `=`.

No incluye: comentarios, cadenas, condicionales, ciclos ni funciones.

---

## Gramática

```text
programa     → asignacion*
asignacion   → IDENTIFICADOR = expresion
expresion    → termino ((+ | -) termino)*
termino      → factor ((* | /) factor)*
factor       → NUMERO | IDENTIFICADOR | ( expresion )
```

Precedencia (de mayor a menor):

1. Paréntesis
2. Multiplicación y división
3. Suma y resta

Los operadores binarios se asocian a la izquierda.

---

## Fases del compilador

| Fase | Módulo | Resultado |
| --- | --- | --- |
| Léxico | `backend/lexer.py` | Lista de tokens |
| Sintáctico | `backend/parser.py` | Árbol de sintaxis |
| Semántico | `backend/semantic.py` | Tabla de símbolos |
| Intermedio | `backend/intermediate.py` | Código de tres direcciones |
| Optimización | `backend/optimizer.py` | Código intermedio reducido y técnicas usadas |
| Destino | `backend/code_generator.py` | Ensamblador MiniCPU |

`backend/compiler.py` ejecuta las fases en ese orden y construye la respuesta JSON.

### Optimizaciones

- Propagación de constantes
- Plegado de constantes (`2 + 3` → `5`)
- Simplificación algebraica (`x + 0` → `x`, `x * 1` → `x`, `x / 1` → `x`)
- Eliminación de código muerto (solo temporales `t1`, `t2`, … que ya no se usan)

### Código destino

MiniCPU es una **arquitectura educativa ficticia**. No es x86 ni ARM.

Registros: `R0`, `R1`, `R2`.

Instrucciones: `MOV`, `ADD`, `SUB`, `MUL`, `DIV`.

Convención:

- `R0`: operando izquierdo y resultado
- `R1`: operando derecho
- `R2`: auxiliar

El ensamblador se genera a partir del código **ya optimizado**.

---

## Estructura de carpetas

```text
mini-compiler/
├── backend/
│   ├── app.py
│   ├── compiler.py
│   ├── lexer.py
│   ├── parser.py
│   ├── semantic.py
│   ├── intermediate.py
│   ├── optimizer.py
│   └── code_generator.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/
│   └── test_casos.py
├── README.md
├── requirements.txt
└── .gitignore
```

`compiler.py` no forma parte de una fase concreta: coordina el pipeline para que Flask solo se ocupe del HTTP.

---

## Requisitos

- macOS (también funciona en otros sistemas con Python 3)
- Python 3.9 o superior
- Un navegador actual (Chrome, Safari, Firefox, Edge)
- Conexión local; no se necesita internet después de instalar dependencias

---

## Instalación

```bash
cd /Users/macbookair/Documents/mini-compiler
```

(o la ruta donde esté el repositorio)

### Entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

En macOS el prompt debe mostrar `(venv)`.

### Dependencias

```bash
pip install -r requirements.txt
```

Paquetes: `Flask` y `flask-cors`.

---

## Ejecución

Hacen falta **dos** terminales.

### Backend

```bash
cd /Users/macbookair/Documents/mini-compiler
source venv/bin/activate
python backend/app.py
```

Debe escuchar en [http://127.0.0.1:5000](http://127.0.0.1:5000).

### Frontend

```bash
cd /Users/macbookair/Documents/mini-compiler/frontend
python3 -m http.server 8080
```

Abrir [http://127.0.0.1:8080](http://127.0.0.1:8080).

No abras el HTML como archivo (`file://`): el navegador bloquearía la llamada al API.

---

## Pruebas

```bash
cd /Users/macbookair/Documents/mini-compiler
source venv/bin/activate
python -m unittest discover -s tests -v
```

---

## Ejemplos

### Compilación correcta

```text
a = 10
b = 5
resultado = (a + b) * 2
```

### Error léxico

```text
a = 10 @ 5
```

Carácter `@` no permitido.

### Error sintáctico

```text
x = 10 +
```

Falta un operando después de `+`.

### Error semántico

```text
resultado = a + 5
```

La variable `a` no fue declarada.

### Plegado de constantes

```text
x = 2 + 3
```

El intermedio se reduce a `x = 5`.

### Simplificación algebraica

```text
a = 10
resultado = a * 1
```

`a * 1` se simplifica a `a` (y luego puede propagarse la constante `10`).

### Ensamblador

Tras optimizar `(a + b) * 2` con `a = 10` y `b = 5`, el destino copia `30` en `resultado` mediante `MOV`.

---

## Manejo de errores

1. Se indica la **fase** donde ocurrió el problema (léxico, sintáctico o semántico).
2. El mensaje describe el error (y, si es posible, línea y posición).
3. La compilación **se detiene**.
4. Las fases posteriores aparecen como no ejecutadas, nunca como correctas.

En la interfaz:

- **✓** fase correcta
- **✗** fase con error
- **•** fase no ejecutada

---

## Tecnologías

| Capa | Tecnología |
| --- | --- |
| Frontend | HTML5, CSS3, JavaScript (sin frameworks) |
| Backend | Python 3, Flask |
| API | JSON, CORS |
| Pruebas | unittest |

---

## Licencia

Proyecto académico. Uso educativo.
