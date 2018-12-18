##########################################################################
#
#  Copyright (c) 2014, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
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

import unittest

import IECore

class StringAlgoTest( unittest.TestCase ) :

	def testMatch( self ) :

		for s, p, r in [
			( "", "", True ),
			( "a", "a", True ),
			( "a", "*", True ),
			( "ab", "a*", True ),
			( "cat", "dog", False ),
			( "dogfish", "*fish", True ),
			( "dogcollar", "*fish", False ),
			( "dog collar", "dog collar", True ),
			( "dog collar", "dog co*", True ),
			( "dog collar", "dog *", True ),
			( "dog collar", "dog*", True ),
			( "cat", "ca?", True ),
			( "", "?", False ),
			( "?", "?", True ),
			( "a", "[abc]", True ),
			( "catA", "cat[ABC]", True ),
			( "catD", "cat[A-Z]", True ),
			( "cars", "ca[rb]s", True ),
			( "cabs", "ca[rb]s", True ),
			( "cats", "ca[rb]s", False ),
			( "catD", "cat[CEF]", False ),
			( "catD", "cat[!CEF]", True ),
			( "cars", "ca[!r]s", False ),
			( "cabs", "ca[!r]s", True ),
			( "catch22", "c*[0-9]2", True ),
			( "x", "[0-9]", False ),
			( "x", "[!0-9]", True ),
			( "x", "[A-Za-z]", True ),
			# We should treat a leading or trailing
			# '-' as a regular character and not
			# a range specifier.
			( "_", "[-|]", False ),
			( "_", "[!-|]", True ),
			( "-", "[!-]", False ),
			( "x-", "x[d-]", True ),
			( "hyphen-ated", "*[-]ated", True ),
			# The following are mildly confusing, because we
			# must type two backslashes to end up with a single
			# backslash in the string literals we're constructing.
			( "\\", "\\\\", True ),   # \ matches \\
			( "d\\", "d\\\\", True ), # d\ matches d\\
			( "*", "\\*", True ),     # * matches \*
			( "a*", "a\\*", True ),   # a* matches a\*
			( "a", "\\a", True ),     # a matches \a
			( "\\", "\\x", False ),   # \ doesn't match \x
			( "?", "\\?", True ),     # ? matches \?
		] :

			if r :
				self.assertTrue( IECore.StringAlgo.match( s, p ), '"{0}" should match "{1}"'.format( s, p ) )
			else :
				self.assertFalse( IECore.StringAlgo.match( s, p ), '"{0}" shouldn\'t match "{1}"'.format( s, p ) )

			if " " not in s :
				self.assertEqual( IECore.StringAlgo.matchMultiple( s, p ), r )

	def testMatchMultiple( self ) :

		for s, p, r in [
			( "", "", True ),
			( "a", "b a", True ),
			( "a", "c *", True ),
			( "ab", "c a*", True ),
			( "cat", "dog fish", False ),
			( "cat", "cad cat", True ),
			( "cat", "cad ", False ),
			( "cat", "cat ", True ),
			( "cat", "cadcat", False ),
			( "dogfish", "cat *fish", True ),
			( "dogcollar", "dog *fish", False ),
			( "dogcollar", "dog collar", False ),
			( "a1", "*1 b2", True ),
			( "abc", "a*d abc", True ),
			( "a", "a? a", True ),
			( "ab", "x? ab", True ),
			( "ab", "?x ab", True ),
			( "a1", "\\x a1", True ),
			( "R", "[RGB] *.[RGB]", True ),
			( "diffuse.R", "[RGB] *.[RGB]", True ),
			( "diffuse.A", "[RGB] *.[RGB]", False ),
		] :

			if r :
				self.assertTrue( IECore.StringAlgo.matchMultiple( s, p ), '"{0}" should match "{1}"'.format( s, p ) )
			else :
				self.assertFalse( IECore.StringAlgo.matchMultiple( s, p ), '"{0}" shouldn\'t match "{1}"'.format( s, p ) )

	def testHasWildcards( self ) :

		for p, r in [
			( "", False ),
			( "a", False ),
			( "*", True ),
			( "a*", True ),
			( "a**", True ),
			( "a*b", True ),
			( "*a", True ),
			( "\\", True ),
			( "?", True ),
			( "\\?", True ),
			( "[abc]", True ),
		] :

			if r :
				self.assertTrue( IECore.StringAlgo.hasWildcards( p ), "{0} has wildcards".format( p ) )
			else :
				self.assertFalse( IECore.StringAlgo.hasWildcards( p ), "{0} doesn't have wildcards".format( p ) )

	def testMatchPaths( self ) :

		self.assertTrue( IECore.StringAlgo.match( [ "a", "b", "c" ], [ "a", "b", "c" ] ) )
		self.assertTrue( IECore.StringAlgo.match( [ "a", "b", "c" ], [ "a", "b", "*" ] ) )
		self.assertTrue( IECore.StringAlgo.match( [ "a", "b", "c" ], [ "*", "*", "*" ] ) )

		self.assertFalse( IECore.StringAlgo.match( [ "a", "b", "c" ], [ "a", "b", "d" ] ) )
		self.assertFalse( IECore.StringAlgo.match( [ "a", "b", "c" ], [ "*" ] ) )

	def testMatchPatternPath( self ) :

		self.assertEqual( IECore.StringAlgo.matchPatternPath( "/a/.../b*/d" ), [ "a", "...", "b*", "d" ] )
		self.assertEqual( IECore.StringAlgo.matchPatternPath( "" ), [] )
		self.assertEqual( IECore.StringAlgo.matchPatternPath( "a.b.c", separator = "." ), [ "a", "b", "c" ] )
		self.assertEqual( IECore.StringAlgo.matchPatternPath( "a...b", separator = "." ), [ "a", "...", "b" ] )

if __name__ == "__main__":
	unittest.main()
