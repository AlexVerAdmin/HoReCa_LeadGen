#!/bin/bash
cd /home/alex/Documents/ICH/Projects/LeadGen
source venv/bin/activate

# Ensure ports are clean
fuser -k 8000/tcp 8001/tcp 2>/dev/null || true
sleep 1

echo "Starting mock HoReCa API server..."
uvicorn tests.mock_horeca_api:app --port 8001 --log-level warning &
MOCK_PID=$!

echo "Starting main API server..."
uvicorn app:app --port 8000 --log-level warning &
APP_PID=$!

echo "Waiting for servers to start..."
sleep 5

echo "Logging in..."
TOKEN_RESP=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}')
echo "LOGIN RESPONSE: $TOKEN_RESP"
TOKEN=$(echo $TOKEN_RESP | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token','ERROR'))")
echo "TOKEN: $TOKEN"

if [ "$TOKEN" == "ERROR" ] || [ -z "$TOKEN" ]; then
  echo "Failed to get token"
else
  echo "Getting leads..."
  LEAD_RESP=$(curl -s http://localhost:8000/api/leads/ \
    -H "Authorization: Bearer $TOKEN")
  echo "LEADS: $LEAD_RESP"
  LEAD_ID=$(echo $LEAD_RESP | python3 -c "import sys,json; leads=json.load(sys.stdin); print(leads[0]['id'] if (isinstance(leads, list) and len(leads) > 0) else 'NO_LEADS')" 2>/dev/null)
  echo "LEAD_ID: $LEAD_ID"

  if [[ "$LEAD_ID" =~ ^[0-9]+$ ]]; then
    echo "Creating proposal..."
    PROP_RESP=$(curl -s -X POST http://localhost:8000/api/proposals/ \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"lead_id\": $LEAD_ID, \"language\": \"ru\"}")
    echo "PROPOSAL RESPONSE: $PROP_RESP"
    PROP_ID=$(echo $PROP_RESP | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id','ERROR'))" 2>/dev/null)
    echo "PROPOSAL_ID: $PROP_ID"

    if [[ "$PROP_ID" =~ ^[0-9]+$ ]]; then
      echo "Downloading PDF..."
      HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        http://localhost:8000/api/proposals/$PROP_ID/pdf \
        -H "Authorization: Bearer $TOKEN")
      echo "PDF download HTTP code: $HTTP_CODE"
    else
      echo "Failed to create proposal or invalid PROP_ID"
    fi
  else
    echo "No leads available - skipping proposal creation"
  fi
fi

echo "Cleaning up..."
kill $MOCK_PID $APP_PID 2>/dev/null || true
