from llama_index.llms import LlamaCPP


def LlamaCppWrapper(
    model_url: str | None = None,
    model_path: str | None = None,
):
    # GPU を使用する場合の設定
    n_gpu_layers = 40
    n_batch = 16
    n_ctx = 4096

    # LlamaCPP の設定
    if isinstance(model_url, str):
        model_url_or_path = model_url
    elif isinstance(model_path, str):
        model_url_or_path = model_path

    model = LlamaCPP(
        model_url=model_url_or_path,
        model_path=model_url_or_path,
        temperature=0.1,
        max_new_tokens=2048,
        context_window=3900,
        model_kwargs={
            "n_gpu_layers=": n_gpu_layers,
            "n_batch=": n_batch,
            "n_ctx=": n_ctx,
        },
        verbose=True,
    )
    return model
