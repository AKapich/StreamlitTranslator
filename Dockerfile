FROM nvidia/cuda:12.0.0-base-ubuntu22.04

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y libgl1 wget sshfs libarchive13 && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda

COPY environment/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

COPY environment/env.yaml environment/install_env.sh /tmp/
RUN bash /tmp/install_env.sh

COPY environment/requirements.txt environment/install_pip.sh /tmp/
RUN bash /tmp/install_pip.sh

WORKDIR /repo

COPY mainapp.py /repo/mainapp.py

VOLUME /database