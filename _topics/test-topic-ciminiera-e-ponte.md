---
layout: topic
title: "Test Topic: Ciminiera e Ponte"
date: 2026-02-25
featured_photos:
  - id: piazzacarmine_con_ciminiera
    commentary: "Veduta della piazza con la ciminiera; utile per testare il collegamento col dataset foto."
  - id: viaCarmine-ponte_torano_verso_piazza_carmine_1900
    commentary: "Percorso storico verso Piazza Carmine; verifica rendering e link al dettaglio."
  - id: Via_Carmine_Cotonificio
    commentary : "Vista su Via Carmine e ruderi Cotonificio, ex Convento"
  - id: ciminiera_cotonificio_dalla_pretura
    commentary : "ciminiera cotonificio dalla pretura"
map:
  map_height: 500px
  center_lat: 41.3550422
  center_lng: 14.3721446
  zoom: 19
  activelayers: ["esri","1940","foto","foto_fov","foto_line"]

---

Questo e un topic di prova per verificare che la collezione `topics` mostri correttamente i collegamenti alle foto.

## Obiettivi di test

- Verificare che il topic appaia nella sidebar sotto "Topics".
- Verificare che i due elementi in `featured_photos` siano leggibili dal template.
- Usare questo contenuto come base per la futura `topic.html`.
