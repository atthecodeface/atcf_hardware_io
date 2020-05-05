CDL_ROOT ?= $(abspath $(dir $(abspath $(shell which cdl)))/.. )
include ${CDL_ROOT}/lib/cdl/cdl_templates.mk
SRC_ROOT   = $(abspath ${CURDIR})
OTHER_SRCS = ${SRC_ROOT}/../*
BUILD_ROOT = ${SRC_ROOT}/build
TEST_DIR   = ${CURDIR}/test

all: sim

-include ${BUILD_ROOT}/Makefile

$(eval $(call cdl_makefile_template,${SRC_ROOT},${BUILD_ROOT},${OTHER_SRCS}))

smoke: ${SIM}
	@echo "atcf_hardware_io has no tests yet"

#	${Q}(cd ${TEST_DIR} && PATH=${TEST_DIR}/python:${PATH} ${MAKE} Q=${Q} SIM=${SIM} smoke)

