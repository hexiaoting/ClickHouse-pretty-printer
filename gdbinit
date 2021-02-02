handle SIGUSR1 noprint nostop

python
import sys
# libcxx
sys.path.insert(0, '{ClickHouse-pretty-printer-dir}')
from libcxx.v1.printers import register_libcxx_printers 
register_libcxx_printers(None) 

# libstdcpp
from libstdcxx.v6.printers import register_libstdcxx_printers
register_libstdcxx_printers (None)

# clickhouse pretty printer
sys.path.insert(0, '{ClickHouse-pretty-printer-dir/clickhouse}')
from printers import register_ch_printers
register_ch_printers()
end
