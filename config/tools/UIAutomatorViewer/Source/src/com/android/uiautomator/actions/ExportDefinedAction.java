package com.android.uiautomator.actions;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import com.android.uiautomator.UiAutomatorViewer;
import com.android.uiautomator.utils.SaveFileDialogHelper;
import com.android.uiautomator.utils.UIAutomatorException;
import com.android.uiautomator.utils.steptypes.BooleanEnum;
import com.android.uiautomator.utils.steptypes.Paramsetstep;
import com.android.uiautomator.utils.steptypes.Refstep;
import com.android.uiautomator.utils.steptypes.Refsteps;
import com.android.uiautomator.utils.steptypes.Stepgroup;
import com.android.uiautomator.utils.Constants.ErrorCode;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.swt.widgets.TableItem;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;

/**
 * ExportLmlAction class is used for export defined widgets to .lml file. 
 * 
 * @author ugc1hc
 *
 */
public class ExportDefinedAction extends Action {
	List<Map<String, String>> mListAttributes;
	UiAutomatorViewer mViewer;
	TableViewer mTable;
	
	static final String WIDGET_DEFINE_TEMPLATE = "*{%s}['%s']=dict%s";
	static final String WIDGET_DICT_NAME = ".dWidget";
	static final String WIDGET_INIT_STEPGROUP_NAME = ".Init";
	
	static final String ROBOT_RESOURCE_FILE_TEMPLATE = "*** Variables ***\n"
													 + "&{%s}\t%s=%s=%s";
	
	/***
	 * Error strings
	 */	
	@SuppressWarnings("serial")
	static Map<ErrorCode, String> mapErrorStrings = new HashMap<ErrorCode, String>() {{
		put(ErrorCode.ERR_EXCEEDED_MAX_ITEMS, "Unable to export definitions to %s.resource file! \n"
											+ "Robot resource file only accepts one locator for each element.");
	}};
	
	   
	
	@SuppressWarnings("serial")
	static Map<String, Method> mapMethods = new HashMap<String, Method>() {{
		try {
			put("lml", ExportDefinedAction.class.getDeclaredMethod("export2Lml", File.class, List.class));
			put("resource", ExportDefinedAction.class.getDeclaredMethod("export2robotresource", File.class, List.class));
		} catch (NoSuchMethodException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		} catch (SecurityException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
	}};
	
	/**
	 * Constructor of ExportLmlAction class.
	 * 
	 * @param window	The UiAutomatorviewer window
	 */
	public ExportDefinedAction(UiAutomatorViewer window) {
		mViewer = window;
        setText("&Export definitions to file...");

    }
	
	/**
	 * Get all selected defined widgets for exporting. 
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
	
	/**
	 * Export defined widgets to .lml file.
	 * 
	 * @param dest		lml file object.
	 * @param mItems	List of widget items.
	 */
	@SuppressWarnings("unused")
	private void export2Lml(File dest, List<TableItem>mItems)
	{
		try {
			 //Create JAXB Context
            JAXBContext jaxbContext = JAXBContext.newInstance(Refsteps.class);
             
            //Create Marshaler
            Marshaller jaxbMarshaller = jaxbContext.createMarshaller();
 
            //Required formatting??
            jaxbMarshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
            
            String returnParam = mViewer.getActivityName() + WIDGET_DICT_NAME;
            String stepgroupName = mViewer.getActivityName() + WIDGET_INIT_STEPGROUP_NAME;
            
            Refsteps refStep = new Refsteps();
            Stepgroup stepGroup = new Stepgroup(stepgroupName, returnParam);
            Refstep refInit = new Refstep(stepgroupName);
			Paramsetstep paramReturn = new Paramsetstep(returnParam + "=ddict{}", BooleanEnum.TRUE);
            
            stepGroup.addStep(paramReturn);            
            refStep.addStepgroup(stepGroup);
            refStep.addStepgroup(refInit);
            
            for (int i =0; i < mItems.size(); i++)
			{
				Paramsetstep paramsetStep = new Paramsetstep(String.format(WIDGET_DEFINE_TEMPLATE, 	returnParam, 
																									mItems.get(i).getText(0), 
																									mItems.get(i).getText(1)),
															null );
				stepGroup.addStep(paramsetStep);
			}
             
            //Writes XML file to file-system
            jaxbMarshaller.marshal(refStep, dest);
            
		} catch (JAXBException e) {
			e.printStackTrace();
		}
	}	
	
	@SuppressWarnings("unused")
	private void export2robotresource(File dest, List<TableItem>mItems)
	{	
		try {					
			FileOutputStream fis = new FileOutputStream(dest);
			String content = "";
			String elementName = "";
			String locatorName = "";
			String locatorValue = "";
			JSONParser parser = new JSONParser(); 
			elementName = mItems.get(0).getText(0);		 
			String [] propertiesArr = mItems.get(0).getText(1).split(",");
			if (propertiesArr.length > 1)
			{
				fis.close();
				throw new UIAutomatorException(String.format(mapErrorStrings.get(ErrorCode.ERR_EXCEEDED_MAX_ITEMS), 
																dest.getName()), 	
												mViewer.getShell());
			}
			
			String definedStr = propertiesArr[0].replaceAll("^\\{|\\}$", "");
			locatorName = definedStr.split(":")[0].trim().replaceAll("^\'|\'$", "");
			locatorValue = definedStr.split(":")[1].trim().replaceAll("^\'|\'$", "");	
			content = String.format(ROBOT_RESOURCE_FILE_TEMPLATE, mViewer.getActivityName(), elementName, locatorName, locatorValue);			
			fis.write(content.getBytes());            
			fis.close();
		}
		catch (UIAutomatorException e) {
			e.ShowMessageBox();
			e.printStackTrace();
		}
		catch (Exception e) {
			e.printStackTrace();
		}
	}
	
	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.Action#getImageDescriptor()
	 */
	@Override
    public ImageDescriptor getImageDescriptor() {
        return ImageHelper.loadImageDescriptorFromResource("images/export.png");
    }
	
	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.Action#run()
	 */
	@Override
    public void run() {
		List<TableItem> ls = getTableItems(mTable);
		ExportDefinedAction currentIns = this;
		SaveFileDialogHelper exportDialog = new SaveFileDialogHelper("lml|resource", null, mViewer.getActivityName()) {
			@Override
			public void AproveAction(File file, Object... args) {
				@SuppressWarnings("unchecked")
				List<TableItem> itemList = List.class.isInstance(args[0]) ? (List<TableItem>)args[0] : null; 
				if(itemList != null)
				{
					String extension = FilenameUtils.getExtension(file.getName());
					try {
						Method exportMtd = mapMethods.get(extension);
						exportMtd.setAccessible(true);
						exportMtd.invoke(currentIns, file, itemList);
					} catch (IllegalAccessException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} catch (IllegalArgumentException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					} catch (InvocationTargetException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
				}
			}
		};
		
		exportDialog.openDialog(ls);
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
