Support pretty print STL and variables in ClickHouse

# How to use it?
1. Install gdb and verify that it supports Python scripting (invoke `gdb --version` and check for `--with-python=...` lines).
2. Create a `~/.gdbinit` file and put these lines in it, or just `mv gdbinit ~/.gdbinit`

```
python
import sys
sys.path.insert(0, '/full/path/to/repo')
from printers import register_ch_printers
register_ch_printers()
end
```

Note: the .gdbinit file will make gdb register libcxx pretty printer, libcxx pretty printer  and ClickHouse pretty printer when gdb started.

3. Run gdb and type `info pretty-printer`. You should see something like that:

```
(gdb) info pretty-printer 
global pretty-printers:
  ...
  clickhouse
    PODArray
    ...
  libstdc++-v6
    ...
```

<br>


# What does it do?

Adds some nice representation of ClickHouse's internal data structures in GDB. 

For example, when printing the `DB::PaddedPODArray`'s contents, instead of

```
$1 = (DB::PaddedPODArray<DB::ArrayIndexNumImpl<unsigned long, unsigned long, DB::Index
ToOne, false>::ResultType> &) @0x7ffff7847030: {<DB::PODArrayBase<1, 4096, Allocator<f711 alse, false>, 15, 16>> = {
<boost::noncopyable_::noncopyable> = {<boost::noncopyable_:: base_token> = {<No data fields>}, <No data fields>}, 
<Allocator<false, false>> = {stat713 ic clear_memory = false, static mmap_flags = 34}, static pad_right = 15, 
static pad_left = 16, static null = <optimized out>, c_start = 0x7ffff78a5c10 "", 
c_end = 0x7ffff78a5c42 '\245' <repeats 62 times>, 'Z' <repeats 128 times>, "\202\031", 
c_end_of_storage= 0x7ffff78a5c71 '\245' <repeats 15 times>, 'Z' <repeats 128 times>, "\202\031", 
mprotected = false}, <No data fields>}    
```
you would see this:

```
$1 = DB::PaddedPODArray<DB::ArrayIndexNumImpl<unsigned
long, unsigned long, DB::IndexToOne, false> of length 50, capacity 97 = 
{0 '\000', 0 '\000', 0
'\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000
', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0
'\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000
', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0
'\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000
', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0
'\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000
', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0 '\000', 0
'\000', 0 '\000', 0 '\000', 0 '\000'}
```



Note: 
* You can write your own pretty printer for some clickhouse classes
* If you want to know an IAST's real type, use `info vtbl ast` (here ast is an IAST type var)


<br>

# gdb python print symbol

```
(gdb) info pretty-printer
...........
(gdb) python
>import gdb
>sn=gdb.selected_frame()
>symbol_table_adn_line=sn.find_sal()
>symtab=symbol_table_adn_line.symtab
>print(symtab.filename, symtab.objfile)
>global_block=symtab.global_block()
>super_block=global_block.superblock
>print(global_block, super_block, global_block.is_global)
>
>### get each symbol in the block
>for sym in global_block:
>    if "ColumnArray" in sym.name:
>        print(sym.name, "     ##########     " , sym.symtab)
>end
```

<br>

# links:
* https://github.com/ClickHouse/ClickHouse/issues/13601
* https://github.com/myrrc/clickhouse-devtools.git
* https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html

