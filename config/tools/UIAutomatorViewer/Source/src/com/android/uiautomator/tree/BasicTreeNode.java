/*
 * Copyright (C) 2012 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.android.uiautomator.tree;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;


public class BasicTreeNode {
    private static final BasicTreeNode[] CHILDREN_TEMPLATE = new BasicTreeNode[] {
            
        };
    protected BasicTreeNode mParent;
    protected final List<BasicTreeNode> mChildren = new ArrayList<BasicTreeNode>();
    protected final List<String> mUnSupportedClasses = new ArrayList<String>(Arrays.asList(
                "android.widget.FrameLayout", "android.widget.LinearLayout",
                "android.widget.ScrollView"));
    public int x;
    public int y;
    public int width;
    public int height;

    // whether the boundary fields are applicable for the node or not
    // RootWindowNode has no bounds, but UiNodes should
    protected boolean mHasBounds = false;

    public void addChild(BasicTreeNode child) {
        if (child == null) {
            throw new NullPointerException("Cannot add null child");
        }

        if (mChildren.contains(child)) {
            throw new IllegalArgumentException("node already a child");
        }

        mChildren.add(child);
        child.mParent = this;
    }

    public List<BasicTreeNode> getChildrenList() {
        return Collections.unmodifiableList(mChildren);
    }

    public BasicTreeNode[] getChildren() {
        return mChildren.toArray(CHILDREN_TEMPLATE);
    }

    public BasicTreeNode getParent() {
        return mParent;
    }

    public boolean hasChild() {
        return mChildren.size() != 0;
    }

    public int getChildCount() {
        return mChildren.size();
    }

    public void clearAllChildren() {
        for (BasicTreeNode child : mChildren) {
            child.clearAllChildren();
        }

        mChildren.clear();
    }

    /**
     *
     * Find nodes in the tree containing the coordinate
     *
     * The found node should have bounds covering the coordinate, and none of its children's
     * bounds covers it. Depending on the layout, some app may have multiple nodes matching it,
     * the caller must provide a {@link IFindNodeListener} to receive all found nodes
     *
     * @param px
     * @param py
     * @return
     */
    public boolean findLeafMostNodesAtPoint(int px, int py,
        IFindNodeListener listener) {
        boolean foundInChild = false;

        for (BasicTreeNode node : mChildren) {
            foundInChild |= node.findLeafMostNodesAtPoint(px, py, listener);
        }

        // checked all children, if at least one child covers the point, return directly
        if (foundInChild) {
            return true;
        }

        // check self if the node has no children, or no child nodes covers the point
        if (mHasBounds) {
            if ((x <= px) && (px <= (x + width)) && (y <= py) &&
                    (py <= (y + height))) {
                listener.onFoundNode(this);

                return true;
            } else {
                return false;
            }
        } else {
            return false;
        }
    }

    public void getAllSupportWidget(ArrayList<AttributePair> arrRes) {
        //    	ArrayList<AttributePair> arrRes = null;
        if (this.hasChild() == false) {
            if (!mUnSupportedClasses.contains(
                        ((AttributePair) this.getAttributesArray()[3]).value)) {
                arrRes.add(new AttributePair("ele",
                        String.format("{%s:%s}",
                            ((AttributePair) this.getAttributesArray()[2]).key,
                            ((AttributePair) this.getAttributesArray()[2]).value)));
            }

            return;
        }

        for (BasicTreeNode node : mChildren) {
            if (!mUnSupportedClasses.contains(
                        ((AttributePair) node.getAttributesArray()[3]).value)) {
                arrRes.add(new AttributePair("ele",
                        String.format("{%s:%s}",
                            ((AttributePair) this.getAttributesArray()[2]).key,
                            ((AttributePair) this.getAttributesArray()[2]).value)));
            }

            node.getAllSupportWidget(arrRes);
        }

        //		return arrRes;
    }

    //    public String getIdentifyString(BasicTreeNode node)
    //    {
    //    	String sRes = "";
    //    	String sKey = "";
    //    	String sValue = "";
    //    	String className = ((AttributePair)node.getAttributesArray()[3]).value;
    //    	if (className.endsWith("TextView"))
    //    	{
    //    		sKey = "txt_" + ((AttributePair)node.getAttributesArray()[1]).value.split(" ")[0];
    //    		sValue = "text:" + ((AttributePair)node.getAttributesArray()[1]).value.split(" ")[0];
    //    	}
    //    	else
    //    	{
    //    	 
    //    	}
    //    	return sRes;
    //    }
    public Object[] getAttributesArray() {
        return null;
    }

    public static interface IFindNodeListener {
        void onFoundNode(BasicTreeNode node);
    }
}
