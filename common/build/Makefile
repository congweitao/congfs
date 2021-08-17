include ../../build/Makefile


$(call build-static-library,\
   congfs-common,\
   $(shell find ../source -iname '*.cpp'),\
   dl,\
   ../source)

$(call build-shared-library,\
   congfs_ib,\
   $(shell find ../ib_lib -iname '*.cpp'),\
   rdma,\
   ../source ../ib_lib)


$(call build-test,\
   test-runner,\
   $(shell find ../tests -name '*.cpp'),\
   common,\
   ../tests)
