#!/bin/bash
# Exit when a command fails
set -o errexit
# Exit when tries to use undeclared variables
set -o nounset
# The exit status of the last command that threw a non-zero exit code is returned
set -o pipefail
# Debuggibg
#set -o xtrace

if [[ "$(id -u)" != "0" ]]; then
  echo "You have to be root"
  exit 1
fi

COMMANDS="dh_make dh_gencontrol dh_installsystemd dh_installdeb dh_installdirs dh_install dh_builddeb"
for CMD in ${COMMANDS}; do
  if [[ "$(which ${CMD})" == "" ]]; then
    echo "${CMD} has not been found"
    exit 1
  fi
done

if [[ "$(which dpkg)" == "" ]]; then
  echo "This script is for DEB Linux"
  exit 1
fi

if [[ -e VERSION ]]; then
  SENSORS_VERSION=$(cat VERSION)
else
  echo "The file VERSION has not been found"
  exit 1
fi

BUILD_DIR='/tmp/sensors-debian-packages'
BASE_DIR="$(dirname $(realpath $0))"
DEBS_DIR="${BASE_DIR}/debs"
mkdir -p ${DEBS_DIR}
VERSION="${SENSORS_VERSION}"
EMAIL="alex_yakimov@list.ru"

MAINTAINER="Alex Yakimov <${EMAIL}>"
HOMEPAGE="https://github.com/alex-v-yakimov/sensors"
RECEIVER_DEPENDS="python3, python3-configargparse"
SENDER_DEPENDS="python3, python3-configargparse, lm-sensors"
RECEIVER_DESCRIPTION="The Sensors Receiver"
SENDER_DESCRIPTION="The Sensors Sender"

DH_MAKE_CMD="dh_make --email ${EMAIL}  --native --copyright bsd --indep --yes"
RECEIVER_DH_GENCONTROL_CMD="dh_gencontrol -- \
                           -Vmisc:Depends='${RECEIVER_DEPENDS}' \
                           -DDescription='${RECEIVER_DESCRIPTION}' \
                           -DHomepage='${HOMEPAGE}' -DMaintainer='${MAINTAINER}'"
SENDER_DH_GENCONTROL_CMD="dh_gencontrol -- \
                         -Vmisc:Depends='${SENDER_DEPENDS}' \
                         -DDescription='${SENDER_DESCRIPTION}' \
                         -DHomepage='${HOMEPAGE}' -DMaintainer='${MAINTAINER}'"
DH_INSTALLSYSTEMD_CMD='dh_installsystemd --no-enable --no-start'
DH_BUILDDEB_CMD="dh_builddeb --destdir=${DEBS_DIR}"

RECEIVER_DIR="${BUILD_DIR}/sensors-receiver-${VERSION}"
SENDER_DIR="${BUILD_DIR}/sensors-sender-${VERSION}"

[ -d ${BUILD_DIR} ] && rm -rf ${BUILD_DIR}

mkdir -p ${RECEIVER_DIR} ${SENDER_DIR}

# --- receiver ---

cd ${BASE_DIR}
echo "sensors/__init__.py opt/sensors-receiver/sensors" > ${BUILD_DIR}/sensors-receiver.install
find sensors/receiver -type f -name "*.py" -printf "%p opt/sensors-receiver/sensors/receiver\n" >>  ${BUILD_DIR}/sensors-receiver.install
find sensors/common -type f -name "*.py" -printf "%p opt/sensors-receiver/sensors/common\n" >>  ${BUILD_DIR}/sensors-receiver.install
find distro/configuration_files -type f -name "sensors-receiver.conf" -printf "%p etc\n" >>  ${BUILD_DIR}/sensors-receiver.install

cd ${RECEIVER_DIR}
eval ${DH_MAKE_CMD}
cd debian
cp ${BUILD_DIR}/sensors-receiver.install .
mkdir -p tmp
cp -a ${BASE_DIR}/sensors tmp
cp -a ${BASE_DIR}/distro tmp
cp "${BASE_DIR}/distro/systemd/sensors-receiver.service" .
cd ${RECEIVER_DIR}
eval ${DH_INSTALLSYSTEMD_CMD}
dh_installdeb
dh_installdirs
dh_install
eval ${RECEIVER_DH_GENCONTROL_CMD}
eval ${DH_BUILDDEB_CMD}

# --- sender ---

cd ${BASE_DIR}
echo "sensors/__init__.py opt/sensors-sender/sensors" > ${BUILD_DIR}/sensors-sender.install
find sensors/sender -type f -name "*.py" -printf "%p opt/sensors-sender/sensors/sender\n" >>  ${BUILD_DIR}/sensors-sender.install
find sensors/common -type f -name "*.py" -printf "%p opt/sensors-sender/sensors/common\n" >>  ${BUILD_DIR}/sensors-sender.install
find distro/configuration_files -type f -name "sensors-sender.conf" -printf "%p etc\n" >>  ${BUILD_DIR}/sensors-sender.install

cd ${SENDER_DIR}
eval ${DH_MAKE_CMD}
cd debian
cp ${BUILD_DIR}/sensors-sender.install .
mkdir -p tmp
cp -a ${BASE_DIR}/sensors tmp
cp -a ${BASE_DIR}/distro tmp
cp "${BASE_DIR}/distro/systemd/sensors-sender.service" .
cd ${SENDER_DIR}
eval ${DH_INSTALLSYSTEMD_CMD}
dh_installdeb
dh_install
eval ${SENDER_DH_GENCONTROL_CMD}
eval ${DH_BUILDDEB_CMD}
