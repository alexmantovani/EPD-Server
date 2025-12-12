#!/bin/bash

# Script per leggere lo stato corrente del display EPD
# Uso: ./read_display.sh

SERVER_URL="http://127.0.0.1:5000"

echo "Lettura stato del display..."
echo ""

# Ottieni lo stato del display
RESPONSE=$(curl -s -X GET "$SERVER_URL/status")

# Verifica se la richiesta è andata a buon fine
if [ $? -ne 0 ]; then
    echo "✗ Errore nella connessione al server"
    exit 1
fi

# Mostra la risposta formattata
echo "Stato del display:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Estrai e mostra informazioni chiave
echo ""
echo "═══════════════════════════════════════"

TEMPLATE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('template', 'N/A'))" 2>/dev/null)
STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('status', 'N/A'))" 2>/dev/null)
LAST_UPDATE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('last_update', 'N/A'))" 2>/dev/null)
QUEUE_SIZE=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('queue_size', 'N/A'))" 2>/dev/null)

echo "Template attivo: $TEMPLATE"
echo "Stato: $STATUS"
echo "Ultimo aggiornamento: $LAST_UPDATE"
echo "Richieste in coda: $QUEUE_SIZE"
echo "═══════════════════════════════════════"
