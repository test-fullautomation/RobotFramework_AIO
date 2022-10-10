package com.android.uiautomator.utils;

import org.eclipse.swt.SWT;
import org.eclipse.swt.widgets.MessageBox;
import org.eclipse.swt.widgets.Shell;

@SuppressWarnings("serial")
public class UIAutomatorException extends Exception {
	
	Shell mWindowShell = null;
	public UIAutomatorException(String str, Shell parent)
	{
		super(str);  
		mWindowShell = parent;		
	}
	
	public void ShowMessageBox()
	{
		MessageBox msgBox = new MessageBox(mWindowShell, SWT.ICON_ERROR);
		msgBox.setMessage(this.getMessage());  
    	msgBox.open();
	}
}
