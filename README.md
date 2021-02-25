Support pretty print STL and variables in ClickHouse

# 0. Prerequisite
To generate full debug info using clang, we should add option `-fno-limit-debug-info`. My cmake command:
```
$ git clone --recursive https://github.com/ClickHouse/ClickHouse.git
$ cd ClickHouse
$ mkdir build
$ cd build
$ cmake ../src/ -DENABLE_TESTS=0 -DCLICKHOUSE_SPLIT_BINARY=1 -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_FLAGS="-fno-limit-debug-info" -DCMAKE_CXX_COMPILER=clang++-10 -DCMAKE_C_COMPILER=clang-10 -DCMAKE_EXE_LINKER_FLAGS="-Wl,--dynamic-linker,/lib64/ld-linux-x86-64.so.2"
```
otherwise when gdb print types defined in Clickhouse shows:
```
(gdb) p col_array
$1 = (const DB::ColumnArray *) 0x7fff0527e100
(gdb) p *col_array
$2 = <incomplete type>
```

# 1. How to use it?
1. Install gdb and verify that it supports Python scripting (invoke `gdb --version` and check for `--with-python=...` lines).
2. Recompile `programs/clickhouse` to remove `-Wl,--gdb-index` options in the compile command.
3. `gdb-add-index programs/clickhouse` to generate .gdb_index section in ELF.
4. Create a `~/.gdbinit` file and copy file gdbinit content into it, or just `(gdb) source $DIR/gdbinit`

```
python
import sys
sys.path.insert(0, '/full/path/to/repo')
from printers import register_ch_printers
register_ch_printers()
end
```

Note: the .gdbinit file will make gdb register libcxx pretty printer, libcxx pretty printer  and ClickHouse pretty printer when gdb started.

5. Run gdb and type `info pretty-printer`. You should see something like that:

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


# 2. What does it do?

Adds some nice representation of ClickHouse's internal data structures in GDB. 

## 2.1 IAST
For example, when printing the `DB::IAST`'s contents, you can get the type of ast and the sql:
```
(gdb) p *ast                                                                                                           │           q
type=ASTSelectWithUnionQuery, sql="SELECT 1"
```
## 2.2 IColumn
When printing the `DB::Columnxxx`'s contents, instead of
```
(gdb) p *col_map
$10 = {<COWHelper<DB::IColumn, DB::ColumnMap>> = {<DB::IColumn> = {<COW<DB::IColumn>> = {<boost::sp_adl_block::intrusive_ref_counter<DB::IColumn, boost::sp_adl_block::thread_safe_counter>> = {m_ref_counter = {
            value_ = {<std::__1::__atomic_base<int, true>> = {<std::__1::__atomic_base<int, false>> = {__a_ = {<std::__1::__cxx_atomic_base_impl<int>> = {__a_value = 9}, <No data fields>},
                  static is_always_lock_free = <optimized out>}, <No data fields>}, <No data fields>}}}, <No data fields>}, _vptr$IColumn = 0x9f8fcd8 <vtable for DB::ColumnMap+16>}, <No data fields>}, nested = {
    value = {<boost::intrusive_ptr<DB::IColumn const>> = {px = 0x7fff30e9c200}, <No data fields>}}}
(gdb) p keys_data
$8 = (const DB::IColumn &) @0x7fff2985af30: {<COW<DB::IColumn>> = {<boost::sp_adl_block::intrusive_ref_counter<DB::IColumn, boost::sp_adl_block::thread_safe_counter>> = {m_ref_counter = {
        value_ = {<std::__1::__atomic_base<int, true>> = {<std::__1::__atomic_base<int, false>> = {__a_ = {<std::__1::__cxx_atomic_base_impl<int>> = {__a_value = 1}, <No data fields>},
              static is_always_lock_free = <optimized out>}, <No data fields>}, <No data fields>}}}, <No data fields>}, _vptr$IColumn = 0x9f925d0 <vtable for DB::ColumnVector<char8_t>+16>}
(gdb) p nested_column
$9 = (const DB::ColumnArray &) @0x7fff30e9c200: {<COWHelper<DB::IColumn, DB::ColumnArray>> = {<DB::IColumn> = {<COW<DB::IColumn>> = {<boost::sp_adl_block::intrusive_ref_counter<DB::IColumn, boost::sp_adl_block::thread_safe_counter>> = {
          m_ref_counter = {value_ = {<std::__1::__atomic_base<int, true>> = {<std::__1::__atomic_base<int, false>> = {__a_ = {<std::__1::__cxx_atomic_base_impl<int>> = {__a_value = 1}, <No data fields>},
                  static is_always_lock_free = <optimized out>}, <No data fields>}, <No data fields>}}}, <No data fields>}, _vptr$IColumn = 0x9f8b230 <vtable for DB::ColumnArray+16>}, <No data fields>}, data = {
    value = {<boost::intrusive_ptr<DB::IColumn const>> = {px = 0x7fff2d3148e0}, <No data fields>}}, offsets = {value = {<boost::intrusive_ptr<DB::IColumn const>> = {px = 0x7fff30e745c0}, <No data fields>}}}
(gdb)
```
you would see this:
```
(gdb) p *col_map
$5 = {<COWHelper<DB::IColumn, DB::ColumnMap>> = {<DB::IColumn> = type="Map(UInt8, Int32)", size=0., <No data fields>}, nested = {value = {<boost::intrusive_ptr<DB::IColumn const>> = {px = 0x7fff30e9c200}, <No data fields>}}}

(gdb) p nested_column
$6 = ColumnArray size=0
(gdb) p keys_data
$7 = type="UInt8", size=0.
```

## 2.3 IDataType
When printing the `DB::DataTypexxx`'s contents, instead of 
```
(gdb) p map_type
$1 = (const DB::DataTypeMap *) 0x7fff1a40d018
(gdb) p *map_type
$2 = {<DB::DataTypeWithSimpleSerialization> = {<DB::IDataType> = {<boost::noncopyable_::noncopyable> = {<boost::noncopyable_::base_token> = {<No data fields>}, <No data fields>},
      _vptr$IDataType = 0x9f50740 <vtable for DB::DataTypeMap+16>, custom_name = {__ptr_ = {<std::__1::__compressed_pair_elem<DB::IDataTypeCustomName const*, 0, false>> = {__value_ =
    0x0}, <std::__1::__compressed_pair_elem<std::__1::default_delete<DB::IDataTypeCustomName const>, 1, true>> = {<std::__1::default_delete<DB::IDataTypeCustomName const>> = {<No data fields>}, <No data fields>}, <No data fields>}},
      custom_text_serialization = {__ptr_ = {<std::__1::__compressed_pair_elem<DB::IDataTypeCustomTextSerialization const*, 0, false>> = {
            __value_ = 0x0}, <std::__1::__compressed_pair_elem<std::__1::default_delete<DB::IDataTypeCustomTextSerialization const>, 1, true>> = {<std::__1::default_delete<DB::IDataTypeCustomTextSerialization const>> = {<No data fields>}, <No data fields>}, <No data fields>}}, custom_streams = {__ptr_ = {<std::__1::__compressed_pair_elem<DB::IDataTypeCustomStreams const*, 0, false>> = {
            __value_ = 0x0}, <std::__1::__compressed_pair_elem<std::__1::default_delete<DB::IDataTypeCustomStreams const>, 1, true>> = {<std::__1::default_delete<DB::IDataTypeCustomStreams const>> = {<No data fields>}, <No data fields>}, <No data fields>}}}, <No data fields>}, key_type = {__ptr_ = 0x7ffff6477218, __cntrl_ = 0x7ffff6477200}, value_type = {__ptr_ = 0x7ffff6477258, __cntrl_ = 0x7ffff6477240}, nested = {__ptr_ = 0x7ffff61a7758, __cntrl_ = 0x7ffff61a7740},
  static is_parametric = true}
(gdb)
```
you would see this:
```
(gdb) source /home/hewenting/workspace/gdb/ClickHouse-pretty-printer/gdbinit
(gdb) p *map_type
$3 = {<DB::DataTypeWithSimpleSerialization> = {<DB::IDataType> = IDataType = "Map(UInt8,Int32)", <No data fields>}, key_type = std::shared_ptr (count 4, weak 0) = 0x7ffff6477218 => IDataType = "UInt8", value_type =
    std::shared_ptr (count 4, weak 0) = 0x7ffff6477258 => IDataType = "Int32", nested = std::shared_ptr (count 1, weak 0) = 0x7ffff61a7758 => IDataType = "Array(Tuple(keys UInt8, values Int32))", static is_parametric = true}
(gdb)
```

## 2.4 PaddedPODArray 
when printing the `DB::PaddedPODArray`'s contents, instead of

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
* You can write your own pretty printer for some clickhouse classes, If there is some difficuties, let me know(create an issue), I will help you.


<br>

# 3. Gdb useful commands related

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

(gdb) info vtbl ast
vtable for 'DB::IAST' @ 0xbecac50 (subobject @ 0x7fff30ea5458):
[0]: 0x1a3d5840 <DB::ASTSelectWithUnionQuery::~ASTSelectWithUnionQuery()>
[1]: 0x1daecb70 <DB::ASTSelectWithUnionQuery::~ASTSelectWithUnionQuery()>
[2]: 0x18fd17f0 <DB::IAST::appendColumnName(DB::WriteBuffer&) const>
[3]: 0x18fd18f0 <DB::IAST::appendColumnNameWithoutAlias(DB::WriteBuffer&) const>
[4]: 0x18fd19f0 <DB::IAST::getAliasOrColumnName() const>
[5]: 0x18fd1a20 <DB::IAST::tryGetAlias() const>
[6]: 0x18fd1a50 <DB::IAST::setAlias(std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > const&)>
[7]: 0x1daecbb0 <DB::ASTSelectWithUnionQuery::getID(char) const>
[8]: 0x1daec170 <DB::ASTSelectWithUnionQuery::clone() const>
[9]: 0x1db2bf50 <DB::IAST::updateTreeHashImpl(SipHash&) const>
[10]: 0x18fd1b40 <DB::IAST::collectIdentifierNames(std::__1::set<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >, std::__1::less<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > >, std::__1::allocator<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> > > >&) const>
[11]: 0x1dade2c0 <DB::ASTQueryWithOutput::formatImpl(DB::IAST::FormatSettings const&, DB::IAST::FormatState&, DB::IAST::FormatStateStacked) const>
(gdb)
```

<br>

# 4. links:
* https://github.com/ClickHouse/ClickHouse/issues/13601
* https://github.com/myrrc/clickhouse-devtools.git
* https://sourceware.org/gdb/current/onlinedocs/gdb/Python-API.html

