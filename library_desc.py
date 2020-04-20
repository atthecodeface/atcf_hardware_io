import cdl_desc
from cdl_desc import CdlModule, CModel

class Library(cdl_desc.Library):
    name = "io"
    pass

class IOModules(cdl_desc.Modules):
    name = "io"
    c_src_dir   = "cmodel"
    src_dir     = "cdl"
    tb_src_dir  = "tb_cdl"
    include_dir = "cdl"
    libraries = {"std": True, "utils":True, }
    export_dirs = [ src_dir, include_dir ]
    modules = []
    modules += [ CdlModule("apb_logging") ]
    modules += [ CdlModule("apb_target_dprintf_uart")]
    modules += [ CdlModule("apb_target_ps2_host")]
    modules += [ CdlModule("apb_target_uart_minimal")]
    modules += [ CdlModule("i2c_interface")]
    modules += [ CdlModule("i2c_master")]
    modules += [ CdlModule("i2c_slave")]
    modules += [ CdlModule("i2c_slave_apb_master")]
    modules += [ CdlModule("led_seven_segment")]
    modules += [ CdlModule("led_ws2812_chain")]
    modules += [ CdlModule("ps2_host")]
    modules += [ CdlModule("ps2_host_keyboard")]
    modules += [ CdlModule("uart_minimal")]
    pass
