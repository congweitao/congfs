#!/bin/bash

set -e

CFLAGS="-D__KERNEL__ $LINUXINCLUDE $KBUILD_CFLAGS $KBUILD_CPPFLAGS -DKBUILD_BASENAME=\"congfs\" -DKBUILD_MODNAME=\"congfs\""

_generate_includes() {
   for i in "$@"; do
      echo "#include <$i>"
   done
}

_marker_if_compiles() {
   local marker=$1
   shift

   if $CC $CFLAGS -x c -o /dev/null -c - 2>/dev/null
   then
      echo -D$marker
   fi
}

_check_struct_field_input() {
   local field=$1
   shift 1

   _generate_includes "$@"

   cat <<EOF
void want_symbol(void) {
   struct ${field%%::*} s;
   (void) (s.${field##*::});
}
EOF
}

check_struct_field() {
   local field=$1
   local marker=$2
   shift 2

   _check_struct_field_input "$field" "$@" | _marker_if_compiles "$marker"
}

_check_struct_field_type_input() {
   local field=$1
   local ftype=$2
   shift 2

   _generate_includes "$@"

   cat <<EOF
void want_symbol(void) {
   struct ${field%%::*} s;
   char predicate[
      2 * __builtin_types_compatible_p(__typeof(s.${field##*::}), $ftype) - 1
   ];
}
EOF
}

check_struct_field_type() {
   local field=$1
   local ftype=$2
   local marker=$3
   shift 3

   _check_struct_field_type_input "$field" "$ftype" "$@" | _marker_if_compiles "$marker"
}

_check_function_input() {
   local name=$1
   local signature=$2
   shift 2

   _generate_includes "$@"
   cat <<EOF
void want_fn(void) {
   char predicate[
      2 * __builtin_types_compatible_p(__typeof($name), $signature) - 1
   ];
}
EOF
}

_check_symbol() {
   local name=$1
   shift

   _generate_includes "$@"
   cat <<EOF
   __typeof__($name) predicate = $name;
EOF
}

check_function() {
   local name=$1
   local signature=$2
   local marker=$3
   shift 3

   _check_function_input "$name" "$signature" "$@" | _marker_if_compiles "$marker"
}

check_header() {
   local header=$1
   local marker=$2
   shift 2

   _generate_includes "$header" | _marker_if_compiles "$marker"
}

check_symbol() {
   local name=$1
   local marker=$2
   shift 2

   _check_symbol "$name" "$@" | _marker_if_compiles "$marker"
}

check_function \
   generic_readlink "int (struct dentry *, char __user *, int)" \
   KERNEL_HAS_GENERIC_READLINK \
   linux/fs.h

check_header \
   linux/sched/signal.h \
   KERNEL_HAS_SCHED_SIG_H

# cryptohash does not include linux/types.h, so the type comparison fails
check_function \
   half_md4_transform "__u32 (__u32[4], __u32 const in[8])" \
   KERNEL_HAS_HALF_MD4_TRANSFORM \
   linux/types.h linux/cryptohash.h

check_function \
   vfs_getattr "int (const struct path *, struct kstat *, u32, unsigned int)" \
   KERNEL_HAS_STATX \
   linux/fs.h

check_function \
   kref_read "unsigned int (const struct kref*)" \
   KERNEL_HAS_KREF_READ \
   linux/kref.h

check_function \
   file_dentry "struct dentry* (const struct file *file)" \
   KERNEL_HAS_FILE_DENTRY \
   linux/fs.h

check_function \
   super_setup_bdi_name "int (struct super_block *sb, char *fmt, ...)" \
   KERNEL_HAS_SUPER_SETUP_BDI_NAME \
   linux/fs.h

check_function \
   have_submounts "int (struct dentry *parent)" \
   KERNEL_HAS_HAVE_SUBMOUNTS \
   linux/dcache.h

check_function \
   kernel_read "ssize_t (struct file *, void *, size_t, loff_t *)" \
   KERNEL_HAS_KERNEL_READ \
   linux/fs.h

check_function \
   skwq_has_sleeper "bool (struct socket_wq*)" \
   KERNEL_HAS_SKWQ_HAS_SLEEPER \
   net/sock.h

check_struct_field_type \
   sock::sk_data_ready "void (*)(struct sock*, int)" \
   KERNEL_HAS_SK_DATA_READY_2 \
   net/sock.h

check_struct_field \
   sock::sk_sleep \
   KERNEL_HAS_SK_SLEEP \
   net/sock.h

check_function \
   sk_has_sleeper "int (struct sock*)" \
   KERNEL_HAS_SK_HAS_SLEEPER \
   net/sock.h

check_function \
   __wake_up_sync_key "void (struct wait_queue_head* , unsigned int, void*)" \
   KERNEL_WAKE_UP_SYNC_KEY_HAS_3_ARGUMENTS \
   linux/wait.h

# we have to communicate with the calling makefile somehow. since we can't really use the return
# code of this script, we'll echo a special string at the end of our output for the caller to
# detect and remove again.
# this string has to be something that will, on its own, never be a valid compiler option. so let's
# choose something really, really unlikely like
echo "--~~success~~--"
