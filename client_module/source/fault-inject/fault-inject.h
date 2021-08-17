#ifndef _fault_inject_fault_inject_h_dBK5RbRnOrGDnIW5Y7zvnv
#define _fault_inject_fault_inject_h_dBK5RbRnOrGDnIW5Y7zvnv

#include <linux/types.h>

#if defined(CONGFS_DEBUG) && defined(CONFIG_FAULT_INJECTION)

#include <linux/fault-inject.h>

#ifndef CONFIG_DEBUG_FS
#error debugfs required for congfs fault injection
#endif
#ifndef CONFIG_FAULT_INJECTION_DEBUG_FS
#error CONFIG_FAULT_INJECTION_DEBUG_FS required for congfs fault injection
#endif

#define CONGFS_SHOULD_FAIL(name, size) should_fail(&congfs_fault_ ## name, size)
#define CONGFS_DEFINE_FAULT(name) extern struct fault_attr congfs_fault_ ## name

CONGFS_DEFINE_FAULT(readpage);
CONGFS_DEFINE_FAULT(writepage);

CONGFS_DEFINE_FAULT(write_force_cache_bypass);
CONGFS_DEFINE_FAULT(read_force_cache_bypass);

CONGFS_DEFINE_FAULT(commkit_sendheader_timeout);
CONGFS_DEFINE_FAULT(commkit_polltimeout);
CONGFS_DEFINE_FAULT(commkit_recvheader_timeout);

CONGFS_DEFINE_FAULT(commkit_readfile_receive_timeout);
CONGFS_DEFINE_FAULT(commkit_writefile_senddata_timeout);

extern bool congfs_fault_inject_init(void);
extern void congfs_fault_inject_release(void);

#else // CONGFS_DEBUG

#define CONGFS_SHOULD_FAIL(name, size) (false)

static inline bool congfs_fault_inject_init(void)
{
   return true;
}

static inline void congfs_fault_inject_release(void)
{
}

#endif // CONGFS_DEBUG

#endif
