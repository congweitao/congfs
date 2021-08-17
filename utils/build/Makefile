include ../../build/Makefile

TARGETS = ctl fsck java_lib event_listener

all: $(TARGETS)

export CONGFS_COMMON_PATH
export CONGFS_THIRDPARTY_PATH
export CONGFS_EVENT_LISTENER_PATH
export CONGFS_VERSION
export CONGFS_DEBUG

ctl:
	$(MAKE) -C $(CONGFS_ONLINE_CFG_PATH)/build
	cp $(CONGFS_ONLINE_CFG_PATH)/build/congfs-ctl .
	
fsck:
	$(MAKE) -C $(CONGFS_FSCK_PATH)/build
	cp $(CONGFS_FSCK_PATH)/build/congfs-fsck .

java_lib:
	$(MAKE) -C $(CONGFS_JAVA_LIB_PATH)/build
	cp $(CONGFS_JAVA_LIB_PATH)/build/libjcongfs.so $(CONGFS_JAVA_LIB_PATH)/build/jcongfs.jar .

event_listener:
	$(MAKE) -C $(CONGFS_EVENT_LISTENER_PATH)/build
	cp $(CONGFS_EVENT_LISTENER_PATH)/build/congfs-event-listener .

clean: clean-siblings

clean-siblings:
	$(MAKE) -C $(CONGFS_ONLINE_CFG_PATH)/build clean
	$(MAKE) -C $(CONGFS_FSCK_PATH)/build clean
	$(MAKE) -C $(CONGFS_EVENT_LISTENER_PATH)/build clean
#	$(MAKE) -C $(CONGFS_JAVA_LIB_PATH)/build clean
	
	rm -f congfs-ctl
	rm -f congfs-fsck
	rm -f congfs-event-listener
