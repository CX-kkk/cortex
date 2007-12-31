//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2007, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//     * Redistributions of source code must retain the above copyright
//       notice, this list of conditions and the following disclaimer.
//
//     * Redistributions in binary form must reproduce the above copyright
//       notice, this list of conditions and the following disclaimer in the
//       documentation and/or other materials provided with the distribution.
//
//     * Neither the name of Image Engine Design nor the names of any
//       other contributors to this software may be used to endorse or
//       promote products derived from this software without specific prior
//       written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "boost/static_assert.hpp"

#include "IECore/TypedPrimitiveOp.h"
#include "IECore/CompoundObject.h"
#include "IECore/CompoundParameter.h"
#include "IECore/PrimitiveOp.h"
#include "IECore/NullObject.h"
#include "IECore/MeshPrimitive.h"

using namespace IECore;

template<typename T>
TypedPrimitiveOp<T>::TypedPrimitiveOp( const std::string name, const std::string description )
	:	PrimitiveOp( name, description )
{
}

template<typename T>
TypedPrimitiveOp<T>::~TypedPrimitiveOp()
{
}

template<typename T>
void TypedPrimitiveOp<T>::modifyPrimitive( PrimitivePtr primitive, ConstCompoundObjectPtr operands )
{
	typename T::Ptr typedPrimitive = boost::dynamic_pointer_cast<T>( primitive );
	
	// Parameter validation should ensure that this is object is of the correct type, hence the assertion
	assert( typedPrimitive );

	modifyTypedPrimitive( typedPrimitive, operands );
}

template<typename T>
TypeId TypedPrimitiveOp<T>::primitiveType() const
{
	return T::staticTypeId();
}

template <typename T> 
TypeId TypedPrimitiveOp<T>::typeId() const
{
	return staticTypeId();
}

template <typename T> 
TypeId TypedPrimitiveOp<T>::staticTypeId()
{
	BOOST_STATIC_ASSERT( sizeof(T) == 0 ); // this function must be specialised for each type!
	return InvalidTypeId;
}

template <typename T> 
std::string TypedPrimitiveOp<T>::typeName() const
{
	return staticTypeName();
}

template <typename T> 
std::string TypedPrimitiveOp<T>::staticTypeName()
{
	BOOST_STATIC_ASSERT( sizeof(T) == 0 ); // this function must be specialised for each type!
	return "";
}

template<typename T>
bool TypedPrimitiveOp<T>::isInstanceOf( TypeId typeId ) const
{
	if( typeId==staticTypeId() )
	{
		return true;
	}
	return PrimitiveOp::isInstanceOf( typeId );
}

template<typename T>
bool TypedPrimitiveOp<T>::isInstanceOf( const std::string &typeName ) const
{
	if( typeName==staticTypeName() )
	{
		return true;
	}
	return PrimitiveOp::isInstanceOf( typeName );
}

template<typename T>
bool TypedPrimitiveOp<T>::inheritsFrom( TypeId typeId )
{
	return PrimitiveOp::staticTypeId()==typeId ? true : PrimitiveOp::inheritsFrom( typeId );
}

template<typename T>
bool TypedPrimitiveOp<T>::inheritsFrom( const std::string &typeName )
{
	return PrimitiveOp::staticTypeName()==typeName ? true : PrimitiveOp::inheritsFrom( typeName );
}

#define IE_CORE_DEFINETYPEDPRIMITIVEOPSPECIALISATION( T, TNAME ) \
 \
	template<> \
	TypeId TypedPrimitiveOp<T>::staticTypeId() \
	{ \
		return TNAME ## TypeId; \
	} \
 \
	template<> \
	std::string TypedPrimitiveOp<T>::staticTypeName() \
	{ \
		return # TNAME; \
	} \
 \
	template class TypedPrimitiveOp<T>;
	
namespace IECore
{
IE_CORE_DEFINETYPEDPRIMITIVEOPSPECIALISATION( MeshPrimitive, MeshPrimitiveOp );
}	
