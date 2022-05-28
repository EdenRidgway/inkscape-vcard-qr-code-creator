#!/bin/bash

today=$(date +%Y.%m.%d.%H.%M)
zipfilename="/tmp/vcardqr_$today.zip"

zip -r $zipfilename ./* -x .git* -x pylint* -x .pep8 -x Makefile -x "no-package*" -x "*__pycache__*" -x package_extension.sh

gpg --detach-sign --armor -u maren@goos-habermann.de -o $zipfilename.sig $zipfilename

gpg --verify $zipfilename.sig $zipfilename
