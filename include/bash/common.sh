########################################################################################
#
# this script provides common functions for the install and build process
#
#########################################################################################

ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_BLACK=$ESC_SEQ"30;01m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_BLUE=$ESC_SEQ"34;01m"
COL_MAGENTA=$ESC_SEQ"35;01m"
COL_CYAN=$ESC_SEQ"36;01m"

BG_BLACK='\033[40m'      
BG_RED='\033[41m'         
BG_GREEN='\033[42m'     
BG_YELLOW='\033[43m'    
BG_BLUE='\033[44m'      
BG_PURPLE='\033[45m'    
BG_CYAN='\033[46m'      
BG_WHITE='\033[47m'     

mypath=$(realpath $(dirname $0))

function errormsg(){
   echo -e "${COL_RED}>>>> ERROR: $1!${COL_RESET}"
   echo
   exit 1
}

function goodmsg(){
   echo -e "${COL_GREEN}>>>> $1.${COL_RESET}"
   echo
}

function greenmsg(){
   echo -e "${COL_GREEN}> $1.${COL_RESET}"   
}

function logresult(){
	if [ "$1" -eq 0 ]; then
	    goodmsg "Successfully $2"
	else
		errormsg "FATAL: Could not $3"
	fi
}