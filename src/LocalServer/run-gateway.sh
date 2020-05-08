#!/bin/bash

python ./gateway.py \
  --registry_id=gateway-sdk-registry \
  --gateway_id=sdk-gateway \
  --cloud_region=us-central1 \
  --private_key_file=rsa_private.pem \
  --algorithm=RS256 \
  --ca_certs=roots.pem \
  --mqtt_bridge_hostname=mqtt.googleapis.com \
  --mqtt_bridge_port=8883 \
  --jwt_expires_minutes=1200