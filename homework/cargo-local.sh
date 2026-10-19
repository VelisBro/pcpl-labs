#!/bin/sh
# Используем обычный Cargo, либо отдельную установку на этом компьютере.
set -eu
cd "$(dirname "$0")"
if command -v cargo >/dev/null 2>&1; then
    exec cargo "$@"
fi
export CARGO_HOME="$HOME/.local/share/pcpl-rust/cargo"
export RUSTUP_HOME="$HOME/.local/share/pcpl-rust/rustup"
exec "$CARGO_HOME/bin/cargo" "$@"
