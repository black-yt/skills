---
name: huggingface-dataset-publishing
description: "当需要创建、上传、验证和维护 Hugging Face Dataset 时使用，尤其是包含图片、多图字段、文本步骤、答案、JSON/metadata 字段的数据集；包括 datasets Features/Image/Sequence 的规范用法、push_to_hub、上传后 load_dataset 回读验证、Dataset Viewer 图片浏览检查、clone dataset repo 后用 git 维护 README/dataset card，以及 token 安全。"
---

# Hugging Face Dataset Publishing

## 核心原则

- 不要把 Hugging Face token 写进代码、notebook、README、日志或 git history；使用 `HF_TOKEN` 环境变量或 `huggingface-cli login`。
- 图片字段必须用 `datasets.Image` 特征类型，不要只上传本地图片路径字符串；多图字段用 `Sequence(Image())`。
- 上传前先本地构造 `Dataset`/`DatasetDict` 并检查 `features`、样本、图片解码和 JSON 字段。
- 上传后必须用 `load_dataset` 从 Hub 回读验证，确认图片能解码、metadata 可解析、split/config 正确。
- 上传完成后建议 `git clone https://huggingface.co/datasets/<org>/<repo>` 到本地，用 git 维护 `README.md`、dataset card、示例和后续小改动。
- 大数据或大量图片不要随手放在当前目录；明确构建目录、清理临时样本，不把 token、缓存或中间碎片提交。

如果用户贴出了明文 HF token，提醒其撤销/轮换该 token，并在后续代码中改用环境变量。

## 依赖与登录

安装依赖：

```bash
python -m pip install -U datasets huggingface_hub pillow
```

推荐登录方式：

```bash
export HF_TOKEN="hf_xxx"
huggingface-cli login --token "$HF_TOKEN"
```

Python 中只从环境变量读取：

```python
import os
from huggingface_hub import login

token = os.environ.get("HF_TOKEN")
if token:
    login(token=token)
```

## 数据结构选择

常见字段设计：

- 单图：`"image": HFImage()`
- 多图：`"images": Sequence(HFImage())`
- 文本：`Value("string")`
- 文本列表：`Sequence(Value("string"))`
- JSON metadata：优先用 `Value("string")` 存 JSON 字符串，上传前后用 `json.loads` 校验。
- 结构固定的 metadata：可用嵌套 `Features`，但如果字段经常变化，JSON string 更稳。

标准 split 名优先使用 `train`、`validation`、`test`。`DatasetDict({"subset_name": dataset})` 中的 key 会被当作 split 名；如果确实需要多个 dataset config/subset，要单独确认 `push_to_hub` 的 `config_name` 方案，不要把 split 和 subset 混用。

## 多图数据集模板

这个模板会生成本地样例图片、构造多图字段、写 JSON metadata 字符串、上传到 Hub，并避免硬编码 token。

```python
import json
import os
from pathlib import Path

from datasets import Dataset, DatasetDict, Features, Image as HFImage, Sequence, Value
from huggingface_hub import login
from PIL import Image

repo_id = os.environ["HF_DATASET_REPO"]  # e.g. "CoCoOne/Demo"
token = os.environ.get("HF_TOKEN")
if token:
    login(token=token)

work_dir = Path("hf_dataset_build")
image_dir = work_dir / "images"
image_dir.mkdir(parents=True, exist_ok=True)

for i in range(3):
    img_path = image_dir / f"sample_{i}.png"
    Image.new("RGB", (64, 64), color=(i * 50, 100, 150)).save(img_path)

rows = [
    {
        "question": "What is the effect of X on Y?",
        "images": [str(image_dir / "sample_0.png"), str(image_dir / "sample_1.png")],
        "steps": ["Step 1: Analyze data", "Step 2: Interpret results"],
        "answer": "X positively affects Y.",
        "metadata": json.dumps({"difficulty": 0.8, "domain": "biology"}, ensure_ascii=False),
    },
    {
        "question": "How does temperature influence reaction Z?",
        "images": [str(image_dir / "sample_2.png")],
        "steps": ["Step 1: Measure temperature", "Step 2: Record reaction time"],
        "answer": "Higher temperature accelerates reaction Z.",
        "metadata": json.dumps({"difficulty": 0.6, "simulator": None}, ensure_ascii=False),
    },
]

features = Features(
    {
        "question": Value("string"),
        "images": Sequence(HFImage()),
        "steps": Sequence(Value("string")),
        "answer": Value("string"),
        "metadata": Value("string"),
    }
)

dataset = Dataset.from_list(rows, features=features)
dataset_dict = DatasetDict({"train": dataset})

print(dataset_dict)
print(dataset_dict["train"].features)
print(dataset_dict["train"][0]["images"][0])
json.loads(dataset_dict["train"][0]["metadata"])

dataset_dict.push_to_hub(repo_id)
```

运行示例：

```bash
export HF_TOKEN="hf_xxx"
export HF_DATASET_REPO="CoCoOne/Demo"
python publish_dataset.py
```

## 上传前检查

上传前至少检查：

```python
assert len(dataset) > 0
assert "images" in dataset.features
assert dataset.features["images"].feature.__class__.__name__ == "Image"

sample = dataset[0]
assert sample["question"]
assert sample["images"]
assert sample["images"][0].mode in {"RGB", "RGBA", "L"}
json.loads(sample["metadata"])
```

常见问题：

- 如果 Hub 页面只显示图片路径字符串，说明没有用 `HFImage()` 或 `Sequence(HFImage())`。
- 如果多图字段无法浏览，检查 `features["images"]` 是否真的是 `Sequence(Image())`。
- 如果图片路径报错，先确认路径相对于运行脚本的工作目录存在。
- 如果 metadata 无法解析，上传前逐条 `json.loads` 校验。
- 如果 JSON 字符串太大或嵌套很多，考虑拆成多个结构化列或附加文件。

## 上传后验证

上传完成后，不要只相信 `push_to_hub` 成功。必须从 Hub 回读：

```python
import json
import os
from datasets import load_dataset

repo_id = os.environ["HF_DATASET_REPO"]
ds = load_dataset(repo_id, split="train")

print(ds)
print(ds.features)

sample = ds[0]
print(sample["question"])
print(type(sample["images"][0]), sample["images"][0].size)
json.loads(sample["metadata"])
```

还要在浏览器打开 Hugging Face Dataset Viewer，确认：

- split/config 名称正确；
- `images` 列能显示图片缩略图或可展开图片；
- 文本、steps、answer 和 metadata 显示正常；
- README/dataset card 没有泄露 token、私有路径或本地绝对路径。

## Clone 后用 Git 维护

上传完成后建议 clone 数据集仓库维护 README 和小规模元信息更新：

```bash
git lfs install
git clone "https://huggingface.co/datasets/$HF_DATASET_REPO"
cd "$(basename "$HF_DATASET_REPO")"
git status
```

维护 `README.md`，至少包含：

- dataset summary；
- fields/features；
- split/config；
- image and metadata format；
- license；
- citation；
- limitations；
- intended use；
- data construction or quality checks。

提交 README 更新：

```bash
git add README.md
git commit -m "Update dataset card"
git push
```

不要手动改 `push_to_hub` 生成的大型 parquet/shard 文件，除非明确知道后果。大规模数据更新优先重新运行构建脚本并 `push_to_hub`，README 和小文件用 git 维护。

## Dataset Card 骨架

`README.md` 建议包含 YAML metadata 和正文：

```markdown
---
license: other
task_categories:
- image-text-to-text
language:
- en
size_categories:
- n<1K
---

# Dataset Name

## Dataset Summary

[Briefly describe the task, inputs, outputs, and intended use.]

## Data Fields

- `question`: natural-language question.
- `images`: a list of images stored with the Hugging Face `Image` feature.
- `steps`: intermediate steps or procedure description.
- `answer`: target answer.
- `metadata`: JSON string with auxiliary attributes.

## Splits

| Split | Count |
| --- | ---: |
| train | [N] |

## Data Construction And Quality Checks

[Describe image validation, JSON validation, deduplication, and manual/model checks.]

## Limitations

[Known limitations and appropriate use.]
```

## 更新工作流

小改 README：

```bash
cd /path/to/cloned-dataset-repo
git pull
# edit README.md
git add README.md
git commit -m "Update dataset card"
git push
```

更新数据：

1. 在构建脚本中修改数据源或 features。
2. 本地运行上传前检查。
3. `push_to_hub(repo_id)` 上传。
4. `load_dataset(repo_id, split=...)` 回读验证。
5. 打开 Dataset Viewer 检查图片显示。
6. clone 仓库或进入已有 clone，更新 README/changelog 描述。

## 安全检查

发布前检查：

```bash
grep -RIn "hf_[A-Za-z0-9]" . --exclude-dir=.git
git status --short
```

确认：

- 没有硬编码 token；
- 没有上传本地绝对路径、私有用户名、内部路径或代理凭据；
- 图片是需要公开或授权公开的内容；
- README 没有泄露未公开数据来源；
- 临时构建目录不需要保留时已清理。
