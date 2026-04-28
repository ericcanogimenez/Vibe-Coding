# Vibe-Coding/Mini Street Fighter at main · ericcanogimenez/Vibe-Coding · GitHub

**URL:** https://github.com/ericcanogimenez/Vibe-Coding/blob/main/Mini%20Street%20Fighter

---

Skip to content
Navigation Menu
Platform
Solutions
Resources
Open Source
Enterprise
Pricing
Sign in
Sign up
ericcanogimenez
/
Vibe-Coding
Public
Notifications
Fork 0
 Star 0
Code
Issues
Pull requests
Actions
Projects
Security and quality
Insights
Files
 main
Diagrames
Mini Street Fighter
Breadcrumbs
Vibe-Coding
/Mini Street Fighter
Latest commit
ericcanogimenez
Translate game document from Catalan to Spanish
2e16601
 · 
History
History
File metadata and controls
Code
Blame
Raw
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
**1. Título provisional del juego


Mini Street Fighter


**2. Tipo de microvideojuego


Juego de lucha 1 vs 1 simplificado (arcade 2D).


**3. Objetivo del juego


Derrotar al enemigo reduciendo su vida a 0 antes de que él haga lo mismo contigo.


**4. Rol del jugador


El jugador controla a un luchador en 2D.


**Acciones:


Moverse a izquierda y derecha
Atacar (golpe básico)
Bloquear (opcional, si hay tiempo)


**5. Reglas básicas
Cada personaje tiene una barra de vida.
Los ataques solo hacen daño si el jugador está lo suficientemente cerca.
El enemigo se mueve automáticamente hacia el jugador.
El enemigo ataca de forma simple (cada cierto tiempo).


**6. Condiciones de victoria y derrota


Victoria:
La vida del enemigo llega a 0.


Derrota:
La vida del jugador llega a 0.


**7. Bucle principal del juego
Leer input del jugador
Mover jugador
Mover enemigo hacia el jugador
Gestionar ataques (jugador y enemigo)
Detectar colisiones de ataque
Actualizar vida
Comprobar victoria o derrota
Repetir


**8. Reto principal y dificultad


Reto:
Atacar en el momento adecuado y mantener la distancia.


Dificultad:


Baja al inicio
Media si el enemigo aumenta la frecuencia de ataque


**9. Limitaciones explícitas


Este juego no incluirá:


Combos
Animaciones complejas
Múltiples personajes
Escenarios diferentes
Multijugador
Sonido avanzado
Física realista


**10. Riesgos técnicos
Detección de colisiones de ataque (hitbox mal ajustada)
IA enemiga demasiado simple o incorrecta
Control del timing de los ataques


**11. Exploración con IA


Prompt 1:
"Cómo hacer un juego de pelea simple en JavaScript sin librerías"


Respuesta resumida:


Uso de canvas
Representación de personajes como rectángulos
Detección de colisiones básicas
Control de movimiento con teclado


Prompt 2:
"Ejemplo de lógica de ataque y vida en un juego 2D"


Respuesta resumida:


Variables de vida
Cooldown de ataque
Sistema de daño por colisión


**12. Propuesta final elegida


Mini juego de lucha 1 vs 1 con gráficos simples (rectángulos) en JavaScript usando Canvas.


**13. Justificación de viabilidad
No requiere animaciones complejas
Mecánicas muy reducidas
IA sencilla
Se puede desarrollar con HTML y JavaScript sin motor
Apto para completarse en menos de 10 horas


**14. Mini plan de trabajo


Fase 1 (1h):
Configuración de HTML y Canvas


Fase 2 (3h):


Movimiento del jugador
Movimiento del enemigo


Fase 3 (3h):


Sistema de ataque
Sistema de vida


Fase 4 (2h):


Colisiones
Condiciones de victoria/derrota


Fase 5 (1h):
Ajustes finales y balance de dificultad


**15. Herramientas previstas y justificación


JavaScript + HTML Canvas:
Permite desarrollar el juego directamente en el navegador.


VS Code:
Editor ligero y eficiente.


Navegador web:
Permite probar el juego de forma inmediata.


IA (ChatGPT):
Apoyo en generación de código y resolución de errores.
While the code is focused, press Alt+F1 for a menu of operations.