package com.android.uiautomator.actions;

import com.android.uiautomator.GenerateOptionsDialog;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.window.ApplicationWindow;
import org.eclipse.swt.widgets.MessageBox;

/**
 * GenerateAction support action for generate definition for all widgets in an Activity.
 * @author ugc1hc
 *
 */
public class GenerateAction extends Action {

    ApplicationWindow mWindow;
    static final String MSGBOX_SUCCESS_STR = "Lml file is created successfully!!!";
    static final String MSGBOX_FAILURE_STR = "Problem occurs when generating lml. \nDetail:%s";

    /**
     * Constructor of GenerateAction class
     * @param window
     */
    public GenerateAction(ApplicationWindow window) {
        mWindow = window;
        setText("&Auto generate definitions");
    }

    @Override
    public ImageDescriptor getImageDescriptor() {
        return ImageHelper.loadImageDescriptorFromResource("images/generate.png");
    }

    @Override
    public void run() {
        GenerateOptionsDialog d = new GenerateOptionsDialog(mWindow.getShell());
		MessageBox msgBox = new MessageBox(mWindow.getShell());
        try        
        {
        	d.open();
        }
        catch (Exception e) {
        	msgBox.setMessage(String.format(MSGBOX_FAILURE_STR, e.toString()));  
        	msgBox.open();
        }    
                
    }
}
