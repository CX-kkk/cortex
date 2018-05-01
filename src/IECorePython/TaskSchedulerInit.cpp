//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2018, Image Engine Design Inc. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//      * Redistributions of source code must retain the above
//        copyright notice, this list of conditions and the following
//        disclaimer.
//
//      * Redistributions in binary form must reproduce the above
//        copyright notice, this list of conditions and the following
//        disclaimer in the documentation and/or other materials provided with
//        the distribution.
//
//      * Neither the name of Image Engine Design Inc nor the names of
//        any other contributors to this software may be used to endorse or
//        promote products derived from this software without specific prior
//        written permission.
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

#include "boost/python.hpp"

#include "IECorePython/TaskSchedulerInit.h"

#include "tbb/tbb.h"

using namespace boost::python;

namespace
{

// Wraps task_scheduler_init so it can be used as a python
// context manager.
class TaskSchedulerInitWrapper : public tbb::task_scheduler_init
{

	public :

		TaskSchedulerInitWrapper( int max_threads )
			:	tbb::task_scheduler_init( deferred ), m_maxThreads( max_threads )
		{
			if( max_threads != automatic && max_threads <= 0 )
			{
				PyErr_SetString( PyExc_ValueError, "max_threads must be either automatic or a positive integer" );
				throw_error_already_set();
			}
		}

		void enter()
		{
			initialize( m_maxThreads );
		}

		bool exit( boost::python::object excType, boost::python::object excValue, boost::python::object excTraceBack )
		{
			terminate();
			return false; // don't suppress exceptions
		}

	private :

		int m_maxThreads;

};

} // namespace


void IECorePython::bindTaskSchedulerInit()
{
	object tsi = class_<TaskSchedulerInitWrapper, boost::noncopyable>( "tbb_task_scheduler_init", no_init )
		.def( init<int>( arg( "max_threads" ) = int( tbb::task_scheduler_init::automatic ) ) )
		.def( "__enter__", &TaskSchedulerInitWrapper::enter, return_self<>() )
		.def( "__exit__", &TaskSchedulerInitWrapper::exit )
	;
	tsi.attr( "automatic" ) = int( tbb::task_scheduler_init::automatic );
}

