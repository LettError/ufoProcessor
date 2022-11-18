# Designspaces and python

Designspaces can do different things in different processes. Maybe you want to generate a variable font. Maybe you want to generate UFOs. Maybe you want to resample an existing designspace into something else. 
While [fonttools.designspacelib](https://fonttools.readthedocs.io/en/latest/designspaceLib/index.html) contains the basic objects to construct, read and write designspaces, the [ufoProcessor package](https://github.com/LettError/ufoProcessor) can also generate instances. 

## Basics
First I have to make a `DesignSpaceDocument` object. This is an empty container, it has no masters, no axes, no path.

    from fontTools.designspaceLib import *
    ds = DesignSpaceDocument()
        
Now I will add an axis to the document by making an `AxisDescriptor` object and adding some values to its attributes.

    ad = AxisDescriptor()
    ad.name = "weight" # readable name
    ad.tag = "wght" 	 # 4 letter tag
    ad.minimum = 200
    ad.maximum = 1000
    ad.default = 400

Finally we add the axisDescriptor to the document:

    ds.addAxis(ad)
    print(ds)
    path = "my.designspace"
    ds.write(path)

This writes a very small designspace file:   
    
    <?xml version='1.0' encoding='UTF-8'?>
        <designspace format="4.0">
        <axes>
            <axis tag="wght" name="weight" minimum="200" maximum="1000" default="400"/>
        </axes>
    </designspace>

Let's add some sources to the designspace: this needs the absolute path to the file (usually a ufo). When the document is saved the paths will be written as relative to the designspace document. A `SourceDescriptor` object has a lot of attributes, but `path` and `location` are the most important ones.

    s1 = SourceDescriptor()
    s1.path = "geometryMaster1.ufo"
    s1.location = dict(weight=200)
    ds.addSource(s1)

    s2 = SourceDescriptor()
    s2.path = "geometryMaster2.ufo"
    s2.location = dict(weight=1000)
    ds.addSource(s2)

Let's add some instances. Instances are specific locations in the designspace with names and sometimes paths associated with them. In a variable font you might want these to show up as styles in a menu. But you could also generate UFOs from them.

    for w in [ad.minimum, .5*(ad.minimum + ad.default), ad.default, .5*(ad.maximum + ad.default), ad.maximum]:
        # you will probably know more compact
        # and easier ways to write this, go ahead!
        i = InstanceDescriptor()
        i.fileName = "InstanceFamily"
        i.styleName = "Weight_%d" % w
        i.location = dict(weight = w)
        i.filename = "instance_%s.ufo" % i.styleName
        ds.addInstance(i)
        
The XML now has all it needs: an axis, some sources and ome instances.

	<?xml version='1.0' encoding='UTF-8'?>
	<designspace format="4.0">
	  <axes>
	    <axis tag="wght" name="weight" minimum="200" maximum="1000" default="400"/>
	  </axes>
	  <sources>
	    <source filename="geometryMaster1.ufo">
	      <location>
	        <dimension name="weight" xvalue="200"/>
	      </location>
	    </source>
	    <source filename="geometryMaster2.ufo">
	      <location>
	        <dimension name="weight" xvalue="1000"/>
	      </location>
	    </source>
	  </sources>
	  <instances>
	    <instance stylename="Weight_200" filename="instance_Weight_200.ufo">
	      <location>
	        <dimension name="weight" xvalue="200"/>
	      </location>
	      <kerning/>
	      <info/>
	    </instance>
	    <instance stylename="Weight_300" filename="instance_Weight_300.ufo">
	      <location>
	        <dimension name="weight" xvalue="300"/>
	      </location>
	      <kerning/>
	      <info/>
	    </instance>
	    <instance stylename="Weight_400" filename="instance_Weight_400.ufo">
	      <location>
	        <dimension name="weight" xvalue="400"/>
	      </location>
	      <kerning/>
	      <info/>
	    </instance>
	    <instance stylename="Weight_700" filename="instance_Weight_700.ufo">
	      <location>
	        <dimension name="weight" xvalue="700"/>
	      </location>
	      <kerning/>
	      <info/>
	    </instance>
	    <instance stylename="Weight_1000" filename="instance_Weight_1000.ufo">
	      <location>
	        <dimension name="weight" xvalue="1000"/>
	      </location>
	      <kerning/>
	      <info/>
	    </instance>
	  </instances>
	</designspace>

Whoop well done.

