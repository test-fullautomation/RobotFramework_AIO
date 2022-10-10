/*
 * Copyright (C) 2012 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.android.uiautomator;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.ModifyEvent;
import org.eclipse.swt.events.ModifyListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;

import com.android.uiautomator.tree.AttributePair;
import com.android.uiautomator.utils.Constants.AddModWidget;

import java.io.File;
import java.util.List;

/**
 * Implements a file selection dialog for both screen shot and xml dump file
 *
 * "OK" button won't be enabled unless both files are selected
 * It also has a convenience feature such that if one file has been picked, and the other
 * file path is empty, then selection for the other file will start from the same base folder
 *
 */
public class InputDialog extends Dialog {

    private static final int FIXED_TEXT_FIELD_WIDTH = 300;
    private static final int DEFAULT_LAYOUT_SPACING = 20;
    private static final String WIDGET_NAME_LABEL = "Widget name";
    private static final String WIDGET_ATTRIBUTES_LABEL = "Widget attributes";
    private static final String WIDGET_DEFAULT_NAME_TEMPLATE = "Wiget_%d";
    private static final String WIDGET_DEFAULT_ATTRIBUTE_TEMPLATE = "'%s': '%s'";
    
    //private static final String LML
    private Text mTxtWidgetName;
    private Text mTxtWidgetAttrs;
    private String mWidgetName;
    private String widgetAttrsString;
    private File mScreenshotFile;
    private File mXmlDumpFile;
    private boolean mFileChanged = false;
    private Button mOkButton;
    private List<TableItem> mItems;
    public static int mCount = 0;
    private AddModWidget mMode;

    /**
     * Create the dialog.
     * @param parentShell
     */
    public InputDialog(Shell parentShell, List<TableItem> lItem) {
        super(parentShell);
        mItems = lItem;
        mMode = AddModWidget.ADD;
        setShellStyle(SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL | SWT.RESIZE );
    }
    
    public InputDialog(Shell parentShell, List<TableItem> lItem, AddModWidget mode) {
        super(parentShell);
        mItems = lItem;
        mMode = mode;
        setShellStyle(SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL | SWT.RESIZE );
    }

    /**
     * Create contents of the dialog.
     * @param parent
     */
    @Override
    protected Control createDialogArea(Composite parent) {
        loadDataFromModel();

        Composite container = (Composite) super.createDialogArea(parent);
        GridLayout gl_container = new GridLayout(1, false);
        gl_container.verticalSpacing = DEFAULT_LAYOUT_SPACING;
        gl_container.horizontalSpacing = DEFAULT_LAYOUT_SPACING;
        gl_container.marginWidth = DEFAULT_LAYOUT_SPACING;
        gl_container.marginHeight = DEFAULT_LAYOUT_SPACING;
        container.setLayout(gl_container);

        Group grpWidgetName = new Group(container, SWT.NONE);
        grpWidgetName.setLayout(new GridLayout(2, false));
        grpWidgetName.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true, false, 1, 1));
        grpWidgetName.setText(WIDGET_NAME_LABEL);

        mTxtWidgetName = new Text(grpWidgetName, SWT.BORDER | SWT.READ_ONLY);
        mTxtWidgetName.setEditable(true);
        
        GridData gdWidgetNameText = new GridData(SWT.FILL, SWT.FILL, true, false, 1, 1);
        gdWidgetNameText.minimumWidth = FIXED_TEXT_FIELD_WIDTH;
        gdWidgetNameText.widthHint = FIXED_TEXT_FIELD_WIDTH;
        mTxtWidgetName.setLayoutData(gdWidgetNameText);
        mWidgetName = mTxtWidgetName.getText();
        mTxtWidgetName.addModifyListener(new ModifyListener() {
        	@Override
            public void modifyText(ModifyEvent e) {
            	mWidgetName = mTxtWidgetName.getText();
            }
        });

        Group grpWidgetAttributes = new Group(container, SWT.NONE);
        grpWidgetAttributes.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
        grpWidgetAttributes.setText(WIDGET_ATTRIBUTES_LABEL);
        grpWidgetAttributes.setLayout(new GridLayout(2, false));

        mTxtWidgetAttrs = new Text(grpWidgetAttributes, SWT.BORDER | SWT.READ_ONLY);
        mTxtWidgetAttrs.setEditable(false);
        
        widgetAttrsString = mTxtWidgetAttrs.getText();
        mTxtWidgetAttrs.addModifyListener(new ModifyListener() {
        	@Override
            public void modifyText(ModifyEvent e) {
        		widgetAttrsString = mTxtWidgetAttrs.getText();
            }
        });
        
        GridData gdWidgetAttributesText = new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1);
        gdWidgetAttributesText.minimumWidth = FIXED_TEXT_FIELD_WIDTH;
        gdWidgetAttributesText.widthHint = FIXED_TEXT_FIELD_WIDTH;
        mTxtWidgetAttrs.setLayoutData(gdWidgetAttributesText);
        SetTextValues();
        return container;
    }
    
    private void SetTextValues() {
    	switch (mMode) {
		case ADD:
			mTxtWidgetName.setText(String.format(WIDGET_DEFAULT_NAME_TEMPLATE, mCount));	    	
	    	if (mItems != null) {
	        	String textAtt = "{";
	            for(int i=0; i < mItems.size(); i++)
	            {
	            	textAtt += String.format(WIDGET_DEFAULT_ATTRIBUTE_TEMPLATE, ((AttributePair)mItems.get(i).getData()).key, ((AttributePair)mItems.get(i).getData()).value);
	            	if (i < mItems.size() - 1)
	            		textAtt += ",";            		
	            }
	            textAtt += "}";
	            mTxtWidgetAttrs.setText(textAtt);
	        }
			break;
		case MODIFY:
			mTxtWidgetName.setText(mItems.get(0).getText(0));
			mTxtWidgetAttrs.setText(mItems.get(0).getText(1));
		default:
			break;
		}
    	
    	
	}
    
    public String getWidgetName()
    {
    	return mWidgetName;
    }
    
    public String getAttributes()
    {
    	return widgetAttrsString;
    }

    /**
     * Create contents of the button bar.
     * @param parent
     */
    @Override
    protected void createButtonsForButtonBar(Composite parent) {
        mOkButton = createButton(parent, IDialogConstants.OK_ID, IDialogConstants.OK_LABEL, true);
        createButton(parent, IDialogConstants.CANCEL_ID, IDialogConstants.CANCEL_LABEL, false);
        updateButtonState();
    }

    /**
     * Return the initial size of the dialog.
     */
    @Override
    protected Point getInitialSize() {
        return new Point(368, 300);
    }

    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("Define widget");
    }

    private void loadDataFromModel() {
        mScreenshotFile = UiAutomatorModel.getModel().getScreenshotFile();
        mXmlDumpFile = UiAutomatorModel.getModel().getXmlDumpFile();
    }    

    private void updateButtonState() {
        mOkButton.setEnabled(mScreenshotFile != null && mXmlDumpFile != null
                && mScreenshotFile.isFile() && mXmlDumpFile.isFile());
    }

    public boolean hasFileChanged() {
        return mFileChanged;
    }

    public File getScreenshotFile() {
        return mScreenshotFile;
    }

    public File getXmlDumpFile() {
        return mXmlDumpFile;
    }
}
