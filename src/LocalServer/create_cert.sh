#!/bin/bash

openssl req -x509 -newkey rsa:2048 \
  -nodes -keyout rsa_private.pem -x509 -days 365 -out rsa_cert.pem -subj "/CN=unused"