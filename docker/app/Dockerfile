# ベースイメージの指定
ARG BASE_IMAGE=nvidia/cuda:12.2.0-devel-ubuntu22.04
FROM ${BASE_IMAGE}

# 変数の設定
ARG PROJECT_NAME=paper_translator
ARG PYTHON_VERSION=3.11
ARG APPLICATION_DIRECTORY=/home/${PROJECT_NAME}
ARG RUN_POETRY_INSTALL_AT_BUILD_TIME="true"

# 日本語化
USER root
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        fonts-noto-cjk \
        fonts-noto-cjk-extra && \
    apt-get install locales -y && \
    # ja_JP.UTF-8の行のコメントを解除
    sed -i -E 's/# (ja_JP.UTF-8)/\1/' /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8 && \
    apt-get clean && \
    rm -r /var/lib/apt/lists/*

# 環境変数の設定
ENV DEBIAN_FRONTEND="noninteractive" \
    TZ="Asia/Tokyo" \
    LC_ALL="ja_JP.UTF-8" \
    LANG="ja_JP.UTF-8" \
    LANGUAGE="ja_JP:ja" \
    PYTHONPATH=${APPLICATION_DIRECTORY}

# パッケージインストール
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        sudo \
        wget \
        curl \
        gnupg

# Python の設定
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        git \
        make \
        ssh \
        openssh-client \
        software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install --no-install-recommends -y \
        python${PYTHON_VERSION} \
        python-is-python3 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --set python3 /usr/bin/python${PYTHON_VERSION} && \

# pip install
# https://www.bioerrorlog.work/entry/install-pip-pip3-ubuntu
    curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" && \
    python3 get-pip.py && \
    rm get-pip.py && \

# Poetry install
# Poetry が作成する仮想環境のディレクトリをプロジェクト直下に変更
# Ref: [Poetry documentation (ver. 1.1.6 日本語訳)]
# (https://cocoatomo.github.io/poetry-ja/configuration/)
    python3 -m pip install --upgrade pip setuptools requests && \
    python3 -m pip install poetry && \
    poetry config virtualenvs.in-project true

# 追加パッケージインストール
## Grobidのインストール
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        unzip \
        default-jre \
        default-jdk && \
    wget -q https://github.com/kermitt2/grobid/archive/0.7.3.zip -O /tmp/grobid && \
    cd /tmp/ && \
    unzip grobid -d /usr/lib/ && \
    cd /usr/lib/grobid-0.7.3/ && \
    ./gradlew clean install

# 不要なパッケージの削除
RUN apt-get autoremove -y && \
    apt-get clean && \
    rm -r /var/lib/apt/lists/*

# Poetryのテスト
#COPY ../../src/pyproject.toml poetry.lock poetry.toml . 
RUN test ${RUN_POETRY_INSTALL_AT_BUILD_TIME} = "true" && poetry install || echo "skip to run poetry install."
RUN test ${RUN_POETRY_INSTALL_AT_BUILD_TIME} = "true" && mv ${APPLICATION_DIRECTORY}/.venv ${HOME}/.venv || echo "skip to move .venv."