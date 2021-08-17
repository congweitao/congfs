#ifndef __CONGFS_IOCTL_H__
#define __CONGFS_IOCTL_H__

#include <stdint.h>
#include <sys/ioctl.h>
#include <sys/types.h>


#define CONGFS_IOCTL_CFG_MAX_PATH 4096 // max path length for config file
#define CONGFS_IOCTL_TEST_STRING  "_FhGFS_" /* copied to user space by CONGFS_IOC_TEST_IS_CONGFS to
                                 to confirm an FhGFS/ConGFS mount */
#define CONGFS_IOCTL_TEST_BUFLEN  6 /* note: char[6] is actually the wrong size for the
                                 CONGFS_IOCTL_TEST_STRING that is exchanged, but that is no problem
                                 in this particular case and so we keep it for compatibility */
#define CONGFS_IOCTL_MOUNTID_BUFLEN     256
#define CONGFS_IOCTL_NODESTRID_BUFLEN   256
#define CONGFS_IOCTL_FILENAME_MAXLEN    256 // max supported filename len (incl terminating zero)

// entryID string is made of three 32 bit values in hexadecimal form plus two dashes
// (see common/toolkit/StorageTk.h)
#define CONGFS_IOCTL_ENTRYID_MAXLEN     26


// stripe pattern types
#define CONGFS_STRIPEPATTERN_INVALID      0
#define CONGFS_STRIPEPATTERN_RAID0        1
#define CONGFS_STRIPEPATTERN_RAID10       2
#define CONGFS_STRIPEPATTERN_BUDDYMIRROR  3


/*
 * General notes on ioctls:
 * - the _IOR() macro is for ioctls that read information, _IOW refers to ioctls that write or make
 *    modifications (e.g. file creation).
 *
 * - _IOR(type, number, data_type) meanings:
 *    - note: _IOR() encodes all three values (type, number, data_type size) into the request number
 *    - type: 8 bit driver-specific number to identify the driver if there are multiple drivers
 *       listening to the same fd (e.g. such as the TCP and IP layers).
 *    - number: 8 bit integer command number, so different numbers for different routines.
 *    - data_type: the data type (size) to be exchanged with the driver (though this number can
 *       also rather be seen as a command number subversion, because the actual number given here is
 *       not really exchanged unless the drivers' ioctl handler explicity does the exchange).
 */

#define CONGFS_IOCTYPE_ID                     'f'


#define CONGFS_IOCNUM_GET_CFG_FILE            20
#define CONGFS_IOCNUM_CREATE_FILE             21
#define CONGFS_IOCNUM_TEST_IS_CONGFS          22
#define CONGFS_IOCNUM_GET_RUNTIME_CFG_FILE    23
#define CONGFS_IOCNUM_GET_MOUNTID             24
#define CONGFS_IOCNUM_GET_STRIPEINFO          25
#define CONGFS_IOCNUM_GET_STRIPETARGET        26
#define CONGFS_IOCNUM_MKFILE_STRIPEHINTS      27
#define CONGFS_IOCNUM_CREATE_FILE_V2          28
#define CONGFS_IOCNUM_CREATE_FILE_V3          29
#define CONGFS_IOCNUM_GETINODEID              30
#define CONGFS_IOCNUM_GETENTRYINFO            31


#define CONGFS_IOC_GET_CFG_FILE   _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GET_CFG_FILE, struct BeegfsIoctl_GetCfgFile_Arg)
#define CONGFS_IOC_CREATE_FILE    _IOW( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_CREATE_FILE, struct BeegfsIoctl_MkFile_Arg)
#define CONGFS_IOC_CREATE_FILE_V2  _IOW( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_CREATE_FILE_V2, struct BeegfsIoctl_MkFileV2_Arg)
#define CONGFS_IOC_CREATE_FILE_V3  _IOW( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_CREATE_FILE_V3, struct BeegfsIoctl_MkFileV3_Arg)
#define CONGFS_IOC_TEST_IS_CONGFS  _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_TEST_IS_CONGFS, char[CONGFS_IOCTL_TEST_BUFLEN])
#define CONGFS_IOC_GET_RUNTIME_CFG_FILE    _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GET_RUNTIME_CFG_FILE, struct BeegfsIoctl_GetCfgFile_Arg)
#define CONGFS_IOC_GET_MOUNTID    _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GET_MOUNTID, char[CONGFS_IOCTL_MOUNTID_BUFLEN])
#define CONGFS_IOC_GET_STRIPEINFO          _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GET_STRIPEINFO, struct BeegfsIoctl_GetStripeInfo_Arg)
#define CONGFS_IOC_GET_STRIPETARGET        _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GET_STRIPETARGET, struct BeegfsIoctl_GetStripeTarget_Arg)
#define CONGFS_IOC_GET_STRIPETARGET_V2     _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GET_STRIPETARGET, struct BeegfsIoctl_GetStripeTargetV2_Arg)
#define CONGFS_IOC_MKFILE_STRIPEHINTS      _IOW( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_MKFILE_STRIPEHINTS, \
      struct BeegfsIoctl_MkFileWithStripeHints_Arg)
#define CONGFS_IOC_GETINODEID             _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GETINODEID, struct BeegfsIoctl_GetInodeID_Arg)
#define CONGFS_IOC_GETENTRYINFO             _IOR( \
   CONGFS_IOCTYPE_ID, CONGFS_IOCNUM_GETENTRYINFO, struct BeegfsIoctl_GetEntryInfo_Arg)


/* used to return the client config file name using an ioctl */
struct BeegfsIoctl_GetCfgFile_Arg
{
      char path[CONGFS_IOCTL_CFG_MAX_PATH]; // (out-value) where the result path will be stored
      int length;                          /* (in-value) length of path buffer (unused, because it's
                                              after a fixed-size path buffer anyways) */
};

/* used to pass information for file creation */
struct BeegfsIoctl_MkFile_Arg
{
   uint16_t ownerNodeID; // owner node of the parent dir

   const char* parentParentEntryID; // entryID of the parent of the parent (=> the grandparentID)
   int parentParentEntryIDLen;

   const char* parentEntryID; // entryID of the parent
   int parentEntryIDLen;

   const char* parentName;   // name of parent dir
   int parentNameLen;

   // file information
   const char* entryName; // file name we want to create
   int entryNameLen;
   int fileType; // see linux/fs.h or man 3 readdir, DT_UNKNOWN, DT_FIFO, ...

   const char* symlinkTo;  // Only must be set for symlinks.
                           // The name a symlink is supposed to point to
   int symlinkToLen; // Length of the symlink name

   int mode; // mode (permission) of the new file

   // user ID and group only will be used, if the current user is root
   uid_t uid; // user ID
   gid_t gid; // group ID

   int numTargets;     // number of targets in prefTargets array (without final 0 element)
   uint16_t* prefTargets;  // array of preferred targets (additional last element must be 0)
   int prefTargetsLen; // raw byte length of prefTargets array (including final 0 element)
};

struct BeegfsIoctl_MkFileV2_Arg
{
   uint32_t ownerNodeID; // owner node/group of the parent dir

   const char* parentParentEntryID; // entryID of the parent of the parent (=> the grandparentID)
   int parentParentEntryIDLen;

   const char* parentEntryID; // entryID of the parent
   int parentEntryIDLen;
   int parentIsBuddyMirrored;

   const char* parentName;   // name of parent dir
   int parentNameLen;

   // file information
   const char* entryName; // file name we want to create
   int entryNameLen;
   int fileType; // see linux/fs.h or man 3 readdir, DT_UNKNOWN, DT_FIFO, ...

   const char* symlinkTo;  // Only must be set for symlinks.
                           // The name a symlink is supposed to point to
   int symlinkToLen; // Length of the symlink name

   int mode; // mode (permission) of the new file

   // user ID and group only will be used, if the current user is root
   uid_t uid; // user ID
   gid_t gid; // group ID

   int numTargets;     // number of targets in prefTargets array (without final 0 element)
   uint16_t* prefTargets;  // array of preferred targets (additional last element must be 0)
   int prefTargetsLen; // raw byte length of prefTargets array (including final 0 element)
};

struct BeegfsIoctl_MkFileV3_Arg
{
   uint32_t ownerNodeID; // owner node/group of the parent dir

   const char* parentParentEntryID; // entryID of the parent of the parent (=> the grandparentID)
   int parentParentEntryIDLen;

   const char* parentEntryID; // entryID of the parent
   int parentEntryIDLen;
   int parentIsBuddyMirrored;

   const char* parentName;   // name of parent dir
   int parentNameLen;

   // file information
   const char* entryName; // file name we want to create
   int entryNameLen;
   int fileType; // see linux/fs.h or man 3 readdir, DT_UNKNOWN, DT_FIFO, ...

   const char* symlinkTo;  // Only must be set for symlinks. The name a symlink is supposed to point to
   int symlinkToLen; // Length of the symlink name

   int mode; // mode (permission) of the new file

   // user ID and group only will be used, if the current user is root
   uid_t uid; // user ID
   gid_t gid; // group ID

   int numTargets;     // number of targets in prefTargets array (without final 0 element)
   uint16_t* prefTargets;  // array of preferred targets (additional last element must be 0)
   int prefTargetsLen; // raw byte length of prefTargets array (including final 0 element)
   uint16_t storagePoolId; // if set, this overrides the settings of the parent dir
};


/* uset to get the stripe info of a file */
struct BeegfsIoctl_GetStripeInfo_Arg
{
   unsigned outPatternType; // (out-value) stripe pattern type (STRIPEPATTERN_...)
   unsigned outChunkSize; // (out-value) chunksize for striping
   uint16_t outNumTargets; // (out-value) number of stripe targets of given file
};

/* uset to get the stripe target of a file */
struct BeegfsIoctl_GetStripeTarget_Arg
{
   uint16_t targetIndex; // index of the target that should be queried (0-based)

   uint16_t outTargetNumID; // (out-value) numeric ID of target with given index
   uint16_t outNodeNumID; // (out-value) numeric ID of node to which this target is mapped
   char outNodeStrID[CONGFS_IOCTL_NODESTRID_BUFLEN]; /* (out-value) string ID of node to which this
                                                       target is mapped */
};

struct BeegfsIoctl_GetStripeTargetV2_Arg
{
   /* inputs */
   uint32_t targetIndex;

   /* outputs */
   uint32_t targetOrGroup; // target ID if the file is not buddy mirrored, otherwise mirror group ID

   uint32_t primaryTarget; // target ID != 0 if buddy mirrored
   uint32_t secondaryTarget; // target ID != 0 if buddy mirrored

   uint32_t primaryNodeID; // node ID of target (if unmirrored) or primary target (if mirrored)
   uint32_t secondaryNodeID; // node ID of secondary target, or 0 if unmirrored

   char primaryNodeStrID[CONGFS_IOCTL_NODESTRID_BUFLEN];
   char secondaryNodeStrID[CONGFS_IOCTL_NODESTRID_BUFLEN];
};

/* used to pass information for file creation with stripe hints */
struct BeegfsIoctl_MkFileWithStripeHints_Arg
{
   const char* filename; // file name we want to create
   unsigned mode; // mode (access permission) of the new file

   unsigned numtargets; // number of desired stripe targets, 0 for directory default
   unsigned chunksize; // in bytes, must be 2^n >= 64Ki, 0 for directory default
};

struct BeegfsIoctl_GetInodeID_Arg
{
   // input
   char entryID[CONGFS_IOCTL_ENTRYID_MAXLEN + 1];

   // output
   uint64_t inodeID;

};

struct BeegfsIoctl_GetEntryInfo_Arg
{
   uint32_t ownerID;
   char parentEntryID[CONGFS_IOCTL_ENTRYID_MAXLEN + 1];
   char entryID[CONGFS_IOCTL_ENTRYID_MAXLEN + 1];
   int entryType;
   int featureFlags;
};


#include <congfs/congfs_ioctl_functions.h>


#endif /* __CONGFS_IOCTL_H__ */
