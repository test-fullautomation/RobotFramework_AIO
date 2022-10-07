package com.android.uiautomator.utils.steptypes;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlRootElement;


@XmlRootElement(name = "stepgroup")
@XmlAccessorType(XmlAccessType.PROPERTY)
public class Stepgroup implements Serializable {
 
    private static final long serialVersionUID = 1L;
    
    @XmlAttribute(name = "name")
    private String name;
    
    @XmlAttribute(name = "return")
    private String returnVal;
    
    @XmlAttribute(name = "tracelevel")
    private String tracelevel = "verbose";
    
    @XmlElement(name = "paramsetstep")
    private List<Paramsetstep> paramsetstepList = new ArrayList<>();;
    
    @XmlElement(name = "widgetcmdstep")
    private List<Widgetcmdstep> widgetcmdstepList = new ArrayList<>();;
    
    public Stepgroup() {
        super();
    }
 
    public Stepgroup(String name, String returnVal) {
        super();
        this.name = (name != null) ? name : null;
        this.returnVal = (returnVal != null) ? returnVal : null;
    }
    
    public void addStep(Serializable step)
    {
    	if( Paramsetstep.class.isInstance(step))
    	{
    		paramsetstepList.add((Paramsetstep) step);
    	}
    	else if(Widgetcmdstep.class.isInstance(step))
    	{
    		widgetcmdstepList.add((Widgetcmdstep) step);
    	}
    		
    }
 
    //Setters and Getters
// 
//    @Override
//    public String toString() {
//        return "";
//    }
}