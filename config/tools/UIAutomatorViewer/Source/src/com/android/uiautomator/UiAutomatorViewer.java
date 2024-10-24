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
package com.android.uiautomator;

import com.android.uiautomator.actions.AddModWidgetAction;
import com.android.uiautomator.actions.ExpandAllAction;
import com.android.uiautomator.actions.ExportDefinedAction;
import com.android.uiautomator.actions.GenerateAction;
import com.android.uiautomator.actions.OpenFilesAction;
import com.android.uiautomator.actions.RecorderAction;
import com.android.uiautomator.actions.ScreenshotAction;
import com.android.uiautomator.tree.AttributePair;
import com.android.uiautomator.tree.BasicTreeNode;
import com.android.uiautomator.tree.BasicTreeNodeContentProvider;
import com.android.uiautomator.utils.Constants.AddModWidget;

import org.eclipse.jface.action.Action;
import org.eclipse.jface.action.ToolBarManager;
import org.eclipse.jface.layout.TableColumnLayout;
import org.eclipse.jface.viewers.ArrayContentProvider;
import org.eclipse.jface.viewers.CellEditor;
import org.eclipse.jface.viewers.CheckStateChangedEvent;
import org.eclipse.jface.viewers.CheckboxTableViewer;
import org.eclipse.jface.viewers.ColumnLabelProvider;
import org.eclipse.jface.viewers.ColumnWeightData;
import org.eclipse.jface.viewers.EditingSupport;
import org.eclipse.jface.viewers.ICheckStateListener;
import org.eclipse.jface.viewers.ISelectionChangedListener;
import org.eclipse.jface.viewers.IStructuredSelection;
import org.eclipse.jface.viewers.LabelProvider;
import org.eclipse.jface.viewers.SelectionChangedEvent;
import org.eclipse.jface.viewers.StructuredSelection;
import org.eclipse.jface.viewers.TableViewer;
import org.eclipse.jface.viewers.TableViewerColumn;
import org.eclipse.jface.viewers.TextCellEditor;
import org.eclipse.jface.viewers.TreeViewer;
import org.eclipse.jface.window.ApplicationWindow;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.KeyEvent;
import org.eclipse.swt.events.KeyListener;
import org.eclipse.swt.events.MenuDetectEvent;
import org.eclipse.swt.events.MenuDetectListener;
import org.eclipse.swt.events.MouseAdapter;
import org.eclipse.swt.events.MouseEvent;
import org.eclipse.swt.events.MouseMoveListener;
import org.eclipse.swt.events.PaintEvent;
import org.eclipse.swt.events.PaintListener;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.events.SelectionListener;
import org.eclipse.swt.graphics.GC;
import org.eclipse.swt.graphics.Image;
import org.eclipse.swt.graphics.Point;
import org.eclipse.swt.graphics.Rectangle;
import org.eclipse.swt.layout.FillLayout;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Canvas;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Event;
import org.eclipse.swt.widgets.Group;
import org.eclipse.swt.widgets.Listener;
import org.eclipse.swt.widgets.Menu;
import org.eclipse.swt.widgets.MenuItem;
import org.eclipse.swt.widgets.Monitor;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Table;
import org.eclipse.swt.widgets.TableColumn;
import org.eclipse.swt.widgets.TableItem;
import org.eclipse.swt.widgets.Tree;


public class UiAutomatorViewer extends ApplicationWindow {
    private static final int FIXED_RHS_WIDTH = 350;
    private static final int FIXED_DETAIL_VIEW_HEIGHT = 200;
    private static final int IMG_BORDER = 2;
    private Canvas mScreenshotCanvas;
    private TreeViewer mTreeViewer;
    private Action mOpenFilesAction;
    private Action mExpandAllAction;
    private ScreenshotAction mScreenshotAction;
    private TableViewer mTableViewerNode;
    private TableViewer mTableViewerWidget;
    private AddModWidgetAction mAddWidgetAction;
    private AddModWidgetAction mModifyWidgetAction;
    private AddModWidgetAction mDeleteWidgetAction;
    private ExportDefinedAction mExportLmlAction;
    private RecorderAction mRecorderAction;
    private GenerateAction mGenerateAction;
    private float mScale = 1.0f;
    private Image mCachedScaleImage = null;
    private String sActivity = "";

    /**
     * Create the application window.
     */
    public UiAutomatorViewer() {
        super(null);
        setShellStyle(SWT.RESIZE | SWT.CLOSE | SWT.MIN);
        createActions();
    }

    /**
     * Create contents of the application window.
     *
     * @param parent
     */
    @Override
    protected Control createContents(Composite parent) {
        UiAutomatorModel.createInstance(this);

        Composite basePane = new Composite(parent, SWT.NONE);
        basePane.setLayout(new GridLayout(3, false));
        mScreenshotCanvas = new Canvas(basePane, SWT.NONE);
        mScreenshotCanvas.addMouseListener(new MouseAdapter() {
                @Override
                public void mouseUp(MouseEvent e) {
                    UiAutomatorModel.getModel().toggleExploreMode();
                }
            });
        mScreenshotCanvas.setBackground(getShell().getDisplay()
                                            .getSystemColor(SWT.COLOR_BLACK));
        mScreenshotCanvas.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true,
                true, 1, 3));
        mScreenshotCanvas.addPaintListener(new PaintListener() {
                @Override
                public void paintControl(PaintEvent e) {
                    if (mCachedScaleImage != null) {
                        // shifting the image here, so that there's a border around screen shot
                        // this makes highlighting red rectangles on the screen shot edges more visible
                        e.gc.drawImage(mCachedScaleImage, IMG_BORDER, IMG_BORDER);

                        Rectangle rect = UiAutomatorModel.getModel()
                                                         .getCurrentDrawingRect();

                        if (rect != null) {
                            e.gc.setForeground(e.gc.getDevice()
                                                   .getSystemColor(SWT.COLOR_RED));

                            if (UiAutomatorModel.getModel().isExploreMode()) {
                                // when we highlight nodes dynamically on mouse move,
                                // use dashed borders
                                e.gc.setLineStyle(SWT.LINE_DASH);
                                e.gc.setLineWidth(1);
                            } else {
                                // when highlighting nodes on tree node selection,
                                // use solid borders
                                e.gc.setLineStyle(SWT.LINE_SOLID);
                                e.gc.setLineWidth(2);
                            }

                            e.gc.drawRectangle(IMG_BORDER +
                                getScaledSize(rect.x),
                                IMG_BORDER + getScaledSize(rect.y),
                                getScaledSize(rect.width),
                                getScaledSize(rect.height));
                        }
                    }
                }
            });
        mScreenshotCanvas.addMouseMoveListener(new MouseMoveListener() {
                @Override
                public void mouseMove(MouseEvent e) {
                    if (UiAutomatorModel.getModel().isExploreMode()) {
                        UiAutomatorModel.getModel()
                                        .updateSelectionForCoordinates(getInverseScaledSize(e.x -
                                IMG_BORDER),
                            getInverseScaledSize(e.y - IMG_BORDER));
                    }
                }
            });

        ToolBarManager toolBarManager = new ToolBarManager(SWT.FLAT);
        toolBarManager.add(mOpenFilesAction);
        toolBarManager.add(mExpandAllAction);
        toolBarManager.add(mScreenshotAction);
        toolBarManager.add(mRecorderAction);
        toolBarManager.createControl(basePane);
        
        ToolBarManager toolBarManager2 = new ToolBarManager(SWT.FLAT);
        toolBarManager2.add(mAddWidgetAction);
        toolBarManager2.add(mExportLmlAction);
        toolBarManager2.add(mGenerateAction);
        toolBarManager2.createControl(basePane);
        
        

        
        mTreeViewer = new TreeViewer(basePane, SWT.BORDER);

        Tree tree = mTreeViewer.getTree();
        GridData gd_Tree = new GridData(SWT.FILL, SWT.FILL, true, true, 1, 1);
        gd_Tree.heightHint = 250;
        gd_Tree.minimumHeight = 250;
        gd_Tree.widthHint = 350;
        tree.setLayoutData(gd_Tree);
        mTreeViewer.setContentProvider(new BasicTreeNodeContentProvider());
        // default LabelProvider uses toString() to generate text to display
        mTreeViewer.setLabelProvider(new LabelProvider());
        mTreeViewer.addSelectionChangedListener(new ISelectionChangedListener() {
                @Override
                public void selectionChanged(SelectionChangedEvent event) {
                    if (event.getSelection().isEmpty()) {
                        UiAutomatorModel.getModel().setSelectedNode(null);
                    } else if (event.getSelection() instanceof IStructuredSelection) {
                        IStructuredSelection selection = (IStructuredSelection) event.getSelection();
                        Object o = selection.toArray()[0];

                        if (o instanceof BasicTreeNode) {
                            UiAutomatorModel.getModel()
                                            .setSelectedNode((BasicTreeNode) o);
                        }
                    }
                }
            });
        // move focus so that it's not on tool bar (looks weird)
        tree.setFocus();
        
      ///////////
      Group grpNodeDetail2 = new Group(basePane, SWT.NONE);
      grpNodeDetail2.setLayout(new FillLayout(SWT.VERTICAL));

      GridData gd_grpNodeDetail2 = new GridData(SWT.FILL, SWT.FILL, true,
    		  true, 1, 2);
      gd_grpNodeDetail2.heightHint = FIXED_DETAIL_VIEW_HEIGHT;
      gd_grpNodeDetail2.minimumHeight = FIXED_DETAIL_VIEW_HEIGHT;
      gd_grpNodeDetail2.widthHint = FIXED_RHS_WIDTH;
      gd_grpNodeDetail2.minimumWidth = FIXED_RHS_WIDTH;
      grpNodeDetail2.setLayoutData(gd_grpNodeDetail2);
      grpNodeDetail2.setText("Seleted Widget");

      Composite tableContainer2 = new Composite(grpNodeDetail2, SWT.NONE);
      tableContainer2.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true,
              true, 1, 1));

      TableColumnLayout columnLayout2 = new TableColumnLayout();
      tableContainer2.setLayout(columnLayout2);

      mTableViewerWidget = CheckboxTableViewer.newCheckList(tableContainer2,
              SWT.MULTI | SWT.BORDER | SWT.FULL_SELECTION);

      Table table2 = mTableViewerWidget.getTable();
      table2.setLinesVisible(true);
      // use ArrayContentProvider here, it assumes the input to the TableViewer
      // is an array, where each element represents a row in the table
      mTableViewerWidget.setContentProvider(new ArrayContentProvider());

      TableViewerColumn tableViewerColumnKey2 = new TableViewerColumn(mTableViewerWidget,
              SWT.NONE);
      
      TableColumn tblclmnKey2 = tableViewerColumnKey2.getColumn();
      
      tableViewerColumnKey2.setLabelProvider(new ColumnLabelProvider() {
              @Override
              public String getText(Object element) {
                  if (element instanceof AttributePair) {
                      // first column, shows the attribute name
                      return ((AttributePair) element).key;
                  }

                  return super.getText(element);
              }
          });
      columnLayout2.setColumnData(tblclmnKey2,
          new ColumnWeightData(1, ColumnWeightData.MINIMUM_WIDTH, true));
      
      TableViewerColumn tableViewerColumnValue2 = new TableViewerColumn(mTableViewerWidget,
              SWT.NONE);
      tableViewerColumnValue2.setEditingSupport(new AttributeTableEditingSupport(
              mTableViewerWidget));

      TableColumn tblclmnValue2 = tableViewerColumnValue2.getColumn();
      columnLayout2.setColumnData(tblclmnValue2,
          new ColumnWeightData(2, ColumnWeightData.MINIMUM_WIDTH, true));
      tableViewerColumnValue2.setLabelProvider(new ColumnLabelProvider() {
              @Override
              public String getText(Object element) {
                  if (element instanceof AttributePair) {
                      // second column, shows the attribute value
                      return ((AttributePair) element).value;
                  }

                  return super.getText(element);
              }
          });
      table2.addListener(SWT.Selection,
              new Listener() {
                  public void handleEvent(Event event) {
                      String string = (event.detail == SWT.CHECK) ? "Checked"
                                                                  : "Selected";
                      System.out.println(event.item + " " + string);
                  }
              });
      
      table2.addKeyListener(new KeyListener() {
          @Override
          public void keyReleased(KeyEvent e) {
              // TODO Auto-generated method stub
			  if (e.keyCode == SWT.DEL) 
			  {
                    table2.remove(table2.getSelectionIndices());
              }
          }

          @Override
          public void keyPressed(KeyEvent e) {
              // TODO Auto-generated method stub
          }
      });
//      table2.setMenu(popupMenu);
      Menu popupMenu = new Menu(table2);
      MenuItem editItem = new MenuItem(popupMenu, SWT.CASCADE);
      editItem.setText("Edit");
      editItem.addSelectionListener(new SelectionListener() {
		
		@Override
		public void widgetSelected(SelectionEvent arg0) {
			// TODO Auto-generated method stub
			System.out.println("Edit");
			TableItem[] selectedItems = table2.getSelection();
			if (selectedItems.length > 0)
			{
				mModifyWidgetAction.run();
			}
			System.out.println("Edited");
			
		}
		
		@Override
		public void widgetDefaultSelected(SelectionEvent arg0) {
			// TODO Auto-generated method stub
			
		}
      });
      MenuItem deleteItem = new MenuItem(popupMenu, SWT.NONE);
      deleteItem.setText("Delete");
      deleteItem.addSelectionListener(new SelectionListener() {
  		
  		@Override
  		public void widgetSelected(SelectionEvent arg0) {
  			// TODO Auto-generated method stub
  			System.out.println("Delete");
  			TableItem[] selectedItems = table2.getSelection();
  			if (selectedItems.length > 0)
  			{
  				mDeleteWidgetAction.run();
  			}
  			System.out.println("Deleted");
  			
  		}
  		
  		@Override
  		public void widgetDefaultSelected(SelectionEvent arg0) {
  			// TODO Auto-generated method stub
  			
  		}
        });
      table2.setMenu(popupMenu);
      
      table2.addMenuDetectListener(new MenuDetectListener() {
		
		@Override
		public void menuDetected(MenuDetectEvent arg0) {
			// TODO Auto-generated method stub
			System.out.println("Edit");
		}
	});
      
      ((CheckboxTableViewer) mTableViewerWidget).addCheckStateListener(new ICheckStateListener() {
          @Override
          public void checkStateChanged(CheckStateChangedEvent event) {
              TableItem[] selections = mTableViewerNode.getTable()
                                                       .getSelection();

              for (TableItem item : selections) {
                  item.setChecked(event.getChecked());
              }
          }
      });
      ///////////////

        Group grpNodeDetail = new Group(basePane, SWT.NONE);
        grpNodeDetail.setLayout(new FillLayout(SWT.HORIZONTAL));

        GridData gd_grpNodeDetail = new GridData(SWT.FILL, SWT.FILL, true,
                true, 1, 1);
        gd_grpNodeDetail.heightHint = FIXED_DETAIL_VIEW_HEIGHT;
        gd_grpNodeDetail.minimumHeight = FIXED_DETAIL_VIEW_HEIGHT;
        gd_grpNodeDetail.widthHint = FIXED_RHS_WIDTH;
        gd_grpNodeDetail.minimumWidth = FIXED_RHS_WIDTH;
        grpNodeDetail.setLayoutData(gd_grpNodeDetail);
        grpNodeDetail.setText("Node Detail");

        Composite tableContainer = new Composite(grpNodeDetail, SWT.NONE);
        tableContainer.setLayoutData(new GridData(SWT.FILL, SWT.FILL, true,
                true, 1, 1));

        TableColumnLayout columnLayout = new TableColumnLayout();
        tableContainer.setLayout(columnLayout);

        mTableViewerNode = CheckboxTableViewer.newCheckList(tableContainer,
                SWT.CHECK | SWT.BORDER | SWT.FULL_SELECTION);

        Table table = mTableViewerNode.getTable();
        table.setLinesVisible(true);
        // use ArrayContentProvider here, it assumes the input to the TableViewer
        // is an array, where each element represents a row in the table
        mTableViewerNode.setContentProvider(new ArrayContentProvider());
        TableViewerColumn tableViewerColumnKey = new TableViewerColumn(mTableViewerNode,
                SWT.NONE);
        TableColumn tblclmnKey = tableViewerColumnKey.getColumn();
        tableViewerColumnKey.setLabelProvider(new ColumnLabelProvider() {
                @Override
                public String getText(Object element) {
                    if (element instanceof AttributePair) {
                        // first column, shows the attribute name
                        return ((AttributePair) element).key;
                    }

                    return super.getText(element);
                }
            });
        columnLayout.setColumnData(tblclmnKey,
            new ColumnWeightData(1, ColumnWeightData.MINIMUM_WIDTH, true));

        TableViewerColumn tableViewerColumnValue = new TableViewerColumn(mTableViewerNode,
                SWT.NONE);
        tableViewerColumnValue.setEditingSupport(new AttributeTableEditingSupport(
                mTableViewerNode));

        TableColumn tblclmnValue = tableViewerColumnValue.getColumn();
        columnLayout.setColumnData(tblclmnValue,
            new ColumnWeightData(2, ColumnWeightData.MINIMUM_WIDTH, true));
        tableViewerColumnValue.setLabelProvider(new ColumnLabelProvider() {
                @Override
                public String getText(Object element) {
                    if (element instanceof AttributePair) {
                        // second column, shows the attribute value
                        return ((AttributePair) element).value;
                    }

                    return super.getText(element);
                }
            });

        table.addListener(SWT.Selection,
            new Listener() {
                public void handleEvent(Event event) {
                    String string = (event.detail == SWT.CHECK) ? "Checked"
                                                                : "Selected";
                    System.out.println(event.item + " " + string);
                }
            });
        
        table.addKeyListener(new KeyListener() {
            @Override
            public void keyReleased(KeyEvent e) {
                // TODO Auto-generated method stub
            }

            @Override
            public void keyPressed(KeyEvent e) {
                // TODO Auto-generated method stub
            }
        });

        ((CheckboxTableViewer) mTableViewerNode).addCheckStateListener(new ICheckStateListener() {
            @Override
            public void checkStateChanged(CheckStateChangedEvent event) {
                TableItem[] selections = mTableViewerNode.getTable()
                                                         .getSelection();

                for (TableItem item : selections) {
                    item.setChecked(event.getChecked());
                }
            }
        });
        
        mAddWidgetAction.setTableViewer(mTableViewerNode);
        mModifyWidgetAction.setTableViewer(mTableViewerWidget);
        mDeleteWidgetAction.setTableViewer(mTableViewerWidget);
        mExportLmlAction.setTableViewer(mTableViewerWidget);
        return basePane;
    }

    public void AddWidgetTableItem(String name, String identify)
    {
    	TableItem item = new TableItem (mTableViewerWidget.getTable(), SWT.NONE);
    	item.setText(0, name);
    	item.setText(1, identify);
		item.setChecked(true);
    }
    
    /**
     * Create the actions.
     */
    private void createActions() {
        mOpenFilesAction = new OpenFilesAction(this);
        mExpandAllAction = new ExpandAllAction(this);
        mScreenshotAction = new ScreenshotAction(this);
        mAddWidgetAction = new AddModWidgetAction(this);
        mModifyWidgetAction = new AddModWidgetAction(this, AddModWidget.MODIFY);
        mDeleteWidgetAction = new AddModWidgetAction(this, AddModWidget.DELETE);
        mExportLmlAction = new ExportDefinedAction(this);
        mRecorderAction = new RecorderAction(this);
        mGenerateAction = new GenerateAction(this);
    }
    
    
    /**
     * Launch the application.
     *
     * @param args
     */
    public static void main(String[] args) {
        try {
            UiAutomatorViewer window = new UiAutomatorViewer();
            window.setBlockOnOpen(true);
            window.open();
            Display.getCurrent().dispose();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Configure the shell.
     *
     * @param newShell
     */
    @Override
    protected void configureShell(Shell newShell) {
        super.configureShell(newShell);
        newShell.setText("UI Automator Viewer");
    }

    /**
     * Asks the Model for screenshot and xml tree data, then populates the screenshot
     * area and tree view accordingly
     */
    public void loadScreenshotAndXml() {
        // re-layout screenshot canvas
        GridData gd = new GridData(SWT.CENTER, SWT.CENTER, true, true, 1, 3);
        Rectangle r = UiAutomatorModel.getModel().getScreenshot().getBounds();
        mScale = calcScreenshotScale(r.width, r.height);
        updateScaledImage(UiAutomatorModel.getModel().getScreenshot());
        gd.minimumHeight = getScaledSize(r.height) + (2 * IMG_BORDER);
        gd.minimumWidth = getScaledSize(r.width) + (2 * IMG_BORDER);
        mScreenshotCanvas.setLayoutData(gd);

        // load xml into tree
        BasicTreeNode wrapper = new BasicTreeNode();
        // putting another root node on top of existing root node
        // because Tree seems to like to hide the root node
        wrapper.addChild(UiAutomatorModel.getModel().getXmlRootNode());
        mTreeViewer.setInput(wrapper);
        mTreeViewer.getTree().setFocus();

        // resize & reposition window
        getShell().pack();
        adjustShellLocation();
    }

    /*
     * Causes a redraw of the canvas.
     *
     * The drawing code of canvas will handle highlighted nodes and etc based on data
     * retrieved from Model
     */
    public void updateScreenshot() {
        mScreenshotCanvas.redraw();
    }

    public void expandAll() {
        mTreeViewer.expandAll();
    }

    public void updateTreeSelection(BasicTreeNode node) {
        mTreeViewer.setSelection(new StructuredSelection(node), true);
    }

    public void loadAttributeTable() {
        // udpate the lower right corner table to show the attributes of the node
        mTableViewerNode.setInput(UiAutomatorModel.getModel().getSelectedNode()
                                              .getAttributesArray());
    }

    @Override
    protected Point getInitialSize() {
        return new Point(1150, 600);
    }

    private float calcScreenshotScale(int width, int height) {
        Rectangle r = findCurrentMonitor().getClientArea();
        // add some room
        width += 300;
        height += 100;

        float scale = Math.min(1.0f,
                Math.min(r.width / (float) width, r.height / (float) height));

        // if we are not showing the original size, scale down a bit more
        if (scale < 1.0f) {
            scale *= 0.7f;
        }

        return scale;
    }

    private int getScaledSize(int size) {
        if (mScale == 1.0f) {
            return size;
        } else {
            return new Double(Math.floor((size * mScale))).intValue();
        }
    }

    private int getInverseScaledSize(int size) {
        if (mScale == 1.0f) {
            return size;
        } else {
            return new Double(Math.floor((size / mScale))).intValue();
        }
    }

    private void updateScaledImage(Image image) {
        Image scaled = image;

        if (mScale != 1.0f) {
            // some voodoo to get a smooth scaled image ,otherwise it looks like crap
            // but the actual outcome could still be platform dependent
            int w = image.getBounds().width;
            int h = image.getBounds().height;
            int ws = getScaledSize(w);
            int hs = getScaledSize(h);
            scaled = new Image(getShell().getDisplay(), ws, hs);

            GC gc = new GC(scaled);
            gc.setAntialias(SWT.ON);
            gc.setInterpolation(SWT.HIGH);
            gc.drawImage(image, 0, 0, w, h, 0, 0, ws, hs);
            gc.dispose();
        }

        if (mCachedScaleImage != null) {
            mCachedScaleImage.dispose();
        }

        mCachedScaleImage = scaled;
    }

    /**
     * Find out which monitor the current window's top left corner is in
     *
     * @return
     */
    private Monitor findCurrentMonitor() {
        Rectangle b = getShell().getBounds();

        for (Monitor m : getShell().getDisplay().getMonitors()) {
            Rectangle r = m.getBounds();

            if ((r.x <= b.x) && (b.x < (r.x + r.width)) && (r.y <= b.y) &&
                    (b.y < (r.y + r.height))) {
                return m;
            }
        }

        return null;
    }

    private void adjustShellLocation() {
        Monitor m = findCurrentMonitor();

        if (m == null) {
            System.err.println("Cannot find current monitor!");

            return;
        }

        Rectangle r = m.getBounds();
        Rectangle b = getShell().getBounds();
        int x = b.x;
        int y = b.y;
        boolean shouldChangePosition = false;

        if (!((r.x <= b.x) && ((b.x + b.width) < (r.x + r.width)))) {
            // out of bounds horizontally, need adjustment
            shouldChangePosition = true;
            // since we are scaling down, the window really shouldn't be larger than monitor
            // i.e. should not have negative here, just a safety measure
            x = Math.max(0, (r.width - b.width) / 2) + r.x;
        }

        if (!((r.y <= b.y) && ((b.y + b.height) < (r.y + r.height)))) {
            // out of bounds vertically, need adjustment
            shouldChangePosition = true;
            y = Math.max(0, (r.height - b.height) / 2) + r.y;
        }

        if (shouldChangePosition) {
            getShell().setLocation(x, y);
        }
    }

    public String getActivityName() {
		return sActivity.substring(1);
	}

	public void setActivityName(String sActivity) {
		this.sActivity = sActivity;
	}

	private class AttributeTableEditingSupport extends EditingSupport {
        private TableViewer mViewer;

        public AttributeTableEditingSupport(TableViewer viewer) {
            super(viewer);
            mViewer = viewer;
        }

        @Override
        protected boolean canEdit(Object arg0) {
            return true;
        }

        @Override
        protected CellEditor getCellEditor(Object arg0) {
            return new TextCellEditor(mViewer.getTable());
        }

        @Override
        protected Object getValue(Object o) {
            return ((AttributePair) o).value;
        }

        @Override
        protected void setValue(Object arg0, Object arg1) {
        }
    }
}
