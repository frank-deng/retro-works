#!/bin/sh

gzip -kfS ".$(date '+%Y%m%d_%H%M').gz" "${1}"
