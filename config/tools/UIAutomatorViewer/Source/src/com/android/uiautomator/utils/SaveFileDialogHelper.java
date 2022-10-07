package com.android.uiautomator.utils;

import java.io.File;

import javax.swing.JFileChooser;
import javax.swing.filechooser.FileFilter;
import javax.swing.filechooser.FileNameExtensionFilter;

import org.apache.commons.io.FilenameUtils;

import java.lang.reflect.Array;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;

/**
 * The SaveFileDialogHelper is for supporting create a FileChooser Dialog with defined extension type, working directory and suggestion name.
 * User is required to override the AproveAction method for specific purpose.
 * 
 * @author ugc1hc
 *
 */
public abstract class SaveFileDialogHelper {
	
	String suggestionName 	= "";
	String extensionType  	= "*.*";
	String workingDirectory = "user.dir";
	
	/**
	 * Constructor of SaveFileDialogHelper class
	 * 
	 * @param extensiontype	Save file extension type
	 * @param workingdir	Directory where the file is save
	 * @param defaultname	Suggestion file name
	 */
	public SaveFileDialogHelper(String extensiontype, String workingdir, String defaultname) {	
		extensionType = (extensiontype == null) ? extensionType		: extensiontype;
		suggestionName = (defaultname == null) 	? suggestionName	: defaultname;
		workingDirectory = (workingdir == null) ? workingDirectory	: workingdir;
	}
	
	
	/**
	 * Show the dialog.
	 * 
	 * @param args	Optional input arguments.
	 */
	public void openDialog(Object... args)
	{
		JFileChooser chooser = new JFileChooser();
		String [] extensionArr = extensionType.split("\\|");
		ArrayList<FileNameExtensionFilter> fileExtFilterArr = new ArrayList<FileNameExtensionFilter>();
		for (String etx : extensionArr) {
			FileNameExtensionFilter fileExtFilter = new FileNameExtensionFilter(String.format("%s files (*.%s)", etx, etx), etx);
			chooser.addChoosableFileFilter(fileExtFilter);
			fileExtFilterArr.add(fileExtFilter);
		}
		
		File workingDirectory = new File(System.getProperty("user.dir"));
        chooser.setFileSelectionMode(JFileChooser.FILES_AND_DIRECTORIES);
        chooser.setSelectedFile(new File(suggestionName));
        chooser.setFileFilter(fileExtFilterArr.get(0));
        chooser.setCurrentDirectory(workingDirectory);
        int sf = chooser.showSaveDialog(null);
        if(sf == JFileChooser.APPROVE_OPTION){
	        File file = chooser.getSelectedFile();
	        String extensionSelected = ""; 
	        try
	        {
	        	Field ext = chooser.getFileFilter().getClass().getDeclaredField("extensions");
	        	ext.setAccessible(true);
	            Object [] value = (String [])ext.get(chooser.getFileFilter());
	            extensionSelected = value[0].toString();
	        }
	        catch (Exception e) {
				// TODO: handle exception
			}
	        
	        if (!FilenameUtils.getExtension(file.getName()).equalsIgnoreCase(extensionSelected)) {
	            file = new File(file.getAbsolutePath() + "." + extensionSelected); 
	        }
	        
	        AproveAction(file, args);
        }
	}
	
	
	/**
	 * Action handler for JFileChooser.APPROVE_OPTION
	 * Must be override when using.
	 * 
	 * @param file	Save file object.
	 * @param args	Optional input arguments.
	 */
	public abstract void AproveAction(File file, Object... args);
}
