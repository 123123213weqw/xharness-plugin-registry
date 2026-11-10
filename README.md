# XHarness public plugin registry

当前公有商店只保留 **WordCraft 0.1.0**，不再发布通用调试、重构、单测、
PR 审查或其他旧 Skill 包。旧源码和版本仍可从 Git 历史审计，但不再出现在
当前目录或下载目录中。内置工具和用户自己的私有插件不受影响。

## WordCraft（可选实验插件）

独立下载的约 38.2 MiB ZIP，包含可视化 DOCX 编辑器、stdio MCP 适配器和
原样 WordCraft 0.5.0 WASM。需要配套 XHarness 编辑器支持及用户已有的 Node.js；
不安装运行依赖，不使用用户账号，不进入桌面默认安装包。

安装后 Skill 和 MCP 均关闭。用户明确允许 MCP，并从工作区 DOCX 确认打开编辑器
后才启动 Node 和加载 WASM。配套新版 Host 不再要求全局 Full access：普通模式
保持原有模型工具审批。0.1.0 不可变归档中的旧权限说明以新版宿主文档为准。
插件 Node 程序本身不是命令沙箱；支持的文档操作和宿主保存桥仍限制工作区路径。

隐藏保留未保存状态，但拒绝新的 AI 操作；编辑器必须可见且就绪。保存后再关闭。
重载或崩溃无法恢复未保存的浏览器内存，复杂 DOCX 布局不保证等同 Microsoft Word。
不会自动安装、启用、升级或重启 Host。

## 公有目录与校验

- [GitHub 目录](https://raw.githubusercontent.com/123123213weqw/xharness-plugin-registry/main/catalog.json)
- [Gitee 目录镜像](https://gitee.com/api/v5/repos/wangyue2006/xharness-plugin-registry/contents/catalog.json)

目录提供不可变版本 URL 与 SHA-256。`plugins/wordcraft/prebuilt.json` 绑定唯一 ZIP、
完整展开字节和原样 WASM 哈希；生成器只做严格验证，不声称从 Rust 源码可重复构建。
保留全部引擎、字体和第三方许可证。市场使用通用文档图标，不使用上游品牌作标识。

```sh
python3 scripts/build_catalog.py
python3 scripts/test_registry.py
python3 scripts/test_retired_plugins.py
python3 scripts/check_wordcraft_syntax.py
```

CI 保留包哈希、路径、隐私、版本不可变性和确定性门禁，并检查 WordCraft 的实际
MCP/UI/静态工具目录及 JavaScript 语法。已删除功能的 API/数据库/Docker helper
测试不再运行，替换为旧条目、旧源码、旧下载和多余图标不得重新出现的回归。
无依赖或 GitHub Actions 版本升级。

Gitee/Engine 分发仍由主 XHarness 仓库现有同步流程处理；本仓库不保存凭据。
目录更新不会远程卸载其他用户已选择安装的插件，也不删除聊天、项目或认证数据。
