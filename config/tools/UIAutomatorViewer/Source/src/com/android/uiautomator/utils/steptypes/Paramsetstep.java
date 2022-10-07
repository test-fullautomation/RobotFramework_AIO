package com.android.uiautomator.utils.steptypes;

import java.io.Serializable;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlRootElement;


@XmlRootElement(name = "paramsetstep")
@XmlAccessorType(XmlAccessType.PROPERTY)
public class Paramsetstep implements Serializable {
 
    private static final long serialVersionUID = 1L;
    
   
    @XmlAttribute(name = "params")
    private String params;
    
    @XmlAttribute(name = "optional")
    private BooleanEnum optional;
     
    public Paramsetstep() {
        super();
    }
 
    public Paramsetstep(String params, BooleanEnum optional) {
        super();
        this.params = params != null ? params : null;;
        this.optional = optional != null ? optional : null;
    }
 
    //Setters and Getters
// 
//    @Override
//    public String toString() {
//        return "";
//    }
}