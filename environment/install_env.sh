#!/bin/bash

. /opt/conda/etc/profile.d/conda.sh
conda activate base
. /opt/conda/etc/profile.d/mamba.sh

echo "Installing environment"
mamba env create --name prod -v -f /tmp/env.yaml
echo "Cleaning conda cache"
conda clean -afy
echo "Done installing env"