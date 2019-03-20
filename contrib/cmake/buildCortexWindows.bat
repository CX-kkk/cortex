rem We hide the CMakeLists.txt here and copy it to root so it works correctly
set ROOT_DIR=%~dp0%..\..

mkdir %BUILD_DIR%\doc\licenses
copy LICENSE %BUILD_DIR%\doc\licenses\cortex

mkdir %ROOT_DIR%\gafferBuild
cd %ROOT_DIR%\gafferBuild
del /f CMakeCache.txt

set ARNOLD_OPTIONS=
set USE_ARNOLD=0
if "%ARNOLD_ROOT%" NEQ "" (
	set USE_ARNOLD=1
)

set CMAKE_GENERATOR="Visual Studio 15 2017 Win64"

if not "%1" == "" (
	set BUILD_TYPE=%1
) else (
	set BUILD_TYPE=RELEASE
)

cmake -Wno-dev -G %CMAKE_GENERATOR% ^
-DCMAKE_BUILD_TYPE=%BUILD_TYPE% ^
-DCMAKE_INSTALL_PREFIX=%BUILD_DIR% ^
-DBOOST_LOCATION=%BUILD_DIR% ^
-DPYTHON_LIBRARY=%BUILD_DIR%\lib ^
-DPYTHON_INCLUDE_DIR=%BUILD_DIR%\include ^
-DILMBASE_LOCATION=%BUILD_DIR% ^
-DOPENEXR_LOCATION=%BUILD_DIR% ^
-DWITH_IECORE_GL=1 -DWITH_IECORE_IMAGE=1 ^
-DWITH_IECORE_SCENE=1 ^
-DWITH_IECORE_VDB=1 ^
-DOPENVDB_ROOT=%BUILD_DIR% ^
-DWITH_IECORE_ALEMBIC=1 ^
-DALEMBIC_ROOT=%BUILD_DIR% ^
-DWITH_IECORE_APPLESEED=1 ^
-DAPPLESEED_INCLUDE_DIR=%BUILD_DIR%\appleseed\include ^
-DAPPLESEED_LIBRARY=%BUILD_DIR%\appleseed\lib\appleseed.lib ^
-DOPENVDB_LOCATION=%BUILD_DIR% ^
-DBLOSC_LOCATION=%BUILD_DIR% ^
-DWITH_IECORE_ARNOLD=%USE_ARNOLD% ^
-DARNOLD_ROOT=%ARNOLD_ROOT% ^
%ROOT_DIR%\contrib\cmake

if %ERRORLEVEL% NEQ 0 (exit /b %ERRORLEVEL%)
cmake --build . --config %BUILD_TYPE% --target install
if %ERRORLEVEL% NEQ 0 (exit /b %ERRORLEVEL%)