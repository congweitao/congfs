#include "fault-inject.h"

#include <linux/version.h>

#if defined(CONGFS_DEBUG) && defined(CONFIG_FAULT_INJECTION)

static struct dentry* debug_dir;
static struct dentry* fault_dir;

#define CONGFS_DECLARE_FAULT_ATTR(name) DECLARE_FAULT_ATTR(congfs_fault_ ## name)

CONGFS_DECLARE_FAULT_ATTR(readpage);
CONGFS_DECLARE_FAULT_ATTR(writepage);

CONGFS_DECLARE_FAULT_ATTR(write_force_cache_bypass);
CONGFS_DECLARE_FAULT_ATTR(read_force_cache_bypass);

CONGFS_DECLARE_FAULT_ATTR(commkit_sendheader_timeout);
CONGFS_DECLARE_FAULT_ATTR(commkit_polltimeout);
CONGFS_DECLARE_FAULT_ATTR(commkit_recvheader_timeout);

CONGFS_DECLARE_FAULT_ATTR(commkit_readfile_receive_timeout);
CONGFS_DECLARE_FAULT_ATTR(commkit_writefile_senddata_timeout);

#define INIT_FAULT(name) \
   if(IS_ERR(fault_create_debugfs_attr(#name, fault_dir, &congfs_fault_ ## name))) \
      goto err_fault_dir;

#ifndef KERNEL_HAS_FAULTATTR_DNAME
#define DESTROY_FAULT(name) do { } while (0)
#else
#define DESTROY_FAULT(name) \
   do { \
      if((congfs_fault_ ## name).dname) \
         dput( (congfs_fault_ ## name).dname); \
   } while (0)
#endif

bool congfs_fault_inject_init()
{
   debug_dir = debugfs_create_dir(CONGFS_MODULE_NAME_STR, NULL);
   if(!debug_dir)
      goto err_debug_dir;

   fault_dir = debugfs_create_dir("fault", debug_dir);
   if(!fault_dir)
      goto err_fault_dir;

   INIT_FAULT(readpage);
   INIT_FAULT(writepage);

   INIT_FAULT(write_force_cache_bypass);
   INIT_FAULT(read_force_cache_bypass);

   INIT_FAULT(commkit_sendheader_timeout);
   INIT_FAULT(commkit_polltimeout);
   INIT_FAULT(commkit_recvheader_timeout);

   INIT_FAULT(commkit_readfile_receive_timeout);
   INIT_FAULT(commkit_writefile_senddata_timeout);

   return true;

err_fault_dir:
   debugfs_remove_recursive(debug_dir);
   debug_dir = NULL;
err_debug_dir:
   return false;
}

void congfs_fault_inject_release()
{
   DESTROY_FAULT(readpage);
   DESTROY_FAULT(writepage);

   DESTROY_FAULT(write_force_cache_bypass);
   DESTROY_FAULT(read_force_cache_bypass);

   DESTROY_FAULT(commkit_sendheader_timeout);
   DESTROY_FAULT(commkit_polltimeout);
   DESTROY_FAULT(commkit_recvheader_timeout);

   DESTROY_FAULT(commkit_readfile_receive_timeout);
   DESTROY_FAULT(commkit_writefile_senddata_timeout);

   debugfs_remove_recursive(debug_dir);
}

#endif
