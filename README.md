# godot-cpp-m

The godot-cpp **10.0.0-rc1** API through C++23 modules. Keep upstream `godot::` types and names.

## Quick start

Use mcpp **2026.10.24.1**. Version **10.0.0-rc1.1** is a wrapper candidate until its index entry is published.

```sh
mcpp new godot-math --template godotengine.godot-cpp-m@10.0.0-rc1.1
cd godot-math
mcpp run
```

The default template runs vector and color math without a Godot process.

## Existing projects

```toml
[dependencies]
"godotengine.godot-cpp-m" = "10.0.0-rc1.1"
```

```cpp
import godot_cpp;
int main() {
    return godot::Vector2(3, 4).length() == 5 ? 0 : 1;
}
```

## Scope

The pinned godot-cpp release targets Godot 4.6. Linux, macOS and Windows use the
same module API; the generated bindings are supplied by `compat.godot-cpp`.

Engine objects and registration need a Godot process loading a GDExtension.
For `GDCLASS`, `D_METHOD` and other macros, include `<godot-cpp-m/macros.h>` before imports.
The [summator example](examples/summator) shows the extension structure; the default template exercises standalone math.

## Documentation

[Usage and adaptation details](docs/usage.md) · [Examples](examples) · [MIT](LICENSE)
