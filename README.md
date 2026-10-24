# godot-cpp-m

> godot-cpp 10.0.0-rc1 as C++23 modules, preserving godot:: APIs.

**English** · [简体中文](README.zh.md) · [Upstream](https://github.com/godotengine/godot-cpp) · [Releases](https://github.com/mcpplibs/godot-cpp-m/releases) · [mcpp](https://github.com/mcpp-community/mcpp) · [Index](https://github.com/mcpplibs/mcpp-index)

[![C++23](https://img.shields.io/badge/C%2B%2B-23-blue.svg)](https://en.cppreference.com/w/cpp/23)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![mcpp-community](https://img.shields.io/badge/mcpp--community-mwrap-blue)](https://github.com/mcpp-community)
[![CI](https://github.com/mcpplibs/godot-cpp-m/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mcpplibs/godot-cpp-m/actions/workflows/ci.yml)

## Modules

- `import mcpplibs.mwrap.godot_cpp;`: godot:: math and GDExtension bindings
- `import mcpplibs.mwrap.godot_cpp.macros;`: Version macro mappings

> More Modules API -> [Usage and API](docs/usage.md)

## Install

```sh
mcpp new godot_math --template mcpplibs.mwrap.godot_cpp@10.0.0-rc1
cd godot_math
mcpp run
```

```toml
[dependencies]
mcpplibs.mwrap.godot_cpp = "10.0.0-rc1"
```

## Macros

Use `.macros` for version mappings. For GDCLASS, D_METHOD and memory/control macros, include
`<mwrap/godot_cpp/macros.hpp>` before `import mcpplibs.mwrap.godot_cpp;`.

## The hashfuncs shim

A generated linkage adapter keeps upstream template bodies usable by named modules. [Details](docs/usage.md)

## Example

```cpp
import mcpplibs.mwrap.godot_cpp;
int main() { return godot::Vector2(3, 4).length() == 5 ? 0 : 1; }
```

The default template uses standalone math. [Summator](examples/summator) builds a shared GDExtension; loading needs a matching engine.

## Regenerating the module

Use `tools/gen_module_cppm.py` with the exact compat.godot-cpp source and generated headers; see [usage](docs/usage.md).

## Tests

`mcpp test` covers module/math and textual macros; CI also builds the extension on Linux/macOS/Windows.
This is a prerelease binding, not certification of engine loading.

## License

[Apache-2.0](LICENSE); compat.godot-cpp carries upstream sources, generated bindings and notices.

Wrapper: Apache-2.0, mcpp-community. [Original upstream README and licenses](upstream/godot-cpp/). Upstream licenses remain unchanged.
