package com.android.uiautomator;

import org.apache.commons.io.FilenameUtils;
import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.swt.SWT;
import org.eclipse.swt.custom.TableEditor;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.MessageBox;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Text;
import org.json.simple.parser.JSONParser;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.android.uiautomator.tree.AttributePair;
import com.android.uiautomator.utils.SaveFileDialogHelper;
import com.android.uiautomator.utils.UIAutomatorException;
import com.android.uiautomator.utils.Constants.ErrorCode;
import com.android.uiautomator.utils.steptypes.BooleanEnum;
import com.android.uiautomator.utils.steptypes.Paramsetstep;
import com.android.uiautomator.utils.steptypes.Refstep;
import com.android.uiautomator.utils.steptypes.Refsteps;
import com.android.uiautomator.utils.steptypes.Stepgroup;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;



/**
 * GenerateOptionsDialog class supports to select which attributes is used to define all widgets in an activity.
 * 
 * @author ugc1hc
 *
 */
public class GenerateOptionsDialog extends Dialog {
    private static final int DEFAULT_LAYOUT_SPACING = 10;
    private File mXmlDumpFile;
    private Button mExportButton;
    private TableViewer mDefineChoiceTableViewer;
    
    public static final String NAME = "Widget Type";
    public static final String BYCLASS = "ByClass";
    public static final String BYRESOURCEID = "ByResId";
    public static final String BYTEXT = "ByText";
    public static final String BYINDEX = "ByIndex";
    public static final String[] PROPS = { NAME, BYCLASS, BYRESOURCEID, BYTEXT, BYINDEX};
    
    static final String WIDGET_DEFINE_TEMPLATE = "*{%s}['%s']=dict%s";
	static final String WIDGET_DICT_NAME = ".dWidget";
	static final String WIDGET_INIT_STEPGROUP_NAME = ".Init";
	
	static final String MSGBOX_SUCCESS_STR = "Lml file is created successfully!!!";
    static final String MSGBOX_FAILURE_STR = "Problem occurs when generating lml. \nDetail:%s";
	
    private List<String> supportedClasses = new ArrayList<String>(
    	Arrays.asList(	
    	"android.widget.CheckBox",
		"android.widget.TextView", 
		"android.widget.EditText", 
		"android.widget.ToggleButton",
		"android.widget.ProgressBar", 
		"android.widget.SeekBar", 
		"android.widget.RadioButton",
		"android.widget.Button",
		"android.widget.Switch",
		"android.widget.RadioGroup",
		"android.widget.ListView")
    );
    
    private List<String> supportedDefineOptions = new ArrayList<String>(
        	Arrays.asList(	
        	"class",
        	"resource-id",
    		"text",     		
        	"index")
        );
    
    private static Map<String, List<String>> dictExportOptions = new HashMap<String, List<String>>();    
    private static final String RESID_NAME_REGEX = "(?<=[/]).*";
    private static final String TEXT_NAME_REGEX = ".*";
    private Map<String, AttributePair> dictNamingSupport  = new HashMap<String, AttributePair>();
    private List<String> listNameByText = new ArrayList<String>(
        	Arrays.asList(
    		"android.widget.TextView")
        );
    Shell mParentShell;

    static final String ROBOT_RESOURCE_FILE_TEMPLATE = "*** Variables ***\n"
			 											+ "&{%s}%s";
    
    static final String ROBOT_RESOURCE_ELEMENT_DEFINE_TEMPLATE = "\t%s=%s=%s";
    /***
	 * Error strings
	 */	
	@SuppressWarnings("serial")
	static Map<ErrorCode, String> mapErrorStrings = new HashMap<ErrorCode, String>() {{
		put(ErrorCode.ERR_EXCEEDED_MAX_ITEMS, "Unable to export definitions to %s.resource file! \n"
											+ "Robot resource file only accepts one locator for each element.");
	}};
    
    /**
     * Create the dialog.
     * @param parentShell
     */
    public GenerateOptionsDialog(Shell parentShell) {
        super(parentShell);
		mParentShell = parentShell;
        setShellStyle(SWT.DIALOG_TRIM | SWT.APPLICATION_MODAL);
        exportMapInitialize();
    }
    
    /**
     * Initialize for default define options and name.
     */
    private void exportMapInitialize()
    {
    	// Default attribute for defining object is resource-id
    	dictExportOptions = supportedClasses.stream().collect(Collectors.toMap(k -> k, 
    														k -> new LinkedList<String>(Arrays.asList("resource-id"))));
    	
    	// Default attribute for naming widgets is resource-id, except class defined in listNameByText
    	dictNamingSupport = supportedClasses.stream().collect(Collectors.toMap(k -> k, 
													k -> new AttributePair(listNameByText.contains(k) ? "text" : "resource-id", 
																		   listNameByText.contains(k) ? TEXT_NAME_REGEX : RESID_NAME_REGEX)));
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
        
        Group propsChoiceGroup = new Group(container, SWT.NONE);
        propsChoiceGroup.setLayout(new GridLayout(2, false));
        propsChoiceGroup.setLayoutData(new GridData(SWT.FILL, SWT.CENTER, true, false, 1, 1));
        propsChoiceGroup.setText("Select attriubute for UI define");
        
        Composite tableContainer2 = new Composite(propsChoiceGroup, SWT.NONE);
        tableContainer2.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true,
                true, 1, 1));
        mDefineChoiceTableViewer = new TableViewer(tableContainer2, SWT.FULL_SELECTION | SWT.BORDER);

        Table optionChoiceTable = mDefineChoiceTableViewer.getTable();
        optionChoiceTable.setLinesVisible(true);
        optionChoiceTable.setSize(753, 300);
        
        GridData gridData = new GridData();
        gridData.horizontalAlignment = SWT.FILL;
        gridData.grabExcessHorizontalSpace = true;
        gridData.grabExcessVerticalSpace = true;
        gridData.verticalAlignment = SWT.FILL;
        gridData.heightHint = 500;
        
        mDefineChoiceTableViewer.getTable().setLayoutData(gridData);
        mDefineChoiceTableViewer.getTable().setHeaderVisible(true);
        mDefineChoiceTableViewer.getTable().setLinesVisible(true);
        CellEditor[] cellEditors = new CellEditor[PROPS.length];
        for (int i = 0; i < PROPS.length; i++) {
        	TableViewerColumn tableViewerColumn = new TableViewerColumn(mDefineChoiceTableViewer, SWT.CENTER);
        	TableColumn tableColumn = tableViewerColumn.getColumn();        	
        	tableColumn.setText(PROPS[i]);
        	tableColumn.setMoveable(true);
        	tableColumn.pack();
        	optionChoiceTable.getColumn(i).pack();
        	optionChoiceTable.getColumn(i).setWidth(750 / PROPS.length);
        }

        for (int i=0; i < supportedClasses.size(); i++)
        {
        	TableItem tableItem = new TableItem(optionChoiceTable, SWT.NONE);
        	TableEditor editor = new TableEditor(optionChoiceTable);
        	Text text = new Text(optionChoiceTable, SWT.NONE);
        	String className = supportedClasses.get(i);
        	text.setText(className.split("\\.")[2]);
        	editor.grabHorizontal = true;
        	editor.minimumWidth = text.getSize().x;
        	editor.setEditor(text, tableItem, 0);    
        	List<String> defaultChoice =  dictExportOptions.get(supportedClasses.get(i));
        	for (int j=0; j < supportedDefineOptions.size(); j++)
        	{
        		editor = new TableEditor(optionChoiceTable);
        		Button button = new Button(optionChoiceTable, SWT.CHECK);
        		button.pack();
        		editor.minimumWidth = button.getSize().x;
        		editor.horizontalAlignment = SWT.CENTER;        		
        		if (defaultChoice.contains(supportedDefineOptions.get(j)))
        			button.setSelection(true);        	
        		
        		button.addSelectionListener(new CustomSelectionListener(className, supportedDefineOptions.get(j)));    
        		editor.setEditor(button, tableItem, j + 1);
        	}
        }
        
        mDefineChoiceTableViewer.setCellEditors(cellEditors);
        return container;
    }
    
    /**
     * Get all widgets which are supported for automation.
     * 
     * @return List of Node contains widgets informations.
     */
    protected List<Node> getAutoWigets()
    {
    	List<Node> ret = new ArrayList<Node>();
    	DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
    	DocumentBuilder builder = null;
    	Document doc = null;
		try {
			builder = factory.newDocumentBuilder();
		} catch (ParserConfigurationException e) {
			e.printStackTrace();
		}
		
    	try {
			doc = builder.parse(mXmlDumpFile);
		} catch (SAXException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
    	
    	NodeList nodes = doc.getElementsByTagName("node");
        for(int i=0; i<nodes.getLength(); i++)
        {
            Node node = nodes.item(i);
            if(node.getNodeType() == Node.ELEMENT_NODE)
            {
                Element element = (Element) node;
                if(supportedClasses.contains(element.getAttribute("class")))
                {
                	ret.add(node);
                }
            }
        }
    	return ret;
    }

    /**
     * Create contents of the button bar.
     * @param parent
     */
    @Override
    protected void createButtonsForButtonBar(Composite parent) {
        mExportButton = createButton(parent, IDialogConstants.OK_ID, "Export", true);
        mExportButton.addListener(SWT.Selection, new Listener() {
            @Override
            public void handleEvent(Event event) {
            	handleExportLmlFile();
            }
        });
        createButton(parent, IDialogConstants.CANCEL_ID, IDialogConstants.CANCEL_LABEL, false);
        updateButtonState();
    }

    /**
     * Return the initial size of the dialog.
     */
    @Override
    protected Point getInitialSize() {
        return new Point(800, 480);
    }

    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("Auto generate settings");
    }

    /**
     * Load data from UiAutomatorModel
     */
    private void loadDataFromModel() {
        mXmlDumpFile = UiAutomatorModel.getModel().getXmlDumpFile();
    }
    
    /**
	 * Export defined widgets to .lml file.
	 * 
	 * @param dest		lml file object.
	 * @param mItems	List of nodes.
	 */
	private void export2Lml(File dest, List<Node>mItems)
	{
		try {
			 //Create JAXB Context
            JAXBContext jaxbContext = JAXBContext.newInstance(Refsteps.class);
             
            //Create Marshaler
            Marshaller jaxbMarshaller = jaxbContext.createMarshaller();
 
            //Required formatting??
            jaxbMarshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);
            
            String returnParam = UiAutomatorModel.getModel().getCurrentActivityName() + WIDGET_DICT_NAME;
            String stepgroupName = UiAutomatorModel.getModel().getCurrentActivityName() + WIDGET_INIT_STEPGROUP_NAME;
            
            Refsteps refStep = new Refsteps();
            Stepgroup stepGroup = new Stepgroup(stepgroupName, returnParam);
            Refstep refInit = new Refstep(stepgroupName);
			Paramsetstep paramReturn = new Paramsetstep(returnParam + "=ddict{}", BooleanEnum.TRUE);
            
            stepGroup.addStep(paramReturn);            
            refStep.addStepgroup(stepGroup);
            refStep.addStepgroup(refInit);
            
            for (Node node : mItems)
			{
            	Element element = (Element) node;
            	String className = element.getAttribute("class");
            	List<String> attrs = dictExportOptions.get(className);
            	String paramStr = "{";
            	String widgetAttr = element.getAttribute(dictNamingSupport.get(className).key);
            	String patternStr = dictNamingSupport.get(className).value;
            	Pattern pattern = Pattern.compile(patternStr);
            	Matcher matcher = pattern.matcher(widgetAttr);
            	String widgetName = "";
            	
            	for (String attr : attrs)
            	{
            		paramStr += String.format("'%s':'%s',", attr,  element.getAttribute(attr));  
            	}
            	
            	paramStr = paramStr.replaceAll("[,]$", "");
            	paramStr += "}";
            	if (matcher.find())
            	{
            		widgetName += matcher.group(0);
            	}
            	
            	widgetName = widgetName.replace(" ", "_").replace("*", "");
				Paramsetstep paramsetStep = new Paramsetstep(String.format(WIDGET_DEFINE_TEMPLATE,	returnParam, 
																									widgetName, 
																									paramStr),
															null );
				stepGroup.addStep(paramsetStep);
			}
             
            //Writes XML file to file-system
            jaxbMarshaller.marshal(refStep, dest);
            
		} catch (JAXBException e) {
			e.printStackTrace();
		}
	}
	
	private void export2Resource(File dest, List<Node>mItems) {
		try {					
			FileOutputStream fis = new FileOutputStream(dest);
			String content = "";
			String elementsString = "";
			for (Node node : mItems)
			{
				Element element = (Element) node;
            	String className = element.getAttribute("class");
            	List<String> attrs = dictExportOptions.get(className);
            	String widgetAttr = element.getAttribute(dictNamingSupport.get(className).key);
            	String patternStr = dictNamingSupport.get(className).value;
            	Pattern pattern = Pattern.compile(patternStr);
            	Matcher matcher = pattern.matcher(widgetAttr);            	
				String elementName = "";
				String locatorName = "";
				String locatorValue = "";
				
				if (matcher.find())
            	{
					elementName += matcher.group(0);
            	}
				
				List<String> propertiesArr = dictExportOptions.get(className);
				if (propertiesArr.size() > 1)
				{
					fis.close();
					throw new UIAutomatorException(String.format(mapErrorStrings.get(ErrorCode.ERR_EXCEEDED_MAX_ITEMS), 
																	dest.getName()), 	
													mParentShell);
				}
				
				locatorName = propertiesArr.get(0);
				locatorValue = element.getAttribute(locatorName);	
				elementsString += String.format(ROBOT_RESOURCE_ELEMENT_DEFINE_TEMPLATE, elementName, locatorName, locatorValue);
			}
			
			content = String.format(ROBOT_RESOURCE_FILE_TEMPLATE, UiAutomatorModel.getModel().getCurrentActivityName(), elementsString);			
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

	/**
	 * Handler for exporting lml file.
	 */
    private void handleExportLmlFile() {    	
    	List<Node> ls = getAutoWigets();
    	SaveFileDialogHelper exportDialog = new SaveFileDialogHelper("lml|resource", null, UiAutomatorModel.getModel().getCurrentActivityName()) 
    	{			
			@Override
			public void AproveAction(File file, Object... args) {
				@SuppressWarnings("unchecked")
				List<Node> itemList = List.class.isInstance(args[0]) ? (List<Node>)args[0] : null; 
				if(itemList != null)
				{					
					MessageBox msgBox = new MessageBox(mParentShell);
			        try        
			        {
			        	String extension = FilenameUtils.getExtension(file.getName());
			        	if (extension.equalsIgnoreCase("lml"))
			        	{
			        		export2Lml(file, itemList);      
			        	}
			        	else if (extension.equalsIgnoreCase("resource")) {
							export2Resource(file, itemList);
						}
			            msgBox.setMessage(MSGBOX_SUCCESS_STR);             
			            msgBox.open();
			        }
			        catch (Exception e) {
			        	msgBox.setMessage(String.format(MSGBOX_FAILURE_STR, e.toString()));  
			        	msgBox.open();
			        }
				}
			}
		};
		
		exportDialog.openDialog(ls);
    }

    /**
     * Update Export button state.
     * Export button is only enable if the dump file exists. 
     */
    private void updateButtonState() {
        mExportButton.setEnabled(mXmlDumpFile != null && mXmlDumpFile.isFile());
    }
    
    /**
     * CustomSelectionListener is a custom Listener supporting for getting chosen attributes for widget definition.
     * @author ugc1hc
     *
     */
    private class CustomSelectionListener implements SelectionListener{
    	protected String className;
    	protected String attribute;
    	
    	/**
    	 * Constructor for CustomSelectionListener
    	 * @param className class name of the widget
    	 * @param attribute	attribute of widget.
    	 */
    	public CustomSelectionListener(String className, String attribute)
    	{
    		super();
    		this.className = className;
    		this.attribute = attribute;
    	}
    	
		@Override
		public void widgetSelected(SelectionEvent e) {
			Button button = ((Button) e.widget);
			if(!button.getSelection())
			{
				if(dictExportOptions.get(className).contains(attribute))
				{
					dictExportOptions.get(className).remove(attribute);
				}
			}
			else
			{
				if(!dictExportOptions.get(className).contains(attribute))
				{
					dictExportOptions.get(className).add(attribute);
				}
			}
		}

		@Override
		public void widgetDefaultSelected(SelectionEvent e) {			
		}    	
    }
}
