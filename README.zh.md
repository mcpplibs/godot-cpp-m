# godot-cpp-m

> godot-cpp 10.0.0-rc1 的 C++23 模块封装，保留 godot:: API。

[English](README.md) · **简体中文** · [Upstream](https://github.com/godotengine/godot-cpp) · [Releases](https://github.com/mcpplibs/godot-cpp-m/releases) · [mcpp](https://github.com/mcpp-community/mcpp) · [Index](https://github.com/mcpplibs/mcpp-index)

[![C++23](https://img.shields.io/badge/C%2B%2B-23-blue.svg)](https://en.cppreference.com/w/cpp/23)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![mcpp-community](https://img.shields.io/badge/mcpp--community-mwrap-blue)](https://github.com/mcpp-community)
[![CI](https://github.com/mcpplibs/godot-cpp-m/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mcpplibs/godot-cpp-m/actions/workflows/ci.yml)

## 模块

- `import mcpplibs.mwrap.godot_cpp;`: godot:: 数学与 GDExtension 绑定
- `import mcpplibs.mwrap.godot_cpp.macros;`: 版本宏映射

> More Modules API -> [模块与 API](docs/usage.md)

## 安装

```sh
mcpp new godot_math --template mcpplibs.mwrap.godot_cpp@10.0.0-rc1
cd godot_math
mcpp run
```

```toml
[dependencies]
mcpplibs.mwrap.godot_cpp = "10.0.0-rc1"
```

## 宏

版本映射使用 `.macros`；GDCLASS、D_METHOD 与内存/控制宏在 import 前包含
`<mwrap/godot_cpp/macros.hpp>`，再 `import mcpplibs.mwrap.godot_cpp;`。

## hashfuncs 适配

生成的链接属性适配使上游模板实现可用于命名模块；见[详情](docs/usage.md)。

## 示例

```cpp
import mcpplibs.mwrap.godot_cpp;
int main() { return godot::Vector2(3, 4).length() == 5 ? 0 : 1; }
```

默认模板使用独立数学 API；[Summator](examples/summator) 构建共享扩展，加载需要匹配的引擎。

## 重新生成模块

用精确版本 compat.godot-cpp 源码及生成头运行 `tools/gen_module_cppm.py`；见[使用](docs/usage.md)。

## 测试

`mcpp test` 覆盖模块、数学与文本宏；CI 还在 Linux/macOS/Windows 构建扩展。
这是预发布绑定，不代表引擎实际加载认证。

## 许可证

[Apache-2.0](LICENSE)；compat.godot-cpp 提供上游源码、生成绑定及通知。

封装：Apache-2.0，mcpp-community。[上游原始 README 与许可证](upstream/godot-cpp/)，上游许可保持原样。
