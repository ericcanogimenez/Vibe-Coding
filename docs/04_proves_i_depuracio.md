# 04. Proves i Depuració

## Pla de Proves
S'han realitzat proves unitàries i d'integració sobre els components crítics del joc.

### Proves de Moviment
- **Salt**: Verificació que el personatge no pot fer salts infinits a l'aire.
- **Límits de pantalla**: Comprovació que els lluitadors no surten dels marges del món.

### Proves de Combat
- **Detecció de col·lisions**: Verificació que el dany només s'aplica quan el rectangle d'atac interseca amb el cos de l'oponent.
- **Cooldowns**: Comprovació que no es poden fer atacs ràpids infinits (spam).

## Errors Identificats i Solucionats

| Error | Causa | Solució |
|-------|-------|---------|
| El personatge "tremolava" al terra | Error en el càlcul de la gravetat | S'ha afegit una tolerància de 1 píxel al terra |
| Els projectils no desapareixien | No s'eliminaven de la llista al sortir de pantalla | S'ha afegit un control de límits per netejar la memòria |
| La IA era massa difícil | Probabilitat d'atac massa alta | S'ha ajustat el paràmetre `AI_ATTACK_CHANCE` al fitxer `config.py` |

## Eines de Depuració
- **Logs de consola**: Impressió dels estats de vida i col·lisions.
- **Mode Visual Debug**: Dibuix dels rectangles de col·lisió (hitboxes) durant el desenvolupament.
