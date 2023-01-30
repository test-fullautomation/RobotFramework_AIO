**************************************************************************************************************

VS Codium launch files for robot test execution

30.01.2023

--------------------------------------------------------------------------------------------------------------

Purpose: Configuration of command line of Robot Framework.

The usage of launch files
* is limited to the 'Run' button of VS Codium (the Robot Framework context menu of VS Codium explorer does not consider the launch file)
* is limited to the execution of single robot files (folders are not supported)

The launch file has to be placed within '%ROBOTTESTPATH%\.vscode' folder.

* version-1

  - Log file destination is the subfolder 'reports' within the current workspace folder
  - Fix name of output files (follow up executions overwrite output files of previous execution)
  - Debug version (-b) of output file is activated

* version-2

  - User has to select a target name (out of a list of discrete target names like predefined within the lauch file)
  - Log file destination is the subfolder 'reports' within the current workspace folder. Within this folder another subfolder is created,
    containing the previously selected target name and the name of the executed robot file
  - Debug version (-b) of output file is activated
  - Output files in XML format and in HTML format are moved another level down to the following subfolders:
    'htmllog', 'xmloutput' and 'htmlreport'. This is to avoid too large lists of output files flat in one single folder
  - Robot Framework timestamp function (-T) activated: Every output file gets a timestamp within the name
    (therefore follow up executions do not overwrite output files of previous execution)
