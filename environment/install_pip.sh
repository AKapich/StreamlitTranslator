#!/bin/bash

. /opt/conda/etc/profile.d/conda.sh
conda activate ${VIRTUAL_ENV}
echo "Installing pip packages"
pip install --no-cache-dir -r /tmp/requirements.txt