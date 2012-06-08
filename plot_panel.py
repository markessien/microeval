class PlotPanel (wx.Panel):
    """The PlotPanel has a Figure and a Canvas. OnSize events simply set a 
flag, and the actual resizing of the figure is triggered by an Idle event."""
    def __init__( self, parent, color=None, dpi=None, **kwargs ):
        from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
        from matplotlib.figure import Figure

        # initialize Panel
        if 'id' not in kwargs.keys():
            kwargs['id'] = wx.ID_ANY
        if 'style' not in kwargs.keys():
            kwargs['style'] = wx.NO_FULL_REPAINT_ON_RESIZE
        wx.Panel.__init__( self, parent, **kwargs )

        # initialize matplotlib stuff
        self.figure = Figure( None, dpi )
        self.canvas = FigureCanvasWxAgg( self, -1, self.figure )
        self.SetColor( color )

        self._SetSize()
        self.draw()

        self._resizeflag = False

        self.Bind(wx.EVT_IDLE, self._onIdle)
        self.Bind(wx.EVT_SIZE, self._onSize)

    def SetColor( self, rgbtuple=None ):
        """Set figure and canvas colours to be the same."""
        if rgbtuple is None:
            rgbtuple = wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ).Get()
        clr = [c/255. for c in rgbtuple]
        self.figure.set_facecolor( clr )
        self.figure.set_edgecolor( clr )
        self.canvas.SetBackgroundColour( wx.Colour( *rgbtuple ) )

    def _onSize( self, event ):
        self._resizeflag = True

    def _onIdle( self, evt ):
        if self._resizeflag:
            self._resizeflag = False
            self._SetSize()

    def _SetSize( self ):
        pixels = tuple( self.parent.GetClientSize() )
        self.SetSize( pixels )
        self.canvas.SetSize( pixels )
        self.figure.set_size_inches( float( pixels[0] )/self.figure.get_dpi(),
                                     float( pixels[1] )/self.figure.get_dpi() )

    def draw(self): pass # abstract, to be overridden by child classes


class InfoPanel (PlotPanel):
    """Plots several lines in distinct colors."""
    def __init__( self, parent, point_lists, clr_list, **kwargs ):
        self.parent = parent
        self.point_lists = point_lists
        self.clr_list = clr_list
        
        # initiate plotter
        PlotPanel.__init__( self, parent, **kwargs )
        self.SetColor( (255,255,255) )
        
    def draw( self ):
        """Draw data."""
        if not hasattr( self, 'subplot' ):
            self.subplot = self.figure.add_subplot( 111 )
        

            # self.draw()
        
        """
        for i, pt_list in enumerate( self.point_lists ):
        plot_pts = num.array( pt_list )
        clr = [float( c )/255. for c in self.clr_list[i]]
        # print "Plotting: " + plot_pts[:,0] + " vs " + plot_pts[:,1]
        print "Plotting" + str(i)
        self.line, = self.subplot.plot( plot_pts[:,0], plot_pts[:,1], color=clr )
        """
            
            
            
            
        """
        rad0 = (0.8*theta/(2*num.pi) + 1)
        r0 = rad0*(8 + num.sin( theta*7 + rad0/1.8 ))
        x0 = r0*num.cos( theta )
        y0 = r0*num.sin( theta )
        
        rad1 = (0.8*theta/(2*num.pi) + 1)
        r1 = rad1*(6 + num.sin( theta*7 + rad1/1.9 ))
        x1 = r1*num.cos( theta )
        y1 = r1*num.sin( theta )
        
        #points = [[(xi,yi) for xi,yi in zip( x0, y0 )],
         #       [(xi,yi) for xi,yi in zip( x1, y1 )]]
        points = [[arange(0,10),[9,4,5,2,3,5,7,12,2,3]]]
        clrs = [[225,200,160], [219,112,147]]
        #  , [219,112,147], [(xi,yi) for xi,yi in zip( x1, y1 )]
        chart_panel = wx.Panel(self.parent_win, -1)
        main_area.Add(chart_panel, 1, wx.EXPAND)
        self.graph_panel = InfoPanel(chart_panel, points, clrs )
        
        x = arange(0,100,1)            # x-array
        self.line, = self.graph_panel.subplot.plot(x,sin(x))
        self.line.axes.set_ylim(-5,310)
        # line.set_ydata(x+i)
        self.graph_panel.figure.canvas.draw()
        """