# ベースイメージの指定
ARG BASE_IMAGE=nvidia/cuda:12.2.0-devel-ubuntu22.04
FROM ${BASE_IMAGE}

# ビルド時に使用する変数の定義
ARG PROJECT_NAME=paper_translator
ARG PYTHON_VERSION=3.11
ARG APPLICATION_DIRECTORY=/home/${PROJECT_NAME}
ARG RUN_POETRY_INSTALL_AT_BUILD_TIME="false"
ARG CHROME_DRIVER_VERSION=114.0.5735.90

# 日本語化
USER root
RUN apt update \
  && apt install --no-install-recommends -y \
  fonts-noto-cjk \
  fonts-noto-cjk-extra \
  && apt install locales -y \
  # ja_JP.UTF-8の行のコメントを解除
  && sed -i -E 's/# (ja_JP.UTF-8)/\1/' /etc/locale.gen \
  && locale-gen \
  && update-locale LANG=ja_JP.UTF-8 \
  && apt clean \
  && rm -r /var/lib/apt/lists/*

# 環境変数の設定
ENV DEBIAN_FRONTEND="noninteractive" \
  TZ="Asia/Tokyo" \
  LC_ALL="ja_JP.UTF-8" \
  LANG="ja_JP.UTF-8" \
  LANGUAGE="ja_JP:ja" \
  PYTHONPATH=${APPLICATION_DIRECTORY}

# パッケージインストール
RUN apt update && apt install --no-install-recommends -y \
  sudo \
  wget \
  curl \
  gnupg \
  software-properties-common \
  git \
  make \
  ssh \
  openssh-client \
  python${PYTHON_VERSION} \
  python-is-python3 \
  && apt clean \
  && rm -r /var/lib/apt/lists/*

# Grobidのインストール
# 追加パッケージインストール
RUN apt update && apt install --no-install-recommends -y \
  unzip \
  default-jre \
  default-jdk \
  && apt clean \
  && rm -r /var/lib/apt/lists/*
RUN wget -q https://github.com/kermitt2/grobid/archive/0.7.3.zip -O /tmp/grobid\
  && cd /tmp/ \
  && unzip grobid -d /usr/lib/ \
  && cd /usr/lib/grobid-0.7.3/ \
  && ./gradlew clean install

# Pythonの設定
RUN add-apt-repository ppa:deadsnakes/ppa \
  && apt update -y \
  && apt upgrade -y \
  && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 \
  && update-alternatives --set python3 /usr/bin/python${PYTHON_VERSION} \
  && curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
  && python3 get-pip.py \
  && rm get-pip.py \
  && python3 -m pip install --upgrade pip setuptools requests \
  && python3 -m pip install poetry \
  && poetry config virtualenvs.in-project true

# ユーザーの追加
#RUN groupadd -g ${GID} ${GROUP_NAME} \
#  && useradd -ms /bin/sh -u ${UID} -g ${GID} ${USER_NAME}
#USER ${USER_NAME}
#WORKDIR ${APPLICATION_DIRECTORY}

# Poetryのインストール
#COPY --chown=${UID}:${GID} pyproject.toml poetry.lock poetry.toml .
#RUN test ${RUN_POETRY_INSTALL_AT_BUILD_TIME} = "true" && poetry install || echo "skip to run poetry install."
#RUN test ${RUN_POETRY_INSTALL_AT_BUILD_TIME} = "true" && mv ${APPLICATION_DIRECTORY}/.venv ${HOME}/.venv || echo "skip to move .venv."
