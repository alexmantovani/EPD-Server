#!/bin/bash

# Script per scrivere un messaggio sul display EPD
# Uso: ./write_display.sh [template] [titolo] [messaggio]

SERVER_URL="http://127.0.0.1:5000"

# Valori di default
TEMPLATE="${1:-warning}"
TITLE="${2:-Avviso}"
MESSAGE="${3:-Messaggio di test}"

# Template disponibili: warning, info, success, alert, status, simple

# Costruisci il JSON payload in base al template
case $TEMPLATE in
    "warning"|"info"|"success"|"alert")
        PAYLOAD=$(cat <<EOF
{
  "template": "$TEMPLATE",
  "title": "$TITLE",
  "message": "$MESSAGE"
}
EOF
)
        ;;
    "simple")
        PAYLOAD=$(cat <<EOF
{
  "template": "simple",
  "text": "$MESSAGE"
}
EOF
)
        ;;
    "status")
        PAYLOAD=$(cat <<EOF
{
  "template": "status",
  "system_name": "$TITLE",
  "status": "$MESSAGE",
  "field1_label": "Campo 1",
  "field1_value": "Valore 1",
  "field2_label": "Campo 2",
  "field2_value": "Valore 2"
}
EOF
)
        ;;
    *)
        echo "Template non valido: $TEMPLATE"
        echo "Template disponibili: warning, info, success, alert, status, simple"
        exit 1
        ;;
esac

# Invia la richiesta al server
echo "Invio messaggio al display..."
echo "Template: $TEMPLATE"
echo "Titolo: $TITLE"
echo "Messaggio: $MESSAGE"
echo ""

RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$SERVER_URL/update")

# Mostra la risposta
echo "Risposta del server:"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Verifica il risultato
if echo "$RESPONSE" | grep -q '"status": "OK"'; then
    echo ""
    echo "✓ Messaggio inviato con successo!"
    exit 0
else
    echo ""
    echo "✗ Errore nell'invio del messaggio"
    exit 1
fi
