*** Settings ***
Documentation     An example resource file


*** Keywords ***
do_the_hucklebuck
    [Arguments]     ${nSpeed}=${80}    ${sDirection}=totheright
    [Documentation]     Set the ``hucklebuck`` to ``nSpeed`` beats per minute, with direction is ``sDirection``.
    ...
    ...     **Args:**
    ...
    ...     **nSpeed**  (*integer, optional, default: 80 bpm*)
    ...
    ...     \t Beats per minute when doing the hucklebuck.
    ...
    ...     **sDirection**  (*string, optional, default: totheright*)
    ...
    ...     \t Defines the direction when doing thw hucklebuck.
    ...
    ...     **Returns:**
    ...
    ...     **sResult** (*string*)
    ...
    ...     \t Statement about the result of doing the hucklebuck.

    Log     ======= Doing the hucklebuck.

    set_local_variable      ${sResult}      hucklebuck done.
    [Return]    ${sResult}