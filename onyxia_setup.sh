#!/bin/sh
# chmod +x onyxia_setup.sh

# Customize VSCode extensions
code-server --uninstall-extension ms-python.flake8
code-server --install-extension charliermarsh.ruff
code-server --install-extension tamasfe.even-better-toml

# Webservice url
export API_URL="https://${KUBERNETES_NAMESPACE}-${KUBERNETES_SERVICE_ACCOUNT##*-}-user.user.lab.sspcloud.fr/"

# Add branch name in prompt
BASHRC="$HOME/.bashrc"
sed -i "/PS1='.*01;32m.*\\\\u@\\\\h/c\\
    PS1='\\\${debian_chroot:+(\\\$debian_chroot)}\\\[\\\033[01;32m\\\]\\\u@\\\h\\\[\\\033[00m\\\]:\\\[\\\033[01;34m\\\]\\\w\\\[\\\033[33m\\\]\\\$(__git_ps1 \" (%s)\")\\\[\\\033[00m\\\]\\\$ '" \
"$BASHRC"