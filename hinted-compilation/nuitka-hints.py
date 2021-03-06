#     Copyright 2019, Jorj McKie, mailto:<jorj.x.mckie@outlook.de>
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" This script invokes the Nuitka compiler.

Any option for the Nuitka command line can be entered as an item in list
'my_opts'. This can be used to create "canned" standard compilation profiles
and to limit the command line length.

This special version performs standalone compilations and serves as an invoker
for the user plugin "hinted-mods.py". This plugin controls the inclusion of
modules in the distribution folder.
"""
import json
import os
import platform
import sys

from nuitka.__main__ import main
from nuitka.Version import getNuitkaVersion

nuitka_vsn = getNuitkaVersion()
if not nuitka_vsn >= "0.6.6":
    sys.exit("This needs Nuitka version 0.6.6 or higher.")
python_vsn = sys.version.split()[0]
this_dir = os.path.dirname(os.path.abspath(__file__))
hinted_mods_fn = os.path.join(this_dir, "hinted-mods.py")
if not os.path.exists(hinted_mods_fn):
    sys.exit("no such file: " + hinted_mods_fn)

my_opts = [
    "--standalone",  # the purpose of this script
    "--remove-output",  # delete this if you want
    "--recurse-none",  # exclude everything
]

script = sys.argv[-1]  # name of script to be compiled
if not os.path.exists(script):
    sys.exit("No such file: " + script)

filename, extname = os.path.splitext(script)
json_fname = "%s-%i%i-%s-%i.json" % (
    filename,
    sys.version_info.major,
    sys.version_info.minor,
    sys.platform,
    64 if sys.maxsize > 2 ** 32 else 32,
)

if extname.lower() == ".pyw":
    my_opts.append("--windows-disable-console")

if not os.path.exists(json_fname):
    print("File '%s' is needed for this Nuitka compilation." % json_fname)
    print("Create it by executing 'python get-hints.py %s'" % script)
    sys.exit(1)

# invoke user plugin to work with the JSON file
user_plugin = "--user-plugin=%s=%s" % (hinted_mods_fn, json_fname)
my_opts.append(user_plugin)

# now build a new sys.argv array
new_sysargs = [sys.argv[0]]
for o in my_opts:
    new_sysargs.append(o)

new_sysargs.extend(sys.argv[1:])

sys.argv = new_sysargs

# keep user happy with some type of protocol
print(
    "NUITKA v%s on Python %s (%s) is compiling '%s' with these options:"
    % (nuitka_vsn, python_vsn, sys.platform, sys.argv[-1])
)
for o in sys.argv[1:-1]:
    if "hinted-mods.py" not in o:
        print(" " + o)
print()

main()
