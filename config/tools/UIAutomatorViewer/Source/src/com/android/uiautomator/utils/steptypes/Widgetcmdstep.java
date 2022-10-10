package com.android.uiautomator.utils.steptypes;

import java.io.Serializable;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlRootElement;
import javax.xml.bind.annotation.XmlValue;


@XmlRootElement(name = "widgetcmdstep")
@XmlAccessorType(XmlAccessType.FIELD)
public class Widgetcmdstep implements Serializable {
 
    private static final long serialVersionUID = 1L;
    
    @XmlAttribute(name = "device")
    private String device;
    
    @XmlAttribute(name = "widget")
    private String widget;
    
    @XmlAttribute(name = "widgetargs")
    private String widgetArgs;
    
    @XmlValue
    private String action;    
     
    public Widgetcmdstep() {
        super();
    }
 
    public Widgetcmdstep(String device, String widget, String widgetArgs) {
        super();
        this.device = device;
        this.setWidget(widget);
        this.setWidgetArgs(widgetArgs);
    }

    public String getAction() {
		return this.action;
	}

    public void setAction(String value) {
		this.action = value;
	}

    public String getWidgetArgs() {
		return this.widgetArgs;
	}

    public void setWidgetArgs(String value) {
		this.widgetArgs = value;
	}

    public String getWidget() {
		return widget;
	}

    public void setWidget(String widget) {
		this.widget = widget;
	}
 
    //Setters and Getters
// 
//    @Override
//    public String toString() {
//        return "";
//    }
}