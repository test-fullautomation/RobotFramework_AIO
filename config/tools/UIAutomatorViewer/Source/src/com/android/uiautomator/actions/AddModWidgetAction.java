package com.android.uiautomator.actions;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;


import com.android.uiautomator.InputDialog;
import com.android.uiautomator.UiAutomatorViewer;
import com.android.uiautomator.utils.Constants.AddModWidget;

import org.eclipse.jface.action.Action;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.swt.widgets.TableItem;

/**
 * AddWidgetAction class is used for defining android widgets and add to table.
 * 
 * @author ugc1hc
 *
 */
public class AddModWidgetAction extends Action {
	List<Map<String, String>> mListAttributes;
	UiAutomatorViewer mViewer;
	TableViewer mTable;
	AddModWidget mMode;
	
	/**
	 * Constructor of AddWidgetAction class.
	 * 
	 * @param window	The UiAutomatorviewer window
	 */
	public AddModWidgetAction(UiAutomatorViewer window) {
		mViewer = window;
        setText("&Add widget");
        mMode = AddModWidget.ADD;
    }	
	
	public AddModWidgetAction(UiAutomatorViewer window, AddModWidget mode) {
		mViewer = window;
        setText("&Add widget");
        mMode = mode;
    }	
	
	/**
	 * Get all selected attributes for defining. 
	 * 
	 * @param 	table	Defined widget table.
	 * @return	List of widget items.
	 */
	private List<TableItem> getTableItems(TableViewer table)
    {
    	List<TableItem> res = new ArrayList<TableItem>();
    	TableItem [] items = table.getTable().getItems();
        for (int i = 0; i < items.length; ++i) {
          if (items[i].getChecked())
          {
        	 res.add(items[i]);
          }
           
        }
    	return res;    	
    }
	
	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.Action#getImageDescriptor()
	 */
	@Override
    public ImageDescriptor getImageDescriptor() {
        return ImageHelper.loadImageDescriptorFromResource("images/addwidget.png");
    }
	
	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.Action#run()
	 */
	@Override
    public void run() {
		switch (mMode) {
		case ADD:
			run_add();
			break;
		case MODIFY:
			run_modify();
			break;
		case DELETE:
			run_delete();
			break;
		default:
			break;
		}
        
    }
	
	private void run_delete() {
		TableItem[] ls = mTable.getTable().getSelection();
		for (TableItem tableItem : ls) {
			mTable.getTable().remove(mTable.getTable().indexOf(tableItem));
		}
	}
	
	private void run_add() {
		List<TableItem> ls = getTableItems(mTable);
		InputDialog d = new InputDialog(mViewer.getShell(), ls);
		
        if (d.open() == InputDialog.OK) {
            mViewer.AddWidgetTableItem(d.getWidgetName(), d.getAttributes());
            InputDialog.mCount++;
        }
	}
	
	private void run_modify() {
		TableItem[] ls = mTable.getTable().getSelection();
		InputDialog d = new InputDialog(mViewer.getShell(), Arrays.asList(ls), AddModWidget.MODIFY);
		
        if (d.open() == InputDialog.OK) {
        	ls[0].setText(0, d.getWidgetName());
        	ls[0].setText(1, d.getAttributes());
        }
	}
	
	
	/**
	 * Set TableViewer object.
	 * 
	 * @param table
	 */
	public void setTableViewer(TableViewer table)
	{
		mTable = table;
	}
}
