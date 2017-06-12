#!/bin/bash
function install_dotfiles() {
	rsync --exclude ".git/" \
		--exclude ".DS_Store" \
		--exclude ".osx" \
		--exclude "bootstrap.sh" \
		--exclude "README.md" \
		--exclude "LICENSE-MIT.txt" \
		--exclude ".extra" \
		--exclude "/.sublime" \
		-avh --no-perms . ~;
	source ~/.bash_profile;
}

install_dotfiles;
unset install_dotfiles;