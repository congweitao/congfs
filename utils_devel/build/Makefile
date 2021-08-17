CONGFS_EVENT_LISTENER_PATH ?= ../../event_listener

ifneq ($(CONGFS_VERSION),)
CONGFS_EXTRA_FLAGS += 'CONGFS_VERSION="$(CONGFS_VERSION)"'
endif

ifneq ($(CONGFS_DEBUG),)
CONGFS_EXTRA_FLAGS += 'CONGFS_DEBUG=$(CONGFS_DEBUG)'
endif


all:

clean:

help:
	@echo 'Optional Arguments:'
	@echo '   CONGFS_DEBUG=1:'
	@echo '	     Enables debug information and symbols.'
	@echo '   CXX=<compiler>:'
	@echo '      Specifies a c++ compiler.'
	@echo '   CONGFS_COMMON_PATH=<path>:'
	@echo '      Path to the common directory.'
	@echo
	@echo 'Targets:'
	@echo '   all (default)     - build only'
	@echo '   help              - print this help message'


# Include dependency files
ifneq ($(DEPENDENCY_FILES),)
include $(DEPENDENCY_FILES)
endif

