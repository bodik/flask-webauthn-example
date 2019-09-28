#!/bin/sh
# git helper; do not allow root authored commits
# ln -s ../../extra/git_hookprecommit.sh .git/hooks/pre-commit

if [ "${GIT_AUTHOR_NAME}" = "root" ]; then
        echo "ERROR: not allowed to commit as root"
        exit 1
fi
