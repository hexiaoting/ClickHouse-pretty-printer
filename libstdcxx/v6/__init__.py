import gdb

# Load the xmethods if GDB supports them.
def gdb_has_xmethods():
    try:
        import gdb.xmethod
        return True
    except ImportError:
        return False

def register_libstdcxx_printers(obj):
    # Load the pretty-printers.
    from .printers import register_libstdcxx_printers
    register_libstdcxx_printers(obj)

    if gdb_has_xmethods():
        from .xmethods import register_libstdcxx_xmethods
        register_libstdcxx_xmethods(obj)
