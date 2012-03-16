##########################################################################
#
#  Copyright 2010 Dr D Studios Pty Limited (ACN 127 184 954) (Dr. D Studios),
#  its affiliates and/or its licensors.
#
#  Copyright (c) 2010-2012, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import hou
import IECore
import IECoreHoudini
import unittest
import os

class TestFromHoudiniPolygonsConverter( IECoreHoudini.TestCase ) :

	def createBox( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode("geo", run_init_scripts=False)
		box = geo.createNode( "box" )
		
		return box

	def createTorus( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode("geo", run_init_scripts=False)
		torus = geo.createNode( "torus" )
		
		return torus

	def createPoints( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode("geo", run_init_scripts=False)
		box = geo.createNode( "box" )
		facet = geo.createNode( "facet" )
		facet.parm("postnml").set(True)
		points = geo.createNode( "scatter" )
		facet.setInput( 0, box )
		points.setInput( 0, facet )
		
		return points

	# creates a converter
	def testCreateConverter( self )  :
		box = self.createBox()
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( box )
		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreHoudini.TypeId.FromHoudiniPolygonsConverter ) ) )
		
		return converter

	# creates a converter
	def testFactory( self ) :
		box = self.createBox()
		converter = IECoreHoudini.FromHoudiniGeometryConverter.create( box )
		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreHoudini.TypeId.FromHoudiniPolygonsConverter ) ) )
		
		converter = IECoreHoudini.FromHoudiniGeometryConverter.create( box, IECore.TypeId.MeshPrimitive )
		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreHoudini.TypeId.FromHoudiniPolygonsConverter ) ) )
		
		converter = IECoreHoudini.FromHoudiniGeometryConverter.create( box, IECore.TypeId.Parameter )
		self.assertEqual( converter, None )

	# performs geometry conversion
	def testDoConversion( self ) :
		converter = self.testCreateConverter()
		result = converter.convert()
		self.assert_( result.isInstanceOf( IECore.TypeId.MeshPrimitive ) )

	# convert a mesh
	def testConvertMesh( self ) :
		
		torus = self.createTorus()
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( torus )
		result = converter.convert()
		self.assertEqual( result.typeId(), IECore.MeshPrimitive.staticTypeId() )
		
		bbox = result.bound()
		self.assertEqual( bbox.min.x, -1.5 )
		self.assertEqual( bbox.max.x, 1.5 )
		
		self.assertEqual( result.variableSize( IECore.PrimitiveVariable.Interpolation.Vertex ), 100 )
		self.assertEqual( result.numFaces(), 100 )
		
		self.assertEqual( len( result.verticesPerFace ), 100 )
		for i in range( len( result.verticesPerFace ) ) :
			self.assertEqual( result.verticesPerFace[i], 4 )
		
		self.assertEqual( len( result.vertexIds ), 400 )
		for i in range( len( result.vertexIds ) ) :
			self.assert_( result.vertexIds[i] >= 0 )
			self.assert_( result.vertexIds[i] < 100 )
	
	# test prim/vertex attributes
	def testConvertPrimVertAttributes( self ) :
		torus = self.createTorus()
		geo = torus.parent()

		# add vertex normals
		facet = geo.createNode( "facet", node_name = "add_point_normals" )
		facet.parm("postnml").set(True)
		facet.setInput( 0, torus )

		# add a primitive colour attributes
		primcol = geo.createNode( "primitive", node_name = "prim_colour" )
		primcol.parm("doclr").set(1)
		primcol.parm("diffr").setExpression("rand($PR)")
		primcol.parm("diffg").setExpression("rand($PR+1)")
		primcol.parm("diffb").setExpression("rand($PR+2)")
		primcol.setInput( 0, facet )

		# add a load of different vertex attributes
		vert_f1 = geo.createNode( "attribcreate", node_name = "vert_f1", exact_type_name=True )
		vert_f1.parm("name").set("vert_f1")
		vert_f1.parm("class").set(3)
		vert_f1.parm("value1").setExpression("$VTX*0.1")
		vert_f1.setInput( 0, primcol )

		vert_f2 = geo.createNode( "attribcreate", node_name = "vert_f2", exact_type_name=True )
		vert_f2.parm("name").set("vert_f2")
		vert_f2.parm("class").set(3)
		vert_f2.parm("size").set(2)
		vert_f2.parm("value1").setExpression("$VTX*0.1")
		vert_f2.parm("value2").setExpression("$VTX*0.1")
		vert_f2.setInput( 0, vert_f1 )

		vert_f3 = geo.createNode( "attribcreate", node_name = "vert_f3", exact_type_name=True )
		vert_f3.parm("name").set("vert_f3")
		vert_f3.parm("class").set(3)
		vert_f3.parm("size").set(3)
		vert_f3.parm("value1").setExpression("$VTX*0.1")
		vert_f3.parm("value2").setExpression("$VTX*0.1")
		vert_f3.parm("value3").setExpression("$VTX*0.1")
		vert_f3.setInput( 0, vert_f2 )

		vert_i1 = geo.createNode( "attribcreate", node_name = "vert_i1", exact_type_name=True )
		vert_i1.parm("name").set("vert_i1")
		vert_i1.parm("class").set(3)
		vert_i1.parm("type").set(1)
		vert_i1.parm("value1").setExpression("$VTX*0.1")
		vert_i1.setInput( 0, vert_f3 )

		vert_i2 = geo.createNode( "attribcreate", node_name = "vert_i2", exact_type_name=True )
		vert_i2.parm("name").set("vert_i2")
		vert_i2.parm("class").set(3)
		vert_i2.parm("type").set(1)
		vert_i2.parm("size").set(2)
		vert_i2.parm("value1").setExpression("$VTX*0.1")
		vert_i2.parm("value2").setExpression("$VTX*0.1")
		vert_i2.setInput( 0, vert_i1 )

		vert_i3 = geo.createNode( "attribcreate", node_name = "vert_i3", exact_type_name=True )
		vert_i3.parm("name").set("vert_i3")
		vert_i3.parm("class").set(3)
		vert_i3.parm("type").set(1)
		vert_i3.parm("size").set(3)
		vert_i3.parm("value1").setExpression("$VTX*0.1")
		vert_i3.parm("value2").setExpression("$VTX*0.1")
		vert_i3.parm("value3").setExpression("$VTX*0.1")
		vert_i3.setInput( 0, vert_i2 )

		vert_v3f = geo.createNode( "attribcreate", node_name = "vert_v3f", exact_type_name=True )
		vert_v3f.parm("name").set("vert_v3f")
		vert_v3f.parm("class").set(3)
		vert_v3f.parm("type").set(2)
		vert_v3f.parm("value1").setExpression("$VTX*0.1")
		vert_v3f.parm("value2").setExpression("$VTX*0.1")
		vert_v3f.parm("value3").setExpression("$VTX*0.1")
		vert_v3f.setInput( 0, vert_i3 )

		vertString = geo.createNode( "attribcreate", node_name = "vertString", exact_type_name=True )
		vertString.parm("name").set("vertString")
		vertString.parm("class").set(3)
		vertString.parm("type").set(3)
		vertString.parm("string").set("string $VTX!")
		vertString.setInput( 0, vert_v3f )

		detail_i3 = geo.createNode( "attribcreate", node_name = "detail_i3", exact_type_name=True )
		detail_i3.parm("name").set("detail_i3")
		detail_i3.parm("class").set(0)
		detail_i3.parm("type").set(1)
		detail_i3.parm("size").set(3)
		detail_i3.parm("value1").set(123)
		detail_i3.parm("value2").set(456.789) # can we catch it out with a float?
		detail_i3.parm("value3").set(789)
		detail_i3.setInput( 0, vertString )

		out = geo.createNode( "null", node_name="OUT" )
		out.setInput( 0, detail_i3 )

		# convert it all
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( out )
		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreHoudini.TypeId.FromHoudiniPolygonsConverter ) ) )
		
		result = converter.convert()
		self.assert_( result.isInstanceOf( IECore.TypeId.MeshPrimitive ) )
		
		bbox = result.bound()
		self.assertEqual( bbox.min.x, -1.5 )
		self.assertEqual( bbox.max.x, 1.5 )
		
		self.assertEqual( result.variableSize( IECore.PrimitiveVariable.Interpolation.Vertex ), 100 )
		self.assertEqual( result.numFaces(), 100 )
		
		self.assertEqual( len( result.verticesPerFace ), 100 )
		for i in range( len( result.verticesPerFace ) ) :
			self.assertEqual( result.verticesPerFace[i], 4 )
		
		self.assertEqual( len( result.vertexIds ), 400 )
		for i in range( len( result.vertexIds ) ) :
			self.assert_( result.vertexIds[i] >= 0 )
			self.assert_( result.vertexIds[i] < 100 )
		
		# test point attributes
		self.assert_( "P" in result )
		self.assertEqual( result['P'].data.typeId(), IECore.TypeId.V3fVectorData )
		self.assertEqual( result['P'].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assertEqual( result['P'].data.size(), result.variableSize( IECore.PrimitiveVariable.Interpolation.Vertex ) )
		self.assert_( "N" in result )
		self.assertEqual( result['N'].data.typeId(), IECore.TypeId.V3fVectorData )
		self.assertEqual( result['N'].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assertEqual( result['N'].data.size(), result.variableSize( IECore.PrimitiveVariable.Interpolation.Vertex ) )

		# test detail attributes
		self.assert_( "detail_i3" in result )
		self.assertEqual( result['detail_i3'].data.typeId(), IECore.TypeId.V3iData )
		self.assertEqual( result['detail_i3'].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assertEqual( result['detail_i3'].data.value.x, 123 )
		self.assertEqual( result['detail_i3'].data.value.y, 456 )
		self.assertEqual( result['detail_i3'].data.value.z, 789 )

		# test primitive attributes
		self.assert_( "Cd" in result )
		self.assertEqual( result["Cd"].data.typeId(), IECore.TypeId.Color3fVectorData )
		self.assertEqual( result["Cd"].interpolation, IECore.PrimitiveVariable.Interpolation.Uniform )
		self.assertEqual( result["Cd"].data.size(), result.variableSize( IECore.PrimitiveVariable.Interpolation.Uniform ) )
		
		for i in range( 0, result.variableSize( IECore.PrimitiveVariable.Interpolation.Uniform ) ) :
			for j in range( 0, 3 ) :
				self.assert_( result["Cd"].data[i][j] >= 0.0 )
				self.assert_( result["Cd"].data[i][j] <= 1.0 )

		# test vertex attributes
		attrs = [ "vert_f1", "vert_f2", "vert_f3", "vert_i1", "vert_i2", "vert_i3", "vert_v3f", "vertStringIndices" ]
		for a in attrs :
			self.assert_( a in result )
			self.assertEqual( result[a].interpolation, IECore.PrimitiveVariable.Interpolation.FaceVarying )
			self.assertEqual( result[a].data.size(), result.variableSize( IECore.PrimitiveVariable.Interpolation.FaceVarying ) )
		
		self.assertEqual( result["vert_f1"].data.typeId(), IECore.FloatVectorData.staticTypeId() )
		self.assertEqual( result["vert_f2"].data.typeId(), IECore.V2fVectorData.staticTypeId() )
		self.assertEqual( result["vert_f3"].data.typeId(), IECore.V3fVectorData.staticTypeId() )
		
		for i in range( 0, result.variableSize( IECore.PrimitiveVariable.Interpolation.FaceVarying ) ) :
			for j in range( 0, 3 ) :
				self.assert_( result["vert_f3"].data[i][j] >= 0.0 )
				self.assert_( result["vert_f3"].data[i][j] < 0.4 )
		
		self.assertEqual( result["vert_i1"].data.typeId(), IECore.IntVectorData.staticTypeId() )
		self.assertEqual( result["vert_i2"].data.typeId(), IECore.V2iVectorData.staticTypeId() )
		self.assertEqual( result["vert_i3"].data.typeId(), IECore.V3iVectorData.staticTypeId() )
		
		for i in range( 0, result.variableSize( IECore.PrimitiveVariable.Interpolation.FaceVarying ) ) :
			for j in range( 0, 3 ) :
				self.assertEqual( result["vert_i3"].data[i][j], 0 )
		
		self.assertEqual( result["vert_v3f"].data.typeId(), IECore.V3fVectorData.staticTypeId() )
		
		self.assertEqual( result["vertString"].data.typeId(), IECore.TypeId.StringVectorData )
		self.assertEqual( result["vertString"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assertEqual( result["vertString"].data.size(), 4 )
		self.assertEqual( result["vertStringIndices"].data.typeId(), IECore.TypeId.IntVectorData )
		
		for i in range( 0, result.variableSize( IECore.PrimitiveVariable.Interpolation.FaceVarying ) ) :
			index = result["vertStringIndices"].data[ result.vertexIds[i] ]
			self.assertEqual( result["vertString"].data[ index ], "string %d!" % index )
		
		self.assert_( result.arePrimitiveVariablesValid() )
	
	def testConvertNull( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode("geo", run_init_scripts=False)
		null = geo.createNode( "null" )
		m = IECoreHoudini.FromHoudiniPolygonsConverter( null ).convert()
		self.failUnless( isinstance( m, IECore.MeshPrimitive ) )
		self.assertEqual( m, IECore.MeshPrimitive() )
	
	# convert some points
	def testConvertPoints( self ) :
		points = self.createPoints()
		m = IECoreHoudini.FromHoudiniPolygonsConverter( points ).convert()
		self.failUnless( isinstance( m, IECore.MeshPrimitive ) )
		self.assertEqual( m, IECore.MeshPrimitive() )

	# simple attribute conversion
	def testSetupAttributes( self ) :
		torus = self.createTorus()
		geo = torus.parent()
		attr = geo.createNode( "attribcreate", exact_type_name=True )
		attr.setInput( 0, torus )
		attr.parm("name").set( "test_attribute" )
		attr.parm("type").set(0) # float
		attr.parm("size").set(1) # 1 element
		attr.parm("value1").set(123.456)
		attr.parm("value2").set(654.321)
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( attr )
		result = converter.convert()
		self.assert_( "test_attribute" in result.keys() )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		return attr
	
	# testing point attributes and types
	def testPointAttributes( self ) :
		attr = self.testSetupAttributes()
		
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		attr.parm("value1").set(123.456)
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.FloatVectorData )
		self.assert_( result["test_attribute"].data[0] > 123.0 )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(1) # integer
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.IntVectorData )
		self.assertEqual( result["test_attribute"].data[0], 123 )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(0) # float
		attr.parm("size").set(2) # 2 elementS
		attr.parm("value2").set(456.789)
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V2fVectorData )
		self.assertEqual( result["test_attribute"].data[0], IECore.V2f( 123.456, 456.789 ) )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(1) # int
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V2iVectorData )
		self.assertEqual( result["test_attribute"].data[0], IECore.V2i( 123, 456 ) )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(0) # float
		attr.parm("size").set(3) # 3 elements
		attr.parm("value3").set(999.999)
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V3fVectorData )
		self.assertEqual( result["test_attribute"].data[0],IECore.V3f( 123.456, 456.789, 999.999 ) )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(1) # int
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V3iVectorData )
		self.assertEqual( result["test_attribute"].data[0], IECore.V3i( 123, 456, 999 ) )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set( 3 ) # string
		attr.parm( "string" ).set( "string $PT!" )
		result = IECoreHoudini.FromHoudiniPointsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.StringVectorData )
		self.assertEqual( result["test_attribute"].data[10], "string 10!" )
		self.assertEqual( result["test_attribute"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assertEqual( result["test_attributeIndices"].data.typeId(), IECore.TypeId.IntVectorData )
		self.assertEqual( result["test_attributeIndices"].data[10], 10 )
		self.assertEqual( result["test_attributeIndices"].data.size(), 100 )
		self.assertEqual( result["test_attributeIndices"].interpolation, IECore.PrimitiveVariable.Interpolation.Vertex )
		self.assert_( result.arePrimitiveVariablesValid() )

	# testing detail attributes and types
	def testDetailAttributes( self ) :
		attr = self.testSetupAttributes()
		attr.parm("class").set(0) # detail attribute
		
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		attr.parm("value1").set(123.456)
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.FloatData )
		self.assert_( result["test_attribute"].data > IECore.FloatData( 123.0 ) )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(1) # integer
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.IntData )
		self.assertEqual( result["test_attribute"].data, IECore.IntData( 123 ) )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(0) # float
		attr.parm("size").set(2) # 2 elementS
		attr.parm("value2").set(456.789)
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V2fData )
		self.assertEqual( result["test_attribute"].data.value, IECore.V2f( 123.456, 456.789 ) )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(1) # int
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V2iData )
		self.assertEqual( result["test_attribute"].data.value, IECore.V2i( 123, 456 ) )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(0) # float
		attr.parm("size").set(3) # 3 elements
		attr.parm("value3").set(999.999)
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V3fData )
		self.assertEqual( result["test_attribute"].data.value, IECore.V3f( 123.456, 456.789, 999.999 ) )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set(1) # int
		result = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.V3iData )
		self.assertEqual( result["test_attribute"].data.value, IECore.V3i( 123, 456, 999 ) )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
		attr.parm("type").set( 3 ) # string
		attr.parm( "string" ).set( "string!" )
		result = IECoreHoudini.FromHoudiniPointsConverter( attr ).convert()
		self.assertEqual( result["test_attribute"].data.typeId(), IECore.TypeId.StringData )
		self.assertEqual( result["test_attribute"].data.value, "string!" )
		self.assertEqual( result["test_attribute"].interpolation, IECore.PrimitiveVariable.Interpolation.Constant )
		self.assert_( result.arePrimitiveVariablesValid() )
		
	# testing that float[4] doesn't work!
	def testFloat4attr( self ) : # we can't deal with float 4's right now
		attr = self.testSetupAttributes()
		attr.parm("name").set( "test_attribute" )
		attr.parm("size").set(4) # 4 elements per point-attribute
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( attr )
		result = converter.convert()
		self.assert_( "test_attribute" not in result.keys() ) # invalid due to being float[4]
		self.assert_( result.arePrimitiveVariablesValid() )
		
	# testing conversion of animating geometry
	def testAnimatingGeometry( self ) :
		obj = hou.node( "/obj" )
		geo = obj.createNode( "geo", run_init_scripts=False )
		torus = geo.createNode( "torus" )
		facet = geo.createNode( "facet" )
		facet.parm("postnml").set(True)
		mountain = geo.createNode( "mountain" )
		mountain.parm("offset1").setExpression( "$FF" )
		facet.setInput( 0, torus )
		mountain.setInput( 0, facet )
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( mountain )
		hou.setFrame( 1 )
		mesh1 = converter.convert()
		hou.setFrame( 2 )
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( mountain )
		mesh2 = converter.convert()
		self.assertNotEqual( mesh1["P"].data, mesh2["P"].data )
		self.assertNotEqual( mesh1, mesh2 )

	# testing we can handle an object being deleted
	def testObjectWasDeleted( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode("geo", run_init_scripts=False)
		torus = geo.createNode( "torus" )
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( torus )
		g1 = converter.convert()
		torus.destroy()
		g2 = converter.convert()
		self.assertEqual( g2, g1 )
		self.assertRaises( RuntimeError, IECore.curry( IECoreHoudini.FromHoudiniPolygonsConverter, torus ) )
	
	# testing we can handle an object being deleted
	def testObjectWasDeletedFactory( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode("geo", run_init_scripts=False)
		torus = geo.createNode( "torus" )
		converter = IECoreHoudini.FromHoudiniGeometryConverter.create( torus )
		g1 = converter.convert()
		torus.destroy()
		g2 = converter.convert()
		self.assertEqual( g2, g1 )
		self.assertRaises( RuntimeError, IECore.curry( IECoreHoudini.FromHoudiniGeometryConverter.create, torus ) )

	# testing converting a Houdini particle primitive with detail and point attribs
	def testParticlePrimitive( self ) :
		obj = hou.node("/obj")
		geo = obj.createNode( "geo", run_init_scripts=False )
		popnet = geo.createNode( "popnet" )
		location = popnet.createNode( "location" )
		detailAttr = popnet.createOutputNode( "attribcreate", exact_type_name=True )
		detailAttr.parm("name").set( "float3detail" )
		detailAttr.parm("class").set( 0 ) # detail
		detailAttr.parm("type").set( 0 ) # float
		detailAttr.parm("size").set( 3 ) # 3 elements
		detailAttr.parm("value1").set( 1 )
		detailAttr.parm("value2").set( 2 )
		detailAttr.parm("value3").set( 3 )
		pointAttr = detailAttr.createOutputNode( "attribcreate", exact_type_name=True )
		pointAttr.parm("name").set( "float3point" )
		pointAttr.parm("class").set( 2 ) # point
		pointAttr.parm("type").set( 0 ) # float
		pointAttr.parm("size").set( 3 ) # 3 elements
		pointAttr.parm("value1").set( 1 )
		pointAttr.parm("value2").set( 2 )
		pointAttr.parm("value3").set( 3 )
		
		hou.setFrame( 5 )
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( pointAttr )
		self.assertRaises( RuntimeError, converter.convert )
		
		add = pointAttr.createOutputNode( "add" )
		add.parm( "keep" ).set( 1 ) # deletes primitive and leaves points
		
		m = IECoreHoudini.FromHoudiniPolygonsConverter( add ).convert()
		self.failUnless( isinstance( m, IECore.MeshPrimitive ) )
		self.assertEqual( m, IECore.MeshPrimitive() )
	
	# testing winding order
	def testWindingOrder( self ) :
		obj = hou.node( "/obj" )
		geo = obj.createNode( "geo", run_init_scripts=False )
		grid = geo.createNode( "grid" )
		grid.parm( "rows" ).set( 2 )
		grid.parm( "cols" ).set( 2 )
		
		mesh = IECoreHoudini.FromHoudiniPolygonsConverter( grid ).convert()
		p = mesh["P"].data
		vertexIds = mesh.vertexIds
		self.assertEqual( vertexIds.size(), 4 )
		
		loop = IECore.V3fVectorData( [ p[vertexIds[0]], p[vertexIds[1]], p[vertexIds[2]], p[vertexIds[3]] ] )
		self.assert_( IECore.polygonNormal( loop ).equalWithAbsError( IECore.V3f( 0, 1, 0 ), 0.0001 ) )
	
	# testing vertex data order
	def testVertexDataOrder( self ) :
		obj = hou.node( "/obj" )
		geo = obj.createNode( "geo", run_init_scripts=False )
		grid = geo.createNode( "grid" )
		grid.parm( "rows" ).set( 2 )
		grid.parm( "cols" ).set( 2 )
		attr = grid.createOutputNode( "attribcreate", exact_type_name=True )
		attr.parm("name").set( "vertex" )
		attr.parm("class").set( 3 ) # vertex
		attr.parm("type").set( 0 ) # float
		attr.parm("value1").setExpression( "$VTX" )
		
		mesh = IECoreHoudini.FromHoudiniPolygonsConverter( attr ).convert()
		self.assertEqual( mesh["vertex"].data, IECore.FloatVectorData( [ 3, 2, 1, 0 ] ) )
	
	def testEmptyStringAttr( self ) :
		torus = self.createTorus()
		geo = torus.parent()
		attr = geo.createNode( "attribcreate", exact_type_name=True )
		attr.setInput( 0, torus )
		attr.parm("name").set( "test_attribute" )
		attr.parm("type").set(3) # string
		attr.parm("string").set("")
		converter = IECoreHoudini.FromHoudiniPolygonsConverter( attr )
		result = converter.convert()
		self.assert_( "test_attribute" in result.keys() )
		self.assert_( "test_attributeIndices" in result.keys() )
		self.assertEqual( result["test_attribute"].data.size(), 1 )
		self.assertEqual( result["test_attributeIndices"].data.size(), 100 )
		self.assertEqual( result["test_attribute"].data[0], "" )
		for i in range( 0, 100 ) :
			self.assertEqual( result["test_attributeIndices"].data[i], 0 )
		
		self.assert_( result.arePrimitiveVariablesValid() )
	
	def testGroupName( self ) :
		
		torus = self.createTorus()
		group = torus.createOutputNode( "group" )
		group.parm( "crname" ).set( "testGroup" )
		result = IECoreHoudini.FromHoudiniPolygonsConverter( group ).convert()
		self.assertEqual( result.blindData()['name'].value, "testGroup" )

if __name__ == "__main__":
    unittest.main()