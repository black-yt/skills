# Remote Access And Editing

## 固定信息、登录与路径

交互式登录开发机：

```bash
ssh -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn
```

如果 `h.pjlab.org.cn` 域名 SSH 连接失败、DNS 解析异常或网络到域名不稳定，可以保持相同用户名，把目标主机临时换成开发机 IP 试一次：

```bash
ssh -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@10.102.254.2
```

这只是 SSH 入口的备用连接方式。后续 `rjob` 日志里的服务 IP、worker 内网 IP、KAPI URL 和 `ssh -L` 转发目标仍按对应章节从日志或实际服务信息获取，不要用这个入口 IP 代替服务 IP。

推荐工作方式：先保持一个后台持久 SSH 终端，再在这个终端内连续执行 `cd`、编辑、提交、日志查看和清理。对于 Codex 或其他自动化 agent，这意味着优先维护一个长期 PTY/session，而不是每一步都新发一次 `ssh 'command'`。只有下面这种单次简单检查才适合一次性 SSH：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=1 \
  -CAXY agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn \
  'hostname; command -v rlaunch; command -v rjob'
```

复杂远端操作，例如项目内多步修改、任务脚本编写、`rjob` 提交后跟日志、`rlaunch` worker 交互、服务启动和端口测试，都应在后台持久 SSH 终端中完成。

登录后最小检查：

```bash
hostname
command -v rlaunch
command -v rjob
source /etc/profile.d/ssh-init.sh 2>/dev/null || true
rlaunch --help | sed -n '1,20p'
rjob submit --help | sed -n '1,20p'
```

公共挂载。所有 `rlaunch` 和 `rjob submit` 命令通常都带上这些挂载：

```bash
--mount=gpfs://gpfs1/xuwanghan:/mnt/shared-storage-user/xuwanghan
--mount=gpfs://gpfs1/sciprismax:/mnt/shared-storage-user/sciprismax
--mount=gpfs://gpfs2/gpfs2-shared-public:/mnt/shared-storage-gpfs2/gpfs2-shared-public
--mount=gpfs://gpfs2/sciprismax2:/mnt/shared-storage-gpfs2/sciprismax2
```

常用镜像：

```bash
registry.h.pjlab.org.cn/ailab/ml-base:22.04-pjlab
```

常用 CUDA：

```bash
/mnt/shared-storage-gpfs2/gpfs2-shared-public/soft/cuda/12.8
```

常用 conda env 目录：

```bash
/mnt/shared-storage-user/xuwanghan/conda_env
```

常用 conda 环境：

```bash
conda activate agent   # 开发机默认开发环境
conda activate llmv2   # LLM 训练/部署推荐环境
conda activate llm     # LLM 训练/部署旧环境
```

不要重新安装 conda，不要擅自创建环境或修改已有环境中的包。遇到不清楚的环境名，先问用户。

个人项目根目录。不同项目都在这里，代码和普通项目数据不要存放到其他地方：

```bash
/mnt/shared-storage-user/xuwanghan/projects
```

大文件根目录。大于 5G 的数据或权重放到这里的合适子目录：

```bash
/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan
```

临时文件与缓存控制：

```bash
PROJECT_DIR="/mnt/shared-storage-user/xuwanghan/projects/<project>"
BIG_DIR="/mnt/shared-storage-gpfs2/sciprismax2/xuwanghan/<project>"
mkdir -p "$PROJECT_DIR" "$BIG_DIR"

# 小型项目缓存。不要使用默认 ~/.cache。
export XDG_CACHE_HOME="$PROJECT_DIR/.cache"
export HF_HOME="$PROJECT_DIR/.cache/huggingface"
export TRANSFORMERS_CACHE="$HF_HOME/transformers"
export HF_DATASETS_CACHE="$HF_HOME/datasets"

# 大于 5G 的缓存、数据或权重改放 BIG_DIR，并在命令结束后检查容量。
# export HF_HOME="$BIG_DIR/huggingface"
# export TRANSFORMERS_CACHE="$HF_HOME/transformers"
# export HF_DATASETS_CACHE="$HF_HOME/datasets"

# 必须用临时目录时，只放任务内短生命周期文件，并确保退出时清理。
RUN_TMP="$PROJECT_DIR/.tmp/run-$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$RUN_TMP"
trap 'rm -rf "$RUN_TMP"' EXIT
```

## 远端文件编辑工作流

本地编辑工具只能修改当前本地 workspace，不能直接修改开发机或 worker 上的文件。需要修改远端集群文件时，不要假装本地 `apply_patch` 已经改到了远端；先建立后台持久 SSH 终端，再按下面几种方式处理。

远端目录不一定是 git repo。只有确认远端目录是 git repo 时，才使用 `git status`、`git diff`、`git apply --check`、`git apply`。非 git 目录不要套用 git 流程，改用远端编辑器或完整文件复制。

所有远端临时文件都放到目标项目自己的 `.tmp` 子目录，文件名带任务名或时间戳；任务结束必须删除临时文件，避免 `.tmp` 被杂乱文件塞满。不要把临时编辑文件放到系统 `/tmp`、`/var/tmp` 或 worker 本地盘。

方式一：远端项目是 git repo 时，优先用标准 unified diff + `git apply`。`git apply` 在远端完全可以用，而且比 `sed`/`perl` 更适合多文件或结构化改动。前提是 patch 必须是标准 unified diff，例如 `git diff` 生成的 `diff --git ...`、`---`、`+++`、`@@` 格式；不要把 Codex 本地 `apply_patch` 工具专用的 `*** Begin Patch` / `*** Update File` 格式传给远端 `git apply`，标准 `git apply` 不认识这种格式。

先在本地生成 patch，再传到远端项目 `.tmp`，在后台持久 SSH 终端中检查并应用，最后删除临时 patch 和空 `.tmp` 目录：

```bash
# 本地终端
REMOTE='agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn'
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
PATCH_NAME="cluster-change-$(date +%Y%m%d-%H%M%S).patch"
PATCH_LOCAL="./$PATCH_NAME"

git diff -- <files> > "$PATCH_LOCAL"
ssh -CAXY "$REMOTE" "mkdir -p '$PROJECT/.tmp'"
scp "$PATCH_LOCAL" "$REMOTE:$PROJECT/.tmp/$PATCH_NAME"
rm -f "$PATCH_LOCAL"
```

```bash
# 远端后台持久 SSH 终端
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
PATCH_NAME='<patch-name-from-local-step>'
cd "$PROJECT"
test -d .git
git status --short
git apply --check ".tmp/$PATCH_NAME"
git apply ".tmp/$PATCH_NAME"
git diff
rm -f ".tmp/$PATCH_NAME"
rmdir .tmp 2>/dev/null || true
git status --short
```

`git apply` 使用边界：

- 只在远端目录是 git repo，且 patch 与远端当前文件版本匹配时使用。
- 必须先 `git apply --check`，通过后再 `git apply`。
- 应用后必须看 `git diff`，确认改动范围、行数和语义符合预期。
- patch 文件放项目 `.tmp`，应用后删除；不要把 patch 长期留在 `.tmp`。
- 如果 `git apply --check` 失败，先看是否 patch 基于旧版本、路径不对、已有冲突或误用了 `apply_patch` 格式；不要改成强行覆盖。

方式二：少量手工改动，直接在后台持久 SSH 终端中用远端已有编辑器修改。不要安装新编辑器，不要改全局配置。git repo 用 `git diff` 检查；非 git 目录用 `diff -u` 前后备份检查，检查后删除备份：

```bash
cd /mnt/shared-storage-user/xuwanghan/projects/<project>
vim path/to/file
if [ -d .git ]; then
  git diff -- path/to/file
fi
```

```bash
cd /mnt/shared-storage-user/xuwanghan/projects/<project>
TARGET_FILE="path/to/file"
BACKUP_FILE="${TARGET_FILE}.bak.$(date +%Y%m%d-%H%M%S)"
cp "$TARGET_FILE" "$BACKUP_FILE"
vim "$TARGET_FILE"
diff -u "$BACKUP_FILE" "$TARGET_FILE" || true
rm -f "$BACKUP_FILE"
```

方式三：少量机械替换可用 `perl` 或 `sed`，但只适合非常小、确定、唯一匹配、可立即校验的文本替换。不要用它们做多文件复杂改动、代码重构、结构性编辑或有多处近似匹配的修改；这种情况回到方式一的 `git apply` 或方式四的完整文件替换。

git repo 中的小替换：

```bash
cd /mnt/shared-storage-user/xuwanghan/projects/<project>
TARGET_FILE="path/to/file"

# 示例：跨行或整文件匹配时可用 perl -0pi；替换前后都要检查。
grep -n "OLD_TEXT" "$TARGET_FILE"
perl -0pi -e 's/OLD_TEXT/NEW_TEXT/g' "$TARGET_FILE"
git diff -- "$TARGET_FILE"
```

非 git 目录中的小替换必须先备份，替换后 `diff -u`，最后清理备份：

```bash
cd /mnt/shared-storage-user/xuwanghan/projects/<project>
TARGET_FILE="path/to/file"
BACKUP_FILE="${TARGET_FILE}.bak.$(date +%Y%m%d-%H%M%S)"
cp "$TARGET_FILE" "$BACKUP_FILE"

grep -n "OLD_TEXT" "$TARGET_FILE"
perl -0pi -e 's/OLD_TEXT/NEW_TEXT/g' "$TARGET_FILE"
diff -u "$BACKUP_FILE" "$TARGET_FILE" || true
rm -f "$BACKUP_FILE"
```

`perl`/`sed` 使用边界：

- 替换前先 `grep` 或只读查看，确认匹配对象唯一或所有匹配都应修改。
- 替换后立即 `git diff -- <file>` 或 `diff -u backup file`。
- 不要在不理解正则转义、换行、贪婪匹配影响时使用 `perl -0pi`。
- 不要把 `perl`/`sed` 当作绕过 review 的方式；能用标准 patch 表达的改动优先用 `git apply`。

方式四：本地编辑复杂文件后上传替换。这是传输/替换流程，不是远端编辑；命令叫 `scp`，用于通过 SSH 复制文件。适合一个文件太复杂、不适合在远端用 `sed`、`perl` 或编辑器逐步修改时使用。先在本地编辑好完整文件，再复制到远端项目 `.tmp`，在远端校验后移动到目标路径，并清理临时文件：

```bash
# 本地终端
REMOTE='agent.xuwanghan+root.ailab-ai4sdata.ws@h.pjlab.org.cn'
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
LOCAL_FILE='./file.new'
REMOTE_NAME="file.new.$(date +%Y%m%d-%H%M%S).$$"
REMOTE_TMP="$PROJECT/.tmp/$REMOTE_NAME"

ssh -CAXY "$REMOTE" "mkdir -p '$PROJECT/.tmp'"
scp "$LOCAL_FILE" "$REMOTE:$REMOTE_TMP"
```

```bash
# 远端后台持久 SSH 终端
PROJECT='/mnt/shared-storage-user/xuwanghan/projects/<project>'
REMOTE_NAME='<remote-name-from-local-step>'
TARGET_FILE='path/to/file'
BACKUP_NAME="$(basename "$TARGET_FILE").bak.$(date +%Y%m%d-%H%M%S)"
cd "$PROJECT"
test -s ".tmp/$REMOTE_NAME"
if [ -f "$TARGET_FILE" ]; then
  cp "$TARGET_FILE" ".tmp/$BACKUP_NAME"
fi
cp ".tmp/$REMOTE_NAME" "$TARGET_FILE"
rm -f ".tmp/$REMOTE_NAME"
if [ -d .git ]; then
  git diff -- "$TARGET_FILE"
else
  if [ -f ".tmp/$BACKUP_NAME" ]; then
    diff -u ".tmp/$BACKUP_NAME" "$TARGET_FILE" || true
  fi
fi
rm -f ".tmp/$BACKUP_NAME"
rmdir .tmp 2>/dev/null || true
```
