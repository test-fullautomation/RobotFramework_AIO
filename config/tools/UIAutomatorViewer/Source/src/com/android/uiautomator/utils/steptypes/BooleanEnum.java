package com.android.uiautomator.utils.steptypes;

import javax.xml.bind.annotation.XmlEnum;
import javax.xml.bind.annotation.XmlEnumValue;
import javax.xml.bind.annotation.XmlType;

@XmlType(name = "Enum")
@XmlEnum
public enum BooleanEnum {

    @XmlEnumValue("true")
    TRUE("true"),
    @XmlEnumValue("false")
    FALSE("false");
    
    private final String value;

    BooleanEnum(String v) {
        value = v;
    }

    public String value() {
        return value;
    }

    public static BooleanEnum fromValue(String v) {
        for (BooleanEnum c: BooleanEnum.values()) {
            if (c.value.equals(v)) {
                return c;
            }
        }
        throw new IllegalArgumentException(v);
    }

}