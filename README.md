# XHarness public plugin registry

精选公有目录与可校验、按需安装的 XHarness 插件包。仅公开这里列出的目录与原创制品，不公开私有素材库，也不保存访问密钥。

## 下载

- GitHub: https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/catalog.json
- Gitee mirror: https://gitee.com/wangyue2006/xharness-plugin-registry/raw/main/catalog.json

镜像未上线或更新延迟时，客户端可回退另一源。两个源必须分发同一份 zip，并使用同一 SHA-256。插件包可匿名下载；安装和启用是分别由用户选择的动作。

当前只提供 XHarness 原创 `github` 0.2.0，含 10 个 GitHub CLI 工作流 Skill，不内置 `gh` 或用户凭据，不包含 MCP。

## 维护

`python3 scripts/build_catalog.py` 生成确定性 zip 与 catalog.json。
`python3 scripts/test_registry.py` 校验哈希、内容、目录及双源地址，CI 运行同样的检查。
发布新版本请增加不可变的 packages/<plugin>/<version>/plugin.zip；不要原地替换已发布包。
Gitee 镜像由主 XHarness 仓库的专用工作流复用现有 Gitee Secret 同步；不在公开 registry 中保存 token。
