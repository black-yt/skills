# node 扫描共享盘造成 CPU 高占用

## 原记录与判断范围

备份说明中记录：VS Code/node 扫描大共享目录时 CPU 持续升高，开发机甚至失去响应，因此给项目添加排除设置。

- `node` 可能是 file watcher、search、Git、语言服务器或 agent，不可仅凭进程名就结束它。
- 先根据可执行文件、父子关系、cwd 和 VS Code Process Explorer/日志确定使用者，观察是否在递归扫描共享挂载或海量模型/数据文件。
- 不为 CPU 问题执行 `pkill node`，它可能同时终止 Codex、Claude、VS Code Server 和其他服务。

## 保留原配置并补齐 watcher 边界

原 settings.json 中：

```json
{
  "git.ignoreLimitWarning": true,
  "files.exclude": {
    "**/node_modules": true,
    "**/build": true,
    "**/dist": true,
    "**/.git": true,
    "**/.vscode": true,
    "**/[SHARED_MOUNT_DIRECTORY]/**": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/build": true,
    "**/dist": true,
    "**/.git": true,
    "**/.vscode": true,
    "**/[SHARED_MOUNT_DIRECTORY]/**": true
  }
}
```

- 原始个人配置列了两个绝对共享挂载路径；通用示例保留“避免扫描共享目录”目的，具体 pattern 按工作区相对路径、VS Code glob 语义和实际匹配结果填写，不能盲复制。
- `files.exclude` 主要影响资源管理器显示，`search.exclude` 影响搜索，`git.ignoreLimitWarning` 只是隐藏 Git 警告；这些都不能证明所有 watcher/语言服务器已停止扫描。
- 确认 watcher 是根因后，再添加对应的 `files.watcherExclude`；语言服务器、Git 或 agent 自身的扫描还需各自配置。
- 排除 `.vscode`、`.git` 会隐藏有用文件，只在确需的显示/扫描范围设置；不要因此删除目录。

```json
{
  "files.watcherExclude": {
    "**/[LARGE_SHARED_SUBTREE]/**": true
  }
}
```

## 修改与验收

1. 先备份当前有效 Profile/项目 settings.json，合并相关键，保留 JSONC 注释和其他设置；原备份中的整文件 `cp` 不适合无条件复用。
2. 优先只打开需要的子项目，避免把整个 home、共享盘或模型根目录当 workspace。
3. 用真实访问与监测确认 pattern 命中、CPU/IO 降低以及所需文件搜索和代码智能仍正常。
4. 若无改善，恢复本次排除设置并重新定位进程，不继续盲目扩大排除范围。
5. 重载窗口可能重启扩展宿主与终端，需先确认不会中断用户要求保留的任务。
