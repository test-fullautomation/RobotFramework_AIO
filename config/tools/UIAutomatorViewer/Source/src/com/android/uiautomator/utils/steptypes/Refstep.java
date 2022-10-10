package com.android.uiautomator.utils.steptypes;

import java.io.Serializable;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlRootElement;
import javax.xml.bind.annotation.XmlValue;
 
@XmlRootElement(name = "refstep")
@XmlAccessorType(XmlAccessType.PROPERTY)
public class Refstep implements Serializable {
 
    private static final long serialVersionUID = 1L;

    @XmlValue
    private String value;
     
    public Refstep() {
        super();
    }
 
    public Refstep(String value) {
        super();
        this.value = value;
    }
    //Setters and Getters
 
    @Override
    public String toString() {
        return "";
    }
}