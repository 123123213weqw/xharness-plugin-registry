# XHarness public plugin registry

可匿名下载、校验 SHA-256、由用户选择安装和启用的插件市场。安装不等于启用，也不会自动安装运行依赖或使用用户账号。

## 当前 11 个条目（3 个新增 Beta 待发布）

| 插件 | 用途 | 版本／依赖 |
|---|---|---|
| GitHub | GitHub CLI 平台工作流 | 原有 0.2.0 保持不变；需要 git／gh 和用户授权 |
| Git／PR 工作流 | 变更整理、提交、PR 证据 | 0.1.0-beta.1；需要 git |
| 代码审查 | 代码、测试、异常、注释、类型审查 | 0.1.0-beta.1；复用 Host 工具 |
| 单元测试 | 行为、边界和失败路径测试 | 0.1.0-beta.1；需要项目实际测试环境 |
| 故障排查 | 复现、假设验证、修复与回归 | 0.1.0-beta.1；模型根因报告仍须复核 |
| 代码重构 | 渐进解耦和行为保持 | 0.1.0-beta.1；需要项目实际测试环境 |
| 文档助手 | 有限 Word／Excel／PPT／PDF 操作 | 0.1.0-beta.1；Python／Node／渲染器需单独配置 |
| 浏览器助手 | 观察、交互与结果验证流程 | 0.1.0-beta.1；不内置浏览器执行后端 |
| API 联调 | OpenAPI JSON 索引、GET／HEAD 探测和回归流程 | 0.1.0-beta.1；Python 3.9+；非完整 Schema 校验器 |
| 数据库助手 | 检查、查询诊断和迁移审查 | 0.1.0-beta.1；只读 SQLite helper 需 Python 3.11+；PG/MySQL 使用用户已有客户端 |
| Docker 助手 | Compose 状态、日志诊断和范围内变更验证 | 0.1.0-beta.1；Python 3.9+／已有 Docker 与 Compose；不安装守护进程 |

**Beta 是可选测试版，不是全源能力、全平台或准确性保证。** 每个新包的 `RELEASE.md` 记录实际范围、未实现功能和依赖。文档脚本只有有限 Linux 实测；浏览器 Skill 没有执行后端时只能提供明确未执行的计划。原版／改写版有限对照不代表统计显著的性能或质量提升。仓库不分发私有素材库、真实模型请求、费用账本、认证数据或原供应商运行时。

## 公有下载

- [GitHub 目录](https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/catalog.json)
- [Gitee 目录镜像](https://gitee.com/api/v5/repos/wangyue2006/xharness-plugin-registry/contents/catalog.json)

客户端按目录中的不可变版本地址下载并校验哈希。镜像更新可能滞后，失败时可以回退另一源；同一版本必须得到同一字节。Gitee 使用匿名 Contents API，其 JSON `base64` 文件内容由客户端还原后做同一 SHA-256 校验。

软件进入插件市场后刷新公有目录，用户选择安装、再选择启用。已安装版本不会因为目录更新被自动覆盖；用户自定义目录和数据不被迁移。

## 维护与验证

```sh
python3 scripts/build_catalog.py
python3 scripts/test_registry.py
python3 scripts/test_developer_plugins.py
```

`plugins/*/registry.json` 只提供市场元数据，不进入 ZIP。`plugins/*/.claude-plugin/plugin.json` 是安装元数据。打包确定性生成 `packages/<name>/<version>/plugin.zip`，拒绝原地改写已有版本；Github 0.2.0 原制品必须保持逐字节相同。CI 检查十一个包的哈希、布局、Skill 引用、隐私边界、版本不可变性、确定性和支持脚本语法。

Gitee 同步由主 XHarness 仓库的专用 CI 复用现有 Secret 完成，公开 registry 不保存镜像凭据。发布只改变市场目录和可选下载包，不重启应用、不自动启用插件、不执行 Hook/MCP。

参考来源与保留的许可文本见各包 `provenance.json`／license 文件。新工作流程与支持代码独立编写，不把缺少的源供应商组件冒充已移植。原始归档及独立验收证据保留在维护者隔离测试环境，不包含在公有包中。

新增三包在本地完成包校验、HTTP/SQLite/Compose 支持代码测试后，仍须通过 PR/CI 和发布更新公有目录；本地生成目录的下载地址并不表示远端已经存在。使用 `test_developer_plugins.py` 必须选择 Python 3.11+，它不调用真实模型，也不访问用户数据库或重启现有容器。
