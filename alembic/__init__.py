from alembic import config, command, util
from optparse import OptionParser
import inspect
import os

__version__ = '0.1alpha'

def main(argv):

    # TODO: 
    # OK, what's the super option parser library that 
    # allows <command> plus command-specfic sub-options,
    # and derives everything from callables ?
    # we're inventing here a bit.
    
    commands = {}
    for fn in [getattr(command, n) for n in dir(command)]:
        if inspect.isfunction(fn) and \
            fn.__name__[0] != '_' and \
            fn.__module__ == 'alembic.command':
            
            spec = inspect.getargspec(fn)
            if spec[3]:
                positional = spec[0][1:-len(spec[3])]
                kwarg = spec[0][-len(spec[3]):]
            else:
                positional = spec[0][1:]
                kwarg = []
            
            commands[fn.__name__] = {
                'name':fn.__name__,
                'fn':fn,
                'positional':positional,
                'kwargs':kwarg
            }

    def format_cmd(cmd):
        return "%s %s" % (
            cmd['name'], 
            " ".join(["<%s>" % p for p in cmd['positional']])
        )
    
    def format_opt(cmd, padding=32):
        opt = format_cmd(cmd)
        return "  " + opt + \
                ((padding - len(opt)) * " ") + cmd['fn'].__doc__
        
    parser = OptionParser(
                "usage: %prog [options] <command> [command arguments]\n\n"
                "Available Commands:\n" +
                "\n".join(sorted([
                    format_opt(cmd)
                    for cmd in commands.values()
                ])) +
                "\n\n<revision> is a hex revision id or 'head'"
                )
                
    parser.add_option("-c", "--config", 
                        type="string", 
                        default="alembic.ini", 
                        help="Alternate config file")
    parser.add_option("-t", "--template",
                        default='generic',
                        type="string",
                        help="Setup template for use with 'init'")
    parser.add_option("-m", "--message",
                        type="string",
                        help="Message string to use with 'revision'")

    cmd_line_options, cmd_line_args = parser.parse_args(argv[1:])
    
    if len(cmd_line_args) < 1:
        util.err("no command specified")
    
    cmd = cmd_line_args.pop(0).replace('-', '_')
    
    try:
        cmd_fn = commands[cmd]
    except KeyError:
        util.err("no such command %r" % cmd)
        
    kw = dict(
        (k, getattr(cmd_line_options, k)) 
        for k in cmd_fn['kwargs']
    )
        
    if len(cmd_line_args) != len(cmd_fn['positional']):
        util.err("Usage: %s %s [options]" % (
                        os.path.basename(argv[0]), 
                        format_cmd(cmd_fn)
                    ))

    cfg = config.Config(cmd_line_options.config)
    cmd_fn['fn'](cfg, *cmd_line_args, **kw)



