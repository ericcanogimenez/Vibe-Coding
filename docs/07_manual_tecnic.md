# 07. Manual Tècnic

## Arquitectura del Sistema
El projecte està estructurat seguint un patró de disseny modular.

### Fitxers Principals
- **`src/mini_street_fighter.py`**: Conté la classe `Game` (controlador) i `Fighter` (entitat). Implementa el bucle principal (`while True`).
- **`src/config.py`**: Centralitza totes les constants, colors i configuracions de balanceig.

## Classes i Mètodes Clau

### Classe `Fighter`
Gestiona l'estat d'un lluitador.
- `update()`: Calcula la física, gravetat i estats d'animació.
- `attack()`: Gestiona els rectangles de col·lisió d'atac (hitboxes).
- `take_damage()`: Aplica la reducció d'HP i l'efecte de retrocés (knockback).

### Classe `Game`
Gestiona el flux global.
- `handle_events()`: Captura l'entrada de l'usuari i esdeveniments de sistema.
- `draw()`: Renderitza totes les entitats i la interfície d'usuari.

## Requisits Tècnics
- **Resolució**: 1200x650 píxels.
- **FPS**: 60 (fixats mitjançant `pygame.time.Clock()`).
- **Sistema de Col·lisions**: Basat en l'API `pygame.Rect.colliderect()`.

## Instal·lació de Dependències
```bash
pip install pygame numpy
```
*Nota: `numpy` s'utilitza per a la generació de sons sintètics en temps real.*
