# TODO(jez) Figure out what to do about this warning:
#
#    error: There is a .lldbinit file in the current directory which is not being read.
#    To silence this warning without sourcing in the local .lldbinit,
#    add the following to the lldbinit file in your home directory:
#        settings set target.load-cwd-lldbinit false
#    To allow lldb to source .lldbinit files in the current working directory,
#    set the value of this variable to true.  Only do so if you understand and
#    accept the security risk.
#
# Options for now:
#
#    lldb --local-lldbinit <normal lldb args...>
#    command script import lldbinit.py
#    co sc i lldbinit.py

if __name__ == "__main__":
    print("Run only as script from LLDB... Not as standalone program!")

try:
    import lldb
except:
    pass

import re
import os

# Bazel builds all binaries from a username-specific cache location
# for lldb to work properly we need to map that path back to our main source
project_root = os.path.dirname(os.path.realpath(__file__))
bazel_workspace = os.path.realpath(os.path.join(project_root, "bazel-sorbet"))

if not(os.path.isdir(bazel_workspace)):
    print("You need to compile Sorbet first before loading this file")
else:
    print("(lldb) Mapping paths in ./bazel-sorbet to the project root")
    source_map_command = 'settings set -- target.source-map "%s" "%s"' % (bazel_workspace, project_root)
    ci = lldb.debugger.GetCommandInterpreter()
    res = lldb.SBCommandReturnObject()
    ci.HandleCommand(source_map_command, res)


def __lldb_init_module(debugger, internal_dict):
    result = lldb.SBCommandReturnObject()
    ci = debugger.GetCommandInterpreter()
    ci.HandleCommand("command script add -f lldbinit.cmd_bazelsourcemap bazelsourcemap", result)

    cyan="\x1b[0;36m"
    cnone="\x1b[0m"

    print("(lldb) Run %srubysourcemap%s to set up Ruby source maps" % (cyan, cnone))
    print("(lldb) Run %sbazelsourcemap%s to set up LLVM source maps" % (cyan, cnone))
    print("(lldb) Run %srubystack%s to dump the ruby stack" % (cyan, cnone))


def cmd_bazelsourcemap(debugger, command, result, dict):
    ci = debugger.GetCommandInterpreter()

    external_path = ('%s/bazel-sorbet/external' % project_root)
    # TODO(jez) This hardcodes /proc/self/cwd to get it to work on the buildbox.
    # We should probably do something like the `list main` trick for rubysourcemap to make this more portable.
    source_map_command = 'settings set -- target.source-map /proc/self/cwd/external %s' % external_path
    print('(lldb) %s' % source_map_command)
    ci.HandleCommand(source_map_command, result)

