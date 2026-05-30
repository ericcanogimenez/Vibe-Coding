# 02. Model del Joc

## Disseny Mecànic
El joc es basa en un duel 1vs1 on l'objectiu és reduir la vida de l'oponent a zero. 

### Personatges i Atributs
Cada personatge (Lluitador) es defineix per:
- **HP (Health Points)**: La resistència del personatge.
- **Velocitat**: La rapidesa de desplaçament horitzontal.
- **Potència de Salt**: L'alçada màxima que pot assolir.
- **Dany**: Diferents valors per a cops de puny, puntades i atacs especials.

### Sistema de Control
- **Moviment**: Tecles `A` i `D`.
- **Salt**: Tecla `W`.
- **Atac**: Tecla `Espai`.
- **Especial**: Tecla `S` (en combinació amb atac).

## Lògica de l'Oponent (IA)
L'enemic utilitza una màquina d'estats simple:
1. **Persecució**: Si el jugador està lluny, s'apropa.
2. **Atac**: Si el jugador està en rang, executa un atac amb una probabilitat aleatòria per simular error humà.
3. **Reacció**: Capacitat de saltar o retrocedir davant de projectils.

## Flux de Joc
1. **Menú Principal**: Selecció de mode i personatge.
2. **Combat**: Bucle principal d'actualització i renderització (60 FPS).
3. **Resultat**: Pantalla de victòria o derrota amb opció de reiniciar.
