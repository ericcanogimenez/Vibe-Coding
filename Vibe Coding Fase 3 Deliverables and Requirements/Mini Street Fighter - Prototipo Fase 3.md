# Mini Street Fighter - Prototipo Fase 3

Juego de lucha 1 vs 1 simplificado desarrollado en Python con Pygame.

## Requisitos

- Python 3.7+
- Pygame 2.6.1+

## Instalación

```bash
pip install pygame
```

## Ejecución

```bash
python3 mini_street_fighter.py
```

## Controles

| Acción | Tecla |
|--------|-------|
| Moverse a la izquierda | A |
| Moverse a la derecha | D |
| Saltar | W |
| Atacar | ESPACIO |
| Salir | ESC |

## Características del Prototipo

### Mecánicas Implementadas

- **Movimiento**: El jugador puede moverse a izquierda/derecha y saltar
- **Sistema de Ataque**: Ataques con cooldown y rango limitado
- **Sistema de Vida**: Ambos personajes tienen 100 puntos de vida
- **Detección de Colisiones**: Los ataques solo hacen daño si están en rango
- **IA del Enemigo**: El enemigo se mueve automáticamente hacia el jugador y ataca

### Bucle de Juego

1. Leer entrada del jugador
2. Actualizar posición del jugador y enemigo
3. Gestionar ataques (cooldown y duración)
4. Detectar colisiones de ataque
5. Actualizar vida de ambos personajes
6. Comprobar condiciones de victoria/derrota
7. Renderizar pantalla

### Estados del Juego

- **MENU**: Pantalla inicial con controles
- **PLAYING**: Juego en progreso
- **VICTORY**: El jugador ha ganado
- **GAME_OVER**: El jugador ha perdido

## Estructura del Código

- `Fighter`: Clase que representa a un luchador (jugador o enemigo)
- `Game`: Clase principal que gestiona el bucle del juego
- `GameState`: Enumeración de estados del juego

## Notas de Desarrollo

- El juego utiliza Pygame para renderización y manejo de eventos
- La física es simplificada (gravedad básica para saltos)
- La IA del enemigo es simple pero funcional
- El sistema de colisiones es básico pero efectivo para el prototipo
