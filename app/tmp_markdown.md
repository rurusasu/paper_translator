

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
large language models (LLMs) pose a significant hurdle to deployment due to the substantial storage and the huge amount of computation required. This challenge is particularly pronounced in environments with limited resources such as edge computing devices and personal devices where the constraints can inhibit the widespread adoption of these cutting-edge language models. To address this issue, several model compression strategies have been proposed, including pruning (Ma et al., 2023;Frantar & Alistarh, 2023), distillation (Zhang et al. 2023) and low-rank decomposition (Yao et al,. 2023). Each of these approaches has its own limitations and are closely tied to specific hardware architectures

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
the past few years have witnessed the booming of pre-trained language models (LLMs) in the field of natural language processing and are being used in a wide range of applications. LLMs have billions of parameters and are often pre- trained on large amounts of text data, which require significant computational resources to train and deploy.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
日本語で出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
quantization of large language models (LLMs) presents unique challenges due to the presence of many outliers in the activation values of large models (Dettmers et al., 2022). LLM.int8() splits the input activation values into two parts: non-outlier dimensions computed with INT8, and outliers computed with FP16. In light of these problems, we are driven to achieve W4A8 quantization without relying on QAT or distillation methods, paving the way for efficient deployment of LLMs.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
日本語で出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
the method shall be made low-cost and generalizable for most up-to-date LLMs.  decoding enjoys the speed-up using 8-bit matrix multiplication, while self-decoding is also accelerated via reduced memory access using 4-bit weight.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
1. 方法は、最新のLLMのほとんどに適用できるように低コストであり、一般化可能であるべきである。
2. 復号は、8ビットの行列乗算を使用して速度を向上させることができ、自己復号は、4ビットの重みを使用してメモリアクセスを削減することによっても加速される。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
With our goal in mind, we are driven to design a robust PTQ method. To begin with, we study why vanilla W4A8 quantization is difficult for current LLMs. We first draw the activation distribution of LLaMA-7B in Figure 3 to find the distinct behaviors of different layers. For instance, o proj has compact distribution while down proj spans extensively. This phenomenon reoccurs in many other LLMs, see Appendix A.3.  As we can see from the above analysis, the maximum fluctuation range of input activation values for certain layers ranges from tens to thousands. Using per-tensor static quantization will result in significant quantization errors, but using per-token dynamic quantization for all layers will not bring adequate hardware acceleration. Therefore, it naturally calls for a layer-specific policy to determine the granularity of quantization.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
- 目標を持って、我々は強固なPTQメソッドを設計することに焦点を当てている。
- まず、我々は、現在のLLMにおけるバニラW4A8の精度が困難である理由を研究する。
- まず、LLaMA-7Bの活性分布を図3に示す。
- 例えば、o projはコンパクトな分布を持ち、down projは広範囲にわたる。
- この現象は、他の多くのLLMでも再現される。
- アペンディックスA.3を参照してください。
- 図3から、入力活性値の最大変動範囲は、特定のレイヤーの活性値の範囲にわたって数千に及ぶことがわかる。
- 単一のテンソルの静的な量子化は、大きな量子化エラーを引き起こす可能性があるが、すべてのレイヤーに対して動的な量子化を使用すると、十分なハードウェアアクセラレーションが得られない。
- したがって、レイヤーごとのポリシーを決定することが重要である。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
Motivated by the above analysis, we propose our post-training quantization method which employs a layerwise quantization strategy regarding disparate activation distributions. Our complete procedure is given in Algorithm 1. The key components are discussed in detail.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
1. 本研究の概要
2. 異なる活性化の分布に対する層ごとの量子化戦略
3. 完全な手順
4. キーコンポーネント
5. 詳細
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
- 活性化量子化の困難さの解決の鍵は、外れ値処理にある。
- 活性値の範囲によって異なる量子化戦略を使用できる。ペルテンソル動的量子化は硬件の高速化効果をわずかに犠牲にして、活性範囲が数百の層に必要であるとされる。
- 小数点数の平均化によって離散化友好的な活性化分布を作るための、新しいオフライン対数活性化平準化（LAE）メソッドが提案されている。

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
- 活性化量子化の困難さの解決の鍵は、外れ値処理にある。
- 活性値の範囲によって異なる量子化戦略を使用できる。ペルテンソル動的量子化は硬件の高速化効果をわずかに犠牲にして、活性範囲が数百の層に必要であるとされる。
- 小数点数の平均化によって離散化友好的な活性化分布を作るための、新しいオフライン対数活性化平準化（LAE）メソッドが提案されている。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
 is based on a per-channel quantization scheme with a groupwise weight quantization for all layers to obtain better performance. Logarithmic activation equalization is performed offline (the scale for activation is then fused into LayerNorm) for QKV and Up/Gate. It's also worth noting that the quantized KV cache is applied to save I/O costs.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
 (Frantar et al., 2022) and SmoothQuant (Xiao et al. 2023b) as the most prevalent W8A8 and W4A16 quantization schemes, respectively. To further demonstrate the potential of FPTQ method, we compare it with the QAT method, particularly with LLM-QAT (Liu & Patel, 2003) and compare its cost to that of QAT.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
日本語で出力してください。

- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
Implementation. We find that for the investigated LLMs in our paper, the activation bound v 0 can be typically set as 15 and v 1 150.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
fine-grained post-training quantization (FPTQ) achieved W4A8 quantized models that demonstrated precision strikingly similar to their floating-point counterparts on both the BLOOM-7B1 and all models in the LLaMA series (Touvron et al., 2023) on the LAMBADA dataset. On the MMLU dataset, our approach exhibits a performance gap within 1% for most models compared to SmoothQuant. Notable outliers include LLaMa-7b and LLama-13b, which show a more pronounced drop in precision compared to LLM-QAT.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
Fine-grained post-training quantization (FPTQ) achieved W4A8 quantized models that demonstrated precision strikingly similar to their floating-point counterparts on both the BLOOM-7B1 and all models in the LLaMA series (Touvron et al., 2023) on the LAMBADA dataset. On the MMLU dataset, our approach exhibits a performance gap within 1% for most models compared to SmoothQuant. Notable outliers include LLaMa-7b and LLama-13b, which show a more pronounced drop in precision compared to LLM-QAT.<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
we conducted ablation studies on BLOOM-7B1 and LLaMA-2-7b under W8A8 and W4A8 bit-width settings in Table 6. It was found that using a random dataset often resulted in superior results in most cases. This attests that our method is applicable in data-free situations.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
We observe that the GPTQ method, which compensates weights based on the Hessian matrix, is orthogonal to our existing approach. Therefore, we attempted to fine-tune the weights using the GPTQ method after conducting logarithmic activation equalization (LAE) on the model, to investigate the potential for increased precision. However, our experiments in Table 7 demonstrated that the addition of GPTQ operations generally resulted in a negative impact on precision in most cases. We encourage future researchers to conduct more intriguing explorations in this area.  W16A16 33.60 31.10 38.20 38.40 35.20 69.85 79.16 76.21 72.81 74.51 FPTQ W4A8 30.20 29.95 32.76 35.87 32.02 70.01 78.40 74.46 70.79 73.42 FPTQGPTQ W4A8 28.40 28.33 30.84 33.22 30.03 68.82 78.13 72.88 66.96  

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
we design an INT8INT4 kernel that uses INT8 Tensor Cores for acceleration in context decoding and self-decoding stages while keeping the weights loaded as INT4 to reduce memory access time in the self- decoding stage. For activation quantization, our method completely removes weights for the computation of s i which echoes the findings in Lin et al. (2023) and is promising to randomly draw samples from the token vocabulary as in Table 6.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
1. 日本語で出力してください。
2. 箇条書きの文章ごとに翻訳してください。
3. 1つの項目ごとに100文字以内で翻訳してください。
4. 箇条書きで出力してください。
<|endoftext|>

### 指示 ###
対象とする文章を制約に基づいて翻訳してください。

### 対象とする文章 ###
we introduce a novel posttraining quantization approach that can make the inference of Large Language Model (LLM) inference more efficient without compromising their performance. We successfully achieved high performance and efficiency for W4A8 which has the optimal utilization of computational resources which enhances the speed of both content-decoding and self-decoded stages.

### 文章の制約 ###
- 日本語で出力してください。
- 箇条書きの文章ごとに翻訳してください。
- 1つの項目ごとに100文字以内で翻訳してください。
- 箇条書きで出力してください。

### 出力 ###
1.新しいポストトレーニング量子化アプローチを導入し、LLMの推定をより効率的にすることができる。
2.W4A8のパフォーマンスと効率性を向上させるために、コンテンツのデコードと自己デコードの両方のステージで計算リソースの最適な利用を実現することができた。
3.W4A8は、コンテンツのデコードと自己デコードの両方のステージで、計算リソースの最適な利用を実現することができた。
4.W4A8は、コンテンツのデコードと自己デコードの両方のステージで、計算リソースの最適な利用を実現することができた。
5.W4A8は、コンテンツのデコードと自己デコードの両方のステージで、計算リソースの最適な利用を実現することができた。
6.W4A8は、コンテンツのデコードと自己デコードの両方のステージで、計算リソースの最適な利用を実現することができた。
7.W4A8は、コンテンツのデコードと自己デコードの両方のステージで、計算リソースの最適な利用を実現することができた。
8.W4A8は、コンテンツのデコードと自己デコードの両方のステージで、計算リソースの最適な利用を実現することができた。
9.W4A8は、コンテンツのデコードと自己デコードの�