#!/bin/bash
curl \
  -X POST \
  --header "Content-Type: application/json" \
  --data '{"connection_1":1, "connection_2":2, "connection_3":3, "connection_4": 4, "current_limit": 1e-5, "name": "kalle anka"}' \
  localhost/api/measurement
