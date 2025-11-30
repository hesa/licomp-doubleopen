#!/bin/env python3

# SPDX-FileCopyrightText: 2025 Henrik Sandklef
#
# SPDX-License-Identifier: GPL-3.0-or-later

from licomp_doubleopen.doubleopen import LicompDoubleOpen
from matrix.licenses import LICENSES
from licomp_reclicense.reclicense import LicompReclicense

lr = LicompReclicense()
do = LicompDoubleOpen()
from licomp.interface import Licomp
from licomp.interface import Provisioning
from licomp.interface import UseCase



def checker(outbound, inbound):
    do_ret = lr.outbound_inbound_compatibility(outbound,
                                               inbound)["compatibility_status"]
    lr_ret = lr.outbound_inbound_compatibility(outbound,
                                               inbound)["compatibility_status"]
    same = (do_ret == lr_ret)
    return same, do_ret

for outbound in LICENSES:
    for inbound in LICENSES:
        same, ret = checker(outbound, inbound)
        print(f'{outbound} <--- {inbound} compat: {ret} same:{same} ')

