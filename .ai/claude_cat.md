# Action Items tecnici — Cotonificio Egg / Piedimonte Matese

**Documento di lavoro per Mistral Code e altri LLM**

## Obiettivo generale

Evolvere il progetto esistente [piedimonte-matese-old-photos](https://github.com/kidpixo/piedimonte-matese-old-photos/) mantenendo il sito statico funzionante e introducendo gradualmente:

- un modello dati storico-geografico coerente;
- contenuti multilingue senza duplicazione dei metadati;
- eventi storici e narrazioni temporali;
- distribuzione geospaziale cloud-native con COG e PMTiles;
- API generiche per interrogare e, in futuro, modificare dati e metadati;
- un'applicazione editoriale con revisione, provenienza e gestione delle modifiche.

Il progetto esistente utilizza Python, Jekyll, dati curati in `raw_data/`, collezioni di contenuti e JavaScript personalizzato per le mappe. Prima di modificare queste componenti, Mistral Code deve verificare la struttura e il comportamento reali del repository.

---

# Fase 0 — Audit, documentazione e sicurezza delle modifiche

## AI-001 — Analizzare il repository esistente

**Problema**

Le nuove funzionalità potrebbero duplicare logiche già presenti o rompere il workflow attuale. Le informazioni architetturali disponibili non sostituiscono un audit del codice.

**Soluzione suggerita**

Esaminare:

- struttura delle directory e configurazione Jekyll;
- script Python e pipeline di generazione;
- `raw_data/`, `_topics/` e altre collezioni;
- generazione di immagini, pagine, GeoJSON e raster;
- `assets/js/myscript.js` e gestione dei base layer storici;
- sistema di coordinate, identificativi e metadati;
- modalità di pubblicazione GitHub Pages.

**Deliverable**

Un documento `docs/architecture-audit.md` con architettura attuale, dipendenze, flussi dei dati, punti critici e opportunità di riuso.

**Criteri di accettazione**

- Ogni componente individuato ha una responsabilità documentata.
- Sono identificati i punti di ingresso della pipeline.
- È possibile ricostruire il sito con il workflow esistente.
- Nessun refactoring viene effettuato prima di aver documentato il comportamento attuale.

## AI-002 — Definire una baseline e test di regressione

**Problema**

Una migrazione graduale può alterare URL, metadati, geometrie o visualizzazione delle mappe senza che il problema sia immediatamente evidente.

**Soluzione suggerita**

- Registrare il comando di build corrente.
- Aggiungere test automatici per gli script Python, dove possibile.
- Verificare URL, identificativi e numero di record generati.
- Conservare alcuni output di riferimento per confrontare le generazioni successive.
- Testare la presenza delle risorse cartografiche e dei layer storici.

**Deliverable**

Una procedura documentata di test e build, eventualmente in `docs/development.md`.

**Criteri di accettazione**

Una modifica al modello dati può essere verificata senza dipendere esclusivamente da un controllo manuale del sito.

---

# Fase 1 — Modello dati canonico

## AI-003 — Definire uno schema condiviso per le entità

**Problema**

Metadati simili possono essere duplicati in fotografie, pagine narrative, traduzioni e geometrie. Le copie possono divergere.

**Soluzione suggerita**

Definire un modello canonico per le principali risorse:

- `Entity`: edifici, persone, luoghi, organizzazioni e oggetti storici;
- `Photo`: fotografie e relativi metadati;
- `Event`: eventi storici;
- `Source`: fonti documentarie, cartografiche e bibliografiche;
- `Geometry`: geometrie geografiche e loro versioni temporali;
- `Page`: contenuti editoriali localizzati;
- `Relation`: collegamenti tipizzati fra risorse.

Utilizzare inizialmente YAML o JSON, in continuità con il repository. Non introdurre un database soltanto per normalizzare i dati.

**Deliverable**

- `docs/data-model.md`
- schemi di validazione, ad esempio JSON Schema;
- esempi di record validi e non validi.

**Criteri di accettazione**

Ogni tipo di risorsa ha un identificativo stabile, campi documentati e regole di validazione.

## AI-004 — Separare gli identificativi con significati diversi

**Problema**

L'identità di un edificio, l'identità di una pagina narrativa e la chiave che collega le sue traduzioni non sono necessariamente la stessa cosa.

**Soluzione suggerita**

Definire chiaramente:

- `id`: identificativo univoco del record;
- `entity_id`: entità storica a cui il record si riferisce;
- `translation_key`: gruppo di versioni linguistiche della stessa pagina;
- `lang`: lingua del contenuto;
- `permalink`: URL pubblico della pagina.

Non richiedere che identificativi e slug coincidano.

**Criteri di accettazione**

Una stessa entità può avere più pagine narrative, mentre ogni pagina può essere collegata alle proprie traduzioni senza ambiguità.

## AI-005 — Centralizzare fonti e provenienza

**Problema**

Un dato storico privo di provenienza non consente di distinguere facilmente una misura rilevata sul campo, una lettura cartografica, un'ipotesi e un fatto documentato.

**Soluzione suggerita**

Ogni dato significativo dovrebbe poter essere collegato a una o più fonti, quando disponibili. Registrare, secondo il tipo di informazione:

- identificativo della fonte;
- tipo di fonte e riferimento archivistico;
- data o intervallo documentato;
- metodo di acquisizione;
- precisione o incertezza;
- stato interpretativo, ad esempio documentato, stimato, ipotetico o da verificare;
- autore e data della modifica, quando noti.

Evitare di assegnare precisioni o certezze artificiali a dati storici incompleti.

**Criteri di accettazione**

Le informazioni incerte rimangono esplicitamente incerte e la provenienza è recuperabile dal record o dai suoi riferimenti.

## AI-006 — Separare i dati canonici dai dati derivati

**Problema**

JSON generati, GeoJSON, pagine HTML e file cartografici possono diventare accidentalmente fonti concorrenti.

**Soluzione suggerita**

Definire una pipeline unidirezionale:

`Dati curati → validazione → normalizzazione → prodotti derivati → pubblicazione`

I prodotti derivati comprendono pagine Jekyll, indici JSON, GeoJSON, PMTiles e, quando necessario, COG.

**Criteri di accettazione**

È documentato quali file possono essere modificati manualmente e quali devono essere rigenerati. La pipeline non sovrascrive le fonti originali.

---

# Fase 2 — Multilingua e i18n

## AI-007 — Separare i testi per lingua dai metadati condivisi

**Problema**

Memorizzare testi lunghi in array multilingue rende difficili l'editing, le revisioni e la gestione di Markdown. Duplicare tutti i metadati in ogni file tradotto introduce invece incoerenze.

**Soluzione suggerita**

Utilizzare file Markdown distinti per i contenuti editoriali, con metadati editoriali localizzati e riferimenti alle risorse canoniche.

Esempio concettuale:

```text
_topics/
  cotonificio-egg.it.md
  egg-cotton-mill.en.md
  baumwollspinnerei-egg.de.md
```

I file possono avere titoli e permalink diversi, ma condividono `translation_key` e fanno riferimento all'entità storica tramite `entity_id`.

Le coordinate, le date e le relazioni storiche comuni non devono essere ricopiate nei front matter delle traduzioni.

**Criteri di accettazione**

Modificare una coordinata o una data condivisa non richiede di modificare ogni versione linguistica.

## AI-008 — Implementare il sistema i18n dell'interfaccia

**Problema**

Le etichette dell'interfaccia rischiano di essere sparse in template, JavaScript e HTML, rendendo costose le traduzioni.

**Soluzione suggerita**

Creare dizionari di stringhe per lingua, ad esempio:

```text
data/i18n/it.yml
data/i18n/en.yml
data/i18n/de.yml
```

Utilizzarli per navigazione, filtri, pulsanti, messaggi, stati e didascalie standard dell'interfaccia.

Non utilizzare questi dizionari per contenere intere narrazioni storiche.

**Criteri di accettazione**

Aggiungere una stringa dell'interfaccia non richiede di duplicare template o codice JavaScript per ogni lingua.

## AI-009 — Validare la completezza delle traduzioni

**Problema**

Le pagine tradotte mancanti sono difficili da individuare manualmente; inoltre, i selettori linguistici possono condurre a URL inesistenti.

**Soluzione suggerita**

Aggiungere uno script Python che produca un rapporto per `translation_key` e lingua, identificando:

- traduzioni mancanti;
- chiavi duplicate;
- lingue non riconosciute;
- riferimenti a entità inesistenti;
- permalink duplicati;
- collegamenti linguistici non validi.

Prevedere un fallback esplicito quando una traduzione manca, senza presentare una pagina in una lingua come se fosse tradotta.

**Criteri di accettazione**

Il rapporto delle traduzioni viene generato durante la build e gli errori critici possono bloccare la pubblicazione.

## AI-010 — Migliorare la navigazione multilingue e SEO

**Problema**

Slug differenti e traduzioni mancanti complicano la navigazione e l'indicizzazione.

**Soluzione suggerita**

- Generare i collegamenti linguistici a partire da `translation_key`.
- Impostare correttamente l'attributo HTML `lang`.
- Generare i collegamenti `hreflang` soltanto per le traduzioni effettivamente disponibili.
- Gestire canonical, sitemap e URL localizzati.
- Stabilire una politica per le pagine non ancora tradotte.

**Criteri di accettazione**

Ogni link linguistico conduce alla traduzione corretta o mostra un fallback esplicito.

---

# Fase 3 — Eventi storici e narrazioni temporali

## AI-011 — Introdurre una collezione strutturata di eventi

**Problema**

Una narrazione storica può contenere date, luoghi, persone e fonti incorporate nel testo, difficili da riutilizzare in una timeline o in una ricerca.

**Soluzione suggerita**

Creare una collezione `_events/` o una struttura dati equivalente con campi quali:

- identificativo;
- data iniziale e finale;
- precisione della datazione;
- entità e luoghi coinvolti;
- fonti;
- stato interpretativo;
- descrizioni localizzate o riferimenti a pagine tradotte.

Le strutture definitive devono essere definite dopo l'audit e la scelta del modello canonico.

**Criteri di accettazione**

Un evento può essere interrogato indipendentemente dalla pagina narrativa in cui viene raccontato.

## AI-012 — Creare pagine narrative tematiche

**Problema**

Le pagine dedicate a edifici, persone, oggetti e processi storici devono poter riutilizzare eventi e documenti senza duplicarne i dati.

**Soluzione suggerita**

Usare `_topics/` per le narrazioni e collegare ogni pagina agli eventi, alle entità e alle fonti tramite identificativi.

Una pagina può presentare una selezione ordinata di eventi e documenti, aggiungendo testo editoriale e interpretazione.

**Criteri di accettazione**

La correzione di un evento si riflette in tutte le pagine che lo utilizzano, senza duplicare la sua scheda storica.

## AI-013 — Implementare una timeline narrativa distinta da quella cartografica

**Problema**

Gli eventi storici possono avere date irregolari, mentre le mappe disponibili possono riferirsi soltanto ad alcuni anni.

**Soluzione suggerita**

Creare un modulo JavaScript dedicato, ad esempio `assets/js/story-timeline.js`, che sincronizzi:

- tappa narrativa;
- evento storico;
- contenuti e immagini;
- geometrie pertinenti;
- base layer cartografico disponibile più appropriato.

La timeline narrativa non deve essere confusa con lo slider che cambia anno dei raster.

Quando un evento risale al 1943 e la mappa disponibile è del 1940, mostrare entrambe le date e dichiarare la discrepanza.

**Criteri di accettazione**

La navigazione narrativa funziona anche quando non esiste una mappa per ogni data degli eventi.

## AI-014 — Gestire geometrie che cambiano nel tempo

**Problema**

La geometria attuale di un edificio può non rappresentare la sua estensione storica.

**Soluzione suggerita**

Consentire versioni temporali delle geometrie, con intervalli di validità, fonti e precisione. Distinguere la validità storica dall'eventuale data di acquisizione o registrazione della geometria.

**Criteri di accettazione**

La mappa può visualizzare geometrie differenti per periodi differenti senza sovrascrivere la ricostruzione precedente.

## AI-015 — Sviluppare un prototipo storico verticale

**Problema**

Implementare un sistema generico prima di aver verificato il modello rischia di produrre un'architettura troppo complessa.

**Soluzione suggerita**

Scegliere un edificio o un elemento del cotonificio e ricostruire 3–4 eventi documentabili, con fonti, fotografie, geometrie e una pagina narrativa.

**Criteri di accettazione**

Il prototipo dimostra l'intero percorso dai dati sorgente alla pagina e alla mappa interattiva.

---

# Fase 4 — Distribuzione geospaziale cloud-native

## AI-016 — Verificare l'uso di PMTiles

**Problema**

Distribuire molti dati vettoriali tramite richieste ripetute a file GeoJSON voluminosi può diventare inefficiente.

**Soluzione suggerita**

Generare un archivio PMTiles per le geometrie adatte alla visualizzazione cartografica, ad esempio:

- punti fotografici;
- campi visivi;
- edifici e impronte;
- percorsi e altri elementi geografici.

Verificare la compatibilità con il client cartografico, lo stile, la proiezione, la generazione dei tasselli e il deployment statico.

**Criteri di accettazione**

Un prototipo carica i tasselli direttamente dallo storage HTTP compatibile, senza un tile server dedicato.

## AI-017 — Valutare COG per i raster storici

**Problema**

Mappe storiche e ortofoto possono essere grandi, e caricare l'intero raster è inefficiente quando serve soltanto una porzione.

**Soluzione suggerita**

Selezionare un raster storico e verificarne la conversione in Cloud Optimized GeoTIFF, mantenendo i dati di georeferenziazione e controllando la qualità.

Testare richieste HTTP Range, CORS, livelli overview e compatibilità con il visualizzatore.

**Criteri di accettazione**

Il raster è visualizzabile a diverse scale con accesso remoto alle porzioni necessarie. Il raster originale rimane conservato.

## AI-018 — Distinguere dati analitici e dati di visualizzazione

**Problema**

Un formato efficiente per la mappa non è necessariamente adatto a query, analisi o modifica delle geometrie.

**Soluzione suggerita**

Definire il formato in base all'utilizzo:

- GeoJSON per scambio e dataset piccoli;
- PMTiles per distribuzione vettoriale cartografica;
- COG per raster;
- GeoParquet per eventuali elaborazioni analitiche su dataset consistenti;
- JSON per record e metadati interrogabili.

**Criteri di accettazione**

Nessun artefatto cartografico diventa l'unica copia modificabile del dato.

---

# Fase 5 — API di lettura

## AI-019 — Definire il contratto API prima dell'implementazione

**Problema**

Un'API costruita direttamente dentro il sito rischia di dipendere dai template Jekyll e dal modo in cui i dati sono attualmente organizzati.

**Soluzione suggerita**

Documentare un contratto REST/JSON indipendente dal client, preferibilmente con OpenAPI.

Risorse candidate:

```text
/api/v1/entities
/api/v1/entities/{id}
/api/v1/events
/api/v1/photos
/api/v1/sources
/api/v1/search
/api/v1/changes
```

Definire filtri, paginazione, codici di errore, identificativi, formati di risposta e versionamento.

**Criteri di accettazione**

Il contratto può essere implementato con file statici o con un servizio dinamico senza modificare la semantica delle risorse.

## AI-020 — Generare inizialmente un'API statica

**Problema**

Un servizio serverless dinamico può essere prematuro se le esigenze di interrogazione non sono ancora note.

**Soluzione suggerita**

Generare durante la build indici JSON e record pubblici, per esempio:

```text
/api/v1/entities/cotonificio-egg.json
/api/v1/photos/photo-0042.json
/api/v1/events/index.json
/api/v1/search-index.json
```

I percorsi sono esempi: prima dell'implementazione verificare compatibilità con il routing e il deployment esistenti.

**Criteri di accettazione**

Il sito può interrogare i record tramite un contratto documentato senza richiedere un processo server-side sempre attivo.

## AI-021 — Implementare ricerca e filtri

**Problema**

La ricerca per testo, data e posizione può diventare lenta o richiedere il download di dataset completi.

**Soluzione suggerita**

Iniziare con indici statici e filtri lato client quando i dataset sono piccoli. Valutare API dinamiche per query spaziali, intervalli temporali, paginazione e ricerca combinata.

Considerare OGC API – Features quando offre vantaggi concreti per l'interoperabilità geografica.

**Criteri di accettazione**

La scelta fra ricerca statica e dinamica è basata su dimensioni dei dati, prestazioni e casi d'uso misurabili.

---

# Fase 6 — API di scrittura e applicazione editoriale

## AI-022 — Decidere la fonte autorevole delle modifiche

**Problema**

Mantenere Git e database come due copie modificabili dello stesso dato crea divergenze e conflitti.

**Soluzione suggerita**

Scegliere una sola fonte autorevole.

**Opzione A: Git autorevole**

Le modifiche passano da un servizio che valida i dati e crea commit o pull request. È più vicina al workflow attuale.

**Opzione B: database autorevole**

Un database contiene i record modificabili. Git conserva codice, schemi e snapshot o esportazioni versionate.

La scelta va presa prima di implementare l'API di scrittura.

**Criteri di accettazione**

È documentato dove vive la versione corrente di ogni record e come si ricostruisce la storia delle modifiche.

## AI-023 — Valutare database e infrastruttura

**Problema**

Un'applicazione editoriale necessita di query efficienti, aggiornamenti coerenti, gestione degli utenti e, potenzialmente, operazioni spaziali complesse.

**Soluzione suggerita**

Valutare PostgreSQL/PostGIS come opzione per il nucleo storico-geografico. Confrontare:

- un servizio PostgreSQL gestito;
- Supabase per database, autenticazione e API;
- Workers con un database PostgreSQL gestito e object storage.

Mantenere il sito statico su GitHub Pages se continua a soddisfare le esigenze.

**Criteri di accettazione**

La scelta include costi, backup, autenticazione, gestione delle geometrie, limiti del provider e strategia di esportazione. Nessun servizio viene adottato soltanto perché è di moda.

## AI-024 — Implementare scritture sicure

**Problema**

Un'API di scrittura esposta pubblicamente può introdurre modifiche non autorizzate o dati incoerenti.

**Soluzione suggerita**

Implementare:

- autenticazione;
- autorizzazioni per ruolo;
- validazione degli schemi;
- controlli sulle relazioni;
- protezione da aggiornamenti concorrenti;
- log delle modifiche;
- gestione sicura di upload e allegati;
- separazione tra dati pubblici e bozze.

Le operazioni di scrittura non devono essere disponibili anonimamente per impostazione predefinita.

**Criteri di accettazione**

Un utente non autorizzato non può modificare record e ogni modifica autorizzata è tracciabile.

## AI-025 — Aggiungere bozze, revisione e pubblicazione

**Problema**

Una nuova interpretazione storica non dovrebbe diventare automaticamente un fatto pubblico solo perché è stata salvata.

**Soluzione suggerita**

Definire un workflow editoriale, ad esempio:

`Bozza → In revisione → Approvato → Pubblicato`

Prevedere la possibilità di correggere o ritirare una pubblicazione mantenendo la cronologia.

**Criteri di accettazione**

La pubblicazione del sito e dei prodotti geospaziali utilizza soltanto record approvati secondo le regole del progetto.

## AI-026 — Generare gli artefatti pubblici dopo le modifiche

**Problema**

L'aggiornamento del record canonico può lasciare indietro JSON, pagine, indici e mappe derivate.

**Soluzione suggerita**

Creare una pipeline che, dopo l'approvazione, valida i dati e rigenera gli artefatti necessari. Prevedere una ricostruzione completa oltre agli eventuali aggiornamenti incrementali.

**Criteri di accettazione**

È possibile rigenerare i prodotti pubblici a partire dalla fonte autorevole senza modifiche manuali agli artefatti.

---

# Fase 7 — Qualità, manutenzione e interoperabilità

## AI-027 — Testare il contratto API e gli schemi

**Problema**

Una modifica al modello può interrompere client e strumenti che consumano i dati.

**Soluzione suggerita**

Aggiungere test automatici per schemi, riferimenti, traduzioni, filtri, permessi e formati di risposta. Mantenere la compatibilità degli endpoint versionati.

**Criteri di accettazione**

Una modifica incompatibile viene rilevata prima della pubblicazione.

## AI-028 — Documentare i dati e la loro provenienza

**Problema**

Un archivio distribuito è utile ad altri ricercatori soltanto se i campi e le fonti sono comprensibili.

**Soluzione suggerita**

Documentare dizionario dei dati, sistemi di coordinate, precisione, convenzioni temporali, fonti, licenze, formati e procedure di aggiornamento.

**Criteri di accettazione**

Un utente esterno può comprendere il significato dei dati senza leggere il codice di generazione.

## AI-029 — Monitorare prestazioni e costi

**Problema**

La distribuzione di raster, archivi vettoriali e API può generare costi o problemi di prestazione non visibili in locale.

**Soluzione suggerita**

Misurare dimensioni degli artefatti, tempi di caricamento, cache, traffico e consumo delle funzioni. Impostare limiti e avvisi prima di migrare l'intero archivio.

**Criteri di accettazione**

Le decisioni su storage, API dinamiche e generazione incrementale sono basate su misurazioni.

---

# Ordine di implementazione consigliato

1. AI-001 — Audit del repository.
2. AI-002 — Baseline e test.
3. AI-003–AI-006 — Modello canonico, identificativi, provenienza e pipeline.
4. AI-007–AI-010 — Multilingua e controlli di coerenza.
5. AI-011–AI-015 — Eventi, narrazioni e prototipo temporale.
6. AI-016–AI-018 — Prototipi PMTiles e COG.
7. AI-019–AI-021 — Contratto API e letture.
8. AI-022–AI-026 — Decisione sulla fonte autorevole, scrittura e workflow editoriale.
9. AI-027–AI-029 — Consolidamento, interoperabilità e prestazioni.

L'ordine non è assoluto: la fase geospaziale può essere prototipata in parallelo, purché non richieda una migrazione prematura del modello canonico.

---

# Istruzioni operative per Mistral Code

Per ogni Action Item:

1. Analizza il codice e i dati esistenti prima di proporre modifiche.
2. Elenca file interessati, dipendenze e possibili regressioni.
3. Proponi una modifica circoscritta e attendi conferma prima di un refactoring ampio.
4. Implementa un solo obiettivo verificabile per volta.
5. Aggiungi o aggiorna i test pertinenti.
6. Esegui la build e i controlli disponibili.
7. Riporta file modificati, decisioni, test eseguiti e problemi ancora aperti.
8. Non inventare dati storici e non sovrascrivere fonti originali.
9. Non introdurre database, framework o servizi cloud senza averne documentato la necessità.
10. Aggiorna la documentazione tecnica quando cambia il modello dati o il comportamento della pipeline.

## Primo prompt da utilizzare

> Analizza il repository `piedimonte-matese-old-photos` e aiutami a realizzare l'Action Item AI-001.
>
> In questa fase non modificare il codice. Esamina la struttura, la configurazione Jekyll, gli script Python, i dati sorgente, le collezioni, la generazione delle mappe e il JavaScript dei base layer.
>
> Distingui ciò che hai verificato direttamente da ciò che non hai potuto verificare. Produci una mappa dell'architettura attuale, descrivi il flusso dei dati dalla fonte alla pubblicazione, individua duplicazioni e rischi per le future funzionalità multilingue, temporali e geospaziali.
>
> Concludi con un documento proposto `docs/architecture-audit.md`, una lista di file da esaminare in seguito e una sequenza di interventi incrementali. Non introdurre dipendenze né proporre una riscrittura completa prima dell'audit.

---

# Decisioni architetturali ancora aperte

Queste scelte non devono essere risolte tutte al primo passaggio.

- **Fonte autorevole:** Git con commit/pull request oppure database con cronologia e snapshot esportabili.
- **Database:** necessità effettiva di PostgreSQL/PostGIS rispetto a una prima fase basata su file.
- **Hosting:** mantenere GitHub Pages e aggiungere un servizio separato oppure consolidare sito e API su un'altra piattaforma.
- **API geografica:** GeoJSON, PMTiles, COG e OGC API – Features in base alle esigenze reali.
- **Workflow editoriale:** revisione obbligatoria per ogni modifica o soltanto per le pubblicazioni.
- **Aggiornamento degli artefatti:** build completa o generazione incrementale.

La regola generale è mantenere aperte le scelte reversibili finché il prototipo non dimostra che è necessario impegnarsi in una soluzione specifica.

## Risultato finale atteso

Un archivio storico-geografico con dati coerenti, traduzioni verificabili, provenienza esplicita, narrazioni temporali e distribuzione geospaziale efficiente. Il sito statico rimane un canale di pubblicazione, mentre un'API stabile permette in futuro di aggiungere strumenti editoriali e altri client senza ricostruire il sistema da zero.
