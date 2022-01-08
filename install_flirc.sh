#!/usr/bin/env bash

LSB_FILE=/etc/*-release
HOST=unknown
PKG=unknown
OVERRIDE=no

# This is a general-purpose function to ask Yes/No questions in Bash, either
# with or without a default answer. It keeps repeating the question until it
# gets a valid answer.
# Source:
# https://gist.github.com/davejamesmiller/1965569
ask() {

	if [ ${OVERRIDE} = "yes" ];
	then
		return 0
	fi

    # https://djm.me/ask
    local prompt default reply

    while true; do

        if [ "${2:-}" = "Y" ]; then
            prompt="Y/n"
            default=Y
        elif [ "${2:-}" = "N" ]; then
            prompt="y/N"
            default=N
        else
            prompt="y/n"
            default=
        fi

        # Ask the question (not using "read -p" as it uses stderr not stdout)
        echo -n "$1 [$prompt] "

        # Read the answer (use /dev/tty in case stdin is redirected from somewhere else)
        read reply </dev/tty

        # Default?
        if [ -z "$reply" ]; then
            reply=$default
        fi

        # Check if the reply is valid
        case "$reply" in
            Y*|y*) return 0 ;;
            N*|n*) return 1 ;;
        esac

    done
}

unknown_os ()
{
	echo "Unfortunately, your operating system distribution and version are not supported by this script."
	echo
	echo "You can find a list of supported OSes and distributions on: https://repo.flirc.tv/"
	echo
	echo "Please email support@flirc.tv and let us know if you run into any issues."
	echo
	echo "You can also try installing one of the statically compiled packges from the linux http://www.flirc.tv/downloads page"
	exit 1
}

detect_redhat_os ()
{
	if [[ ( -z "${os}" ) && ( -z "${dist}" ) ]]; then
		if [ -e /etc/os-release ]; then
			. /etc/os-release
			os=${ID}
			if [ "${os}" = "poky" ]; then
				dist=`echo ${VERSION_ID}`
			elif [ "${os}" = "sles" ]; then
				dist=`echo ${VERSION_ID}`
			elif [ "${os}" = "opensuse" ]; then
				dist=`echo ${VERSION_ID}`
			else
				dist=`echo ${VERSION_ID} | awk -F '.' '{ print $1 }'`
			fi
		elif [ `which lsb_release 2>/dev/null` ]; then
			# get major version (e.g. '5' or '6')
			dist=`lsb_release -r | cut -f2 | awk -F '.' '{ print $1 }'`

			# get os (e.g. 'centos', 'redhatenterpriseserver', etc)
			os=`lsb_release -i | cut -f2 | awk '{ print tolower($1) }'`

		elif [ -e /etc/oracle-release ]; then
			dist=`cut -f5 --delimiter=' ' /etc/oracle-release | awk -F '.' '{ print $1 }'`
			os='ol'

		elif [ -e /etc/fedora-release ]; then
			dist=`cut -f3 --delimiter=' ' /etc/fedora-release`
			os='fedora'

		elif [ -e /etc/redhat-release ]; then
			os_hint=`cat /etc/redhat-release  | awk '{ print tolower($1) }'`
			if [ "${os_hint}" = "centos" ]; then
				dist=`cat /etc/redhat-release | awk '{ print $3 }' | awk -F '.' '{ print $1 }'`
				os='centos'
			elif [ "${os_hint}" = "scientific" ]; then
				dist=`cat /etc/redhat-release | awk '{ print $4 }' | awk -F '.' '{ print $1 }'`
				os='scientific'
			else
				dist=`cat /etc/redhat-release  | awk '{ print tolower($7) }' | cut -f1 --delimiter='.'`
				os='redhatenterpriseserver'
			fi

		else
			aws=`grep -q Amazon /etc/issue`
			if [ "$?" = "0" ]; then
				dist='6'
				os='aws'
			else
				unknown_os
			fi
		fi
	fi

	if [[ ( -z "${os}" ) || ( -z "${dist}" ) ]]; then
		unknown_os
	fi

	# remove whitespace from OS and dist name
	os="${os// /}"
	dist="${dist// /}"

	echo "Detected operating system as ${os}/${dist}."
}

detect_os ()
{
	if grep -iq debian ${LSB_FILE}
	then
		HOST=debian
		PKG=deb
	elif grep -iq redhat ${LSB_FILE}
	then
		HOST=redhat
		PKG=rpm
		detect_redhat_os
	elif find /etc/*-release -type f -exec cat {} + | grep -iq ubuntu
	then
		HOST=debian
		PKG=deb
	else
		unknown_os
	fi
}

curl_check ()
{
	echo "Checking for curl..."
	if command -v curl > /dev/null; then
		echo "Detected curl..."
		return 0
	else
		return 1
	fi
}

deb_install_curl ()
{
    echo "Installing curl..."
    apt-get install -q -y curl
    if [ "$?" -ne "0" ]; then
		echo "Unable to install curl! Your base system has a problem; please check your default OS's package repositories because curl should work."
		echo "Repository installation aborted."
		exit 1
    fi
}

rpm_install_curl ()
{
	echo "Installing curl..."
    yum install -d0 -e0 -y curl
}

display_logo ()
{
#
# image generated with http://www.text-image.com/convert/ascii.html
#
  cat << "EOF"

                     `..-:://++ooossyyyyhhhhhhhhhhhhhhhhyyysso++/:-.`
         `.:/+oosyhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhyo:`
    -/oyhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhy
  /hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh-
  hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh:
  yhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh:
  ohhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh-
  -hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh`
   yhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhs
   /hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh/
    yhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhho:-:+hhhhhhhhhhhh.
    /hhhhhhhhhhhs-   -shhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh.     `hhhhhhhhhhs
     yhhhhhhhhhh`     .hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh       yhhhhhhhhh-
     :hhhhhhhhhho`   `ohhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhs:` `-shhhhhhhhho
      shhhhhhhhhhhssshhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh`
      .hhhhhhhhhhhhhhysso++///:::-----........-----:://+oshhhhhhhhhhh:
       :hhhhhhhhhhhs/:---......```````````.......---:::/+ohhhhhhhhhho
        +hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhs
         ohhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhy`
          +hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhs`
           -shhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhys:
             `.-://++oosssyyyyyhhhhhhhhhhhhhyyyssoo++//:--.`
EOF
}

rpm_install_repo ()
{
	echo "Installing flirc yum-repo..."
	if [ "${os}" = "sles" ] || [ "${os}" = "opensuse" ]; then
		YUM_REPO_PATH=/etc/zypp/repos.d/flirc_fury.repo
	else
		YUM_REPO_PATH=/etc/yum.repos.d/flirc_fury.repo
	fi

	# Overwrite with first line, and append to sure new file
	echo "[flirc_fury]" > ${YUM_REPO_PATH}
	echo "name=Flirc Public Repo" >> ${YUM_REPO_PATH}
	echo "baseurl=https://yum.fury.io/flirc/" >> ${YUM_REPO_PATH}
	echo "enabled=1" >> ${YUM_REPO_PATH}
	echo "gpgcheck=0" >> ${YUM_REPO_PATH}

	echo "Installing yum-utils..."
	yum install -y yum-utils --disablerepo='flirc_fury'
	yum_utils_check=`rpm -qa | grep -qw yum-utils`
	if [ "$?" != "0" ]; then
		echo
		echo "WARNING: "
		echo "The yum-utils package could not be installed. This means you may not be able to install source RPMs or use other yum features."
		echo ""
	fi

	echo "Generating yum cache for flirc_repo..."
	yum -q makecache -y --disablerepo='*' --enablerepo='flirc_fury'
}

deb_install_repo ()
{
	echo "Installing flirc deb-repo..."

	# Need to first run apt-get update so that apt-transport-https can be
	# installed
	echo -n "Running apt-get update... "
	apt-get update &> /dev/null
	echo "done."

	echo -n "Installing apt-transport-https... "
	apt-get install -y apt-transport-https &> /dev/null
	echo "done."

	APT_SOURCE_PATH="/etc/apt/sources.list.d/flirc_fury.list"

	echo -n "Installing ${APT_SOURCE_PATH}..."

	# create an apt config file for this repository
	echo "deb [trusted=yes] https://apt.fury.io/flirc/ /" > ${APT_SOURCE_PATH}
	echo "done."

	echo -n "Running apt-get update... "
	# update apt on this system
	apt-get update &> /dev/null
	echo "done."
}

rpm_install_app ()
{
    yum install -d0 -e0 -y flirc
	echo "done."
}

deb_install_app ()
{
    apt-get install -q -y flirc &> /dev/null
	echo "done."
}

# Pass the script yes
if [ $# -ne 0 ];
then
	if [ $1 = "-y" ];
	then
		OVERRIDE=yes
	fi
fi

detect_os
display_logo

echo "Distribution:" ${HOST}

# Check for Curl
curl_check

# If CURL is not installed, install it
if [ "$?" == 1 ]
then
    echo "error checking for curl"
	${PKG}_install_curl
fi

# Install our repo
${PKG}_install_repo

# Default to Yes, ask user to install flirc
if ask "Do you want to install the flirc utilities?" Y; then
	echo -n "Installing flirc utilities..."
	${PKG}_install_app
fi
