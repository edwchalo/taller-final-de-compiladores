# Guía de sustentación — MiniCompiler Web

Documento para la exposición oral. No es código del compilador: es un guion de demostración.

Antes de empezar, deja corriendo:

- backend: `python backend/app.py`
- frontend: `python3 -m http.server 8080` dentro de `frontend/`
- navegador: http://127.0.0.1:8080

---

## Qué decir en 1 minuto

MiniCompiler Web es un compilador educativo. Recibe un programa escrito en MiniLang (asignaciones y aritmética) y muestra las seis fases clásicas: léxico, sintáctico, semántico, código intermedio, optimización y ensamblador.

El frontend (HTML, CSS y JavaScript) llama a `POST /api/compile`. Flask ejecuta las fases en orden. Si una falla, se detiene y las siguientes no se marcan como correctas.

El ensamblador no es x86 ni ARM: es MiniCPU, una máquina ficticia con registros R0, R1 y R2.

---

## Guion de demostración (en este orden)

Copia cada programa en el editor y pulsa **Compilar**. Explica lo que aparece.

### 1. Compilación completa

```text
a = 10
b = 5
resultado = (a + b) * 2
```

Qué señalar:

- **Tokens:** identificadores, `=`, paréntesis, `+`, `*`, números.
- **Sintáctico:** el árbol respeta paréntesis y luego la multiplicación: `((a + b) * 2)`.
- **Semántico:** tabla de símbolos con `a`, `b` y `resultado`.
- **Intermedio:**
  ```text
  a = 10
  b = 5
  t1 = a + b
  t2 = t1 * 2
  resultado = t2
  ```
- **Optimizado:** como `a` y `b` son constantes, termina en `resultado = 30`. Menciona las técnicas listadas.
- **Ensamblador:** `MOV` hacia `a`, `b` y `resultado`. Leer el comentario de MiniCPU.

Frase útil: “El compilador calculó `(10 + 5) * 2` en tiempo de compilación; por eso el ensamblador ya no hace ADD ni MUL.”

### 2. Error léxico

```text
a = 10 @ 5
```

Debe verse **✗** en Tokens y las demás fases en gris.

Explicación: el léxico no reconoce `@`. No tiene sentido seguir.

### 3. Error sintáctico

```text
x = 10 +
```

Tokens correctos; falla el parser: después de `+` hacía falta un número, un identificador o `(`.

Explicación: la gramática de `expresion` exige un `termino` a cada lado de `+`.

### 4. Error semántico

```text
resultado = a + 5
```

Léxico y sintaxis correctos. Falla porque `a` no se declaró antes.

Explicación: MiniLang declara al asignar. Primero se analiza la derecha y después se registra la izquierda. Por eso `a = a + 1` también fallaría si `a` no existía.

### 5. Plegado de constantes

```text
x = 2 + 3
```

Intermedio: `t1 = 2 + 3` y `x = t1`.  
Optimizado: `x = 5`.  
Técnicas: plegado, propagación y eliminación del temporal.

### 6. Simplificación algebraica

```text
a = 10
resultado = a * 1
```

Busca en la lista: **Simplificación algebraica** (`t1 = a * 1 → t1 = a`).

Otros ejemplos por si preguntan:

```text
a = 10
resultado = a + 0
```

```text
a = 10
resultado = a / 1
```

### 7. Ensamblador con ADD y MUL (sin optimizar de más)

Si preguntan “¿dónde está el ADD?”, explica: con constantes el optimizador pliega todo. MiniCPU se ve mejor si las operaciones no se pueden calcular en compilador.

En la terminal (opcional, 20 segundos):

```bash
cd /Users/macbookair/Documents/mini-compiler
source venv/bin/activate
python backend/code_generator.py
```

Ahí aparece:

```text
MOV R0, a
MOV R1, b
ADD R0, R1
MOV t1, R0
```

---

## Cómo explicar cada fase (si preguntan “¿qué hace?”)

**Léxico.** Divide el texto en tokens. Ignora espacios. Si hay un carácter ilegal, error léxico.

**Sintáctico.** Descenso recursivo según la gramática. `*` y `/` están en `termino`, por eso ganan a `+` y `-` de `expresion`.

**Semántico.** Tabla de símbolos. No hay tipos complejos: solo “¿esta variable ya existe?”.

**Intermedio.** Cada operación binaria crea un temporal `t1`, `t2`, … Código de tres direcciones: como máximo un operador por instrucción.

**Optimizador.** Recorre ese código y aplica las cuatro técnicas. Las variables del usuario no se borran; solo los temporales muertos.

**Destino.** Traduce cada instrucción intermedia a MiniCPU: carga operandos en R0 y R1, opera, guarda el destino.

---

## Preguntas frecuentes

**¿Por qué no es un compilador real?**  
Porque MiniCPU no existe en hardware. El objetivo es mostrar las fases, no generar un ejecutable.

**¿Dónde está la precedencia?**  
En la gramática: `expresion` llama a `termino`, y `termino` llama a `factor`. No se usa una tabla de precedencia aparte.

**¿Qué pasa si divido por cero?**  
`10 / 0` es sintaxis válida. El plegado no calcula esa división para no romper el compilador. Quedaría para tiempo de ejecución (que este proyecto no simula).

**¿Por qué R2 casi no se usa?**  
Con el esquema carga-opera-guarda bastan R0 y R1. R2 está documentado como auxiliar.

**¿Frontend y backend van juntos?**  
No. El navegador está en el puerto 8080 y Flask en el 5000. CORS permite la petición.

**¿Cómo se detiene un error?**  
`compiler.py` hace `return` en cuanto captura `LexerError`, `ParserError` o `SemanticError`. Las fases siguientes quedan `skipped`.

---

## Orden sugerido de la exposición (8–10 minutos)

1. Título, objetivo y MiniLang (1 min).  
2. Arquitectura frontend/backend (1 min).  
3. Gramática y precedencia (1 min).  
4. Demo 1: programa completo (3 min).  
5. Demos 2–4: los tres errores (2 min).  
6. Demos 5–6: optimizaciones (1 min).  
7. MiniCPU y cierre (1 min).

Si el tiempo es corto, no omitas el programa completo ni un error de cada tipo.
