# godot-cpp-m

> godot-cpp as a C++23 module for mcpp — the same API, reached with `import godot_cpp;`.

```cpp
import std;
import godot_cpp;

int main() {
    godot::Vector2 v{3, 4};
    std::println("{}", v.length());   // 5 — the same godot-cpp you already know, no #include
}
```

- **Nothing forked, nothing reimplemented.** Upstream's sources and its
  pre-generated GDExtension bindings arrive through the
  [`compat.godot-cpp`](https://github.com/mcpplibs/mcpp-index) index package,
  which compiles all 1022 translation units directly — no SCons, no CMake, and
  no Python anywhere in the build. This repository is only the module layer.
- **The whole `godot` namespace is re-exported**, generated from the headers
  rather than curated by hand: ~1750 names, every engine class, every builtin
  Variant type, the global enums *and their enumerators* (so `godot::OK` and
  `godot::ERR_FILE_NOT_FOUND` still spell the same), `godot::Math`, the
  templates.
- **Macros keep working too**, through an optional side header — see below.

## Install

```toml
[dependencies]
godot-cpp = "4.5.0"
```

The version tracks upstream: `4.5.0` is the godot-cpp release this wraps, the
same version `compat.godot-cpp` carries, so the number tells you which Godot
you are targeting.

## Macros

C++ named modules cannot export macros, and GDExtension code is written in
them: `GDCLASS`, `GDREGISTER_CLASS`, `GDVIRTUAL_*`, `D_METHOD`,
`memnew`/`memdelete`, the `ERR_*` family. A translation unit that registers
classes includes the side header next to the import:

```cpp
#include <godot-cpp-m/macros.h>
import godot_cpp;

using namespace godot;

class Player : public Node2D {
    GDCLASS(Player, Node2D)
protected:
    static void _bind_methods() {
        ClassDB::bind_method(D_METHOD("get_speed"), &Player::get_speed);
    }
public:
    void _process(double delta) override { /* ... */ }
    double get_speed() const { return speed; }
private:
    double speed = 1.0;
};
```

The headers it pulls in denote the same global-module entities the module
re-exports (they sit in the module's global module fragment), so mixing the
include and the import this way is well-formed. `tests/godot_cpp_macros.cpp`
covers exactly this shape. Any other upstream header can be included the same
way — they are all on the include path.

## What is NOT re-exported

| name | why |
|---|---|
| `HashMap`, `HashSet`, `HashMapElement`, `HashMapHasherDefault`, `HashHasher`, `HashableHasher`, `PairHash` | their inline bodies reach `hash_murmur3_one_float/double`, which are `static` **and** declare an unnamed union. An unnamed union type is TU-local, and exposing a TU-local *type* from a module interface is a hard error, not a warning. These are godot-cpp's internal container plumbing — extension code uses `Dictionary`/`Array`/`TypedArray` — and they stay reachable through the headers. |
| `godot::internal` | the gdextension interface plumbing; the module's own definitions use it without it being public API. |
| namespace-scope `const`/`constexpr` variables | internal linkage, so not exportable at all. Take them from the header. |

## Example

`examples/summator/` is a complete GDExtension — registered class, bound
methods, entry point — built as the shared library Godot loads, written with
`import godot_cpp;`:

```sh
cd examples/summator && mcpp build
# then drop the library + summator.gdextension into a Godot 4.5 project
```

## Regenerating the module

`src/godot_cpp.cppm` is generated, not hand-written. After a `compat.godot-cpp`
version bump:

```sh
python3 tools/gen_module_cppm.py <godot-cpp-checkout-with-gen/> > src/godot_cpp.cppm
mcpp test
```

The checkout has to be one that has already run upstream's
`binding_generator.py` — which is exactly what the `compat.godot-cpp` archive
contains, so unpacking that is the simplest source.

## Tests

```sh
mcpp test
```

- `tests/godot_cpp_module.cpp` — the module surface: Variant math whose
  definitions live in the library's `.cpp` files (so it can only pass if the
  library really linked), plus generated engine classes and global enums.
- `tests/godot_cpp_macros.cpp` — the macro surface: a `GDCLASS` subclass with a
  bound method and an overridden engine virtual, next to the import.

Neither runs engine code: anything routed through the `gdextension_interface_*`
function pointers needs a Godot process that has loaded the extension.

## License

MIT for the module layer. Upstream godot-cpp is MIT as well.
