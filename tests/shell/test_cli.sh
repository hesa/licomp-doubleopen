#!/bin/bash

# SPDX-FileCopyrightText: 2024 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

lo()
{
    PYTHONPATH=. ./licomp_doubleopen/__main__.py $*
    if [ $? -ne 0 ]
    then
        echo "failed: $*"
        exit 1
    fi
}

lo --help
lo --name
lo --version
lo supported-provisionings
lo supported-usecases
lo supported-licenses
lo verify -il MIT -ol BSD-3-Clause
