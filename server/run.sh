#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -z "${PROTOC:-}" ] && [ -x .local/protobuf/bin/protoc ]; then
  export PROTOC="$PWD/.local/protobuf/bin/protoc"
fi
if [ "$(uname)" = Darwin ] && [ -z "${SDKROOT:-}" ] && [ -d /Library/Developer/CommandLineTools/SDKs/MacOSX15.4.sdk ]; then
  export SDKROOT=/Library/Developer/CommandLineTools/SDKs/MacOSX15.4.sdk
fi
exec cargo "${1:-run}" --manifest-path server/Cargo.toml
