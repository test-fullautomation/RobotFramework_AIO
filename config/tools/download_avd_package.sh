ANDROID_HOME=$RobotDevtools/Android

function download_package(){
	proxy_args=""
	if [ "$use_cntlm" == "Yes" ]; then
		proxy_args="--proxy-ntlm -x 127.0.0.1:3128"
	fi
	package_name=$1
	package_url=$2
	package_out=$3

	retry_counter=0
	max_retries=5
	success=false

	echo curl $proxy_args "$package_url" -o "$package_out"
	while [[ "$retry_counter" -lt "$max_retries" && "$success" == "false" ]];do
		curl $proxy_args -L -k "$package_url" -o "$package_out"

		if [ $? -eq 0 ]; then
			success=true
			goodmsg "Successfully downloaded $package_name"
		else
			((retry_counter++))
			echo "Failed to download $package_url (attempt: $retry_counter)"
			sleep 1
			if [ "$use_cntlm" == "Yes" ]; then
				restart_cntlm
			fi
		fi
	done

	if [ "$success" == "false" ]; then
		errormsg "FATAL: Could not download $package_url after $max_retries attempts"
	fi
}

function packaging_android() {
	download_android_emulator_hypervisor_driver=https://github.com/google/android-emulator-hypervisor-driver/releases/download/v2.2/aehd-windows_v2_2_0.zip
	download_android_google_apis=https://dl.google.com/android/repository/sys-img/google_apis/x86_64-34_r13.zip

	archived_android_emulator_hypervisor_driver=aehd-windows_v2_2_0.zip
	archived_android_google_apis=x86_64-34_r13.zip

	echo "Packaging Android ..."

	npm_proxy_args=""
	if [ "$use_cntlm" == "Yes" ]; then
		npm_proxy_args="--proxy=http://localhost:3128"
	fi

	echo "Downloading Android Emulator hypervisor driver"
	download_package "AEHD" ${download_android_emulator_hypervisor_driver} "${ANDROID_HOME}/${archived_android_emulator_hypervisor_driver}"
	/usr/bin/yes A | unzip "${ANDROID_HOME}/${archived_android_emulator_hypervisor_driver}" -d "$ANDROID_HOME/aehd-windows"
   rm "${ANDROID_HOME}/${archived_android_emulator_hypervisor_driver}"

	mkdir  "$ANDROID_HOME/system-images"
	mkdir  "$ANDROID_HOME/system-images/android-34"
	mkdir  "$ANDROID_HOME/system-images/android-34/google_apis"

	echo "Downloading Android Google APIs"
	download_package "Android Google APIs" ${download_android_google_apis} "${ANDROID_HOME}/${archived_android_google_apis}"
	/usr/bin/yes A | unzip "${ANDROID_HOME}/${archived_android_google_apis}" -d "$ANDROID_HOME/system-images/android-34/google_apis"
	rm "${ANDROID_HOME}/${archived_android_google_apis}"
}

packaging_android