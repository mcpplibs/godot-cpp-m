#!/usr/bin/env python3
"""Generate godot-cpp-m's `godot_cpp` C++23 module interface unit.

godot-cpp ships no module interface unit, so this index provides one. A module
exports only what it names, and godot-cpp's public surface is ~1000 generated
engine classes plus the hand-written core/variant/templates layer -- far too
much to curate by hand, and it moves every Godot release. So the wrapper is
GENERATED from the headers of a checkout that has already run upstream's own
`binding_generator.py`:

    python3 tools/gen_module_cppm.py <godot-cpp-checkout> > src/godot_cpp.cppm

The scanner walks the header text with a brace/namespace-aware state machine and
collects every declaration at namespace scope under `godot` (plus the nested
`godot::Math` / `godot::helpers`; `godot::internal` is deliberately NOT exported
-- it is the gdextension interface plumbing, reachable from the module's own
inline/template definitions without being part of the public API).

What a module cannot carry, and this therefore does not: MACROS. GDCLASS,
GDREGISTER_CLASS, memnew/memdelete, the ERR_* family and GDVIRTUAL_* are
preprocessor constructs, so a registration TU still needs the corresponding
`#include`. See the descriptor's header comment for the supported spelling.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Namespaces whose members get re-exported. `internal` is excluded on purpose.
EXPORTED_NAMESPACES = ("godot", "godot::Math", "godot::helpers")

# Declarations that must not be re-exported.
#   * `_gde_UnexistingClass` is a placeholder for unexposed engine types.
#   * The `Ref`/`TypedArray` etc. forward declarations are covered by their
#     real definitions; duplicates are removed by the dedup below.
SKIP_NAMES = {
    "_gde_UnexistingClass",
    # godot-cpp's default hashers inline-call `hash_murmur3_one_float/double`,
    # which are `static` AND declare an unnamed union in their bodies. An
    # unnamed union type is TU-local, and exposing a TU-local TYPE from a
    # module interface is a hard error (not the -Wexpose-global-module-tu-local
    # warning), so these cannot be re-exported. They are godot-cpp's internal
    # container plumbing -- extension code uses Dictionary/Array/TypedArray --
    # and stay reachable through the headers for anyone who needs them.
    # Reaching them: HashMap/HashSet default their Hasher template parameter
    # to HashMapHasherDefault, so re-exporting the container re-exports the
    # hasher's inline bodies with it.
    "HashMapHasherDefault",
    "HashableHasher",
    "HashHasher",
    "HashMap",
    "HashMapElement",
    "HashSet",
    "PairHash",
}

COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
STRING_RE = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'')
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

# Keywords that can never be the declared name.
NON_NAMES = {
    "const", "constexpr", "consteval", "constinit", "static", "inline", "extern",
    "friend", "virtual", "explicit", "typename", "class", "struct", "union",
    "enum", "template", "using", "typedef", "namespace", "public", "private",
    "protected", "operator", "return", "if", "else", "for", "while", "do",
    "switch", "case", "default", "break", "continue", "goto", "new", "delete",
    "sizeof", "alignof", "noexcept", "decltype", "auto", "void", "bool", "char",
    "char8_t", "char16_t", "char32_t", "wchar_t", "short", "int", "long",
    "signed", "unsigned", "float", "double", "nullptr", "true", "false",
    "thread_local", "mutable", "volatile", "restrict", "register", "export",
    "requires", "concept", "static_assert", "namespace", "operator",
    "this", "throw", "try", "catch", "typeid", "asm", "co_await", "co_return",
    "co_yield", "constexpr", "final", "override",
}

# Attribute-ish macros godot-cpp puts in front of declarations.
DECORATORS = {
    "_ALWAYS_INLINE_", "_FORCE_INLINE_", "_NO_DISCARD_", "GDE_EXPORT",
    "_NO_INLINE_", "_ALLOW_DISCARD_",
}


def strip_noise(text: str) -> str:
    """Remove comments, string/char literals and preprocessor lines.

    Literals go first so a `"//"` inside a string cannot start a comment, and
    preprocessor lines go last so a `#define` body cannot leak braces.
    """
    text = STRING_RE.sub('""', text)
    text = COMMENT_RE.sub(" ", text)
    out = []
    in_directive = False
    for line in text.split("\n"):
        stripped = line.lstrip()
        if in_directive or stripped.startswith("#"):
            # A directive swallows every line it continues onto -- macro
            # bodies are full of declaration-shaped text (`MAKE_PTRARG(m_type)`,
            # `static_assert(...)`) that would otherwise be read as real
            # declarations at namespace scope.
            in_directive = line.rstrip().endswith("\\")
            out.append("")
            continue
        out.append(line)
    return "\n".join(out)


def split_template_head(head: str) -> str:
    """Drop a leading `template <...>` (possibly several) from a declarator."""
    while True:
        m = re.match(r"\s*template\s*<", head)
        if not m:
            return head
        i = m.end() - 1
        depth = 0
        while i < len(head):
            if head[i] == "<":
                depth += 1
            elif head[i] == ">":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        head = head[i + 1:]


def declared_name(head: str) -> tuple[str, str] | None:
    """Return (category, name) for a namespace-scope declarator head."""
    head = split_template_head(head).strip()
    if not head:
        return None
    for dec in DECORATORS:
        head = head.replace(dec, " ")
    head = head.strip()

    m = re.match(r"(?:class|struct|union)\s+([A-Za-z_][A-Za-z0-9_]*)", head)
    if m:
        return ("record", m.group(1))

    m = re.match(r"enum\s+(?:class\s+|struct\s+)?([A-Za-z_][A-Za-z0-9_]*)", head)
    if m:
        scoped = bool(re.match(r"enum\s+(?:class|struct)\s", head))
        return ("scoped_enum" if scoped else "enum", m.group(1))

    m = re.match(r"using\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", head)
    if m:
        return ("alias", m.group(1))

    if head.startswith("using ") or head.startswith("namespace "):
        return None
    if head.startswith("static ") or " static " in f" {head} ":
        # internal linkage -- exporting it is ill-formed
        return None
    if head.startswith("typedef"):
        # `typedef R (*name)(args)` or `typedef T name`
        m = re.search(r"\(\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", head)
        if m:
            return ("alias", m.group(1))
        ids = IDENT_RE.findall(head)
        ids = [i for i in ids if i not in NON_NAMES]
        return ("alias", ids[-1]) if ids else None

    # function or variable
    paren = find_declarator_paren(head)
    if paren is not None:
        before = head[:paren]
        m = re.search(r"operator\s*(?:[^\s\w(]+|\bnew\b|\bdelete\b|\"\"\s*\w+)\s*$", before)
        if m:
            # `Vector2 &Vector2::operator*=(...)` is an out-of-line member
            # definition, not a namespace-scope operator
            if "::" in before[:m.start()]:
                return None
            return ("operator", m.group(0).strip())
        ids = list(IDENT_RE.finditer(before))
        if not ids or ids[-1].group(0) in NON_NAMES:
            return None
        # skip out-of-line member definitions (`Vector3::normalized`)
        if "::" in before[max(0, ids[-1].start() - 2):ids[-1].start()]:
            return None
        # A declaration always has a return type in front of the name. A head
        # that is JUST `NAME(args)` is a function-like MACRO INVOCATION at
        # namespace scope -- godot-cpp has many (`MAKE_PTRARG(bool);`,
        # `GDVIRTUAL_NATIVE_PTR(AudioFrame);`) and they declare nothing that
        # can be named from outside.
        if not before[:ids[-1].start()].strip():
            return None
        return ("function", ids[-1].group(0))

    # variable: last identifier before `=` or end
    before = head.split("=", 1)[0]
    # drop array bounds -- `inline constexpr uint32_t primes[HASH_TABLE_SIZE_MAX]`
    # would otherwise be read as declaring the bound, not the array
    before = re.sub(r"\[[^\]]*\]", " ", before)
    if "::" in before:
        return None
    # A namespace-scope `const`/`constexpr` variable has INTERNAL linkage
    # unless it is `extern` or `inline`, and exporting one is ill-formed
    # ("does not have external linkage"). Consumers that need such a constant
    # take it from the header.
    words = set(re.findall(r"[A-Za-z_]+", before))
    if ("const" in words or "constexpr" in words) and not (words & {"extern", "inline"}):
        return None
    ids = [i for i in IDENT_RE.findall(before) if i not in NON_NAMES]
    if ids:
        return ("variable", ids[-1])
    return None


def find_declarator_paren(head: str) -> int | None:
    """Index of the `(` that opens a function parameter list, if any."""
    depth_angle = 0
    i = 0
    while i < len(head):
        c = head[i]
        if c == "<":
            depth_angle += 1
        elif c == ">":
            depth_angle = max(0, depth_angle - 1)
        elif c == "(" and depth_angle == 0:
            return i
        i += 1
    return None


def enum_constants(body: str) -> list[str]:
    """Enumerator names from an enum body (`A = 1, B, C`)."""
    names = []
    depth = 0
    current = []
    for ch in body:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            names.append("".join(current))
            current = []
        else:
            current.append(ch)
    names.append("".join(current))
    out = []
    for entry in names:
        entry = entry.split("=", 1)[0].strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", entry):
            out.append(entry)
    return out


class Scanner:
    def __init__(self) -> None:
        # name -> category, per namespace
        self.decls: dict[str, dict[str, str]] = {ns: {} for ns in EXPORTED_NAMESPACES}
        self.order: dict[str, list[str]] = {ns: [] for ns in EXPORTED_NAMESPACES}

    def record(self, ns: str, name: str, category: str) -> None:
        if ns not in self.decls or name in SKIP_NAMES:
            return
        if name.startswith("__"):
            return
        if name not in self.decls[ns]:
            self.decls[ns][name] = category
            self.order[ns].append(name)

    def scan(self, text: str) -> None:
        text = strip_noise(text)
        i = 0
        n = len(text)
        ns_stack: list[str] = []
        # depth of `{` opened inside the current namespace body
        block_depth = 0
        head_start = 0
        while i < n:
            c = text[i]
            if c == "{":
                head = text[head_start:i]
                if block_depth == 0:
                    m = re.match(r"\s*namespace\s+([A-Za-z_][A-Za-z0-9_:]*)\s*$", head)
                    if m:
                        ns_stack.append(m.group(1).replace("::", "::"))
                        head_start = i + 1
                        i += 1
                        continue
                    if re.match(r"\s*(?:extern\s*|inline\s+namespace\b)", head) and "namespace" in head:
                        ns_stack.append("")
                        head_start = i + 1
                        i += 1
                        continue
                    ns = "::".join(x for x in ns_stack if x)
                    info = declared_name(head)
                    if info and ns in self.decls:
                        category, name = info
                        self.record(ns, name, category)
                        if category == "enum":
                            end = match_brace(text, i)
                            for constant in enum_constants(text[i + 1:end]):
                                self.record(ns, constant, "enumerator")
                    # skip the whole block
                    end = match_brace(text, i)
                    i = end + 1
                    head_start = i
                    continue
                block_depth += 1
                i += 1
                continue
            if c == "}":
                if block_depth == 0 and ns_stack:
                    ns_stack.pop()
                    head_start = i + 1
                    i += 1
                    continue
                block_depth = max(0, block_depth - 1)
                i += 1
                head_start = i
                continue
            if c == ";" and block_depth == 0:
                head = text[head_start:i]
                ns = "::".join(x for x in ns_stack if x)
                info = declared_name(head)
                if info and ns in self.decls:
                    self.record(ns, info[1], info[0])
                head_start = i + 1
                i += 1
                continue
            i += 1


def match_brace(text: str, start: int) -> int:
    """Index of the `}` matching the `{` at `start`."""
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return len(text) - 1


HEADER = """\
// godot_cpp -- C++23 module interface unit for godot-cpp {version}.
//
// GENERATED by tools/gen_module_cppm.py from the godot-cpp headers
// (upstream `include/` plus the `gen/` tree produced by upstream's own
// binding_generator.py). Do not hand-edit: regenerate instead.
//
// The whole public `godot` namespace is re-exported, so code that used to say
//
//     #include <godot_cpp/classes/node.hpp>
//     godot::Node *n = ...;
//
// says `import godot_cpp;` instead and is otherwise unchanged. Macros are the one
// thing a module cannot carry (GDCLASS, GDREGISTER_CLASS, memnew, ERR_*,
// GDVIRTUAL_*): a TU that registers classes still includes the header that
// defines them.
module;

{includes}

export module godot_cpp;

"""


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        sys.stderr.write(f"usage: {argv[0]} <godot-cpp-checkout>\n")
        return 2
    root = Path(argv[1])
    include_roots = [root / "include", root / "gen" / "include"]
    for r in include_roots:
        if not r.is_dir():
            sys.stderr.write(f"error: {r} not found (run binding_generator.py first)\n")
            return 1

    headers: list[tuple[Path, str]] = []
    for r in include_roots:
        for p in sorted(r.rglob("*.hpp")):
            headers.append((p, str(p.relative_to(r).as_posix())))

    scanner = Scanner()
    for path, _rel in headers:
        scanner.scan(path.read_text(encoding="utf-8", errors="replace"))

    version = "unknown"
    version_hpp = root / "gen" / "include" / "godot_cpp" / "core" / "version.hpp"
    if version_hpp.is_file():
        text = version_hpp.read_text(encoding="utf-8")
        major = re.search(r"#define GODOT_VERSION_MAJOR\s+(\d+)", text)
        minor = re.search(r"#define GODOT_VERSION_MINOR\s+(\d+)", text)
        patch = re.search(r"#define GODOT_VERSION_PATCH\s+(\d+)", text)
        if major and minor and patch:
            version = f"{major.group(1)}.{minor.group(1)}.{patch.group(1)}"

    includes = "\n".join(f"#include <{rel}>" for _p, rel in headers)
    out = [HEADER.format(version=version, includes=includes)]

    for ns in EXPORTED_NAMESPACES:
        names = scanner.order[ns]
        if not names:
            continue
        out.append(f"export namespace {ns} {{\n")
        for name in names:
            if name.startswith("operator"):
                out.append(f"using ::{ns}::{name};\n")
            else:
                out.append(f"using ::{ns}::{name};\n")
        out.append("}\n\n")

    sys.stdout.write("".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
