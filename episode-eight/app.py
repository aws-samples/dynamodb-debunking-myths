#!/usr/bin/env python3
import os

import aws_cdk as cdk

from ddb_permissions_lab.ddb_permissions_lab_stack import DdbPermissionsLabStack


app = cdk.App()
DdbPermissionsLabStack(app, "DdbPermissionsLabStack")
app.synth()
