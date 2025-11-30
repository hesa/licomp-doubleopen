#!/bin/bash

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Top 10 licenses from
# https://gitlab.com/automated-foss-license-compliance/foss-license-analysis/-/blob/main/top-20.md?ref_type=heads&plain=1
# that are supported by finos
LICENSES=" MIT  Apache-2.0 GPL-3.0 BSD-3-Clause  AGPL-3.0 GPL-2.0 ISC BSD-2-Clause LGPL-3.0 MPL-2.0 LGPL-2.1 0BSD  EPL-2.0   BSL-1.0"

# discarded licenses due to lack of support by finos:
# Unlicense
# CC0-1.0
# WTFPL
# MIT-0
# EUPL-1.2
# OFL-1.1
# Zlib

for license in $LICENSES
do
    echo "# $license"
    #ls licenses/$license.yaml
    grep "description: " licenses/$license.yaml | awk '{ printf "## %s\n", $0}'
done
