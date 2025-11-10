## Development Environment

Install uv with following command:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

Install dependencies for cpu

```shell
uv sync --extra cpu
```

Install dependencies for cuda

```shell
uv sync --extra cuda
```

!!! Note
    By default, this will install the CPU version of PyTorch. For GPU support, use the `cuda` extra which will install the appropriate CUDA version of PyTorch.

### Run

Starting the Webservice:

```shell
uv run whisper-asr-webservice --host 0.0.0.0 --port 9000
```

### Build

=== ":octicons-file-code-16: `Docker`"

    With `Dockerfile`:

    === ":octicons-file-code-16: `CPU`"
    
        ```shell
        # Build Image
        docker build -t whisper-asr-webservice .
        
        # Run Container
        docker run -d -p 9000:9000 whisper-asr-webservice
        # or with specific model
        docker run -d -p 9000:9000 -e ASR_MODEL=base whisper-asr-webservice
        ```
    
    === ":octicons-file-code-16: `GPU`"
    
        ```shell
        # Build Image
        docker build -f Dockerfile.gpu -t whisper-asr-webservice-gpu .
        
        # Run Container
        docker run -d --gpus all -p 9000:9000 whisper-asr-webservice-gpu
        # or with specific model
        docker run -d --gpus all -p 9000:9000 -e ASR_MODEL=base whisper-asr-webservice-gpu
        ```

    With `docker-compose`:
    
    === ":octicons-file-code-16: `CPU`"
    
        ```shell
        docker-compose up --build
        ```
    
    === ":octicons-file-code-16: `GPU`"
    
        ```shell
        docker-compose -f docker-compose.gpu.yml up --build
        ```
=== ":octicons-file-code-16: `uv`"

    Build .whl package
    
    ```shell
    uv build
    ```