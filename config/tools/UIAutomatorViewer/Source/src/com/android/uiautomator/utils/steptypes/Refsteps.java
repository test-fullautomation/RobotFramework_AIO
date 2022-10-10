package com.android.uiautomator.utils.steptypes;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;
 
@XmlRootElement(name = "refsteps")
@XmlAccessorType(XmlAccessType.PROPERTY)
public class Refsteps implements Serializable {
 
    private static final long serialVersionUID = 1L;

    @XmlAttribute(name = "xmlns:xsi")
    private String xmlns = "http://www.w3.org/2001/XMLSchema-instance";
    
    @XmlAttribute(name = "xsi:noNamespaceSchemaLocation")
    private String noNamespaceSchemaLocation = "http://www-app.hi.de.bosch.com/hi-cm-datastore/xsd/refsteps.xsd";
    
    @XmlElement(name = "stepgroup")
    private List<Stepgroup> stepgroupList = new ArrayList<>();
    
    @XmlElement(name = "refstep")
    private List<Refstep> refstepList = new ArrayList<>();
     
    public Refsteps() {
        super();
    }
 
    public Refsteps(String xmlns, String noNamespaceSchemaLocation) {
        super();
        this.xmlns = xmlns;
        this.noNamespaceSchemaLocation = noNamespaceSchemaLocation;
    }
 
    public void addStepgroup(Serializable stepGroup)
    {
    	if( Stepgroup.class.isInstance(stepGroup))
    	{
    		stepgroupList.add((Stepgroup) stepGroup);
    	}
    	else if(Refstep.class.isInstance(stepGroup))
    	{
    		refstepList.add((Refstep) stepGroup);
    	}
    }
    //Setters and Getters
 
    @Override
    public String toString() {
        return "";
    }
}