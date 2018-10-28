#!/bin/bash

gzip -k -S ".$(date +%Y%m%d_%H%M).gz" "${1}"
