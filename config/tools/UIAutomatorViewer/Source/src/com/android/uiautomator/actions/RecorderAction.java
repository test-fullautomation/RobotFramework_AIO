package com.android.uiautomator.actions;

import com.android.uiautomator.UiAutomatorViewer;
import com.android.uiautomator.utils.SaveFileDialogHelper;
import com.android.uiautomator.utils.steptypes.BooleanEnum;
import com.android.uiautomator.utils.steptypes.Paramsetstep;
import com.android.uiautomator.utils.steptypes.Refsteps;
import com.android.uiautomator.utils.steptypes.Stepgroup;
import com.android.uiautomator.utils.steptypes.Widgetcmdstep;

import org.apache.commons.lang3.mutable.MutableBoolean;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.Status;
import org.eclipse.jface.action.Action;
import org.eclipse.jface.dialogs.ErrorDialog;
import org.eclipse.jface.dialogs.MessageDialog;
import org.eclipse.jface.dialogs.ProgressMonitorDialog;
import org.eclipse.jface.operation.IRunnableWithProgress;
import org.eclipse.jface.resource.ImageDescriptor;
import org.eclipse.swt.widgets.Display;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.lang.reflect.InvocationTargetException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;

/**
 * RecorderAction class is for supporting actions recording.
 * 
 * @author ugc1hc
 *
 */
public class RecorderAction extends Action {

	UiAutomatorViewer mViewer;	
	static final int RUNNING_STATE = 1;
	static final int NORMAL_STATE = 0;
	static final int RECORDING_MAX_TIME = 3600000;	
	static final String WIDGET_PLAYBACK_STEPGROUP_NAME = ".ActionsPlayback";
	
	static final String EVENT_TYPE_REG = "(?<=EventType:\\s)(.*?)(?=;)";
	static final Pattern eventTypePattern = Pattern.compile(EVENT_TYPE_REG);
	
	static final String EVENT_PROPERTIES_REG = "(?=ClassName)(.*?)(?!.*\\s\\])";
	static final Pattern eventPropsPattern = Pattern.compile(EVENT_PROPERTIES_REG);
	
	static final String EVENT_CURRENT_IDX_REG = "(?<=CurrentItemIndex: )(.*?)(?=;)";
	static final Pattern eventCurrentIdxPattern = Pattern.compile(EVENT_CURRENT_IDX_REG);
	
	
	int state = NORMAL_STATE;
	List<String> records = new ArrayList<String>();

	static Map<String, String> supportedActionList = new HashMap<String, String>() {
		private static final long serialVersionUID = 9120224700594339594L;
		{
			put("TYPE_VIEW_CLICKED", "set click");
			put("TYPE_VIEW_TEXT_CHANGED", "set text");
			put("TYPE_VIEW_SELECTED", "set value");
		}
	};

																
	static Map<String, String> convertClassNameDict = new HashMap<String, String>() {
		private static final long serialVersionUID = 8442697657816432462L;
		{
			put("ClassName", "class");
			put("Text", "text");
//			put("CurrentItemIndex", "value");
		}
	};
	/**
	 * Constructor of RecorderAction class.
	 * 
	 * @param viewer
	 */
	public RecorderAction(UiAutomatorViewer viewer) {
		mViewer = viewer;
		setText("&Action recorder");
	}	

	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.Action#getImageDescriptor()
	 */
	@Override
	public ImageDescriptor getImageDescriptor() {
		if(this.state == NORMAL_STATE)
			return ImageHelper.loadImageDescriptorFromResource("images/recorder.png");
		else
			return ImageHelper.loadImageDescriptorFromResource("images/stop_record.png");
	}

	/* (non-Javadoc)
	 * @see org.eclipse.jface.action.Action#run()
	 */
	@Override
	public void run() {
		state = RUNNING_STATE;
		firePropertyChange(IMAGE, null, null);		
		ProgressMonitorDialog dialog = new ProgressMonitorDialog(mViewer.getShell()) 
		{					
			private boolean cancelConfirmed() {
				Display d = Display.getDefault();
				final MutableBoolean cancel = new MutableBoolean(false);
				d.syncExec(new Runnable() {
					@Override
				    public void run() 
					{
						cancel.setValue(MessageDialog.openQuestion(null,
								"Stop recording",
								"Are you sure you want to stop the actions recording?"));
					}
				});				
				return cancel.booleanValue();
			}			
			
			@Override
			protected void cancelPressed() {
				if (cancelConfirmed())
			    {
					ProcRunner.state = ProcRunner.STOP_STATE;
					SaveFileDialogHelper exportFile = new SaveFileDialogHelper("lml", null, null) {						
						@Override
						public void AproveAction(File file, Object... args) {
							@SuppressWarnings("unchecked")
							List<String> recordActions = List.class.isInstance(args[0]) ? (List<String>)args[0] : null; 
							if(records != null)
								export2Lml(file, recordActions);
						}
					};
					
					exportFile.openDialog(records);
					super.cancelPressed();					
			    }
				
			}
		};		
		
		try 
		{
			records.removeAll(records);
			dialog.run(true, true, new IRunnableWithProgress() {
				private void showError(final String msg, final Throwable t, IProgressMonitor monitor) {
					monitor.done();
					mViewer.getShell().getDisplay().syncExec(new Runnable() {
						@Override
						public void run() {
							Status s = new Status(IStatus.ERROR, "Action recording", msg, t);
							ErrorDialog.openError(mViewer.getShell(), "Error", "Cannot record actions", s);
						}
					});
				}				
				
				@Override
				public void run(IProgressMonitor monitor) throws InvocationTargetException, InterruptedException {
					ProcRunner procRunner = null;
					String serial = System.getenv("ANDROID_SERIAL");
					int retCode = -1;

					monitor.beginTask("Recording action...", IProgressMonitor.UNKNOWN);
					monitor.subTask("Restart ADB server. Please wait...");
					procRunner = getAdbRunner(serial, "kill-server");
					try {						
						retCode = procRunner.run(30000);
						if (retCode != 0) {
							throw new IOException(
									"Non-zero return code from kill-server command:\n" + procRunner.getOutputBlob());
						}						
					} catch (IOException e) {
						e.printStackTrace();
						showError("Failed to kill-server", e, monitor);
						return;
					}
					
					procRunner = getAdbRunner(serial, "devices");
					try {						
						retCode = procRunner.run(30000);
						if (retCode != 0) {
							throw new IOException(
									"Non-zero return code from restart server command:\n" + procRunner.getOutputBlob());
						}						
					} catch (IOException e) {
						e.printStackTrace();
						showError("Failed to restart server", e, monitor);
						return;
					}
					
//					Thread.sleep(2000);
					
//					monitor.beginTask("Recording action...", IProgressMonitor.UNKNOWN);
					monitor.subTask("Start recording...");
					procRunner = getAdbRunner(serial, "shell", "uiautomator", "events");
					try {
						retCode = procRunner.run(RECORDING_MAX_TIME);						
						if (retCode != 0 && retCode != 1) {
							System.out.println(retCode);
							throw new IOException(
									"Non-zero return code from record command:\n" + procRunner.getOutputBlob());
						}						
					} catch (IOException e) {
						e.printStackTrace();
						showError("Failed to record actions", e, monitor);
						return;
					}
					
					records.addAll(0, procRunner.mOutput);
					monitor.done();
				}
			});			
		} 
		catch (InvocationTargetException e) {
			e.printStackTrace();
		}
		catch (InterruptedException e) {
			e.printStackTrace();
		}
		
		state = NORMAL_STATE;
		firePropertyChange(IMAGE, null, null);
	}

	/*
	 * Convenience function to construct an 'adb' command, e.g. use 'adb' or 'adb -s
	 * NNN'
	 */
	private ProcRunner getAdbRunner(String serial, String... command) {
		List<String> cmd = new ArrayList<String>();
		cmd.add("adb");
		if (serial != null) {
			cmd.add("-s");
			cmd.add(serial);
		}
		for (String s : command) {
			cmd.add(s);
		}
		return new ProcRunner(cmd);
	}

	/**
	 * Convenience class to run external process.
	 *
	 * Always redirects stderr into stdout, has timeout control
	 *
	 */
	private static class ProcRunner {

		ProcessBuilder mProcessBuilder;		
		static final int STOP_STATE = 1;
		static final int RUN_STATE = 0;
		static int state = RUN_STATE; 
		public List<String> mOutput = new ArrayList<String>();

		public ProcRunner(List<String> command) {
			mProcessBuilder = new ProcessBuilder(command).redirectErrorStream(true);
		}

		public int run(long timeout) throws IOException {
			final Process p = mProcessBuilder.start();
			ProcRunner.state = ProcRunner.RUN_STATE;
			Thread threadRunningCmd = new Thread() {
				@Override
				public void run() {
					String line;
					mOutput.clear();					
					System.out.println("[START]===========================RECORD ADD=============================");
					try {
						BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream(), "utf-8"));
						while ((ProcRunner.state == RUN_STATE) && (line = br.readLine()) != null) {
							System.out.println(line); // for debug
							mOutput.add(line);
						}
						br.close();
					} catch (IOException e) {
						e.printStackTrace();
					}
					System.out.println("[END]===========================RECORD ADD=============================");
				};
			};
			
			Thread threadObserveState = new Thread() {
				@Override
				public void run() 
				{					
					while (ProcRunner.state == RUN_STATE)
					{
						try {
							Thread.sleep(50);
						} catch (InterruptedException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
						}
					}
					p.destroyForcibly();
				};
			};
			
			threadObserveState.start();
			threadRunningCmd.start();					
			try {
				threadRunningCmd.join(timeout);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			if (threadRunningCmd.isAlive()) {
				throw new IOException("external process not terminating.");
			}
			
			ProcRunner.state = STOP_STATE;					
			try {				
				return p.waitFor();
			} catch (InterruptedException e) {
				e.printStackTrace();
				throw new IOException(e);
			}
		}

		/**
		 * @return
		 */
		public String getOutputBlob() {
			
			StringBuilder sb = new StringBuilder();
			for (String line : mOutput) {
				sb.append(line);
				sb.append(System.getProperty("line.separator"));
			}
			return sb.toString();
		}
	}
	
	/**
	 * Export defined widgets to .lml file.
	 * 
	 * @param dest		lml file object.
	 * @param mItems	List of widget items.
	 */
	private void export2Lml(File dest, List<String>records)
	{
		try {
			 //Create JAXB Context
            JAXBContext jaxbContext = JAXBContext.newInstance(Refsteps.class);
             
            //Create Marshaler
            Marshaller jaxbMarshaller = jaxbContext.createMarshaller();
 
            //Required formatting??
            jaxbMarshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, Boolean.TRUE);

            String fileName = dest.getName();
            int pos = fileName.lastIndexOf(".");
            if (pos > 0) {
            	fileName = fileName.substring(0, pos);
            }
            
            String stepgroupName = fileName + WIDGET_PLAYBACK_STEPGROUP_NAME;
            
            Refsteps refSteps = new Refsteps();
            Stepgroup stepGroup = new Stepgroup(stepgroupName, null);
            Paramsetstep paramDevice = new Paramsetstep("deviceName=android", BooleanEnum.TRUE);
            
            String action = "";
            String widgetDefineStr = "";
            
            refSteps.addStepgroup(stepGroup);
            stepGroup.addStep(paramDevice);
            int nCurrentIndex = 0;
            Boolean bCurrentIndexChanged = true;
            String sCurrentText = "";
            
            for (String record : records)
            {  
				System.out.println("[START]===========================RECORD PROCESS=============================");
                System.out.println("Record:" + record);
            	Matcher matcher = eventTypePattern.matcher(record);
                if (matcher.find())
                {
                	action = matcher.group(1);               
					System.out.println("Action:" + action);
	                if(!action.isEmpty() && supportedActionList.containsKey(action))
	                {
	                	matcher = eventPropsPattern.matcher(record);
	                    if (matcher.find())
	                    {
							System.out.println("matcher:" + matcher.group(1));
	                    	String [] propArray = matcher.group(1).split(";");
	                    	String widget_args = "";
	                    	String className = "";
	                    	widgetDefineStr = "{";
	                    	for (String prop : propArray)
	                    	{
	                    		String propName = prop.split(":")[0].trim();
	                    		String propValue = prop.split(":")[1].trim();
	                    		
	                    		if(convertClassNameDict.containsKey(propName))
	                    		{
	                    			propName = convertClassNameDict.get(propName);
	                    			propValue = propValue.replaceAll("[\\[,\\]]", "");
	                    			if (!propValue.isEmpty())
	                    			{
		                    			widgetDefineStr += String.format("'%s':'%s',", propName, propValue );
		                    			if (propName.equals("class"))
		                    			{
		                    				className = propValue;
		                    			}
	                    			}
	                    		}
	                    		else if(propName.equalsIgnoreCase("CurrentItemIndex"))
	                    		{
	                    			widget_args = propValue;
	                    		}
	                    	}
	                    	
	                    	widgetDefineStr = widgetDefineStr.replaceAll("[,]$", "");
	                    	widgetDefineStr += "}";	                    	
	                    	Widgetcmdstep cmdStep = new Widgetcmdstep("${deviceName}", widgetDefineStr, null);
		                	cmdStep.setAction(supportedActionList.get(action));
							System.out.println("widget_args:" + widget_args);
		                	if (className.equalsIgnoreCase("android.widget.SeekBar"))
		                		cmdStep.setWidgetArgs(widget_args);
		                	else if(className.equalsIgnoreCase("android.widget.EditText"))
		                	{
			                	Pattern pattern = Pattern.compile("(?<='text':').*(?='})");
			                	matcher = pattern.matcher(widgetDefineStr);
			                	if (matcher.find())
			                	{
									if (bCurrentIndexChanged) {
                                        sCurrentText = matcher.group(0);
                                        bCurrentIndexChanged = false;
                                    } else {
                                        sCurrentText += (matcher.group(0).substring(sCurrentText.length()));
                                    }
			                		cmdStep.setWidgetArgs(sCurrentText);
			                	}
			                		
		                		widgetDefineStr = widgetDefineStr.replaceAll("'text':.*(?!})", "");
		                		widgetDefineStr += String.format(" 'index': '%d'", nCurrentIndex  + 1);
			                    widgetDefineStr += "}";	  
			                    cmdStep.setWidget(widgetDefineStr);
		                	}		                	
		                	stepGroup.addStep(cmdStep);
	                    }
	                	
	                }
	                else if(action.equals("TYPE_VIEW_FOCUSED"))
	                {
	                	matcher = eventCurrentIdxPattern.matcher(record);
	                	if (matcher.find())
	                    {
	                		nCurrentIndex = Integer.parseInt(matcher.group(1));
							bCurrentIndexChanged = true;
	                    }
	                }
                }
				System.out.println("[END]===========================RECORD PROCESS=============================");
            }
             
            //Writes XML file to file-system
            jaxbMarshaller.marshal(refSteps, dest);
            
		} catch (JAXBException e) {
			e.printStackTrace();
		}
	}
}
