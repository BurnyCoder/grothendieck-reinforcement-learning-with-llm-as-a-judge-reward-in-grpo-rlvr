# Source from the repository root; normalize Windows line endings without rewriting secrets.
# Bash sources shell text: https://www.gnu.org/software/bash/manual/html_node/Bourne-Shell-Builtins.html
if test -f .env; then
  set -a
  source <(sed 's/\r$//' .env)
  set +a
fi
